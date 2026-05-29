import psutil
import cpuinfo
import platform
import os
from src.info.utilidades import *

def dados_cpu():
    info = cpuinfo.get_cpu_info()

    dados = {
        "nome": info.get("brand_raw", "Desconhecido"),
        "arquitetura": info.get("arch", "Desconhecida"),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_logicos": psutil.cpu_count(logical=True)
    }

    return dados

def dados_cache():
    sistema = platform.system()
    caches = {}

    if sistema == "Windows":
        try:
            comando = ["powershell",  "-NoProfile", "-Command", 'Get-CimInstance Win32_CacheMemory | ForEach-Object { \"$($_.Level),$($_.InstalledSize)\" }']
            saida = subprocess.run(comando, text=True, timeout=5, capture_output=True).stdout

            if saida:
                linhas = formatar_comando(saida)

                for linha in linhas:
                    try:
                        nivel, tamanho_kb = linha.split(',')
                        tamanho_kb = int(tamanho_kb)

                        if nivel == "3":
                            caches["L1"] += tamanho_kb
                        elif nivel == "4":
                            caches["L2"] += tamanho_kb
                        elif nivel == "5":
                            caches["L3"] += tamanho_kb
                    except (ValueError, IndexError):
                        continue
        except Exception:
            pass

    elif sistema == "Linux" and os.path.exists("/sys/devices/system/cpu/cpu0/cache/"):
        try:
            for i in range(4):
                caminho_tamanho = f"/sys/devices/system/cpu/cpu0/cache/index{i}/size"
                caminho_nivel = f"/sys/devices/system/cpu/cpu0/cache/index{i}/level"

                if os.path.exists(caminho_tamanho):
                    tamanho = open(caminho_tamanho, "r").read().strip()
                    nivel = open(caminho_nivel, "r").read().strip()
                    caches[f"L{nivel}"] = tamanho
        except Exception:
            pass

    return caches
