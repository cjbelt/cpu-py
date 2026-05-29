import psutil
import cpuinfo
import platform
import os

if platform.system() == "Windows":
    import wmi
    import pythoncom

import subprocess
from src.info.utilidades import *
# from utilidades import *

def dados_cpu():
    info = cpuinfo.get_cpu_info()

    dados = {
        "nome": info.get("brand_raw", "Desconhecido"),
        "arquitetura": info.get("arch", "Desconhecida"),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_logicos": psutil.cpu_count(logical=True),
        "frequencia": psutil.cpu_freq()[2] / 1000
    }

    return dados

def dados_cache():
    sistema = platform.system()
    caches = {}

    if sistema == "Windows":
        pythoncom.CoInitialize()

        try:
            conexao = wmi.WMI()
            caches_wmi = conexao.Win32_CacheMemory()

            for cache in caches_wmi:
                try:
                    nivel = getattr(cache, "Level", 0)
                    tamanho = getattr(cache, "InstalledSize", 0)

                    if nivel == "3":
                        caches["L1"] = caches.get("L1", 0) + tamanho
                    elif nivel == "4":
                        caches["L2"] = caches.get("L2", 0) + tamanho
                    elif nivel == "5":
                        caches["L3"] = caches.get("L3", 0) + tamanho
                except (ValueError, IndexError):
                    continue

            for cache in caches:
                caches[cache] = f"{caches[cache]}K"

        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()

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

if __name__ == '__main__':
    print(dados_cpu()["frequencia"])
