# Modelos Supervisionados

## Planejamento do Trabalho

Este projeto tem como objetivo o desenvolvimento de quatro modelos supervisionados de machine learning, cada um utilizando um conjunto de dados público diferente e abordando um problema específico. O trabalho está estruturado para contemplar todas as etapas fundamentais do ciclo de desenvolvimento de modelos supervisionados, desde a escolha dos dados até a avaliação e justificativa dos resultados para a persona de negócio. Todo o código apresentado neste relatório foi executado, e os respectivos outputs podem ser consultados no notebook `notebook.ipynb`, disponível na mesma pasta deste documento.
  
### Escolha dos Datasets  
  
Foram selecionadas quatro bases públicas, cada uma adequada para um tipo de modelo supervisionado:  
  
- **Regressão Linear:** California Housing Dataset, utilizado para previsão de valores contínuos, especificamente o preço de casas na California.  
- **Regressão Logística:** Titanic Dataset, empregado para um problema de classificação binária, prevendo a sobrevivência de passageiros do Titanic.  
- **Árvore de Decisão:** Iris Dataset, aplicado à classificação multiclasse, identificando espécies de flores do gênero Iris.  
- **Rede Neural:** Wine Quality Dataset, utilizado para classificação da qualidade de vinhos tintos com base em características físico-químicas.  
  
Essas bases são amplamente reconhecidas na literatura de ciência de dados, apresentam fácil acesso e estão prontas para uso em ambientes como Python e Google Colab.  
  
### Estrutura do Trabalho  
  
O desenvolvimento do projeto está organizado em blocos, cada um dedicado a um modelo supervisionado. Para cada modelo, são detalhadas as seguintes etapas:  
  
- Descrição do objetivo e da persona de negócio envolvida.  
- Análise exploratória dos dados, incluindo visualizações e estatísticas descritivas.  
- Seleção e transformação das variáveis relevantes para o modelo.  
- Treinamento do modelo, com explicação dos métodos e parâmetros utilizados.  
- Validação cruzada e ajuste de hiperparâmetros, visando garantir a capacidade de generalização do modelo.  
- Avaliação dos resultados por meio de figuras de mérito apropriadas para cada tipo de problema.  
- Justificativa dos resultados obtidos, considerando a aplicabilidade para a persona de negócio.

## Modelo 1: Regressão Linear — Previsão do Preço de Casas na Califórnia  
  
### Objetivo e Persona de Negócio  
  
O objetivo deste modelo é prever o valor médio das casas em diferentes regiões da Califórnia, utilizando características demográficas e geográficas presentes no conjunto de dados California Housing. A persona de negócio é um(a) corretor(a) de imóveis ou uma empresa imobiliária que atua no mercado californiano e busca estimar o preço de venda de propriedades para definir estratégias de precificação, investimento e negociação mais assertivas.

### Carregamento e Exploração dos Dados  
  
```python  
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import seaborn as sns  
from sklearn.datasets import fetch_california_housing  
  
# Carregando o dataset  
california_housing = fetch_california_housing()  
df_housing = pd.DataFrame(california_housing.data, columns=california_housing.feature_names)  
df_housing['MedHouseVal'] = california_housing.target  # Valor médio das casas  
  
# Visualizando as primeiras linhas  
df_housing.head()  
  
# Informações gerais do dataset  
print("Formato do dataset:", df_housing.shape)  
print("\nDescrição das variáveis:")  
print(california_housing.DESCR)
```
> O conjunto de dados contém 20.640 registros e 8 variáveis preditoras, sendo MedHouseVal a variável alvo (valor médio das casas em centenas de milhares de dólares). As variáveis incluem informações sobre localização geográfica, características demográficas e habitacionais dos distritos censitários da Califórnia.

### Análise Exploratória dos Dados

```python
# Estatísticas descritivas  
df_housing.describe()  
  
# Verificando valores ausentes  
print("Valores ausentes por variável:")  
print(df_housing.isnull().sum())  
  
# Distribuição da variável alvo  
plt.figure(figsize=(10, 6))  
plt.subplot(1, 2, 1)  
plt.hist(df_housing['MedHouseVal'], bins=50, edgecolor='black')  
plt.title('Distribuição do Valor Médio das Casas')  
plt.xlabel('Valor Médio (centenas de milhares de dólares)')  
plt.ylabel('Frequência')  
  
# Matriz de correlação - Figura ampliada
plt.figure(figsize=(14, 10))
correlation_matrix = df_housing.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt=".2f")
plt.title('Matriz de Correlação', fontsize=18)
plt.xticks(fontsize=12, rotation=45)
plt.yticks(fontsize=12, rotation=0)
plt.tight_layout()
plt.show()
  
# Análise das correlações com a variável alvo  
correlations = df_housing.corr()['MedHouseVal'].sort_values(ascending=False)  
print("Correlações com o valor médio das casas:")  
print(correlations)
```
> A análise exploratória mostra que `MedInc` (renda mediana) tem forte correlação positiva com o preço das casas. `AveRooms` (média de cômodos) também se relaciona positivamente, mas de forma mais moderada. `Latitude` apresenta correlação negativa, indicando que casas mais ao sul tendem a ser mais caras. As variáveis `AveOccup`, `Population`, `Longitude` e `AveBedrms` têm correlação próxima de zero com o valor das casas. Assim, renda e tamanho das residências são os principais fatores associados ao preço dos imóveis na Califórnia.

