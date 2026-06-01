import platform
import psutil
import subprocess
import os
import json
if platform.system() == "Windows":
    import wmi
    import pythoncom

from src.info.utilidades import *
# from utilidades import *

def dados_memoria():
    memoria = psutil.virtual_memory()
    dados = {
        "total": bytes_para_gb(memoria.total),
        "disponivel": bytes_para_gb(memoria.available),
        "em_uso": bytes_para_gb(memoria.used),
        "percentual_uso": memoria.percent,
    }

    return dados

def mapear_ddr(codigo):
    codigos = {
        "21": "DDR2",
        "24": "DDR3",
        "26": "DDR4",
        "30": "LPDDR4",
        "34": "DDR5",
        "35": "LPDDR5"
    }

    return codigos.get(codigo, "N/A")

def dados_ddr():
    sistema = platform.system()

    if sistema == 'Windows':
        comando = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_PhysicalMemory | Select-Object -ExpandProperty SMBIOSMemoryType"]
        saida = subprocess.run(comando, text=True, capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW).stdout
        linhas = formatar_comando(saida)

        if linhas:
            return mapear_ddr(linhas[0])

    elif sistema == 'Linux':
        try:
            comando = ["pkexec", "dmidecode", "--type", "memory"]
            saida = subprocess.run(comando, text=True, capture_output=True).stdout
            linhas = formatar_comando(saida)

            for linha in linhas:
                if "Type:" in linha and "DDR" in linha:
                    return linha.split("Type:")[1].strip()
        except Exception:
            pass

    return "Desconhecido"

def dados_discos():
    discos = []
    particoes = psutil.disk_partitions()

    for particao in particoes:
        if 'cdrom' in particao.opts or not particao.device:
            continue

        try:
            uso = psutil.disk_usage(particao.mountpoint)
            discos.append({
                "dispositivo": particao.device,
                "ponto_montagem": particao.mountpoint,
                "tipo_sistema_arquivos": particao.fstype,
                "total": bytes_para_gb(uso.total),
                "usado": bytes_para_gb(uso.used),
                "livre": bytes_para_gb(uso.free),
                "percentual": uso.percent
            })
        except PermissionError:
            continue

    return discos

def dados_placa_mae():
    sistema = platform.system()

    if sistema == "Windows":
        pythoncom.CoInitialize()

        try:
            conexao = wmi.WMI()
            placas = conexao.Win32_BaseBoard()

            for placa in placas:
                modelo = getattr(placa, "Product", "Desconhecido")
                fabricante = getattr(placa, "Manufacturer", "Desconhecido")
                break
            return {
                "fabricante": fabricante,
                "modelo": modelo
            }
        except Exception:
            return {"fabricante": "Desconhecido", "modelo": "Desconhecido"}
        finally:
            pythoncom.CoUninitialize()

    elif sistema == "Linux":
        try:
            fabricante = open("/sys/class/dmi/id/board_vendor", "r").read().strip()
            nome = open("/sys/class/dmi/id/board_name", "r").read().strip()
            return {"fabricante": fabricante, "modelo": nome}
        except Exception:
            pass

    return {"fabricante": "Desconhecido", "modelo": "Desconhecido"}

def temperatura_placa_mae():
    sistema = platform.system()

    if sistema == "Windows":
        pythoncom.CoInitialize()

        try:
            conexao = wmi.WMI(namespace="root\\wmi")
            zonas_termicas = conexao.MSAcpi_ThermalZoneTemperature()
            return f"{round(zonas_termicas[1].CurrentTemperature / 10.0 - 273.15,1)}°C"
        except Exception:
            return "--°C"
        finally:
            pythoncom.CoUninitialize()

    elif sistema == "Linux":
        sensores = psutil.sensors_temperatures()

        try:
            return f"{sensores['acpitz'][0].current}°C"
        except Exception:
            return "--°C"

if __name__ == '__main__':
    # print(dados_cache())
    # print(dados_ddr())
    print(dados_discos())
    print(temperatura_placa_mae())
