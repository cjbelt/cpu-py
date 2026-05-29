import platform
import os
import subprocess
import json
import math
import psutil
from utilidades import formatar_comando

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
        script = """
        $monitors = @(Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorConnectionParams)
        $sizes = @(Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorBasicDisplayParams)
        Add-Type -AssemblyName System.Windows.Forms
        $screens = [System.Windows.Forms.Screen]::AllScreens

        $output = @()
        for ($i=0; $i -lt $monitors.Count; $i++) {
            $m = $monitors[$i]
            $s = $sizes | Where-Object { $_.InstanceName -eq $m.InstanceName }
            $scr = if ($i -lt $screens.Count) { $screens[$i] } else { $screens[0] }

            $output += [PSCustomObject]@{
                Connection = $m.VideoOutputTechnology
                WidthCm = if ($s) { $s.MaxHorizontalImageSize } else { 0 }
                HeightCm = if ($s) { $s.MaxVerticalImageSize } else { 0 }
                Primary = if ($scr) { $scr.Primary } else { $false }
                WidthPx = if ($scr) { $scr.Bounds.Width } else { 0 }
                HeightPx = if ($scr) { $scr.Bounds.Height } else { 0 }
            }
        }
        $output | ConvertTo-Json
        """

        try:
            comando = ["powershell", "-NoProfile", "-Command", script]
            saida = subprocess.check_output(comando, text=True, stderr=subprocess.DEVNULL).strip()

            if saida:
                dados = json.loads(saida)

                if not isinstance(dados, list):
                    dados = [dados]

                conexoes = {0: "VGA", 4: "DVI", 5: "HDMI", 10: "LVDS", 14: "DisplayPort", 15: "DisplayPort Integrado"}

                for item in dados:
                    conexao = conexoes.get(item.get("Connection"), "Outra / Desconhecida")
                    comprimento_cm = item.get("WidthCm", 0)
                    altura_cm = item.get("HeightCm", 0)

                    if comprimento_cm > 0 and altura_cm > 0:
                        diagonal_polegadas = math.sqrt((comprimento_cm / 2.54)**2 + (altura_cm / 2.54)**2)
                        tamanho = f'{round(diagonal_polegadas, 1)}\"'
                    else:
                        tamanho = "N/A"

                    monitores.append({
                        "conexao": conexao,
                        "primario": "Sim" if item.get("Primary") else "Não",
                        "resolucao": f"{item.get('WidthPx')}x{item.get('HeightPx')}",
                        "tamanho": tamanho
                    })
        except Exception:
            pass

    elif sistema == "Linux":
        try:
            saida = subprocess.check_output("xrandr", text=True, stderr=subprocess.DEVNULL)
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

if __name__ == '__main__':
    # print(dados_bateria())
    print(dados_monitores())
