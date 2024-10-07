# Infraestrutura Hadoop

## Proposta geral do trabalho
- Refazer utilizando a API do PySpark as análises presentes no projeto de Infraestrutura Hadoop.
- Desenvolver um projeto de Machine Learning utilizando Spark MLlib em um notebook, com as seguintes etapas:
    - Contextualização dos dados e do problema, bem como algoritmo e/ou técnica utilizados (regressão linear, regressão logística, clusterização, etc.) 
    - Tratamento e limpeza dos dados de forma documentada
    - Divisão dos dados entre dois conjuntos: treino e teste
    - Treinar o modelo e apresentar as métricas de desempenho
    - Aplicar o modelo na base de teste, comparando o desempenho com a base de treino
    - Propor sugestões para próximos passos

## Consideração inicial
Considerando a facilidade da replicação do projeto, optei por desenvolver os notebooks no Google Colab (https://colab.research.google.com/). Basta realizar o upload do notebook (e de arquivos adicionais quando aplicável) e executar. 

## Análise de dados em PySpark
Para recriar as análises realizados no projeto de Infraestrutura Hadoop ([referência](../infraestrutura_hadoop/README.md)), criei um notebook Jupyter documentado, que pode ser encontrado [aqui](./notebooks/01_analise_dados_spark.ipynb).<br>
É necessário realizar o upload do arquivo bash `scripts/download_and_extract.sh` ([referência](./scripts/download_and_extract.sh)), responsável pelo download e a extração dos arquivos utilizados.

