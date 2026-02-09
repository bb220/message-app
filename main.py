from typing import List

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam
from openai.types.responses.response_input_param import ResponseInputParam
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Load settings
settings = Settings()

app = FastAPI(title="basic-app")

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)

# In-memory message storage
messages_store: List[EasyInputMessageParam] = []


class SMSRequest(BaseModel):
    message: str


class MessageRecord(BaseModel):
    timestamp: str
    user_message: str
    assistant_response: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/messages")
def get_messages():
    """Retrieve all stored messages."""
    return {"messages": messages_store}

SYSTEM_PROMPT = """
You are a helpful assistant responding to messages. Keep responses concise and friendly.
"""

@app.post("/sms")
def receive_sms(payload: SMSRequest):
    if not payload.message:
        raise HTTPException(status_code=400, detail="message is required")

    # Build conversation history
    conversation: ResponseInputParam = [
        {
            "role": "developer",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Add previous messages to conversation
    for record in messages_store:
        conversation.append(record)

    # Add current message
    conversation.append({"role": "user", "content": payload.message})

    # Call OpenAI Responses API
    try:
        response = openai_client.responses.create(
            model="gpt-4.1", input=conversation
        )

        assistant_message = response.output_text

        # Store the message exchange (messages only)
        messages_store.append({"role": "user", "content": payload.message})
        messages_store.append({"role": "assistant", "content": assistant_message})

        return {"response": assistant_message}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling OpenAI API: {str(e)}"
        )
