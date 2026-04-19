[15:38, 19/04/2026] .: <!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Acesso liberado</title>
</head>

<body style="text-align:center;font-family:Arial;background:#f5f5f5">

<h1>Pagamento confirmado ✅</h1>
<p>Seu acesso foi liberado</p>

<a href="https://SEU-LINK-DA-IA-AQUI">
<button style="padding:15px 30px;font-size:18px">
Entrar na IA
</button>
</a>

<p>Se tiver problema, fale no WhatsApp</p>

</body>
</html>
[15:53, 19/04/2026] .: from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()
client = OpenAI()

# LIBERA ACESSO DO SITE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(
    texto: str = Form(""),
    idioma: str = Form("pt"),
    file: UploadFile = File(None)
):
    if idioma == "pt":
        system = "Responda em português de forma natural."
    else:
        system = "Respond in English."

    if file:
        imagem = await file.read()

        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": texto},
                    {"type": "input_image", "image": imagem}
                ]
            }]
        )
    else:
        resposta = client.responses.create(
            model="gpt-4.1-mini",
            input=system + " " + texto
        )

    return {"resposta": resposta.output[0].content[0].text}