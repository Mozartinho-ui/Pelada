📘 Explicação Completa do Projeto
1. Como abrir o aplicativo
O projeto foi feito em Python usando o framework Kivy.
Para rodar: acessar a pasta frontend e dar o  comando     python -m frontend.main
 Antes, precisa instalar as dependências:
pip install kivy

2. Estrutura do projeto
/projeto
 ├── backend/
 │   └── app.py          # Lida com o banco de dados (SQLite)
 ├── pelada.kv           # Layout visual do app
 ├── main.py             # Lógica principal (telas, navegação, integração)
 ├── script_banco.sql    # Script para criar o banco

3. O que cada parte faz
🔹 main.py (Lógica principal)
Importações
Usa sqlite3, os, sys e os módulos do Kivy.
Isso permite conectar o banco com a interface gráfica.

Conexão com o backend
from backend.app import create_user, verify_user, authenticate_user
Aqui o app importa as funções que lidam com usuários e banco de dados.

Carrega o layout (.kv)
Builder.load_file("pelada.kv")
O .kv define como ficam os botões, textos e telas.

Telas criadas
LoginScreen → Login do usuário
RegisterScreen → Registro de novo usuário
TelaCadastro → Cadastro de jogadores
TelaTimes → Organização dos times
Gerenciador de Telas (ScreenManager)
Controla a navegação entre as telas (exemplo: sair do login e ir para cadastro de jogadores).

🔹 pelada.kv (Layout visual)
Define como aparecem os botões, textos e caixas de input.
Exemplo:
<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Login"
        TextInput:
            id: usuario
        TextInput:
            id: senha
            password: True
        Button:
            text: "Entrar"


👉 Isso cria uma tela simples de login com usuário, senha e botão.
🔹 backend/app.py (Banco de dados + lógica de usuários)
Aqui ficam as funções que trabalham com o banco SQLite:
create_user → cria novo usuário.
verify_user → confirma usuário com código de verificação (via e-mail).
authenticate_user → checa login e senha.
Tudo é salvo localmente em sqlite3.

🔹 script_banco.sql (Criação do banco)
Esse script gera a tabela de usuários no SQLite:
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    verified INTEGER DEFAULT 0
);


👉 Assim você tem:
username (único)
password (armazenada)
verified (0 = não verificado, 1 = verificado)

4. Fluxo do aplicativo
Cadastro
Usuário cria conta → app envia código por e-mail.
Precisa verificar para ativar a conta.
Login
Usuário digita login e senha.
Se verificado → entra no sistema.
Se não → pede verificação.

Cadastro de Jogadores
Usuário adiciona nomes.
O sistema mostra a contagem de jogadores cadastrados.

Organização de Times
Jogadores cadastrados são organizados em times equilibrados.

5. Tecnologias usadas
Python
Kivy (interface gráfica)
SQLite (banco de dados local)
smtplib (opcional) → para envio de e-mails de verificação.

6. Porque essas escolhas?
Kivy → permite criar apps com interface gráfica de forma simples e rápida.
SQLite → banco leve e embutido, não precisa instalar nada extra.
ScreenManager → facilita ter várias telas sem complicar o código.
Verificação por e-mail → adiciona segurança e deixa o app mais profissional.
