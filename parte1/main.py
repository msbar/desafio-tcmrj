import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode
from sqlalchemy import create_engine

from helpers import remover_prefixo, carregar_csv, padronizar_nome, tratar_siglas

if __name__ == "__main__":
    # bloco de aquisicao dos dados
    url_base = "https://dados.gov.br/dataset/serie-historica-de-precos-de-combustiveis-por-revenda"
    resposta = requests.get(url_base)
    soup     = BeautifulSoup(resposta.text, features="html.parser")

    # captura dos links com os arquivos csv
    csvs = [remover_prefixo(link.get('href')) for link in list(soup.findAll('a', href=re.compile("csv")))]

    # bloco de filtragem
    glp             = filter(lambda x: '2022/precos-glp-' in x, csvs)
    etanol_gasolina = filter(lambda x: '2022/precos-gasolina-etanol' in x, csvs)
    diesel          = filter(lambda x: '2022/precos-diesel-gnv' in x, csvs)

    # leitura em dataframes
    df_diesel             = pd.concat([carregar_csv(link) for link in diesel])
    df_diesel['nome_produto']  = ['Óleo Diesel S-500 e S-10 + GNV'] * len(df_diesel)

    df_glp                = pd.concat([carregar_csv(link) for link in glp])
    df_glp['nome_produto']     = ['GLP P13'] * len(df_glp)

    df_etanol_gasolina    = pd.concat([carregar_csv(link) for link in etanol_gasolina])
    df_etanol_gasolina['nome_produto'] = ['Etanol + Gasolina Comum'] * len(df_etanol_gasolina)

    # concatenação dos arquivos
    df = pd.concat([df_diesel, df_glp, df_etanol_gasolina])
    
    # bloco de tratamento das colunas
    df.columns = [tratar_siglas(unidecode(padronizar_nome(c))) for c in df.columns]
    df['cnpj_completo'] = df['cnpj_da_revenda'].apply(lambda x : x.replace('.','').replace('/','').replace('-', ''))
    df['cnpj_basico'] = df['cnpj_da_revenda'].apply(lambda x : x.replace('.','')[:8])
    df = df.rename(columns={'nome_da_rua':'rua', 'numero_rua':'numero', 'valor_de_venda':'valor_venda', 'valor_de_compra':'valor_compra', 'data_da_coleta':'data_coleta'})
    
    # manipulacao dos daos
    df_prods = pd.DataFrame({'id':[0,1,2], 'nome_produto':['Etanol + Gasolina Comum', 'GLP P13', 'Óleo Diesel S-500 e S-10 + GNV']})

    df_estabelecimentos = df[['cnpj_completo', 'cnpj_basico', 'revenda', 'regiao_sigla', 'estado_sigla', 'municipio', 'rua',
                              'numero', 'complemento', 'bairro', 'cep']]

    df_estabelecimentos = df_estabelecimentos.drop_duplicates()


    df_precos = df[['cnpj_completo', 'data_coleta', 'valor_venda', 'valor_compra', 'unidade_de_medida', 'bandeira','nome_produto']]
    df_precos = df_precos.merge(df_prods, on='nome_produto').drop(['nome_produto'], axis = 1)

    df.valor_venda = df.valor_venda.apply(lambda x : x.replace(',','.'))

    # escrita no banco de dados
    engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
    df_precos.to_sql('precos', engine)
    df_prods.to_sql('produtos', engine)
    df_estabelecimentos.to_sql('estabelecimentos', engine)
