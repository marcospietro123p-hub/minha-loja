from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, stripe, json

# ===== CONFIG =====
STRIPE_KEY = "mk_1TNspeQ2qC1aa7OkaMLEvabW"
WEBHOOK_SECRET = "sk_test_51TNsp3Q2qC1aa7OkIakQOpGcobxOiKwSXr6RRcjtFMYJF4vxfWu1mVBlSir4f7F7fjooi8u8UXa6hjsRGpkcqmSa00lHMhxokN"

SUCCESS_URL = "http://localhost:5500/sucesso.html"
CANCEL_URL = "http://localhost:5500/loja.html"

stripe.api_key = STRIPE_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== BANCO =====
db = sqlite3.connect("loja.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS produtos (
 id INTEGER PRIMARY KEY,
 nome TEXT,
 preco REAL,
 price_id TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 email TEXT,
 total REAL,
 status TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS itens (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 pedido_id INTEGER,
 produto_id INTEGER,
 nome TEXT,
 preco REAL
)
""")

db.commit()

# ===== PRODUTOS (EDITA AQUI COM SEUS PRICE_ID) =====
def seed():
    cur.execute("SELECT COUNT(*) FROM produtos")
    if cur.fetchone()[0] == 0:
        cur.execute("price_1TNt1uQ2qC1aa7OkKHMRM6HW")
        cur.execute("price_1TNt1RQ2qC1aa7OkOobXFWFB")
        cur.execute("price_1TNt01Q2qC1aa7OkenkDqpbj")
        db.commit()

seed()

# ===== LISTAR PRODUTOS =====
@app.get("/produtos")
def listar():
    cur.execute("SELECT * FROM produtos")
    return [
        {"id": r[0], "nome": r[1], "preco": r[2]}
        for r in cur.fetchall()
    ]

# ===== CHECKOUT =====
@app.post("/checkout")
def checkout(email: str = Form(...), itens: str = Form(...)):
    itens = json.loads(itens)

    line_items = []
    total = 0

    for i in itens:
        cur.execute("SELECT nome, preco, price_id FROM produtos WHERE id=?", (i,))
        p = cur.fetchone()
        if not p:
            raise HTTPException(404, "Produto inválido")

        line_items.append({"price": p[2], "quantity": 1})
        total += p[1]

    # salvar pedido
    cur.execute("INSERT INTO pedidos (email,total,status) VALUES (?,?,?)",
                (email, total, "pendente"))
    pedido_id = cur.lastrowid

    for i in itens:
        cur.execute("SELECT nome, preco FROM produtos WHERE id=?", (i,))
        p = cur.fetchone()
        cur.execute(
            "INSERT INTO itens (pedido_id,produto_id,nome,preco) VALUES (?,?,?,?)",
            (pedido_id, i, p[0], p[1])
        )

    db.commit()

    session = stripe.checkout.Session.create(
        payment_method_types=["card","pix"],
        mode="payment",
        customer_email=email,
        line_items=line_items,
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
        metadata={"pedido_id": pedido_id}
    )

    return {"url": session.url}

# ===== WEBHOOK =====
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        pedido_id = session["metadata"]["pedido_id"]

        cur.execute("UPDATE pedidos SET status='pago' WHERE id=?", (pedido_id,))
        db.commit()

    return {"ok": True}

# ===== ADMIN =====
@app.get("/pedidos")
def pedidos():
    cur.execute("SELECT * FROM pedidos ORDER BY id DESC")
    return cur.fetchall()