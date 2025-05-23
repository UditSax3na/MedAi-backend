import sys
import pickle

from .ChatClass import ChatClass
from .ImageToSymptoms import ImageToSymptoms
from ..Constants.path import USERDATAFILE

class UserConnected:
    def __init__(self, sid: str):
        self.msgStack = []
        self.quesStack = []
        self.sid = sid
        self.name = ""
        self.email = ""
        self.chat = ChatClass()
        self.symimg = ImageToSymptoms()

    def __str__(self):
        return f"{self.sid}: {self.name}"

    def displaySelf(self):
        print(f"in dictionary: {self.to_dict()}")
    
    def resetMsgQuestStack(self):
        self.msgStack = []
        self.quesStack = []

    def to_dict(self):
        chatdata = self.chat.to_dict()
        return {
            "msgStack": self.msgStack,
            "quesStack": self.quesStack,
            "sid": self.sid,
            "name": self.name,
            "email": self.email,
            "chat": chatdata
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['sid'])
        obj.msgStack = data['msgStack']
        obj.quesStack = data['quesStack']
        obj.name = data['name']
        obj.email = data['email']
        obj.chat = ChatClass.dict_from(data['chat'])
        return obj

class ConnectionManager:
    def __init__(self):
        self.ConnectedUser = {}
        self.udl = UserDataLoader() 
        self.loadedDataStatus = False
        self.iter = ""

    def __iter__(self):
        self.iter = iter(self.ConnectedUser.values())
        return self.iter

    def __next__(self):
        return self.iter

    def __contains__(self, sid):
        return sid in self.ConnectedUser

    def __setitem__(self, sid, user: UserConnected):
        self.ConnectedUser[sid] = user

    def __getitem__(self, sid):
        return self.ConnectedUser.get(sid)

    def __delitem__(self, sid):
        if sid in self.ConnectedUser:
            del self.ConnectedUser[sid]
            return True
        return False
    
    def getInputInStack(self, sid: str, data: dict):
        user = self.ConnectedUser.get(sid)
        user.msgStack.append(data)

    def displayUsersInfo(self):
        for _, user in self.ConnectedUser.items():
            user.displaySelf()

    def searchUsers(self, sid: str, mode:str='sid'):
        if mode == 'sid':
            for sido, user in self.ConnectedUser.items():
                if sido == sid:
                    return user, True
            return False, False
        
        elif mode == 'email':
            for sido, user in self.ConnectedUser.items():
                print(f"type of user : {type(user)}")
                if user.email == sid:
                    return user, True
            return False, False
        
        else:
            return False, False
            
    def healthCheckUp(self):
        if len(self.ConnectedUser) >= 10:
            return True
        else:
            return False
        
    def ExistCleanup(self):
        self.udl.SaveUsers(self.ConnectedUser)
        print("Server is shutting down... ")
        sys.exit(0)

    def SignalHandler(self, sig, frame):
        print(f"signalHandler from manager : {self.ConnectedUser}")
        self.udl.SaveUsers(self.ConnectedUser)
        print(f"Received signal {sig}")
        sys.exit(0)
        
class UserDataLoader:
    def LoadUsers(self):
        try:
            with open(USERDATAFILE, 'rb') as myfile:
                data = pickle.load(myfile)

            dic = {sid: UserConnected.from_dict(data) for sid, data in data.items()}
            for i, j in dic.items():
                print(f"{i}: {j} and {j.email}")
            return dic
        
        except FileNotFoundError:
            return {}

    def SaveUsers(self, allusers):
        print(f"SaveUsers from Cleanup : {allusers}")
        data = {sid: user.to_dict() for sid, user in allusers.items()}
        if data:
            print(f"Data : {data}")
            with open(USERDATAFILE, 'wb') as myfile:
                pickle.dump(data, myfile)