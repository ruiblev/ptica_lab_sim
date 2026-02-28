#!/bin/bash

# Garantir que o script corre sempre na diretoria correta, onde quer que seja chamado
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================="
echo " Simulador de Ótica - AL 11.º Ano"
echo "================================="
# Criar um ambiente virtual se não existir (necessário em Mac/Linux recentes devido à PEP 668)
if [ ! -d ".venv" ]; then
    echo "A criar o ambiente virtual Python (.venv)..."
    python3 -m venv .venv
fi

# Ativar o ambiente virtual
source .venv/bin/activate

echo "A verificar dependências no ambiente virtual..."
# Instalar requisitos (usa pip dentro do venv)
pip install -r requirements.txt -q

echo "A iniciar a aplicação. O seu browser deverá abrir brevemente..."
echo "A primeira execução pode demorar alguns segundos."
echo "Para encerrar, volte a este terminal e pressione CTRL+C."
echo "================================="

# Executa o Streamlit
python -m streamlit run app.py
