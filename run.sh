#!/bin/bash

# Garantir que o script corre sempre na diretoria correta, onde quer que seja chamado
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================="
echo " Simulador de Ótica - AL 11.º Ano"
echo "================================="
echo "A verificar dependências..."

# Instalar requisitos (usa pip3 para mac/linux)
pip3 install -r requirements.txt -q

echo "A iniciar a aplicação. O seu browser deverá abrir brevemente..."
echo "A primeira execução pode demorar alguns segundos."
echo "Para encerrar, volte a este terminal e pressione CTRL+C."
echo "================================="

# Executa o Streamlit
python3 -m streamlit run app.py
