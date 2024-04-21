import json, os, requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.websockets import WebSocketState
from llm import LlmClient

from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

import sys

llm_client = LlmClient()
call_details = None
load_dotenv()

RETELL_APIKEY = os.getenv("RETELL_APIKEY")

class Settings(BaseSettings):
    # ... The rest of our FastAPI settings

    BASE_URL: str = "http://localhost:8000"
    USE_NGROK: str = os.getenv("USE_NGROK")

settings = Settings()

def create_agent(llm_websocket_url):

    url = "https://api.retellai.com/create-agent"
    headers = {
        "Authorization": f"Bearer {RETELL_APIKEY}",
        "Content-Type": "application/json"
    }
    llm_websocket_url = llm_websocket_url.replace("https", "wss") + "/llm-websocket/"
    data = {
        "llm_websocket_url": llm_websocket_url,
        "voice_id": "openai-Alloy",
        "enable_backchannel": True,
        "agent_name": "Alloy"
    }

    response = requests.post(url, headers=headers, json=data)
    agent_id = response.json()['agent_id']

def list_agent():

    url = "https://api.retellai.com/list-agents"
    headers = {
        "Authorization": f"Bearer {RETELL_APIKEY}"
    }

    response = requests.get(url, headers=headers)

    print(response.status_code)
    agent_id = response.json()[0]['agent_id']
    print("AGENT_ID:", agent_id)
    return agent_id
    
def delete_agent(agent_id):
    url = f"https://api.retellai.com/delete-agent/{agent_id}"
    headers = {
        "Authorization": f"Bearer {RETELL_APIKEY}"
    }

    response = requests.delete(url, headers=headers)

def update_agent(agent_id, llm_websocket_url):
    
    url = f"https://api.retellai.com/update-agent/{agent_id}"
    headers = {
        "Authorization": f"Bearer {RETELL_APIKEY}",
        "Content-Type": "application/json"
    }
    llm_websocket_url = llm_websocket_url.replace("https", "wss") + "/llm-websocket/"
    data = {
        "llm_websocket_url": llm_websocket_url,
    }

    response = requests.patch(url, headers=headers, json=data)
    
def register_call(agent_id):
    
    url = "https://api.retellai.com/register-call"
    headers = {
        "Authorization": f"Bearer {RETELL_APIKEY}",
        "Content-Type": "application/json"
    }
    payload = {
            "agent_id": agent_id,
            "audio_websocket_protocol": 'web',
            "audio_encoding": 's16le',
            "sample_rate": 44100,
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def init_webhooks(base_url):
    global call_details
    # create_agent(base_url)
    agent_id = list_agent()
    update_agent(agent_id, base_url)
    call_details = register_call(agent_id)
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass

# Initialize the FastAPI app for a simple web server
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.USE_NGROK and os.getenv("NGROK_AUTHTOKEN"):
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    from pyngrok import ngrok

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8000"

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    logger.info(f'''ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"''')

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    init_webhooks(public_url)

@app.get("/get_call_details")
async def get_call_details():
    return call_details

@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    await websocket.accept()
    # A unique call id is the identifier of each call
    print(f"Handle llm ws for: {call_id}")

    # send begin message to signal ready of server
    response_id = 0
    first_event = llm_client.draft_begin_messsage()
    await websocket.send_text(json.dumps(first_event))

    # listen for new updates
    try:
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            # print out transcript
            os.system('cls' if os.name == 'nt' else 'clear')
            print(json.dumps(request, indent=4))

            # no response needed, process live transcript update if needed
            if 'response_id' not in request:
                continue 

            if request['response_id'] > response_id:
                response_id = request['response_id']
            # Draft response based on request and stream
            for event in llm_client.draft_response(request):
                await websocket.send_text(json.dumps(event))
                # new response needed, abondon this one
                if request['response_id'] < response_id:
                    continue 
    except Exception as e:
        print(f'LLM WebSocket error for {call_id}: {e}')
    finally:
        try:
            await websocket.close()
        except RuntimeError as e:
            print(f"Websocket already closed for {call_id}")
        print(f"Closing llm ws for: {call_id}")