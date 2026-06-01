import platform
import os
import sys
import subprocess
import json
import math
import psutil
import sounddevice as sd
import miniaudio
import numpy as np
from src.info.utilidades import formatar_comando
# from utilidades import formatar_comando

if platform.system() == "Windows":
    import wmi
    import pythoncom
    import win32api
    import win32con

def dados_so():
    dados = {
        "sistema": platform.system(),
        "versao": platform.release(),
        "versao_detalhada": platform.version,
        "arquitetura": platform.machine()
    }

    if dados["sistema"] == "Linux":
        info_distro = platform.freedesktop_os_release()
        dados["distro_nome"] = info_distro.get("NAME", "Linux")
        dados["distro_versao"] = info_distro.get("VERSION_ID", "Desconhecida")
        dados["ambiente_grafico"] = os.environ.get("XDG_CURRENT_DESKTOP", "Desconhecido")
        dados["servidor_janelas"] = os.environ.get("XDG_SESSION_TYPE", "Desconhecido")

    return dados

def dados_monitores():
    sistema = platform.system()
    monitores = []

    if sistema == "Windows":
        saida = []
        pythoncom.CoInitialize()

        try:
            conexao = wmi.WMI(namespace="root\\wmi")
            monitores_conexoes = conexao.WmiMonitorConnectionParams()
            tamanhos = conexao.WmiMonitorBasicDisplayParams()
            mapeamento_tamanhos = {tamanho.InstanceName: tamanho for tamanho in tamanhos}
            telas_sistema = win32api.EnumDisplayMonitors()
            info_telas = []

            for handle, _, _ in telas_sistema:
                info_telas.append(win32api.GetMonitorInfo(handle))

            for i, m in enumerate(monitores_conexoes):
                tamanho = mapeamento_tamanhos.get(m.InstanceName)

                if i < len(info_telas):
                    tela = info_telas[i]
                elif info_telas:
                    tela = info_telas[0]
                else:
                    tela = None

                comprimento_cm = tamanho.MaxHorizontalImageSize if tamanho else 0
                altura_cm = tamanho.MaxVerticalImageSize if tamanho else 0

                if tela:
                    primario = bool(tela.get("Flags", 0) and win32con.MONITORINFOF_PRIMARY)
                    formato = tela.get("Monitor", (0, 0, 0, 0))
                    comp_px = formato[2] - formato[0]
                    altura_px = formato[3] - formato[1]
                else:
                    primario = False
                    comp_px = 0
                    altura_px = 0

                saida.append({
                    "Connection": getattr(m, "VideoOutputTechnology", 0),
                    "WidthCm": comprimento_cm,
                    "HeightCm": altura_cm,
                    "Primary": primario,
                    "Heightpx": altura_px,
                    "WidthPx": comp_px
                })

        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()

        try:
            if saida:
                conexoes = {0: "VGA", 4: "DVI", 5: "HDMI", 10: "LVDS", 14: "DisplayPort", 15: "DisplayPort Integrado"}

                for item in saida:
                    conexao = conexoes.get(item.get("Connection"), "Outra / Desconhecida")
                    comprimento_item = item.get("WidthCm", 0)
                    altura_item = item.get("HeightCm", 0)

                    if comprimento_item > 0 and altura_item > 0:
                        diagonal_polegadas = math.sqrt((comprimento_item / 2.54)**2 + (altura_item / 2.54)**2)
                        tamanho_item = f'{round(diagonal_polegadas, 1)}\"'
                    else:
                        tamanho_item = "N/A"

                    monitores.append({
                        "conexao": conexao,
                        "primario": "Sim" if item.get("Primary") else "Não",
                        "resolucao": f"{item.get('WidthPx')}x{item.get('HeightPx')}",
                        "tamanho": tamanho_item
                    })
        except Exception:
            pass

    elif sistema == "Linux":
        try:
            saida = subprocess.run("xrandr", text=True, capture_output=True).stdout
            linhas = formatar_comando(saida)

            for linha in linhas:
                if " connected" in linha:
                    partes = linha.split()
                    nome_porta = partes[0]

                    if "HDMI" in nome_porta.upper(): conexao = "HDMI"
                    elif "DP" in nome_porta.upper(): conexao = "DisplayPort"
                    elif "VGA" in nome_porta.upper(): conexao = "VGA"
                    elif "EDP" in nome_porta.upper(): conexao = "Notebook (eDP)"
                    else: conexao = "Outra / Desconhecida"

                    primario = "primary" in linha

                    resolucao = "Desconhecida"

                    for parte in partes:
                        if "x" in parte and "+" in parte:
                            resolucao = parte.split("+")[0]
                            break

                    tamanho = "N/A"

                    if linha.endswith("mm") or "mm " in linha:
                        dimensoes = [parte.replace("mm", "") for parte in partes if "mm" in parte]

                        if len(dimensoes) >= 2:
                            try:
                                comprimento_polegadas = float(dimensoes[-2]) / 25.4
                                altura_polegadas = float(dimensoes[-1]) / 25.4
                                diagonal_polegadas = math.sqrt(altura_polegadas**2 + comprimento_polegadas**2)
                                tamanho = f'{round(diagonal_polegadas, 1)}\"'
                            except ValueError:
                                pass

                    monitores.append({
                        "conexao": conexao,
                        "primario": "Sim" if primario else "Não",
                        "resolucao": resolucao,
                        "tamanho": tamanho
                    })

        except Exception:
            pass

    return monitores

