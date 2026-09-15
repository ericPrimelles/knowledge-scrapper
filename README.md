# Knowledge Scraper

Containerized web-content extraction service built with FastAPI, Playwright, BeautifulSoup, NGINX, and AWS ECS Fargate.

> **Project status:** This repository is part of an experimental real-estate platform that is no longer under active development. It is published as a technical portfolio project and should not be considered production-ready.

The service was designed to provide an AI agent with additional context from public web pages. It accepts a collection of URLs, retrieves browser-rendered content, removes common page noise, extracts readable text, and passes the collected information through a summarization layer.

## Architecture

```text
                      Internet
                         │
                         ▼
                ┌─────────────────┐
                │ Application     │
                │ Load Balancer   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      NGINX      │
                │  Reverse Proxy  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     FastAPI     │
                │   Scraper API   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   Playwright    │
                │    Chromium     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ BeautifulSoup   │
                │ Content Cleanup │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Summarization  │
                └─────────────────┘
```

NGINX and the FastAPI application run as separate containers within the same ECS Fargate task.

## Scraping Pipeline

The API accepts a list of URLs through the `/scrapper` endpoint.

For each URL, the service:

1. checks the site's `robots.txt` rules
2. skips explicitly excluded domains
3. loads the page using headless Chromium through Playwright
4. retrieves the rendered HTML
5. removes scripts, navigation, forms, popups, advertisements, and other common page noise
6. extracts and normalizes visible text
7. aggregates successfully retrieved content
8. sends the resulting text to the summarization layer

Individual page failures are isolated so that one inaccessible URL does not prevent the remaining URLs from being processed.

## API

The application exposes a small FastAPI interface.

### Content extraction

```http
POST /scrapper
```

Example request:

```json
{
  "urls": [
    "https://example.com/page-one",
    "https://example.com/page-two"
  ]
}
```

### Health check

```http
GET /health
```

The health endpoint is also used by the container and load-balancer infrastructure.

## Container Architecture

The application is packaged into two containers:

**FastAPI / Playwright**

Runs the Python API, Chromium browser automation, HTML processing, and summarization workflow.

**NGINX**

Provides the external HTTP entry point and reverse-proxies requests to the FastAPI application.

The same services can be run locally using Docker Compose.

```bash
docker compose up --build
```

## AWS Deployment

The cloud deployment is defined with AWS CloudFormation.

The stack provisions:

* Amazon ECS cluster
* AWS Fargate task and service
* Application Load Balancer
* target group and listener
* security groups
* CloudWatch log groups
* ECS task execution IAM role

The Fargate task runs the NGINX and scraper containers together, with the load balancer forwarding external traffic to NGINX.

Container Insights is enabled on the ECS cluster, and application/container logs are sent to CloudWatch.

## Infrastructure Flow

```text
Application Load Balancer
          │
          ▼
     ECS Fargate Task
          │
    ┌─────┴─────┐
    │           │
  NGINX      FastAPI
                │
                ▼
          Playwright
          + Chromium
                │
                ▼
        Content Cleanup
                │
                ▼
          Summarization
```

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml
├── api/
│   ├── app/
│   │   ├── main.py
│   │   ├── scrapper.py
│   │   ├── openai_summary.py
│   │   ├── prompt.py
│   │   └── requirements.txt
│   └── dockerfile
├── nginx/
│   ├── dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── template.yml
```

## Technologies

**Backend:** Python, FastAPI, Gunicorn, Uvicorn
**Browser Automation:** Playwright, Chromium
**HTML Processing:** BeautifulSoup, lxml
**Containers:** Docker, Docker Compose, NGINX
**AWS:** ECS, Fargate, Application Load Balancer, CloudWatch, IAM
**Infrastructure as Code:** AWS CloudFormation, YAML
**CI/CD:** GitHub Actions

## Project Context

This service was developed as part of an experimental AI-assisted real-estate platform.

Its purpose was to separate browser-based content retrieval from the AI agent itself. The agent could discover relevant public sources while this service handled browser execution, extraction, cleanup, and summarization as an independently deployable containerized workload.