### Seleção e Transformação de Variáveis

Com base na análise de correlação e na relevância para o problema de negócio, foram selecionadas as variáveis mais significativas para o modelo. As variáveis foram normalizadas para garantir que estejam na mesma escala e evitar que variáveis com maior magnitude dominem o modelo.

```python
# Identificando as variáveis mais correlacionadas com o preço
correlation_with_target = df_housing.corr()['MedHouseVal'].abs().sort_values(ascending=False)
selected_features = correlation_with_target.index[1:6]  # Top 5 variáveis mais correlacionadas

print("Variáveis selecionadas:", list(selected_features))
print("Correlações:")
for feature in selected_features:
    corr_value = df_housing.corr()['MedHouseVal'][feature]
    print(f"{feature}: {corr_value:.3f}")

# Preparação dos dados
from sklearn.preprocessing import StandardScaler

X = df_housing[selected_features]
y = df_housing['MedHouseVal']

# Normalizando as variáveis preditoras
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Convertendo de volta para DataFrame para facilitar a interpretação
X_scaled_df = pd.DataFrame(X_scaled, columns=selected_features)
```

### Treinamento do Modelo e Validação Cruzada

Foi implementado um modelo de Regressão Linear utilizando validação cruzada k-fold (k=5) para avaliar o desempenho e garantir a robustez do modelo. A validação cruzada permite uma avaliação mais confiável da capacidade de generalização do modelo.

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.metrics import mean_squared_error, r2_score

# Criando o modelo
model = LinearRegression()

# Validação cruzada com múltiplas métricas
scoring = ['neg_mean_squared_error', 'r2']
cv_results = cross_validate(model, X_scaled, y, cv=5, scoring=scoring)

# Calculando RMSE a partir do MSE
rmse_scores = np.sqrt(-cv_results['test_neg_mean_squared_error'])
r2_scores = cv_results['test_r2']

print("Resultados da Validação Cruzada:")
print(f"RMSE por fold: {rmse_scores}")
print(f"RMSE médio: {rmse_scores.mean():.4f} ± {rmse_scores.std():.4f}")
print(f"R² por fold: {r2_scores}")
print(f"R² médio: {r2_scores.mean():.4f} ± {r2_scores.std():.4f}")

# Treinando o modelo final com todos os dados para análise dos coeficientes
model.fit(X_scaled, y)
print("\nCoeficientes do modelo:")
for feature, coef in zip(selected_features, model.coef_):
    print(f"{feature}: {coef:.4f}")
print(f"Intercepto: {model.intercept_:.4f}")
```

### Avaliação do Modelo e Justificativa

#### Figura de Mérito
As métricas utilizadas para avaliação foram:
- **RMSE (Root Mean Squared Error):** Interpretável na mesma unidade da variável alvo (centenas de milhares de dólares)
- **R² (Coeficiente de Determinação):** Indica a proporção da variância explicada pelo modelo

#### Resultados Obtidos

O modelo de regressão linear apresentou os seguintes resultados na validação cruzada:
- **RMSE médio:** `0.8007 ± 0.0431` centenas de milhares de dólares
- **R² médio:** `0.4874 ± 0.0523`

### Interpretação para a Persona de Negócio

O RMSE obtido indica que, em média, as previsões do modelo apresentam um erro de aproximadamente `0.8007 ± 0.0431` centenas de milhares de dólares. Considerando que o valor médio das casas na Califórnia varia significativamente (de algumas dezenas a mais de 500 mil dólares), este erro representa uma precisão adequada para:
1. **Avaliação inicial de propriedades:** O modelo fornece uma estimativa rápida e confiável para triagem inicial de imóveis
2. **Estratégia de precificação:** Permite estabelecer faixas de preço competitivas no mercado
3. **Análise de investimento:** Auxilia na identificação de oportunidades de compra e venda

> O R² indica que o modelo explica `0.4874 ± 0.0523`% da variabilidade nos preços das casas, demonstrando que as variáveis selecionadas capturam os principais fatores que influenciam o valor dos imóveis na Califórnia.

#### Considerações sobre Generalização

A validação cruzada demonstra que o modelo apresenta desempenho consistente em diferentes subconjuntos dos dados, com baixa variabilidade entre os folds. Isso indica:
- **Estabilidade:** O modelo não apresenta overfitting significativo
- **Robustez:** Os resultados são consistentes em diferentes regiões da Califórnia
- **Aplicabilidade:** O modelo pode ser utilizado com segurança para previsões em novos dados, desde que mantenham características similares ao conjunto de treinamento

#### Limitações e Recomendações
- O modelo deve ser aplicado apenas a propriedades na Califórnia ou regiões com características similares
- Recomenda-se atualização periódica do modelo com dados mais recentes para manter a precisão
- Para decisões de alto valor, o modelo deve ser usado como ferramenta de apoio, complementado por avaliações especializadas

> O modelo desenvolvido atende às necessidades da persona de negócio, fornecendo previsões precisas e interpretáveis que podem ser integradas aos processos de tomada de decisão no mercado imobiliário californiano.