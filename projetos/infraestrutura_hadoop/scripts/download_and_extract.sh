# Diretório para salvar os datasets
output_dir="./datasets"
mkdir -p "$output_dir"

# URLs para datasets IMDB
urls=(
  "https://datasets.imdbws.com/name.basics.tsv.gz"
  "https://datasets.imdbws.com/title.akas.tsv.gz"
  "https://datasets.imdbws.com/title.basics.tsv.gz"
  "https://datasets.imdbws.com/title.crew.tsv.gz"
  "https://datasets.imdbws.com/title.episode.tsv.gz"
  "https://datasets.imdbws.com/title.principals.tsv.gz"
  "https://datasets.imdbws.com/title.ratings.tsv.gz"
)

echo "Iniciando o processo de download e extração em $(date)"

# Itera por cada URL para realizar o download
for url in "${urls[@]}"; do
  # Extrai o nome do arquivo através da URL
  file_name=$(basename "$url")
  
  # Realiza o download e informa o status
  echo "Baixando o arquivo $file_name..."
  if wget -c "$url" -P "$output_dir"; then
    echo "O download do arquivo $file_name foi realizado com sucesso."
  else
    echo "O download do arquivo $file_name falhou."
    # Deleta download e pula a iteração
    rm -f "$output_dir/$file_name"  
    continue
  fi
done

# Espera a finalização de todos os downloads
wait

# Itera novamente para extrair os arquivos .gz
for url in "${urls[@]}"; do
  file_name=$(basename "$url")
  
  # Extrai o arquivo e informa o status
  echo "Extraindo o arquivo $file_name..."
  if gunzip -f "$output_dir/$file_name"; then
    echo "Extração do arquivo $file_name realizada com sucesso."
  else
    echo "Extração do arquivo $file_name falhou."
  fi
done

echo "Processo finalizado em $(date)"