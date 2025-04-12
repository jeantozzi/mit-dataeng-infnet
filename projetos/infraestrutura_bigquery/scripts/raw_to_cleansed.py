from google.cloud import bigquery
from google.oauth2 import service_account
import time

CREDENTIAL_PATH = "key.json"  # Substitua pelo caminho do seu arquivo de credenciais
DATASET_NAME = "PROUNI"
SOURCE_TABLE_NAME = "raw_data"
OUTPUT_TABLE_NAME = "cleansed_data"

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
    """Verifica se uma tabela existe no BigQuery"""
    print(f"\nVerificando existência da tabela {dataset_name}.{table_name}...")
    try:
        table_ref = client.dataset(dataset_name).table(table_name)
        table = client.get_table(table_ref)
        print(f"ℹ️ Tabela encontrada com {table.num_rows} linhas e {len(table.schema)} colunas")
        return True
    except Exception as e:
        print(f"⚠️ Tabela não encontrada: {str(e)}")
        return False

def execute_raw_to_cleansed_transformation(client):
    """Executa a transformação de raw para cleansed usando a query SQL"""
    print("\n[2/4] Preparando transformação de dados...")
    
    # Verifica se a tabela de origem existe
    if not check_table_exists(client, DATASET_NAME, SOURCE_TABLE_NAME):
        raise Exception(f"Tabela de origem {SOURCE_TABLE_NAME} não encontrada!")
    
    print("\n[3/4] Executando transformação...")
    print("🔧 Operações que serão realizadas:")
    print("- Converter tipos de dados (datas, números)")
    print("- Particionar por ANO_CONCESSAO_BOLSA (2005-2020)")
    print("- Clusterizar por UF, Município e Tipo de Bolsa")
    print("- Adicionar coluna TIPO_BOLSA_CATEGORIZADO (parcial, complementar ou integral)")
    
    start_time = time.time()
    
    # Query SQL para transformação
    query = f"""
    CREATE OR REPLACE TABLE `{client.project}.{DATASET_NAME}.{OUTPUT_TABLE_NAME}`
    PARTITION BY RANGE_BUCKET(ANO_CONCESSAO_BOLSA, GENERATE_ARRAY(2005, 2020, 1))
    CLUSTER BY SIGLA_UF_BENEFICIARIO_BOLSA, MUNICIPIO_BENEFICIARIO_BOLSA, TIPO_BOLSA
    AS
    SELECT
      SAFE_CAST(ANO_CONCESSAO_BOLSA AS INT64) AS ANO_CONCESSAO_BOLSA,
      SAFE_CAST(CODIGO_EMEC_IES_BOLSA AS INT64) AS CODIGO_EMEC_IES_BOLSA,
      
      NOME_IES_BOLSA,
      TIPO_BOLSA,
      CASE
        WHEN TIPO_BOLSA LIKE '%PARCIAL%' THEN 'PARCIAL'
        WHEN TIPO_BOLSA LIKE '%COMPLEMENTAR%' THEN 'COMPLEMENTAR'
        WHEN TIPO_BOLSA LIKE '%INTEGRAL%' THEN 'INTEGRAL'
        ELSE 'OUTROS'
      END AS TIPO_BOLSA_CATEGORIZADO,
      CASE
        WHEN UPPER(MODALIDADE_ENSINO_BOLSA) LIKE '%DISTÂNCIA%' THEN 'EAD'
        ELSE UPPER(MODALIDADE_ENSINO_BOLSA)
      END AS MODALIDADE_ENSINO_BOLSA,
      NOME_CURSO_BOLSA,
      CASE
        WHEN UPPER(NOME_TURNO_CURSO_BOLSA) LIKE '%CURSO%' THEN 'EAD'
        ELSE UPPER(NOME_TURNO_CURSO_BOLSA)
      END AS NOME_TURNO_CURSO_BOLSA,
      CPF_BENEFICIARIO_BOLSA,
      CASE 
        WHEN UPPER(SEXO_BENEFICIARIO_BOLSA) IN ('MASCULINO', 'M') THEN 'M'
        WHEN UPPER(SEXO_BENEFICIARIO_BOLSA) IN ('FEMININO', 'F') THEN 'F'
        ELSE NULL
      END AS SEXO_BENEFICIARIO_BOLSA,
      CASE
        WHEN UPPER(RACA_BENEFICIARIO_BOLSA) LIKE '%INFO%' THEN NULL
        WHEN UPPER(RACA_BENEFICIARIO_BOLSA) LIKE 'IND%' THEN 'INDÍGENA'
        ELSE UPPER(RACA_BENEFICIARIO_BOLSA)
      END AS RACA_BENEFICIARIO_BOLSA,
      
      SAFE.PARSE_DATE('%d/%m/%Y', DT_NASCIMENTO_BENEFICIARIO) AS DT_NASCIMENTO_BENEFICIARIO,

      CASE 
        WHEN UPPER(BENEFICIARIO_DEFICIENTE_FISICO) IN ('SIM', 'S') THEN TRUE
        WHEN UPPER(BENEFICIARIO_DEFICIENTE_FISICO) IN ('NÃO', 'N') THEN FALSE
        ELSE NULL
      END AS BENEFICIARIO_DEFICIENTE_FISICO,
      NULLIF(UPPER(REGIAO_BENEFICIARIO_BOLSA), 'NAN') AS REGIAO_BENEFICIARIO_BOLSA,
      NULLIF(SIGLA_UF_BENEFICIARIO_BOLSA, 'nan') AS SIGLA_UF_BENEFICIARIO_BOLSA,
      NULLIF(MUNICIPIO_BENEFICIARIO_BOLSA, 'nan') AS MUNICIPIO_BENEFICIARIO_BOLSA
    FROM `{client.project}.{DATASET_NAME}.{SOURCE_TABLE_NAME}`
    """
    
    # Configuração do job
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False
    
    # Executa a query
    print("\n🚀 Iniciando execução da query no BigQuery...")
    query_job = client.query(query, job_config=job_config)
    
    query_job.result()  # Aguarda a conclusão final
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ Transformação concluída em {elapsed_time:.2f} segundos!")
    
    # Verifica estatísticas da tabela resultante
    print("\n[4/4] Verificando tabela resultante...")
    table_ref = client.dataset(DATASET_NAME).table(OUTPUT_TABLE_NAME)
    table = client.get_table(table_ref)
    
    print(f"\n📊 Resultado final:")
    print(f"- Tabela: {DATASET_NAME}.{table.table_id}")
    print(f"- Linhas processadas: {table.num_rows:,}")
    print(f"- Colunas criadas: {len(table.schema)}")
    print(f"- Tamanho: {table.num_bytes/1e6:.2f} MB")
    print(f"- Partições: Por ANO_CONCESSAO_BOLSA (2005-2020)")
    print(f"- Clusterização: Por UF, Município e Tipo de Bolsa")

def main():
    print("\n" + "="*50)
    print(" INÍCIO DO PROCESSO RAW_TO_CLEANSED ")
    print("="*50)
    
    try:
        # Autentica no GCP
        client = authenticate_gcp(CREDENTIAL_PATH)
        
        # Executa a transformação
        execute_raw_to_cleansed_transformation(client)
        
        print("\n" + "="*50)
        print(" PROCESSO CONCLUÍDO COM SUCESSO! ")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERRO NO PROCESSAMENTO")
        print(f"Motivo: {str(e)}")
        print("="*50)
        raise

if __name__ == "__main__":
    main()