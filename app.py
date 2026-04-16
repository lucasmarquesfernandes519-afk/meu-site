from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_segura')

# Criar banco
def criar_banco():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

criar_banco()

# Página inicial
@app.route('/')
def home():
    return render_template('login.html')

# Login
@app.route('/login', methods=['POST'])
def fazer_login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        return "Preencha todos os campos"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email=?", (email,))
    usuario = c.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario[2], senha):
        session['usuario'] = email
        return redirect('/dashboard')
    else:
        return "Login inválido"

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            return "Preencha todos os campos"

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Verificar se já existe
        c.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        if c.fetchone():
            conn.close()
            return "Email já cadastrado"

        senha_hash = generate_password_hash(senha)

        c.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha_hash))
        conn.commit()
        conn.close()

        return redirect('/')
    
    return render_template('register.html')

# Dashboard protegido
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('dashboard.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

# Rodar localmente
if __name__ == '__main__':
    app.run(debug=True)