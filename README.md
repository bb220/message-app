# FastAPI Messaging App

A messaging application integrated with OpenAI's Responses API.

## Features

- **Persistent Storage**: SQLite Database, using SQLAlchemy ORM
- **Logging**: Logging with middleware for request durations
- **API Key Authentication**: Header-based auth for protected endpoints
- **Slack Integration**: Event webhook handler and signature verification

## Getting Started

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure environment variables**

   Create a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_SIGNING_SECRET=your_slack_signing_secret
   API_KEY=your_custom_api_key
   ```

3. **Run the application**
   ```bash
   uv run uvicorn main:app --reload
   ```

## Endpoints

- `GET /` - Health check
- `GET /messages` - Retrieve all messages
- `POST /sms` - Send a message and receive AI response
- `POST /slack/events` - Slack webhook handler for slackbot integration.

## Quick Start

```bash
# Send a message to the chatbot
curl -s -X POST http://127.0.0.1:8000/sms \
    -H 'Content-Type: application/json' \
    -H 'x-api-key: <API_KEY>' \
    -d '{"message": "What is the capital of Montana?"}'

# Retrieve message history
curl -s -H 'x-api-key: <API_KEY>' http://127.0.0.1:8000/messages
```
#### Slack
After configuring the slack application in your workspace, @ or DM your slackbot and receive AI response.

---

🏄 [brandonbellero](https://www.brandonbellero.com/)
