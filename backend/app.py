import sqlite3
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_NAME = "users.db"

# --------------------------
# Banco de Dados
# --------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_code TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --------------------------
# Criação de Usuário
# --------------------------
def create_user(username, email, password):
    verification_code = str(random.randint(100000, 999999))
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password, verification_code)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password, verification_code))
        conn.commit()
        conn.close()

        # envia o e-mail de verificação
        send_verification_email(email, verification_code)

        return True, f"Cadastro realizado! Código de verificação enviado para {email}."
    except sqlite3.IntegrityError:
        return False, "Usuário ou e-mail já cadastrados."

# --------------------------
# Verificação de Conta
# --------------------------
def verify_user(identifier, code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT verification_code FROM users WHERE username=? OR email=?", (identifier, identifier))
    result = cursor.fetchone()
    if result and result[0] == code:
        cursor.execute("UPDATE users SET is_verified=1 WHERE username=? OR email=?", (identifier, identifier))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


# --------------------------
# Autenticação de Usuário
# --------------------------
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password, is_verified FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password, is_verified = result
        if stored_password == password:
            return True, is_verified
        else:
            return False, 0
    return False, 0

# --------------------------
# Envio de Email
# --------------------------
def send_verification_email(to_email, code):
    sender_email = "peladapro.noreply@gmail.com"
    sender_password = "gekp qrjc uxft evzb"  # App Password do Gmail
    subject = "Código de Verificação - PeladaPro"
    body = f"Olá!\n\nSeu código de verificação do PeladaPro é: {code}\n\nDigite este código no aplicativo para ativar sua conta."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"E-mail enviado para {to_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# --------------------------
# Inicializa DB ao importar
# --------------------------
init_db()
