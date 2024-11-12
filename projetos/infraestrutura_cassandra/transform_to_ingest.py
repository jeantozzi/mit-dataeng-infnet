import csv
import glob
import os
from datetime import datetime

# Diretório onde os arquivos estão localizados
file_path = './raw_data/datatran_*.csv'

# Nome do arquivo de saída consolidado e diretório
output_dir = "./clean_data"
output_file = os.path.join(output_dir, "datatran_2017_2024.csv")

# Cria o diretório se não existir
os.makedirs(output_dir, exist_ok=True)

# Colunas para manter no arquivo de saída
columns_to_use = [
    "id", "data_inversa", "dia_semana", "classificacao_acidente", 
    "fase_dia", "condicao_metereologica", "mortos"
]
output_columns = ["id", "ano", "data", "dia_semana", "classificacao_acidente", "fase_dia", "condicao_metereologica", "mortos"]

# Função para extrair o ano da data
def extract_year(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").year
    except ValueError:
        return None

# Função para converter valores para inteiro, incluindo notação científica
def to_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

# Abre o arquivo de saída para escrita
with open(output_file, mode="w", newline="", encoding="utf-8") as out_csv:
    writer = csv.writer(out_csv, delimiter=";")
    
    # Escreve o cabeçalho no arquivo de saída
    writer.writerow(output_columns)
    
    # Loop pelos arquivos de entrada
    for file in glob.glob(file_path):
        # Abre cada arquivo CSV para leitura
        with open(file, mode="r", encoding="iso-8859-1") as in_csv:
            reader = csv.DictReader(in_csv, delimiter=";")
            
            # Verifica se todas as colunas necessárias estão presentes
            if not all(col in reader.fieldnames for col in columns_to_use):
                print(f"Arquivo {file} não possui as colunas necessárias. Pulando...")
                continue
            
            # Processa cada linha do arquivo
            for row in reader:
                # Extração do ano e substituição do nome da coluna
                ano = extract_year(row["data_inversa"])
                
                if ano is not None:
                    # Cria uma nova linha com o schema final, convertendo 'id' e 'mortos' para inteiros
                    output_row = [
                        to_int(row["id"]),
                        ano,
                        row["data_inversa"],
                        row["dia_semana"],
                        row["classificacao_acidente"],
                        row["fase_dia"],
                        row["condicao_metereologica"],
                        to_int(row["mortos"])
                    ]
                    
                    writer.writerow(output_row)

print(f"Arquivo consolidado gerado com sucesso: {output_file}")
