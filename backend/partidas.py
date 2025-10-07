class PartidaManager:
    def __init__(self):
        self.fila = []            # Times esperando
        self.partida_atual = None # Quem está jogando agora

    def iniciar(self, times):
        """
        Inicia o campeonato com uma lista de times.
        Exemplo: [["João","Pedro"], ["Ana","Carlos"], ["Lucas","Marcos"]]
        """
        self.fila = times.copy()
        if len(self.fila) >= 2:
            self.partida_atual = (self.fila.pop(0), self.fila.pop(0))
        else:
            self.partida_atual = None

    def registrar_resultado(self, vencedor):
        """
        Atualiza a fila de acordo com o vencedor da partida atual.
        vencedor = "time1" ou "time2"
        """
        if not self.partida_atual:
            return None

        time1, time2 = self.partida_atual

        if vencedor == "time1":
            ganhador, perdedor = time1, time2
        elif vencedor == "time2":
            ganhador, perdedor = time2, time1
        else:
            raise ValueError("Vencedor inválido. Use 'time1' ou 'time2'.")

        # Ganhador volta pro início da fila
        self.fila.insert(0, ganhador)
        # Perdedor vai para o fim da fila
        self.fila.append(perdedor)

        # Nova partida
        if len(self.fila) >= 2:
            self.partida_atual = (self.fila.pop(0), self.fila.pop(0))
        else:
            self.partida_atual = None

        return self.partida_atual
