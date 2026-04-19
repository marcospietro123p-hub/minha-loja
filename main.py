from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(texto: str = Form(""), file: UploadFile = File(None)):
    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=texto
    )
    return {"resposta": resposta.output[0].content[0].text}
