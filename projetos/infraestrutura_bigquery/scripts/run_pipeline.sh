#!/bin/bash

# Executa a instalação das dependências
echo "Instalando dependências do requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Falha na instalação das dependências. Verifique o arquivo requirements.txt."
    exit 1
fi

# Executa o script source_to_raw.py
echo "Executando source_to_raw.py..."
python source_to_raw.py

if [ $? -ne 0 ]; then
    echo "Falha na execução de source_to_raw.py."
    exit 1
fi

# Executa o script raw_to_cleansed.py
echo "Executando raw_to_cleansed.py..."
python raw_to_cleansed.py

if [ $? -ne 0 ]; then
    echo "Falha na execução de raw_to_cleansed.py."
    exit 1
fi

# Executa o script cleansed_to_csv.py
echo "Executando cleansed_to_csv.py..."
python cleansed_to_csv.py

if [ $? -ne 0 ]; then
    echo "Falha na execução de cleansed_to_csv.py."
    exit 1
fi

echo "Pipeline executado com sucesso!"