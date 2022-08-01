import pandas as pd
from unidecode import unidecode
from sqlalchemy import create_engine

def gerar_url(i):
    return f'http://compras.dados.gov.br/pregoes/v1/pregoes.csv?co_uasg=986001&order_by=dt_data_edital&order=desc&offset={i}'

def consumir_api(i):
    return pd.read_csv(gerar_url(i))

def padronizar_nome(x):
     x = x.lower()
     x = unidecode(x)
     chrs_rm, chars_rep = ['%','!', '?', '>'], ['-', ' ']
     for c in chrs_rm:
         x = x.replace(c,'')
     for c in chars_rep:
         x = x.replace(c, '_')
     return x

if __name__ == "__main__":
    dfs, i = [], 0
    while True:
        print(f"Extraindo dados com offset : {i}")
        df = consumir_api(i)
        if pd.to_datetime(df['Data de Abertura do Edital'], dayfirst=True).dt.year.max() < 2021:
            break
        dfs.append(df)
        i += 500

    df = pd.concat(dfs)

    df['Data de Abertura do Edital'] = pd.to_datetime(df['Data de Abertura do Edital'], dayfirst=True)
    df = df[df['Data de Abertura do Edital'].dt.year >= 2021]
    df[['Numero do Pregao', 'Código processo', 'Data portaria', 'Objeto do pregão', 
        'Data de Abertura do Edital', 'Data de início da proposta', 'Data do fim da proposta']]
    df.columns = [unidecode(padronizar_nome(c)) for c in df.columns]

    engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
    df.to_sql('api_data', engine)