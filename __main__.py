# Sepecific Import
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Custom Modules Import
from __init__ import router  
from Constants.path import TEMPLATES_PATH, LOGFILE, ensure_dirs, USERDATAFILE
from core.ServerMgmtClass import UserConnected, ConnectionManager

# Import
import uvicorn
import socketio
import traceback
import datetime
# import atexit
# import signal


# making all the folders and files it they are missing
ensure_dirs()
            
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins='*',
    allow_upgrades=True,
)

manager = ConnectionManager()

# Server crashing logic
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("App is starting...")
#     yield
#     print("App is shutting down...") 
#     manager.ExistCleanup()

# fastapiapp = FastAPI(lifespan=lifespan)

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

app = socketio.ASGIApp(sio, other_asgi_app=fastapiapp)

# adding cleanup function if server crashes or is terminated
# signal.signal(signal.SIGINT, manager.SignalHandler)
# signal.signal(signal.SIGTERM, manager.SignalHandler)
# atexit.register(manager.ExistCleanup)

# for loading the data which existed before server stopped (backup data)
# if USERDATAFILE.exists() and manager.loadedDataStatus==False:
#     manager.ConnectedUser = manager.udl.LoadUsers()
#     manager.loadedDataStatus = True
#     for i, j in manager.ConnectedUser.items():
#         print(f"manager.ConnectedUser[{i}]: {j.email} and {j.chat.user_inputs} ")

@sio.event
async def connect(sid, env):
    if manager.healthCheckUp():
        await sio.disconnect(sid)
    else:
        user = UserConnected(sid)
        manager[sid] = user
        print("Client connected:", sid)

@sio.event
def disconnect(sid):
    del manager[sid]
    print("Client disconnected:", sid)

@sio.event
async def my_event(sid, data: dict)->None:
    try:
        print(f"Message {sid}: {data}")
        if (data['answer'][0:4]=="/arg"):
            arg = data['answer'].split('-')[1]
            dic={
                'q':str(eval(arg)),
                'qkey': -404,
                'ic':-1,
                'ql':[],
                'p':None,
                'r':None
            }
            print(f"{data['answer']}: {dic['q']}")
            await sio.emit("response", dic, to=sid)

        else:
            user = manager[sid]
            if len(user.quesStack)!=0:
                data.update({'qkey':user.quesStack[len(user.quesStack)-1]['qkey']})
            else:
                data.update({'qkey':1})

            manager.getInputInStack(sid, data)
            if (data['atype']=='img'):
                imgsym = user.symimg.Predict(data['answer'])
                data.update({'answer': imgsym})
            questdic = user.chat.chat_sp(user.name, data)
            print(f"this is questdic: {questdic}")
            if questdic['qkey'] == 0:
                user.resetMsgQuestStack()
            await sio.emit("response", questdic, to=sid)
            user.quesStack.append(questdic)

    except Exception as e:
        print(f"!Error Occured!\nCheck the log file ->{LOGFILE}")
        with open(LOGFILE, 'a') as myfile:  # Append mode
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_trace = traceback.format_exc()  # Full traceback
            myfile.write(f"[{timestamp}] Error: {str(e)}\n")
            myfile.write(f"[{timestamp}] Traceback:\n{error_trace}\n")
            myfile.write(f"[{timestamp}] File Location: {__file__}\n")
            myfile.write("-" * 60 + "\n")

        await sio.emit("response", {"error":"Internal Error"}, to=sid)

@sio.event
async def set_name(sid, data) -> None:
    # user, flag = manager.searchUsers(data['email'], mode='email')
    # if flag: # used to set the data before crash
    #     tempsid = user.sid
    #     user.sid = sid
    #     del manager.ConnectedUser[tempsid]
    #     manager.ConnectedUser[sid] = user
    #     msglen = len(user.msgStack)
    #     queslen = len(user.quesStack)
    #     if user.msgStack[msglen-1]['qkey']==user.quesStack[queslen-1]['qkey']:
    #         questdic = user.chat.chat_sp(user.name, user.msgStack[msglen-1]['qkey'])
    #         print(f"this is questdic: {questdic}")
    #         if questdic['qkey'] == 0:
    #             user.resetMsgQuestStack()
    #         await sio.emit("response", questdic, to=sid)
    #         user.quesStack.append(questdic)

    #     elif user.msgStack[msglen-1]['qkey']<user.quesStack[queslen-1]['qkey']:
    #         await sio.emit('response', user.quesStack[queslen-1], to=sid)

    #     else:
    #         await sio.emit('response', {'q':"internal error", 'qkey':-20}, to=sid)

    # else:
    user, _ = manager.searchUsers(sid)
    user.name = data['name']
    user.email = ''
    print(f"user.email: {user.email}")
    dic = {"q": f"Enter the main symptom you are experiencing Mr/Ms {user.name}", "qkey": 1, "ic": -1,"ql": [], "p": None, "r": None}
    print(f"dic : {dic}")
    await sio.emit("response", dic, to=sid)
    user.quesStack.append(dic)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Server Crashed!\nCheck The log file -> {LOGFILE}")
        with open(LOGFILE, 'a') as myfile:  # Append mode
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_trace = traceback.format_exc()  # Full traceback
            myfile.write(f"[{timestamp}] Error: {str(e)}\n")
            myfile.write(f"[{timestamp}] Traceback:\n{error_trace}\n")
            myfile.write(f"[{timestamp}] File Location: {__file__}\n")
            myfile.write("-" * 60 + "\n")
    # finally:
    #     manager.ExistCleanup()

# Important Commands 

# python -m venv venv -> create virtual env
# venv\Scripts\activate -> activate virtual env
# cd .. -> change to parent directory
# cd MedAIBackend -> change current dir to MedAIBackend directory 
# python -m MedAIBackend -> run MedAIBackend as a package
# uvicorn MedAIBackend.__main__:app --reload run medaibackend.__main__:app with reloading feature

# testing during run time commands
# /arg-manager.ConnectedUser
# /arg-manager["<socket_id>"]
# /arg-manager["<socket_id>"].msgStack
# /arg-manager["<socket_id>"].chat.user_inputs