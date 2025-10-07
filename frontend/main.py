# importando coisas do python
import sqlite3   # acho que precisa pro banco
import os        # esse é para mexer nos caminhos
import sys       # sistema
# coisas do kivy que precisa
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

# aqui eu coloco o backend, não sei se é o jeito certo mas funciona
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app import create_user, verify_user, authenticate_user  # importando funções do outro arquivo

# carregar o arquivo kv (a parte do layout do app)
KV_PATH = os.path.join(os.path.dirname(__file__), "pelada.kv")
Builder.load_file(KV_PATH)  # se não carregar o kv não aparece nada na tela


# TELA DE LOGIN
class LoginScreen(Screen):   # essa tela é só pra login
    def login(self, username, password):
        # se nao tiver usuario ou senha da erro
        if not username or not password:
            self._popup("Preencha username e senha.")
            return

        # aqui chama a função que olha no banco
        found, verified = authenticate_user(username, password)
        if not found:
            self._popup("Usuário ou senha incorretos!")  # se nao achou
            return
        if verified == 0:  # usuario existe mas nao verificou
            self._popup_verification(username)
            return

        # se passar de tudo vai pra tela de cadastro dos jogadores
        self.manager.current = "tela_cadastro"

    def goto_register(self):
        self.manager.current = "register"  # troca pra tela de registrar

    # essa função é só pra abrir popup normal
    def _popup(self, text):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(text=text))
        btn = Button(text="OK", size_hint_y=None, height=40)
        layout.add_widget(btn)
        popup = Popup(title="Aviso", content=layout, size_hint=(0.7, 0.4))
        btn.bind(on_release=popup.dismiss)  # botão fecha o popup
        popup.open()

    # esse popup é especial para colocar o codigo de verificação
    def _popup_verification(self, username):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        input_code = TextInput(hint_text="Código de verificação", multiline=False)
        btn_verify = Button(text="Verificar", size_hint_y=None, height=40)
        layout.add_widget(Label(text=f"Insira o código de verificação enviado para seu email, {username}"))
        layout.add_widget(input_code)
        layout.add_widget(btn_verify)
        popup = Popup(title="Verificação de Conta", content=layout, size_hint=(0.8, 0.5))

        # aqui dentro faz a verificação do código
        def verificar(_):
            code = input_code.text.strip()
            if not code:
                return
            ok = verify_user(username, code)
            if ok:
                popup.dismiss()
                self._popup("Conta verificada com sucesso! Agora faça login.")
            else:
                self._popup("Código incorreto.")  # se o código não bate

        btn_verify.bind(on_release=verificar)  # botão chama a função verificar
        popup.open()


