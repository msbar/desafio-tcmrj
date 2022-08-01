import requests
import pandas as pd
from io import StringIO
from unidecode import unidecode
from fake_useragent import UserAgent

def remover_prefixo(x):
    return x.replace('http://landpage-h.cgu.gov.br/dadosabertos/index.php?url=', '')

def padronizar_nome(x):
     x = x.lower()
     x = unidecode(x)
     chrs_rm, chars_rep = ['%','!', '?', '>'], ['-', ' ']
     for c in chrs_rm:
         x = x.replace(c,'')
     for c in chars_rep:
         x = x.replace(c, '_')
     return x
 

def gerar_request(x):
    ua = UserAgent()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US;q=0.6',
    'Connection': 'keep-alive',
    'User-Agent': ua.chrome}
    return StringIO(requests.get(x, headers=headers).text)

def carregar_csv(x):
    dados = gerar_request(x)
    return pd.read_csv(dados, sep=';', engine='python')

def tratar_siglas(x):
    if 'sigla' in x:
        if 'regiao' in x:
            return 'regiao_sigla'
        elif 'estado' in x:
            return 'estado_sigla'
    else:
        return x
