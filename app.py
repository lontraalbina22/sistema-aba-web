from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ================= BANCO =================

def init_db():
    conn = sqlite3.connect("aba_web.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tentativas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sessao_id INTEGER,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= INTERFACE =================

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Sistema ABA Web</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; background:#121212; color:white; text-align:center; }
button { width:90%%; padding:15px; margin:5px; font-size:18px; border-radius:10px; border:none; }
.ind { background:#2ecc71; }
.verbal { background:#3498db; }
.gestual { background:#9b59b6; }
.fparcial { background:#f1c40f; color:black; }
.ftotal { background:#e67e22; }
.erro { background:#e74c3c; }
.omissao { background:#7f8c8d; }
</style>
</head>
<body>

<h2>Sistema ABA - Registro</h2>

<h3>Total: {{total}}</h3>
<h3>% Independente: {{percent}}%%</h3>

<form method="post">
<button name="tipo" value="Independente" class="ind">Independente</button>
<button name="tipo" value="Ajuda Verbal" class="verbal">Ajuda Verbal</button>
<button name="tipo" value="Ajuda Gestual" class="gestual">Ajuda Gestual</button>
<button name="tipo" value="Ajuda Física Parcial" class="fparcial">Ajuda Física Parcial</button>
<button name="tipo" value="Ajuda Física Total" class="ftotal">Ajuda Física Total</button>
<button name="tipo" value="Erro" class="erro">Erro</button>
<button name="tipo" value="Omissão" class="omissao">Omissão</button>
</form>

<br>
<a href="/nova">Nova Sessão</a>

</body>
</html>
"""

sessao_atual = None

@app.route("/", methods=["GET", "POST"])
def index():
    global sessao_atual

    conn = sqlite3.connect("aba_web.db")
    cursor = conn.cursor()

    if not sessao_atual:
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute("INSERT INTO sessoes (data) VALUES (?)", (data,))
        conn.commit()
        sessao_atual = cursor.lastrowid

    if request.method == "POST":
        tipo = request.form["tipo"]
        cursor.execute("INSERT INTO tentativas (sessao_id, tipo) VALUES (?,?)",
                       (sessao_atual, tipo))
        conn.commit()

    cursor.execute("SELECT tipo FROM tentativas WHERE sessao_id=?", (sessao_atual,))
    dados = cursor.fetchall()

    total = len(dados)
    independentes = len([d for d in dados if d[0] == "Independente"])
    percent = round((independentes/total*100),1) if total>0 else 0

    conn.close()

    return render_template_string(HTML, total=total, percent=percent)

@app.route("/nova")
def nova():
    global sessao_atual
    sessao_atual = None
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)