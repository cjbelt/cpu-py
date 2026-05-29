import platform
from ctypes import c_int, c_void_p, byref, Structure, cdll, sizeof

class ADLTemperature(Structure):
    _fields_ = [
        ("iSize", c_int),
        ("iTemperature", c_int)
    ]

def obter_temperatura():
    try:
        try:
            amd_dll = cdll.LoadLibrary("atiadlxx.dll")
        except OSError:
            amd_dll = cdll.LoadLibrary("atiadlxy.dll")

        temperatura_struct = ADLTemperature()
        temperatura_struct.iSize = sizeof(ADLTemperature)

        resultado = amd_dll.ADL_Overdrive5_Temperature_Get(0, 0, byref(temperatura_struct))

        if resultado == 0:
            return f"{int(temperatura_struct.iTemperature / 1000)}°C"

    except Exception:
        pass

    return "N/A"

if platform.system() == "Windows":
    from ctypes import windll, WINFUNCTYPE

    @WINFUNCTYPE(c_void_p, c_int)
    def adl_alocacao_callback(tamanho):
        """Aloca memoria no Windows"""
        try:
            return windll.ole32.CoTaskMemAlloc(tamanho)
        except Exception:
            return 0

    class ADLPMActivity(Structure):
        _fields_ = [
            ("iSize", c_int),
            ("iEngineClock", c_int),
            ("iMemoryClock", c_int),
            ("iVddc", c_int),
            ("iActivityPercent", c_int),
            ("iCurrentBusSpeed", c_int),
            ("iCurrentBusLanes", c_int),
            ("iMaximumBusLanes", c_int),
            ("iReserved", c_int)
        ]

    def obter_porcentagem_uso(id_adaptador=0):
        try:
            amd_dll = cdll.LoadLibrary("atiadlxx.dll")
        except OSError:
            try:
                amd_dll = cdll.LoadLibrary("atiadlxy.dll")
            except OSError:
                return "Driver não encontrado"

        status_inicial = amd_dll.ADL_Main_Control_Create(adl_alocacao_callback, 1)

        if status_inicial != 0:
            return "Falha ao iniciar subsistema ADL da AMD"

        try:
            atividade = ADLPMActivity()
            atividade.iSize = sizeof(ADLPMActivity)

            resultado = amd_dll.ADL_Overdrive5_CurrentActivity_Get(id_adaptador, byref(atividade))

            if resultado == 0:
                uso_atual = atividade.iActivityPercent

                if 0 <= uso_atual <= 100:
                    return f"{uso_atual}%"
                return "0%"
            else:
                return "Sensor Overdrive inacessível para este adaptador"

        finally:
            amd_dll.ADL_Main_Control_Destroy()
