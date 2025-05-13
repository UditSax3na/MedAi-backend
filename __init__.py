# used for defining the routers
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any


class SymptomInput(BaseModel):
    name: str
    answer: Dict[str, Any]

router = APIRouter()

@router.post("/status")
def TestingStatus():
    return {"message": "API is live!"}

@router.post("/predict")
def Predict_disease(inputText: SymptomInput):
    from .core.ChatClass import ChatClass
    chat = ChatClass()
    print(f"inputText.answer : {inputText.answer}")
    result = chat.chat_sp(inputText.name, inputText.answer)
    return {"result": result}