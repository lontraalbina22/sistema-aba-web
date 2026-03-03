from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# =========================
# BANCO DE DADOS
# =========================

def conectar():
    return sqlite3.connect("aba_web.db")


def init_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER,
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

# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM alunos")
    total_alunos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sessoes")
    total_sessoes = cursor.fetchone()[0]

    cursor.execute("SELECT tipo FROM tentativas")
    dados = cursor.fetchall()

    total = len(dados)
    independentes = len([d for d in dados if d[0] == "Independente"])
    media_indep = round((independentes/total*100),1) if total>0 else 0

    conn.close()

    return render_template("dashboard.html",
                           total_alunos=total_alunos,
                           total_sessoes=total_sessoes,
                           media_indep=media_indep)

# =========================
# CADASTRO DE ALUNOS
# =========================

@app.route("/alunos", methods=["GET", "POST"])
def alunos():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        cursor.execute("INSERT INTO alunos (nome) VALUES (?)", (nome,))
        conn.commit()

    cursor.execute("SELECT * FROM alunos")
    lista = cursor.fetchall()

    conn.close()

    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
    <h2>Alunos</h2>

    <form method="post" class="mb-3">
        <input name="nome" class="form-control mb-2" placeholder="Nome do aluno" required>
        <button class="btn btn-primary">Cadastrar</button>
    </form>

    <ul class="list-group">
        {% for aluno in lista %}
        <li class="list-group-item">{{ aluno[1] }}</li>
        {% endfor %}
    </ul>

    {% endblock %}
    """, lista=lista)

# =========================
# NOVA SESSÃO
# =========================

@app.route("/nova_sessao", methods=["GET", "POST"])
def nova_sessao():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()

    if request.method == "POST":
        aluno_id = request.form["aluno"]
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute("INSERT INTO sessoes (aluno_id, data) VALUES (?,?)", (aluno_id, data))
        conn.commit()
        sessao_id = cursor.lastrowid
        conn.close()
        return redirect(f"/sessao/{sessao_id}")

    conn.close()

    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
    <h2>Nova Sessão</h2>

    <form method="post">
        <select name="aluno" class="form-control mb-3" required>
            {% for aluno in alunos %}
            <option value="{{ aluno[0] }}">{{ aluno[1] }}</option>
            {% endfor %}
        </select>
        <button class="btn btn-success">Iniciar Sessão</button>
    </form>

    {% endblock %}
    """, alunos=alunos)

# =========================
# REGISTRO DE TENTATIVAS
# =========================

@app.route("/sessao/<int:id>", methods=["GET", "POST"])
def sessao(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        tipo = request.form["tipo"]
        cursor.execute("INSERT INTO tentativas (sessao_id, tipo) VALUES (?,?)", (id, tipo))
        conn.commit()

    cursor.execute("SELECT tipo FROM tentativas WHERE sessao_id=?", (id,))
    dados = cursor.fetchall()

    total = len(dados)
    independentes = len([d for d in dados if d[0] == "Independente"])
    percent = round((independentes/total*100),1) if total>0 else 0

    conn.close()

    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}

    <h2>Registro de Sessão</h2>

    <h4>Total: {{total}}</h4>
    <h4>% Independente: {{percent}}%</h4>

    <form method="post" class="d-grid gap-2">
        <button name="tipo" value="Independente" class="btn btn-success">Independente</button>
        <button name="tipo" value="Ajuda Verbal" class="btn btn-primary">Ajuda Verbal</button>
        <button name="tipo" value="Ajuda Gestual" class="btn btn-warning">Ajuda Gestual</button>
        <button name="tipo" value="Ajuda Física Parcial" class="btn btn-info">Ajuda Física Parcial</button>
        <button name="tipo" value="Ajuda Física Total" class="btn btn-dark">Ajuda Física Total</button>
        <button name="tipo" value="Erro" class="btn btn-danger">Erro</button>
        <button name="tipo" value="Omissão" class="btn btn-secondary">Omissão</button>
    </form>

    {% endblock %}
    """, total=total, percent=percent)

# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)