import sqlite3
import smtplib
import random
import hashlib
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

    # Criptografa a senha com SHA-256
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password, verification_code)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, verification_code))
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
        # Criptografa a senha inserida e compara com a do banco
        input_password_hash = hashlib.sha256(password.encode()).hexdigest()
        if stored_password == input_password_hash:
            return True, is_verified
        else:
            return False, 0
    return False, 0

# --------------------------
# Envio de Email de Verificação
# --------------------------
def send_verification_email(to_email, code):
    sender_email = "peladapro.noreply@gmail.com"
    sender_password = "ieeh wkro udvz jnzt"  # App Password do Gmail
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
# Envio de Email de Login/Senha
# --------------------------
# --------------------------
# Envio de Email de Login/Senha (Recuperação de Senha)
# --------------------------
def send_login_email(to_email, username):
    # 1️⃣ Gera nova senha temporária
    temp_password = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
    
    # 2️⃣ Criptografa a senha temporária com SHA-256
    hashed_password = hashlib.sha256(temp_password.encode()).hexdigest()
    
    # 3️⃣ Atualiza o banco com a nova senha
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, to_email))
    conn.commit()
    conn.close()

    # 4️⃣ Envia o e-mail com a nova senha
    sender_email = "peladapro.noreply@gmail.com"
    sender_password = "ieeh wkro udvz jnzt"  # App Password do Gmail
    subject = "Recuperação de Senha - PeladaPro"
    body = f"Olá, {username}!\n\nSua nova senha temporária é: {temp_password}\n\nUse-a para acessar o PeladaPro e altere-a após o login."

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
        print(f"Nova senha enviada para {to_email}")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False


# --------------------------
# Inicializa DB ao importar
# --------------------------
init_db()
