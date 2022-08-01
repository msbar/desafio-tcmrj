# Instruções

Criar um virtual environment com 

`
python -m venv .
`

ativar a seção 

`
source bin/activate
`

instalar as dependências

`
pip install -r requirements.txt
`

Iniciar a imagem docker que contem o banco de dados postgresql

`
docker run --rm -P -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD="1234" --name pg postgres:alpine
`

Rodar o script para aquisição dos dados

`
python main.py
`

Para abrir o EDA 

`
jupyter notebook eda.ipynb
`