# TELA DE REGISTRO
class RegisterScreen(Screen):
    def cadastrar_usuario(self, username, email, password):
        # não pode deixar campo vazio
        if not username or not email or not password:
            self._popup("Preencha todos os campos.")
            return
        try:
            # chama a função de criar usuario no banco
            success, msg = create_user(username, email, password)
            if success:
                self._popup_verificacao(email)  # mostra popup de verificação
            else:
                self._popup(msg)  # deu erro tipo já existe
        except Exception as e:  # se der algum erro no python
            self._popup(f"Falha no cadastro: {e}")

    # igual o popup de antes
    def _popup(self, text):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(text=text))
        btn = Button(text="OK", size_hint_y=None, height=40)
        layout.add_widget(btn)
        popup = Popup(title="Aviso", content=layout, size_hint=(0.7, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    # esse popup é só para verificar o email
    def _popup_verificacao(self, email):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(text=f"Código de verificação enviado para {email}.\nDigite abaixo:"))
        input_code = TextInput(multiline=False, hint_text="Código de verificação")
        layout.add_widget(input_code)
        btn = Button(text="Verificar", size_hint_y=None, height=40)
        layout.add_widget(btn)
        popup = Popup(title="Verificação de Conta", content=layout, size_hint=(0.7, 0.4))

        # verificar se o codigo confere
        def verificar(_):
            code = input_code.text.strip()
            if not code:
                return
            if verify_user(email, code):  # aqui usa email mesmo
                popup.dismiss()
                self._popup("Conta verificada com sucesso! Agora faça login.")
                self.manager.current = "login"  # volta pro login
            else:
                self._popup("Código inválido. Tente novamente.")

        btn.bind(on_release=verificar)
        popup.open()


# TELA DE CADASTRO DE JOGADORES
class TelaCadastro(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jogadores = []  # lista vazia no começo

    def adicionar_jogador(self, nome):
        nome = nome.strip()
        if not nome:  # nao pode nome vazio
            return
        self.jogadores.append(nome)
        self.ids.lista_jogadores.text = "\n".join(self.jogadores)
        self.ids.input_jogador.text = ""
        self.ids.contador.text = f"Jogadores: {len(self.jogadores)}"

    def dividir_times(self):
        if not self.jogadores:
            return
        try:
            num_times = int(self.ids.num_times.text)  # pega numero digitado
            num_por_time = int(self.ids.jogadores_por_time.text)  # mesma coisa
        except Exception:
            return

        players = list(self.jogadores)  # copia lista
        capacidade_total = num_times * num_por_time
        if len(players) > capacidade_total:
            return

        times = []  # aqui cria os times
        idx = 0
        for t in range(num_times):
            take = min(num_por_time, len(players) - idx)
            times.append({"nome": f"Time {t+1}", "jogadores": players[idx: idx + take]})
            idx += take

        tela_times = self.manager.get_screen("tela_times")
        tela_times.iniciar_times(times, num_por_time)

        # reseta os campos depois
        self.jogadores = []
        self.ids.lista_jogadores.text = ""
        self.ids.contador.text = ""
        self.ids.input_jogador.text = ""
        self.ids.num_times.text = ""
        self.ids.jogadores_por_time.text = ""

        self.manager.current = "tela_times"  # troca tela

    def logout(self):
        # limpa tudo e volta pro login
        self.jogadores = []
        self.ids.lista_jogadores.text = ""
        self.ids.contador.text = ""
        self.ids.input_jogador.text = ""
        self.ids.num_times.text = ""
        self.ids.jogadores_por_time.text = ""
        self.manager.current = "login"


# TELA DOS TIMES
class TelaTimes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.times = []
        self.jogadores_por_time = 0
        self.msg_popup = None  # guarda popup

    def iniciar_times(self, times, jogadores_por_time):
        self.times = times
        self.jogadores_por_time = jogadores_por_time
        self.atualizar_tela()  # mostra os times

    def atualizar_tela(self):
        self.ids.grid_times.clear_widgets()  # limpa grid

        # Confronto atual (primeiros dois times)
        if len(self.times) >= 2:
            box_confronto = BoxLayout(orientation="vertical", spacing=5, padding=5, size_hint_y=None)
            altura = (self.jogadores_por_time + 1) * 40
            box_confronto.height = altura

            box_times = BoxLayout(spacing=10)
            for idx in range(2):
                time = self.times[idx]
                box = BoxLayout(orientation="vertical", spacing=2)
                lbl = Label(text=f"[b]{time['nome']}[/b]", markup=True, size_hint_y=None, height=30)
                box.add_widget(lbl)
                for j in time['jogadores']:
                    btn = Button(text=j, size_hint_y=None, height=30)
                    box.add_widget(btn)
                box_times.add_widget(box)
            box_confronto.add_widget(box_times)

            # botoes de resultado
            box_botoes = BoxLayout(size_hint_y=None, height=40, spacing=10)
            btn_vit1 = Button(text=f"Vitória {self.times[0]['nome']}")
            btn_der1 = Button(text=f"Derrota {self.times[0]['nome']}")
            btn_vit2 = Button(text=f"Vitória {self.times[1]['nome']}")
            btn_der2 = Button(text=f"Derrota {self.times[1]['nome']}")
            btn_vit1.bind(on_release=lambda _: self.registrar_vencedor(0))
            btn_der1.bind(on_release=lambda _: self.registrar_derrota(0))
            btn_vit2.bind(on_release=lambda _: self.registrar_vencedor(1))
            btn_der2.bind(on_release=lambda _: self.registrar_derrota(1))
            box_botoes.add_widget(btn_vit1)
            box_botoes.add_widget(btn_der1)
            box_botoes.add_widget(btn_vit2)
            box_botoes.add_widget(btn_der2)
            box_confronto.add_widget(box_botoes)
            self.ids.grid_times.add_widget(box_confronto)

        # mostra os outros times que estão esperando
        for idx in range(2, len(self.times)):
            time = self.times[idx]
            box = BoxLayout(orientation="vertical", spacing=2, padding=5, size_hint_y=None)
            box.height = (len(time['jogadores']) + 1) * 40
            lbl = Label(text=f"[b]{time['nome']}[/b]", markup=True, size_hint_y=None, height=30)
            box.add_widget(lbl)
            for j in time['jogadores']:
                btn = Button(text=j, size_hint_y=None, height=30)
                box.add_widget(btn)
            self.ids.grid_times.add_widget(box)

    def registrar_vencedor(self, vencedor_idx):
        self.atualizar_tela()  # nao faz nada alem de atualizar

    def registrar_derrota(self, perdedor_idx):
        perdedor = self.times.pop(perdedor_idx)
        self.times.append(perdedor)  # manda o perdedor pro fim da fila
        self.atualizar_tela()

    def popup_adicionar_jogador(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        input_nome = TextInput(hint_text="Nome do jogador", multiline=False)
        btn_add = Button(text="Adicionar", size_hint_y=None, height=40)
        layout.add_widget(input_nome)
        layout.add_widget(btn_add)
        popup = Popup(title="Adicionar Jogador", content=layout, size_hint=(0.7, 0.4))

        def adicionar(_):
            nome = input_nome.text.strip()
            if nome:
                sucesso = self.adicionar_jogador(nome)
                if sucesso:
                    popup.dismiss()
            else:
                self.mostrar_popup("Digite um nome válido!")

        btn_add.bind(on_release=adicionar)
        popup.open()

    def mostrar_popup(self, msg):
        if self.msg_popup:
            self.msg_popup.dismiss()
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        label = Label(text=msg)
        btn = Button(text="OK", size_hint_y=None, height=40)
        layout.add_widget(label)
        layout.add_widget(btn)
        popup = Popup(title="Aviso", content=layout, size_hint=(0.6, 0.3))
        btn.bind(on_release=popup.dismiss)
        popup.open()
        self.msg_popup = popup

    def adicionar_jogador(self, nome):
        for time in self.times:
            if len(time['jogadores']) < self.jogadores_por_time:
                time['jogadores'].append(nome)
                self.atualizar_tela()
                return True
        self.mostrar_popup("Não há mais vagas!")
        return False

    def adicionar_time(self):
        novo_idx = len(self.times) + 1
        self.times.append({"nome": f"Time {novo_idx}", "jogadores": []})
        self.atualizar_tela()

    def logout(self):
        self.manager.get_screen("tela_cadastro").logout()
        self.manager.current = "login"  # volta pro login


# classe principal do app
class PeladaProApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(TelaCadastro(name="tela_cadastro"))
        sm.add_widget(TelaTimes(name="tela_times"))
        return sm


# rodar o aplicativo
if __name__ == "__main__":
    PeladaProApp().run()
