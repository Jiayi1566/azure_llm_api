from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv

# load enironment variables
load_dotenv()

#create FastAPI application
app = FastAPI(title="Rabo Azure LLM API")

# configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # more detailed origin name could be set
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure LLM API settings
AZURE_API_KEY = os.getenv("API_KEY")
GPT4O_ENDPOINT = os.getenv("GPT4O_ENDPOINT")
if not AZURE_API_KEY or not GPT4O_ENDPOINT:
    raise ValueError("Please set a valid API_KEY and GPT_ENDPOINT environment variable")

# request model
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

#response model
class ChatResponse(BaseModel):
    response: str
    total_tokens: int

# 

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # transform message format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]


        # set request message
        headers = {
            "Content-Type":"application/json",
            "Authorization":f"Bearer {AZURE_API_KEY}",
        }
        payload = {
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        # use Azure LLM API
        response = requests.post(GPT4O_ENDPOINT,headers=headers, json=payload)

        # check response status
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code,detail=response.text)
        
        # parse response
        response_data = response.json()
        assistant_message = response_data["choices"][0]["message"]["content"]
        total_tokens = response_data["usage"]["total_tokens"]

        return ChatResponse(
            response=assistant_message,
            total_tokens=total_tokens
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request Azure LLM API failed: {str(e)}")
    except KeyError:
        raise HTTPException(status_code=500, detail="Parse response failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server internal error: {str(e)}")

# health check of port 8000
@app.get("/")
async def health_check():
    return{"status":"ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)