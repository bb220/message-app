import logging
import time
from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from openai.types.responses.response_input_param import ResponseInputParam
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from database import init_db, get_session, Message


class Settings(BaseSettings):
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Load settings
settings = Settings()

# Logger instance
logger = logging.getLogger(__name__)

# Initialize database
init_db() 

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


class SMSRequest(BaseModel):
    message: str


class MessageRecord(BaseModel):
    timestamp: str
    user_message: str
    assistant_response: str

# Middleware to log request durations
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url} completed_in={duration:.4f}s status_code={response.status_code}")
    return response

@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/messages")
def get_messages():
    """Retrieve all stored messages."""

    session = get_session()
    try:
        # Query all messages from the database
        messages = session.query(Message).all()
        return {"messages": [msg.to_dict() for msg in messages]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        session.close()

    

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

    session = get_session()
    try:
        try:
            # Load previous messages from the database
            db_messages = session.query(Message).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # Add previous messages to conversation
        for msg in db_messages:
            conversation.append({"role": msg.role, "content": msg.content})

        # Add current message
        conversation.append({"role": "user", "content": payload.message})

        # Call OpenAI Responses API
        try:
            response = openai_client.responses.create(
                model="gpt-4.1", input=conversation
            )

            assistant_message = response.output_text

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error calling OpenAI API: {str(e)}"
            )

        try:
            # Save messages to the database
            user_msg = Message(
                role="user",
                content=payload.message
            )
            assistant_msg = Message(
                role="assistant",
                content=assistant_message
            )
            
            messages = [user_msg, assistant_msg]
            session.add_all(messages)
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving messages to database: {str(e)}")

        return {"response": assistant_message}
    
    finally:
        session.close()