def dados_bateria():
    bateria = psutil.sensors_battery()

    if bateria is None:
        return {"possui_bateria": False}

    return {
        "possui_bateria": True,
        "porcentagem": int(bateria.percent),
        "carregando": bateria.power_plugged
    }

def listar_saidas_audio():
    dispositivos = []
    sistema = platform.system()

    if sistema == "Linux":
        dispositivos.append({
            "id": "linux_default",
            "canais_validos": 2
        })

        return dispositivos

    elif sistema == "Windows":
        caminho_mp3 = obter_caminho_arquivo("src/Corinthians vinheta da Radio! Corinthians.mp3")

        if not os.path.exists(caminho_mp3):
            return ["Nenhum Dispositivo Encontrado"]

        info_audio = miniaudio.decode_file(caminho_mp3)
        taxa_mp3 = info_audio.sample_rate
        canais_mp3 = info_audio.nchannels
        todos_dispositivos = sd.query_devices()

        for idx, dispositivo in enumerate(todos_dispositivos):
            if dispositivo["max_output_channels"] > 0:
                try:
                    canais_teste = min(canais_mp3, dispositivo["max_output_channels"])
                    sd.check_output_settings(device=idx, samplerate=taxa_mp3, channels=canais_teste)

                    dispositivos.append({
                        "id": idx,
                        "nome": dispositivo["name"],
                        "canais_validos": canais_teste
                    })
                except Exception:
                    continue

    if dispositivos:
        return dispositivos

    return ["Nenhum Dispositivo Encontrado"]

def obter_caminho_arquivo(nome_arquivo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nome_arquivo)

    return os.path.join(os.path.abspath("."), nome_arquivo)

def reproduzir_som():
    try:
        caminho = obter_caminho_arquivo("src/Corinthians vinheta da Radio! Corinthians.mp3")
        audio_decodificado = miniaudio.decode_file(caminho)

        frequencia = audio_decodificado.sample_rate
        canais = audio_decodificado.nchannels
        dados_brutos = np.frombuffer(audio_decodificado.samples, dtype=np.int16)

        if canais > 1:
            dados_brutos = dados_brutos.reshape(-1, canais)

        sd.play(dados_brutos, samplerate=frequencia)
        sd.wait()
        return True
    except Exception:
        return False

if __name__ == '__main__':
    # print(dados_bateria())
    # print(dados_monitores())
    # print(listar_saidas_audio())
    reproduzir_som()
