def bytes_para_gb(valor):
    return round(valor / (1024 ** 3), 2)

def executar_primeiro_valido(comandos):
    """ Recebe uma lista de comandos e retorna o primeiro comando
    que nao houver erros
    """

    for comando in comandos:
        try:
            resultado = subprocess.check_output(
                comando,
                text=True,
                stderr=subprocess.DEVNULL
            )
            return resultado
        except Exception:
            continue

        return ""

def formatar_comando(resultado):
    linhas = [linha.strip() for linha in resultado.split('\n') if linha.strip()]
    return linhas

def kb_para_mb(valor_kb):
    valor_mb = round(valor_kb / 1024, 1)
    return valor_mb
