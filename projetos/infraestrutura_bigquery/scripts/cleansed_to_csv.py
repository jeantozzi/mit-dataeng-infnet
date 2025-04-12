from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
import os
import time

CREDENTIAL_PATH = "key.json"  # Caminho do arquivo de credenciais
DATASET_NAME = "PROUNI"
TABLE_NAME = "cleansed_data"
OUTPUT_DIR = "../output"
OUTPUT_FILE = "prouni_cleansed_data.csv"
BUCKET_NAME = None  # Será definido dinamicamente

def authenticate_gcp(credential_path):
    """Autentica no GCP usando credenciais de service account"""
    print("\n[1/4] Iniciando autenticação no GCP...")
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

def check_table_exists(client, dataset_name, table_name):
    """Verifica se a tabela existe no BigQuery"""
    print(f"\n[2/4] Verificando existência da tabela {dataset_name}.{table_name}...")
    try:
        table_ref = client.dataset(dataset_name).table(table_name)
        table = client.get_table(table_ref)
        print(f"ℹ️ Tabela encontrada com {table.num_rows} linhas e {len(table.schema)} colunas")
        return True
    except Exception as e:
        print(f"⚠️ Tabela não encontrada: {str(e)}")
        return False

def ensure_gcs_bucket_exists(storage_client, bucket_name):
    """Verifica se o bucket existe no GCS, criando-o se necessário"""
    print(f"\n[3/4] Verificando bucket GCS {bucket_name}...")
    try:
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            print(f"Bucket não encontrado. Criando novo bucket: {bucket_name}")
            bucket.create(location="US")  # Cria o bucket na região US
            print(f"✅ Bucket criado com sucesso!")
        else:
            print(f"ℹ️ Bucket encontrado: {bucket_name}")
        return bucket
    except Exception as e:
        print(f"❌ Falha ao verificar/criar bucket: {str(e)}")
        raise

def export_table_to_csv(client):
    """Exporta a tabela do BigQuery para um arquivo CSV"""
    print("\n[4/4] Iniciando exportação para CSV...")
    
    # Verifica se a tabela existe
    if not check_table_exists(client, DATASET_NAME, TABLE_NAME):
        raise Exception(f"Tabela {TABLE_NAME} não encontrada!")
    
    # Cria o diretório de output se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    
    # Configuração da exportação
    dataset_ref = client.dataset(DATASET_NAME)
    table_ref = dataset_ref.table(TABLE_NAME)
    
    # Configura o nome do bucket temporário
    global BUCKET_NAME
    BUCKET_NAME = f"{client.project}-temp-exports"
    
    # Autentica no GCS e verifica o bucket
    storage_client = storage.Client.from_service_account_json(CREDENTIAL_PATH)
    bucket = ensure_gcs_bucket_exists(storage_client, BUCKET_NAME)
    
    print(f"\n📤 Exportando dados para {output_path}...")
    start_time = time.time()
    
    # Configura o job de exportação
    job_config = bigquery.ExtractJobConfig()
    job_config.destination_format = bigquery.DestinationFormat.CSV
    job_config.print_header = True
    
    # URI temporário no Google Cloud Storage
    destination_uri = f"gs://{BUCKET_NAME}/temp_export.csv"
    
    # Exporta para o GCS
    extract_job = client.extract_table(
        table_ref,
        destination_uri,
        job_config=job_config,
        location="US"  # Ajuste conforme a localização do seu dataset
    )
    extract_job.result()  # Aguarda a conclusão
    
    # Baixa do GCS para o sistema local
    blob = bucket.blob("temp_export.csv")
    blob.download_to_filename(output_path)
    
    # Limpa o arquivo temporário
    blob.delete()
    
    elapsed_time = time.time() - start_time
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # Tamanho em MB
    
    print(f"\n✅ Exportação concluída com sucesso!")
    print(f"- Arquivo gerado: {output_path}")
    print(f"- Tamanho do arquivo: {file_size:.2f} MB")
    print(f"- Tempo total: {elapsed_time:.2f} segundos")

def main():
    print("\n" + "="*50)
    print(" EXPORTAÇÃO CLEANSED_DATA PARA CSV ")
    print("="*50)
    
    try:
        # Autentica no GCP
        client = authenticate_gcp(CREDENTIAL_PATH)
        
        # Exporta a tabela para CSV
        export_table_to_csv(client)
        
        print("\n" + "="*50)
        print(" PROCESSO CONCLUÍDO COM SUCESSO! ")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERRO NA EXPORTAÇÃO")
        print(f"Motivo: {str(e)}")
        print("="*50)
        raise

if __name__ == "__main__":
    main()