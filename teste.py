import subprocess
import json
import traceback

def investigar_comando(nome_componente, comando_lista):
    print(f"\n==================================================")
    print(f"🔍 INVESTIGANDO: {nome_componente}")
    print(f"==================================================")

    try:
        # Executa o comando exigindo que ele retorne sucesso (check=True)
        resultado = subprocess.run(
            comando_lista,
            capture_output=True,
            text=True,
            check=True
        )

        print("🟢 STATUS: O PowerShell executou o comando com sucesso!")
        print(f"➡️ SAÍDA BRUTA RECONHECIDA:\n{resultado.stdout}")

        # Se você estivesse tentando usar JSON, vamos testar se a conversão passa:
        if "ConvertTo-Json" in "".join(comando_lista):
            try:
                dados_json = json.loads(resultado.stdout)
                print(f"✅ JSON VALIDADO: Convertido para dicionário Python com sucesso.")
                print(f"Dados decodificados: {dados_json}")
            except json.JSONDecodeError as je:
                print(f"❌ ERRO DE PARSING: O texto retornado não é um JSON válido!")
                print(f"Detalhe do erro: {je}")

    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO NO POWERSHELL (Exit Code {e.returncode})")
        print(f"Sua string de comando está mal formatada ou é inválida.")
        print(f"Mensagem interna do Windows:\n{e.stderr}")

    except Exception as e:
        print(f"❌ ERRO INESPERADO NO PYTHON:")
        traceback.print_exc()

# --- EXECUÇÃO DOS TESTES ALVO ---

# 1. Teste do Cache (Usando a abordagem de somar strings sem aspas duplas perigosas)
cmd_cache = [
    "powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_CacheMemory | ForEach-Object { [string]$_.Level + ',' + [string]$_.InstalledSize }"
]
investigar_comando("CACHE MEMORY", cmd_cache)

# 2. Teste da GPU (Puxando dados estruturados via JSON para evitar quebra de colunas)
cmd_gpu = [
    "powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, PNPDeviceID | ConvertTo-Json"
]
investigar_comando("GPU / VÍDEO", cmd_gpu)
