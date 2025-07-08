import openai
import os

from prompt import prompt

def summarize(content):
    openai_api_key = os.getenv('OPENAI_APIKEY')
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        temperature=0.3
    )

    # ✅ Access the content properly (via attribute, not subscript)
    return response.choices[0].message.content.strip()
