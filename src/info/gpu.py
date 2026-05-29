import platform
import subprocess
import os
import src.info.amd_wrapper
from src.info.utilidades import *

def dados_gpu():
    sistema = platform.system()
    gpus = {}

    if sistema == "Windows":
        try:
            comando = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | ForEach-Object { [string]$_.Name + ';' + [string]$_.AdapterRAM + ';' + [string]$_.PNPDeviceID }"]
            saida = subprocess.run(comando, text=True, timeout=5, capture_output=True).stdout
            linhas = formatar_comando(saida)

            for idx, linha in enumerate(linhas):
                slot = f"gpu{idx}"
                nome, vram, pnp_id = linha.split(";")

                try:
                    vram_gb = bytes_para_gb(vram)
                except ValueError:
                    vram_gb = 0

                nome_minusculo = nome.lower()
                dedicada = vram_gb > 1.5 or "geforce" in nome_minusculo or "radeon rx" in nome_minusculo or "nvidia" in nome_minusculo
                tipo = "Dedicada" if dedicada else "Integrada"
                fabricante = "NVIDIA" if "nvidia" in nome_minusculo or "10DE" in pnp_id.upper() else "AMD" if "amd" in nome_minusculo or "1002" in pnp_id.upper() else "Intel"

                gpus[slot] = {
                    "id": idx,
                    "nome": nome,
                    "fabricante": fabricante,
                    "tipo": tipo,
                }

        except Exception:
            pass

    elif sistema == "Linux":
        caminho_drm = "/sys/class/drm/"

        if os.path.exists(caminho_drm):
            slots = [d for d in os.listdir(caminho_drm) if d.startswith("card") and "-" not in d]

            for idx, slot in enumerate(sorted(slots)):
                caminho_placa = os.path.join(caminho_drm, slot, "device")

                if not os.path.exists(caminho_placa):
                    continue

                try:
                    endereco_pci = os.path.basename(os.path.realpath(caminho_placa))
                    saida_lspci = subprocess.run(["lspci", "-s", endereco_pci], text=True, capture_output=True).stdout.strip()
                    nome = saida_lspci.split("controller:")[1].strip()
                except Exception:
                    nome = "Placa de vídeo"

                try:
                    id_fabricante = open(os.path.join(caminho_placa, "vendor"), "r").read().strip()
                except Exception:
                    id_fabricante = ""

                dedicada = os.path.exists(os.path.join(caminho_placa, "mem_info_vram_total")) or "10de" in id_fabricante
                tipo = "Dedicada" if dedicada else "Integrada"

                if "10de" in id_fabricante:
                    fabricante = "NVIDIA"
                elif "1002" in id_fabricante:
                    fabricante = "AMD"
                else:
                    fabricante = "Intel"

                gpus[slot] = {
                    "id": idx,
                    "nome": nome,
                    "fabricante": fabricante,
                    "tipo": tipo,
                }

    return gpus

def telemetria_nvidia(id_slot=0):
    try:
        comando = ["nvidia-smi", "-i", str(id_slot), "--query-gpu=temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"]
        saida = subprocess.run(comando, text=True, capture_output=True, timeout=10).stdout.strip()
        temperatura, uso = saida.split(",")
        return {
            "temperatura": int(temperatura.strip()),
            "uso": int(uso.strip())
        }
    except Exception:
        return {
            "temperatura": "N/A",
            "uso": "N/A"
        }

def telemetria_amd_linux(slot):
    dados = {
        "temperatura": "N/A",
        "uso": "N/A"
    }

    caminho_base = f"/sys/class/drm/{slot}/device"

    try:
        arquivo_uso = os.path.join(caminho_base, "gpu_busy_percent")

        if os.path.exists(arquivo_uso):
            f = open(arquivo_uso, "r")
            dados["uso"] = f"{f.read().strip()}%"

        caminho_hwmon = os.path.join(caminho_base, "hwmon")

        if os.path.exists(caminho_hwmon):
            for h in os.listdir(caminho_hwmon):
                arquivo_temperatura = os.path.join(caminho_hwmon, h, "temp1_input")

                if os.path.exists(arquivo_temperatura):
                    temperatura_mili = int(open(arquivo_temperatura, "r").read().strip())
                    dados["temperatura"] = f"{round(temperatura_mili / 1000)}°C"
                    break
    except Exception:
        pass

    return dados

def telemetria_amd_windows(id_adaptador):
    """ Retorna a porcentagem de uso e a temperatura da gpu AMD.
        O wrapper utilizado foi gerado por IA e não foi possível ser testado, portanto pode não funcionar.
    """

    telemetria = {
        "temperatura": "N/A",
        "uso": "N/A"
    }

    try:
        telemetria["uso"] = amd_wrapper.obter_porcentagem_uso(id_adaptador)
        telemetria["temperatura"] = amd_wrapper.obter_temperatura(id_adaptador)
    except Exception:
        pass

    return telemetria

if __name__ == '__main__':
    print(dados_gpu())
