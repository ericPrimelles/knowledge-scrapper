import requests, json
from urllib.parse import urlparse
from robotexclusionrulesparser import RobotExclusionRulesParser
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from openai_summary import summarize
def is_allowed(url, user_agent='DvstScrapperBot'):
    parsed =  urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    resp = requests.get(robots_url, timeout=5)

    if resp.status_code !=200:
        return True
    
    parser = RobotExclusionRulesParser()
    parser.parse(resp.text)
    return parser.is_allowed(user_agent, url)

def clean_html_content(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, head, footer, nav, and ads
    for tag in soup(['script', 'style', 'head', 'footer', 'nav', 'noscript', 'iframe', 'form', 'svg']):
        tag.decompose()

    # Remove common class/id based noise
    for attr in ['class', 'id']:
        for keyword in ['footer', 'header', 'nav', 'popup', 'modal', 'ads', 'subscribe', 'login', 'banner']:
            for tag in soup.find_all(attrs={attr: lambda x: x and keyword in x.lower()}):
                tag.decompose()

    # Extract visible text
    text = soup.get_text(separator=' ', strip=True)

    # Collapse whitespace
    clean_text = ' '.join(text.split())

    return clean_text

async def scrapper_routine(event, context):
    try:
        urls = event.get('urls', [])
        actionGroup = event.get('actionGroup', None)
        fnc = event.get('function', None)
        responses = []
        if not urls:
            return []
        for url in urls:
            if not is_allowed(url) or 'zillow.com' in url or 'realtor.com' in url:
                continue
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
                )
                page = await context.new_page()
                await page.goto(url)
                content = await page.content()
                await browser.close()
                clean_content = clean_html_content(content)
                responses.append(clean_content)
        responses = ",".join(responses)
        result =  {"data" : summarize(responses)}
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {
            "Error" : str(e)
        }


