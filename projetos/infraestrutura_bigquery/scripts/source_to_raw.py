from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
import time
from tqdm import tqdm  # Para barras de progresso

# Configurações
CREDENTIAL_PATH = "key.json"
DATASET_NAME = "PROUNI"
TABLE_NAME = "raw_data"
RAW_DATA_PATH = "../raw_data"

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f" {title.upper()} ")
    print("="*60)

def authenticate_gcp(credential_path):
    """Autentica no GCP usando credenciais de service account"""
    print_header("1/4 - autenticação no gcp")
    print("🔑 Iniciando autenticação...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credential_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        print("✅ Autenticação bem-sucedida!")
        return client
    except Exception as e:
        print(f"❌ Falha na autenticação: {str(e)}")
        raise

def create_dataset_if_not_exists(client, dataset_name):
    """Cria um dataset no BigQuery se ele não existir"""
    print_header("2/4 - verificação do dataset")
    dataset_ref = client.dataset(dataset_name)
    
    try:
        client.get_dataset(dataset_ref)
        print(f"ℹ️ Dataset {dataset_name} já existe")
    except Exception:
        print("⚠️ Dataset não encontrado. Criando novo dataset...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"✅ Dataset {dataset_name} criado com sucesso")

def load_and_adjust(file_path):
    """Carrega e ajusta dados CSV forçando todas as colunas como strings"""
    print(f"\n📂 Processando arquivo: {os.path.basename(file_path)}")
    start_time = time.time()
    
    try:
        # Força todas as colunas como string desde a leitura
        df = pd.read_csv(file_path, encoding='iso-8859-1', sep=';', dtype=str)
        
        # Renomeia colunas
        rename_columns = {
            'ï»¿ANO_CONCESSAO_BOLSA': 'ANO_CONCESSAO_BOLSA',
            'CPF_BENEFICIARIO': 'CPF_BENEFICIARIO_BOLSA',
            'SEXO_BENEFICIARIO': 'SEXO_BENEFICIARIO_BOLSA',
            'RACA_BENEFICIARIO': 'RACA_BENEFICIARIO_BOLSA',
            'DATA_NASCIMENTO': 'DT_NASCIMENTO_BENEFICIARIO',
            'REGIAO_BENEFICIARIO': 'REGIAO_BENEFICIARIO_BOLSA',
            'UF_BENEFICIARIO': 'SIGLA_UF_BENEFICIARIO_BOLSA',
            'MUNICIPIO_BENEFICIARIO': 'MUNICIPIO_BENEFICIARIO_BOLSA'
        }
        
        df = df.rename(columns=rename_columns)
        
        # Seleciona colunas comuns
        common_columns = [
            'ANO_CONCESSAO_BOLSA', 'CODIGO_EMEC_IES_BOLSA', 'NOME_IES_BOLSA',
            'TIPO_BOLSA', 'MODALIDADE_ENSINO_BOLSA', 'NOME_CURSO_BOLSA',
            'NOME_TURNO_CURSO_BOLSA', 'CPF_BENEFICIARIO_BOLSA',
            'SEXO_BENEFICIARIO_BOLSA', 'RACA_BENEFICIARIO_BOLSA',
            'DT_NASCIMENTO_BENEFICIARIO', 'BENEFICIARIO_DEFICIENTE_FISICO',
            'REGIAO_BENEFICIARIO_BOLSA', 'SIGLA_UF_BENEFICIARIO_BOLSA',
            'MUNICIPIO_BENEFICIARIO_BOLSA'
        ]
        
        # Mantém apenas colunas comuns que existem no DataFrame
        df = df[[col for col in common_columns if col in df.columns]]
        
        # Tratamento de dados
        print("🛠️ Aplicando transformações:")
        print("- Substituindo 'nan' por valores nulos")
        df = df.replace('nan', pd.NA)
        
        print("- Removendo linhas completamente vazias")
        initial_rows = len(df)
        df = df.dropna(how='all')
        removed_rows = initial_rows - len(df)
        
        elapsed_time = time.time() - start_time
        print(f"✅ Arquivo processado em {elapsed_time:.2f}s | Linhas: {len(df):,} | Linhas removidas: {removed_rows:,}")
        
        return df
    except Exception as e:
        print(f"❌ Erro ao processar arquivo {file_path}: {str(e)}")
        raise

def create_table_from_dataframe(client, dataset_name, table_name, df):
    """Cria ou substitui uma tabela no BigQuery com todos os campos como STRING"""
    print_header("4/4 - carregamento no bigquery")
    
    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)
    
    # Configuração do job
    job_config = bigquery.LoadJobConfig(
        schema=[bigquery.SchemaField(name, "STRING") for name in df.columns],
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False
    )
    
    try:
        client.get_table(table_ref)
        print(f"ℹ️ Tabela {table_name} já existente. Será sobrescrita.")
    except Exception:
        print(f"ℹ️ Criando nova tabela {table_name}")
    
    # Faz upload do DataFrame para o BigQuery
    print(f"🚀 Enviando {len(df):,} linhas para o BigQuery...")
    start_time = time.time()
    
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    
    # Barra de progresso simulada
    with tqdm(total=100, desc="Progresso") as pbar:
        while not job.done():
            time.sleep(1)
            pbar.update(10)
    
    job.result()  # Aguarda a conclusão final
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ Carga concluída em {elapsed_time:.2f}s")
    print(f"📊 Estatísticas finais:")
    print(f"- Linhas carregadas: {job.output_rows:,}")
    print(f"- Tabela: {dataset_name}.{table_name}")

def main():
    try:
        print_header("início do processo source_to_raw")
        start_time = time.time()
        
        # Autentica no GCP
        client = authenticate_gcp(CREDENTIAL_PATH)
        
        # Cria o dataset se não existir
        create_dataset_if_not_exists(client, DATASET_NAME)
        
        # Carrega e processa dados de todos os arquivos CSV
        print_header("3/4 - processamento dos arquivos")
        files = [os.path.join(RAW_DATA_PATH, f'pda-prouni-{year}.csv') for year in range(2005, 2020 + 1)]
        
        # Filtra apenas arquivos que realmente existem
        existing_files = [file for file in files if os.path.exists(file)]
        if not existing_files:
            raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {RAW_DATA_PATH}")
        
        print(f"🔍 Encontrados {len(existing_files)} arquivos para processar:")
        for file in existing_files:
            print(f"- {os.path.basename(file)}")
        
        # Processa arquivos com barra de progresso
        dfs = []
        for file in tqdm(existing_files, desc="Processando arquivos"):
            dfs.append(load_and_adjust(file))
        
        # Combina os DataFrames
        print("\n🔗 Combinando todos os DataFrames...")
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Garante que todos os dados sejam strings
        combined_df = combined_df.astype(str)
        
        # Cria/atualiza a tabela no BigQuery
        create_table_from_dataframe(client, DATASET_NAME, TABLE_NAME, combined_df)
        
        elapsed_time = time.time() - start_time
        print_header("processo concluído com sucesso")
        print(f"⏱ Tempo total: {elapsed_time:.2f} segundos")
        print(f"📈 Total de linhas processadas: {len(combined_df):,}")
        
    except Exception as e:
        print_header("erro no processamento")
        print(f"❌ Ocorreu um erro: {str(e)}")
        raise

if __name__ == "__main__":
    main()