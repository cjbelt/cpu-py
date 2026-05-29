import customtkinter as ctk
import platform
import os
import sys
import psutil

caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

if caminho_raiz not in sys.path:
    sys.path.insert(0, caminho_raiz)

import src.info.memorias
import src.info.so
import src.info.gpu
import src.info.cpu

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CPU-PY")
        self.geometry("900x650")
        self.resizable(False, False)

        self.carregar_dados_estaticos()

        self.nav_frame = ctk.CTkFrame(self, height=70, corner_radius=0)
        self.nav_frame.pack(side="top", fill="x")
        self.nav_frame.pack_propagate(False)

        self.criar_botao_nav("CPU", "#1F6AA5", "#144A74", "cpu")
        self.criar_botao_nav("MEMÓRIA / PLACA-MÃE", "#37474F", "#263238", "ram")
        self.criar_botao_nav("GPU", "#2E7D32", "#1B5E20", "gpu")
        self.criar_botao_nav("SISTEMA OPERACIONAL", "#E65100", "#B33900", "so")
        self.criar_botao_nav("DISCOS", "#00838F", "#005662", "disco")


        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.container.pack(side="bottom", fill="both", expand=True)

        self.telas = {}
        self.criar_tela_cpu()
        self.criar_tela_gpu()
        self.criar_tela_ram()
        self.criar_tela_disco()
        self.criar_tela_so()

        self.mudar_aba("cpu")

        self.atualizar_telemetria()

    def mudar_aba(self, nome_aba):
        for tela in self.telas.values():
            tela.pack_forget()

        self.telas[nome_aba].pack(fill="both", expand=True)
        self.aba_atual = nome_aba

    def alternar_slot_gpu(self, texto):
        chave_slot = texto.split(" | ")[0]

        if chave_slot in self.gpus:
            self.gpu_slot_selecionado = chave_slot
            self.lbl_gpu_nome.configure(text=self.gpus[chave_slot]["nome"])
            self.lbl_gpu_fab.configure(text=self.gpus[chave_slot]["fabricante"])
            self.lbl_gpu_tipo.configure(text=self.gpus[chave_slot]["tipo"])

    def criar_botao_nav(self, texto, cor, cor_hover, id_aba):
        btn = ctk.CTkButton(self.nav_frame, text=texto, font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=cor, hover_color=cor_hover, width=160, height=50, corner_radius=0,
        command=lambda: self.mudar_aba(id_aba))

        btn.pack(side="left", padx=10, pady=10)

    def criar_card_informativo(self, mestre, cor_titulo, texto, cor_fundo="#212121", largura_borda=1, cor_borda="#333333", val_padx=30, val_pady=20):
        card = ctk.CTkFrame(mestre, fg_color=cor_fundo, border_width=largura_borda, border_color=cor_borda)
        card.pack(fill="x", padx=val_padx, pady=val_pady)
        lbl_card = ctk.CTkLabel(card, text=texto, font=ctk.CTkFont(size=28, weight="bold"), text_color=cor_titulo)
        lbl_card.pack(anchor="w", padx=20, pady=10)
        return card

    def inserir_linha_informacao(self, card, texto_h, texto_valor):
        linha = ctk.CTkFrame(card, fg_color="transparent")
        linha.pack(fill="x", padx=30, pady=10)
        lbl_h = ctk.CTkLabel(linha, text=texto_h, font=ctk.CTkFont(size=18, weight="bold"))
        lbl_h.pack(side="left")
        lbl_valor = ctk.CTkLabel(linha, text=texto_valor, font=ctk.CTkFont(size=18))
        lbl_valor.pack(side="left")
        return lbl_valor

    def criar_tela_cpu(self):
        tela = ctk.CTkFrame(self.container, fg_color="transparent")

        cabecalho = ctk.CTkFrame(tela, fg_color="#1F6AA5", height=60, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)
        lbl_cabecalho = ctk.CTkLabel(cabecalho, text="Processador", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        lbl_cabecalho.pack(side="left", padx=30, pady=15)

        card_processador = self.criar_card_informativo(tela, "#1F6AA5", "Informações do Processador", val_pady=10)

        self.inserir_linha_informacao(card_processador, "Nome: ", self.cpu["nome"])
        self.inserir_linha_informacao(card_processador, "Frequência: ", f"{round(self.cpu['frequencia'], 2)} GHz")
        self.inserir_linha_informacao(card_processador, "Arquitetura: ", self.cpu["arquitetura"])
        self.inserir_linha_informacao(card_processador, "Núcleos Físicos: ", self.cpu["nucleos_fisicos"])
        self.inserir_linha_informacao(card_processador, "Threads: ", self.cpu["nucleos_logicos"])

        card_cache = self.criar_card_informativo(tela, "#1F6AA5", "Cache Físico", val_pady=10)

        lista_niveis_cache = list(self.caches.keys())
        lista_niveis_cache.sort()

        for nivel in lista_niveis_cache:
            self.inserir_linha_informacao(card_cache, f"{nivel}: ", self.caches[nivel])

        self.telas["cpu"] = tela

    def criar_tela_gpu(self):
        tela = ctk.CTkFrame(self.container, fg_color="transparent")

        cabecalho = ctk.CTkFrame(tela, fg_color="#2E7D32", height=60, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)
        lbl_cabecalho = ctk.CTkLabel(cabecalho, text="Placa de Vídeo", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        lbl_cabecalho.pack(side="left", padx=30, pady=15)

        card_gpu = ctk.CTkFrame(tela, fg_color="#212121", border_width=1, border_color="#333333")
        card_gpu.pack(fill="both", expand=True, padx=30, pady=20)
        linha_selecao = ctk.CTkFrame(card_gpu, fg_color="transparent")
        linha_selecao.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(linha_selecao, text="Selecione a Placa de Vídeo:", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20, pady=5)
        opcoes_menu = [f"{slot} | {self.gpus[slot]['nome']}" for slot in self.gpu_slots]

        if not opcoes_menu:
            opcoes_menu = ["Nenhuma GPU detectada"]

        self.menu_gpu = ctk.CTkOptionMenu(linha_selecao, values=opcoes_menu, command=self.alternar_slot_gpu, fg_color="#2E7D32", button_color="#1b5e20", button_hover_color="#144A75", width=450, font=ctk.CTkFont(size=16))
        self.menu_gpu.pack(anchor="w", padx=20, pady=5)

        self.lbl_gpu_nome = self.inserir_linha_informacao(card_gpu, "Nome: ", self.gpu_selecionada["nome"])
        self.lbl_gpu_fab = self.inserir_linha_informacao(card_gpu, "Fabricante: ", self.gpu_selecionada["fabricante"])
        self.lbl_gpu_tipo = self.inserir_linha_informacao(card_gpu, "Tipo: ", self.gpu_selecionada["tipo"])

        lbl_uso_titulo = ctk.CTkLabel(card_gpu, text="Uso:", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_uso_titulo.pack(anchor="w", padx=30, pady=(10, 0))

        linha_gpu_uso = ctk.CTkFrame(card_gpu, fg_color="transparent")
        linha_gpu_uso.pack(fill="x", padx=30, pady=5)

        self.barra_gpu_uso = ctk.CTkProgressBar(linha_gpu_uso, width=600, height=15, progress_color="#2E7D32", corner_radius=0)
        self.barra_gpu_uso.pack(side="left", padx=(0, 20))
        self.barra_gpu_uso.set(0.0)

        self.lbl_gpu_num = ctk.CTkLabel(linha_gpu_uso, text="N/A", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_gpu_num.pack(side="left")

        self.card_temp = ctk.CTkFrame(card_gpu, fg_color="#1A1A1A", width=250, height=80)
        self.card_temp.pack(anchor="w", padx=300, pady=20)
        self.card_temp.pack_propagate(False)

        self.lbl_gpu_temp = ctk.CTkLabel(self.card_temp, text="Temp: --°C", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E53935")
        self.lbl_gpu_temp.pack(expand=True)

        self.telas["gpu"] = tela

    def criar_tela_ram(self):
        tela = ctk.CTkFrame(self.container, fg_color="transparent")

        cabecalho = ctk.CTkFrame(tela, fg_color="#37474F", height=60, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)
        lbl_cabecalho = ctk.CTkLabel(cabecalho, text="Memória RAM e Placa-Mãe", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        lbl_cabecalho.pack(side="left", padx=30, pady=15)

        card_ram = self.criar_card_informativo(tela, "#37474F", "Memória RAM")
        self.inserir_linha_informacao(card_ram, "Tecnologia: ", self.ram["tecnologia"])

        linha_uso = ctk.CTkFrame(card_ram, fg_color="transparent")
        linha_uso.pack(fill="x", padx=20, pady=10)

        self.barra_ram_uso = ctk.CTkProgressBar(linha_uso, width=600, height=15, progress_color="#37474F", corner_radius=0)
        self.barra_ram_uso.pack(side="left", padx=(0, 20))
        self.barra_ram_uso.set(float(self.ram["percentual_uso"]) / 100)

        self.lbl_ram_uso = ctk.CTkLabel(linha_uso, text=f"{self.ram['em_uso']} GB / {self.ram['total']} GB")
        self.lbl_ram_uso.pack(side="left")

        card_placa_mae = self.criar_card_informativo(tela, "#37474F", "Placa-Mãe")

        self.inserir_linha_informacao(card_placa_mae, "Fabricante: ", self.placa_mae["fabricante"])
        self.inserir_linha_informacao(card_placa_mae, "Modelo: ", self.placa_mae["modelo"])

        self.telas["ram"] = tela

    def criar_tela_so(self):
        tela = ctk.CTkFrame(self.container, fg_color="transparent")
        cabecalho = ctk.CTkFrame(tela, fg_color="#E65100", height=60, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)
        lbl_cabecalho = ctk.CTkLabel(cabecalho, text="Sistema Operacional", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        lbl_cabecalho.pack(side="left", padx=30)

        frame_conteudo = ctk.CTkScrollableFrame(tela, fg_color="transparent", orientation="vertical")
        frame_conteudo.pack(fill="both", expand=True, padx=20, pady=10)

        card_sistema = self.criar_card_informativo(frame_conteudo, "#E65100", "Sistema")

        self.inserir_linha_informacao(card_sistema, "Sistema: ", self.sistem_op["sistema"])
        self.inserir_linha_informacao(card_sistema, "Versão: ", self.sistem_op["versao"])
        self.inserir_linha_informacao(card_sistema, "Arquitetura: ", self.sistem_op["arquitetura"])

        if self.sistem_op["sistema"] == "Linux":
            self.inserir_linha_informacao(card_sistema, "Distribuição: ", self.sistem_op["distro_nome"])
            self.inserir_linha_informacao(card_sistema, "Versão da Distribuição: ", self.sistem_op["distro_versao"])
            self.inserir_linha_informacao(card_sistema, "Ambiente Gráfico: ", self.sistem_op["ambiente_grafico"])
            self.inserir_linha_informacao(card_sistema, "Servidor de Janelas: ", self.sistem_op["servidor_janelas"])

        card_monitores = self.criar_card_informativo(frame_conteudo, "#E65100", "Monitores")
        for i, monitor in enumerate(self.monitores):
            card_monitor = self.criar_card_informativo(card_monitores, "white", f"Monitor {i+1}")
            self.inserir_linha_informacao(card_monitor, "Conexão: ", monitor["conexao"])
            self.inserir_linha_informacao(card_monitor, "Resolução: ", monitor["resolucao"])
            self.inserir_linha_informacao(card_monitor, "Tamanho: ", monitor["tamanho"])
            self.inserir_linha_informacao(card_monitor, "Tipo: ", "Primário" if monitor["primario"] else "Secundário")

        if self.bateria["possui_bateria"]:
            card_bateria = self.criar_card_informativo(frame_conteudo, "#E65100", "Bateria")
            self.nivel_bateria = self.inserir_linha_informacao(card_bateria, "Carga: ", f"{self.bateria['porcentagem']}%")
            self.carregando = self.inserir_linha_informacao(card_bateria, "Carregando: ", "Sim" if self.bateria["carregando"] else "Não")

        self.telas["so"] = tela

    def criar_tela_disco(self):
        tela = ctk.CTkFrame(self.container, fg_color="transparent")
        cabecalho = ctk.CTkFrame(tela, fg_color="#00838F", height=60, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)
        ctk.CTkLabel(cabecalho, text="Partições de Armazenamento", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left", padx=30)
        frame_conteudo = ctk.CTkScrollableFrame(tela, fg_color="transparent", orientation="vertical")
        frame_conteudo.pack(fill="both", expand=True, padx=20, pady=10)

        for i, particao in enumerate(self.discos):
            card_disco = self.criar_card_informativo(frame_conteudo, "#00838F", f"Partição {i+1}")
            self.inserir_linha_informacao(card_disco, "Dispositivo: ", particao["dispositivo"])
            self.inserir_linha_informacao(card_disco, "Ponto de Montagem: ", particao["ponto_montagem"])
            self.inserir_linha_informacao(card_disco, "Sistema de Arquivos: ", particao["tipo_sistema_arquivos"])
            linha_uso = ctk.CTkFrame(card_disco, fg_color="transparent")
            linha_uso.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(linha_uso, text="Uso: ", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=15)
            barra_part_uso = ctk.CTkProgressBar(linha_uso, width=550, height=15, progress_color="#00838F", corner_radius=0)
            particao["barra"] = barra_part_uso
            barra_part_uso.pack(side="left", padx=(0, 20))
            barra_part_uso.set(particao["usado"] / particao["total"])
            lbl_uso = ctk.CTkLabel(linha_uso, text=f"{particao['usado']}GB / {particao['total']}GB", font=ctk.CTkFont(size=16))
            particao["label"] = lbl_uso
            lbl_uso.pack(side="left")

        self.telas["disco"] = tela

    def carregar_dados_estaticos(self):
        self.gpus = src.info.gpu.dados_gpu()
        self.gpu_slots = list(self.gpus.keys())
        self.gpu_slots.sort()

        if self.gpu_slots:
            self.gpu_slot_selecionado = self.gpu_slots[0]
            self.gpu_selecionada = self.gpus[self.gpu_slot_selecionado]
        else:
            self.gpu_selecionada = {
                "nome": "N/A",
                "fabricante": "N/A",
                "tipo": "N/A",
                "id": "N/A"
            }

        self.cpu = src.info.cpu.dados_cpu()
        self.ram = src.info.memorias.dados_memoria()
        self.ram["tecnologia"] = src.info.memorias.dados_ddr()
        self.discos = src.info.memorias.dados_discos()
        self.caches = src.info.cpu.dados_cache()
        self.sistem_op = src.info.so.dados_so()
        self.monitores = src.info.so.dados_monitores()
        self.bateria = src.info.so.dados_bateria()
        self.placa_mae = src.info.memorias.dados_placa_mae()


    def atualizar_telemetria(self):
        try:
            if self.aba_atual == "ram":
                self.ram = src.info.memorias.dados_memoria()
                self.barra_ram_uso.set(float(self.ram["percentual_uso"]) / 100)
                self.lbl_ram_uso.configure(text=f"{self.ram['em_uso']}GB / {self.ram['total']}GB")

            elif self.aba_atual == "gpu":
                if self.gpus[self.gpu_slot_selecionado]["fabricante"] == "NVIDIA":
                    telemetria = src.info.gpu.telemetria_nvidia(self.gpus[self.gpu_slot_selecionado]["id"])
                elif self.gpus[self.gpu_slot_selecionado]["fabricante"] == "AMD":
                    if self.sistem_op["sistema"] == "Windows":
                        telemetria = telemetria_amd_windows(self.gpus[self.gpu_slot_selecionado]["id"])
                    else:
                        telemetria = telemetria_amd_linux(self.gpu_slot_selecionado)

                uso_gpu = telemetria["uso"]
                temp_gpu = telemetria["temperatura"]
                self.lbl_gpu_num.configure(text=f"{uso_gpu}%")
                self.barra_gpu_uso.set(uso_gpu / 100)
                self.lbl_gpu_temp.configure(text=f"Temperatura da GPU: {temp_gpu}°C")

            elif self.aba_atual == "so":
                self.bateria = src.info.so.dados_bateria()
                self.nivel_bateria.configure(text=f"{self.bateria['porcentagem']}%")
                self.carregando.configure(text="Sim" if self.bateria["carregando"] else "Não")

        except Exception:
            pass

        self.after(1000, self.atualizar_telemetria)

if __name__ == '__main__':
    app = MonitorApp()
    app.mainloop()
