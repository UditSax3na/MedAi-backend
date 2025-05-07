# Sepecific Import
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Custom Modules Import
from .Constants.path import TEMPLATES_PATH, LOGFILE
from . import router  
from .ChatClass import ChatClass

# Import
import uvicorn
import socketio
import traceback
import datetime

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
    cors_allowed_origins='*',
    allow_upgrades=True,
)

manager = ConnectionManager()
fastapiapp = FastAPI()
fastapiapp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapiapp.include_router(router) # include router

templates = Jinja2Templates(directory=TEMPLATES_PATH)

@fastapiapp.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("testingws.html", {"request": request})

# app = socketio.ASGIApp(sio, fastapiapp)
app = socketio.ASGIApp(sio, other_asgi_app=fastapiapp)

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
async def my_event(sid, data: dict)->None:
    try:
        if (data):
            pass
        else:
            print(f"Message received from {sid}: {data}")
            manager.getInputInStack(sid, data)
            manager.displayUsersInfo()
            user = manager.searchUsers(sid)
            questdic = user.chat.chat_sp(user.name, data)
            print(f"this is questdic: {questdic}")
            if questdic['qkey'] == 0:
                user.resetMsgStack()
            await sio.emit("response", questdic, to=sid)
    except Exception as e:
        print(f"!Error Occured!\nCheck the log file ->{LOGFILE}")
        with open(LOGFILE, 'a') as myfile:  # Append mode
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_trace = traceback.format_exc()  # Full traceback
            myfile.write(f"[{timestamp}] Error: {str(e)}\n")
            myfile.write(f"[{timestamp}] Traceback:\n{error_trace}\n")
            myfile.write(f"[{timestamp}] File Location: {__file__}\n")
            myfile.write("-" * 60 + "\n")

@sio.event
async def set_name(sid, data) -> None:
    user = manager.searchUsers(sid)
    user.name=data['name']
    await sio.emit("response", {"q": f"Enter the main symptom you are experiencing Mr/Ms {user.name}", "qkey": 1, "ic": -1,"ql": [], "p": None, "r": None}, to=sid)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# cd ..
# python -m MedAIBackend
# cd MedAIBackend
# venv\Scripts\activate