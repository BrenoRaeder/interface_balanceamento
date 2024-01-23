from datetime import datetime
import pytz

def gera_timestamp():
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    utc_atual = datetime.now(pytz.utc)
    timestamp = utc_atual.astimezone(fuso_brasil).strftime('%Y-%m-%d %H:%M:%S %Z')

    return timestamp
