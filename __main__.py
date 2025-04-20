# Sepecific Import
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Custom Modules Import
from .Constants import TEMPLATES_PATH
from . import router  
from .ChatClass import ChatClass

# Import
import uvicorn
import socketio

class UserConnected:
    def __init__(self, sid: str, environ: dict):
        self.msgStack = []
        self.sid = sid
        self.name = ""
        self.environ = environ
        self.chat = ChatClass()

    def displaySelf(self):
        print(f"self.sid : {self.sid} and self.msgStack : {self.msgStack}")
    
    def resetMsgStack(self):
        self.msgStack = []

class ConnectionManager:
    def __init__(self):
        self.ConnectedUser = []

    def connectUser(self, user: UserConnected):
        self.ConnectedUser.append(user)

    def disconnectUser(self, sid):
        for user in self.ConnectedUser:
            if user.sid == sid:
                self.ConnectedUser.remove(user)

    def getInputInStack(self, sid: str, data: dict):
        for user in self.ConnectedUser:
            if user.sid == sid:
                user.msgStack.append(data)

    def displayUsersInfo(self):
        for user in self.ConnectedUser:
            user.displaySelf()

    def searchUsers(self, sid: str):
        for user in self.ConnectedUser:
            if user.sid == sid:
                return user
            
    def healthCheckUp(self):
        if len(self.ConnectedUser) >= 10:
            return True
        else:
            return False
            
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
)

manager = ConnectionManager()
fastapiapp = FastAPI()
fastapiapp.include_router(router) # include router

templates = Jinja2Templates(directory=TEMPLATES_PATH)

@fastapiapp.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("testingws.html", {"request": request})

app = socketio.ASGIApp(sio, fastapiapp)

@sio.event
async def connect(sid, environ):
    if manager.healthCheckUp():
        await sio.disconnect(sid)
    else:
        user = UserConnected(sid, environ)
        manager.connectUser(user)
        print("Client connected:", sid)

@sio.event
def disconnect(sid):
    manager.disconnectUser(sid)
    print("Client disconnected:", sid)

@sio.event
async def my_event(sid, data):
    print(f"Message received from {sid}: {data}")
    manager.getInputInStack(sid, data)
    manager.displayUsersInfo()
    user = manager.searchUsers(sid)
    questdic = user.chat.chat_sp(user.name, data)
    if questdic['qkey'] == 0:
        user.resetMsgStack()
    # if nextQuestion == true
        # sends the question 
    print(f"this is questdic: {questdic}")
    await sio.emit("response", questdic, to=sid)
    # else 
        # sends the response with -10 key (means the prediction is done + serverity , and precautions has been shown )

@sio.event
async def set_name(sid, data):
    user = manager.searchUsers(sid)
    user.name=data['name']
    await sio.emit("response", {"q": f"Enter the main symptom you are experiencing Mr/Ms {user.name}", "qkey": 1, "ic": -1,"ql": [], "p": None, "r": None}, to=sid)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


"""
cd ..
python -m MedAIBackend
"""