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

## Modelo 2: Regressão Logística — Previsão de Sobrevivência no Titanic

### Objetivo e Persona de Negócio

O objetivo deste modelo é prever a probabilidade de sobrevivência de passageiros do Titanic com base em características como classe, sexo, idade e tarifa paga. A persona de negócio é uma seguradora ou empresa de transporte marítimo interessada em avaliar fatores de risco e entender os principais determinantes de sobrevivência em situações de desastre.

### Carregamento e Exploração dos Dados

```python
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import seaborn as sns  
  
# Carregando o dataset Titanic do Seaborn  
df_titanic = sns.load_dataset('titanic')  
  
# Visualizando as primeiras linhas  
df_titanic.head()  
  
# Informações gerais do dataset  
df_titanic.info()
```

> O conjunto de dados contém 891 registros e diversas variáveis, sendo `survived` a variável alvo (0 = não sobreviveu, 1 = sobreviveu).

### Análise Exploratória dos Dados

```python  
# Estatísticas descritivas  
df_titanic.describe(include='all')  
  
# Distribuição da variável alvo  
sns.countplot(x='survived', data=df_titanic)  
plt.title('Distribuição de Sobreviventes')  
plt.xlabel('Sobreviveu')  
plt.ylabel('Quantidade')  
plt.show()  
  
# Taxa de sobrevivência por sexo  
sns.barplot(x='sex', y='survived', data=df_titanic)  
plt.title('Taxa de Sobrevivência por Sexo')  
plt.show()  
  
# Taxa de sobrevivência por classe  
sns.barplot(x='pclass', y='survived', data=df_titanic)  
plt.title('Taxa de Sobrevivência por Classe')  
plt.show()
```

> A análise mostra que mulheres e passageiros da primeira classe tiveram maior taxa de sobrevivência. Idade e tarifa também parecem influenciar as chances de sobrevivência.

### Seleção e Transformação de Variáveis

Foram selecionadas as variáveis `pclass`, `sex`, `age` e `fare`, que apresentam relação com a sobrevivência. As variáveis categóricas foram transformadas em variáveis dummy e os valores ausentes em `age` foram removidos para simplificação.

```python
# Seleção de variáveis e tratamento de valores ausentes  
df_titanic_model = df_titanic[['pclass', 'sex', 'age', 'fare', 'survived']].dropna()  
  
# Transformação de variáveis categóricas  
df_titanic_model = pd.get_dummies(df_titanic_model, columns=['sex'], drop_first=True)  
  
X = df_titanic_model.drop('survived', axis=1)  
y = df_titanic_model['survived']
```

### Treinamento do Modelo e Validação Cruzada

Foi utilizada validação cruzada k-fold (k=5) para avaliar o desempenho do modelo de Regressão Logística. As variáveis preditoras foram padronizadas para melhorar a estabilidade do modelo.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

# Padronização das variáveis preditoras
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Criação e avaliação do modelo
model = LogisticRegression(max_iter=1000, random_state=42)
scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')

print("Resultados da Validação Cruzada:")  
print(f"Acurácia por fold: {scores}")  
print(f"Acurácia média: {scores.mean():.4f} ± {scores.std():.4f}")

# Treinando o modelo final com todos os dados para análise dos coeficientes  
model.fit(X_scaled, y)  
print("\nCoeficientes do modelo:")  
for feature, coef in zip(X.columns, model.coef_[0]):  
    print(f"{feature}: {coef:.4f}")  
print(f"Intercepto: {model.intercept_[0]:.4f}")
```

### Avaliação do Modelo e Justificativa

#### Figura de Mérito

A métrica utilizada para avaliação foi a acurácia, que indica a proporção de previsões corretas feitas pelo modelo.

#### Resultados Obtidos

O modelo de regressão logística apresentou os seguintes resultados na validação cruzada:
- **Acurácia média:** `0.7829 ± 0.0288`

### Interpretação para a Persona de Negócio

A acurácia média de aproximadamente 79% indica que o modelo é capaz de prever corretamente a sobrevivência dos passageiros em cerca de 8 a cada 10 casos. Esse desempenho é considerado bom para um modelo simples, baseado em poucas variáveis, e pode ser útil para análises de risco, definição de perfis de passageiros e estudos históricos sobre o desastre.

#### Considerações sobre Generalização

A validação cruzada demonstra que o modelo apresenta desempenho consistente em diferentes subconjuntos dos dados, com baixa variabilidade entre os folds. Isso indica que o modelo tem boa capacidade de generalização e pode ser utilizado para prever a sobrevivência de passageiros com características semelhantes às do conjunto de dados analisado.

#### Limitações e Recomendações
- O modelo não considera todas as variáveis disponíveis, podendo ser aprimorado com a inclusão de mais informações.
- Para aplicações críticas, recomenda-se complementar a análise com outros métodos e validações.
- O modelo é mais adequado para análises exploratórias e compreensão dos fatores de risco do que para previsões individuais em situações reais.

> O modelo desenvolvido atende ao objetivo proposto, fornecendo uma ferramenta interpretável e eficiente para análise de sobrevivência no contexto do Titanic.

## Modelo 3: Árvore de Decisão — Classificação de Espécies de Flores (Iris)

### Objetivo e Persona de Negócio  
  
O objetivo deste modelo é classificar espécies de flores do gênero Iris com base em medidas morfológicas de sépalas e pétalas. A persona de negócio é um(a) botânico(a) ou pesquisador(a) em taxonomia vegetal que deseja identificar rapidamente a espécie de uma flor a partir de suas características morfológicas, otimizando processos de catalogação e pesquisa científica.

### Carregamento e Exploração dos Dados  
  
```python  
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import seaborn as sns  
from sklearn.datasets import load_iris  
  
# Carregando o dataset  
iris = load_iris()  
df_iris = pd.DataFrame(iris.data, columns=iris.feature_names)  
df_iris['species'] = iris.target  
  
# Mapeando os números para nomes das espécies  
species_names = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}  
df_iris['species_name'] = df_iris['species'].map(species_names)  
  
# Visualizando as primeiras linhas  
df_iris.head()  
  
# Informações gerais do dataset  
print("Formato do dataset:", df_iris.shape)  
print("\nDescrição das variáveis:")  
print(iris.DESCR)
```

> O conjunto de dados contém 150 registros, 4 variáveis preditoras (medidas em centímetros) e 3 classes de espécies (setosa, versicolor e virginica), com 50 amostras de cada espécie.

### Análise Exploratória dos Dados

```python
# Estatísticas descritivas  
df_iris.describe()  
  
# Verificando valores ausentes  
print("Valores ausentes por variável:")  
print(df_iris.isnull().sum())  
  
# Distribuição das espécies  
plt.figure(figsize=(12, 8))  
  
# Distribuição da variável alvo  
plt.subplot(2, 2, 1)  
sns.countplot(x='species_name', data=df_iris)  
plt.title('Distribuição das Espécies')  
plt.xlabel('Espécie')  
plt.ylabel('Quantidade')  
  
# Matriz de correlação  
plt.subplot(2, 2, 2)  
correlation_matrix = df_iris.drop(['species', 'species_name'], axis=1).corr()  
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt=".2f")  
plt.title('Matriz de Correlação')  
  
# Pairplot para visualizar separabilidade das classes  
plt.tight_layout()  
plt.show()  
  
# Pairplot detalhado  
sns.pairplot(df_iris.drop('species', axis=1), hue='species_name', palette='Set1')  
plt.show()  
  
# Análise das correlações  
correlations = df_iris.drop(['species', 'species_name'], axis=1).corr()  
print("Matriz de correlação entre as variáveis:")  
print(correlations)
```
> A análise exploratória mostra que as espécies apresentam características morfológicas distintas, com boa separabilidade visual entre as classes. As variáveis relacionadas às pétalas (comprimento e largura) apresentam maior variabilidade entre as espécies.

### Seleção e Transformação de Variáveis

Todas as variáveis numéricas foram mantidas, pois são relevantes para a classificação das espécies. O dataset não apresenta valores ausentes e as variáveis já estão em escala similar (centímetros).

```python
# Preparação dos dados  
X = df_iris.drop(['species', 'species_name'], axis=1)  
y = df_iris['species']  
  
print("Variáveis preditoras:")  
print(X.columns.tolist())  
print("\nClasses alvo:")  
print(f"0: {species_names[0]}, 1: {species_names[1]}, 2: {species_names[2]}")  
  
# Análise da importância das variáveis através de boxplots  
fig, axes = plt.subplots(2, 2, figsize=(12, 10))  
features = X.columns  
  
for i, feature in enumerate(features):  
    ax = axes[i//2, i%2]  
    sns.boxplot(x='species_name', y=feature, data=df_iris, ax=ax)  
    ax.set_title(f'Distribuição de {feature} por Espécie')  
    ax.set_xlabel('Espécie')  
    ax.set_ylabel(feature)  
  
plt.tight_layout()  
plt.show()
```

### Treinamento do Modelo e Validação Cruzada

Foi implementado um modelo de Árvore de Decisão utilizando validação cruzada k-fold (k=5) para avaliar o desempenho. O hiperparâmetro `max_depth` foi ajustado para evitar overfitting, mantendo a interpretabilidade do modelo.]

```python
from sklearn.tree import DecisionTreeClassifier  
from sklearn.model_selection import cross_val_score  
  
# Criação e avaliação do modelo  
model = DecisionTreeClassifier(max_depth=3, random_state=42)  
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')  
  
print("Resultados da Validação Cruzada:")  
print(f"Acurácia por fold: {scores}")  
print(f"Acurácia média: {scores.mean():.4f} ± {scores.std():.4f}")  
  
# Treinando o modelo final com todos os dados para análise da importância das variáveis  
model.fit(X, y)  
print("\nImportância das variáveis:")  
for feature, importance in zip(X.columns, model.feature_importances_):  
    print(f"{feature}: {importance:.4f}")  
  
# Visualizando a árvore de decisão  
from sklearn.tree import plot_tree  
plt.figure(figsize=(15, 10))  
plot_tree(model, feature_names=X.columns, class_names=list(species_names.values()),   
          filled=True, rounded=True, fontsize=10)  
plt.title('Árvore de Decisão para Classificação de Espécies Iris')  
plt.show()
```

### Avaliação do Modelo e Justificativa

#### Figura de Mérito

A métrica utilizada para avaliação foi a acurácia, adequada para problemas de classificação multiclasse com classes balanceadas.

#### Resultados Obtidos

O modelo de árvore de decisão apresentou os seguintes resultados na validação cruzada:
- **Acurácia média:** `0.9733 ± 0.0249`

#### Interpretação para a Persona de Negócio

A acurácia obtida indica que o modelo é capaz de identificar corretamente a espécie da flor em aproximadamente 97% dos casos. Este resultado é excelente para a persona de negócio, pois permite:
1. **Identificação rápida:** Classificação automática de espécies com alta precisão
2. **Interpretabilidade:** A árvore de decisão fornece regras claras e compreensíveis para a classificação
3. **Eficiência:** Reduz significativamente o tempo necessário para identificação manual
4. **Confiabilidade:** O modelo pode ser usado como ferramenta de apoio em pesquisas taxonômicas

> A análise da importância das variáveis revela quais características morfológicas são mais determinantes para a classificação, fornecendo insights valiosos para estudos botânicos.

### Considerações sobre Generalização

A validação cruzada demonstra que o modelo apresenta desempenho consistente e estável em diferentes subconjuntos dos dados, com baixa variabilidade entre os folds. Isso indica:
1. **Robustez:** O modelo não apresenta overfitting significativo
2. **Estabilidade:** Os resultados são consistentes em diferentes amostras
3. **Aplicabilidade:** O modelo pode ser utilizado com segurança para classificar novas amostras de flores Iris

#### Limitações e Recomendações

- O modelo é específico para o gênero Iris e não deve ser aplicado a outras espécies de flores
- Recomenda-se validação com especialistas botânicos para casos duvidosos
- Para aplicações críticas, sugere-se complementar com análise morfológica detalhada
- O modelo pode ser expandido com mais espécies e características para maior abrangência

> O modelo desenvolvido atende perfeitamente às necessidades da persona de negócio, fornecendo uma ferramenta precisa, interpretável e eficiente para classificação de espécies de Iris, contribuindo significativamente para pesquisas em taxonomia vegetal.

## Modelo 4: Rede Neural — Classificação da Qualidade do Vinho

### Objetivo e Persona de Negócio

O objetivo deste modelo é classificar a qualidade de vinhos tintos com base em características físico-químicas, utilizando uma rede neural. A persona de negócio é um(a) enólogo(a) ou uma vinícola que deseja prever a qualidade do vinho antes da avaliação sensorial, otimizando processos de produção, seleção e comercialização.

### Carregamento e Exploração dos Dados

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Carregando o dataset Wine Quality
url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv'
df_wine = pd.read_csv(url, sep=';')

# Visualizando as primeiras linhas
df_wine.head()

# Informações gerais do dataset
print("Formato do dataset:", df_wine.shape)
print("\nColunas:", df_wine.columns.tolist())
```

> O conjunto de dados contém 1.599 registros, 11 variáveis preditoras e a variável alvo `quality` (nota de 0 a 10).

## Análise Exploratória dos Dados

```python
# Estatísticas descritivas
df_wine.describe()

# Verificando valores ausentes
print("Valores ausentes por variável:")
print(df_wine.isnull().sum())

# Distribuição da variável alvo
plt.figure(figsize=(8, 5))
sns.countplot(x='quality', data=df_wine)
plt.title('Distribuição da Qualidade do Vinho')
plt.xlabel('Qualidade')
plt.ylabel('Quantidade')
plt.show()
```

> A maioria dos vinhos possui qualidade entre 5 e 7, indicando um leve desbalanceamento das classes.

### Seleção e Transformação de Variáveis

Todas as variáveis físico-químicas foram mantidas. Para simplificar, a variável alvo foi transformada em binária: vinhos de qualidade >= 7 são considerados "bons" (1), os demais "não bons" (0).

```python
# Transformando a variável alvo em binária
df_wine['good_quality'] = (df_wine['quality'] >= 7).astype(int)

X = df_wine.drop(['quality', 'good_quality'], axis=1)
y = df_wine['good_quality']

# Normalizando as variáveis preditoras
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Treinamento do Modelo e Validação Cruzada

Foi utilizada uma rede neural do tipo MLPClassifier com validação cruzada k-fold (k=5). O número de neurônios na camada oculta foi ajustado para evitar overfitting e garantir boa capacidade de generalização.

```python
from sklearn.neural_network import MLPClassifier  
from sklearn.model_selection import cross_val_score  
  
# Criação e avaliação do modelo  
model = MLPClassifier(hidden_layer_sizes=(10,), max_iter=1000, random_state=42)  
scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')  
  
print("Resultados da Validação Cruzada:")  
print(f"Acurácia por fold: {scores}")  
print(f"Acurácia média: {scores.mean():.4f} ± {scores.std():.4f}")  
  
# Treinando o modelo final com todos os dados para análise dos coeficientes  
model.fit(X_scaled, y)  
print("\nPesos da primeira camada oculta (parcial):")  
print(model.coefs_[0][:, :5])  # Exibe parte dos pesos para não poluir a saída
```

### Avaliação do Modelo e Justificativa

#### Figura de Mérito

A métrica utilizada para avaliação foi a acurácia, adequada para problemas de classificação binária.

#### Resultados Obtidos

O modelo de rede neural apresentou os seguintes resultados na validação cruzada:
- **Acurácia média:** `0.8605 ± 0.0183`

#### Interpretação para a Persona de Negócio

A acurácia obtida indica que o modelo é capaz de prever corretamente a qualidade do vinho em aproximadamente 86% dos casos. Isso permite à vinícola ou ao enólogo identificar rapidamente vinhos de boa qualidade, otimizando processos de produção, seleção e comercialização, além de reduzir custos com avaliações sensoriais demoradas.

### Considerações sobre Generalização

A validação cruzada demonstra que o modelo apresenta desempenho consistente em diferentes subconjuntos dos dados, com baixa variabilidade entre os folds. Isso indica:
- **Robustez:** O modelo não apresenta overfitting significativo.
- **Estabilidade:** Os resultados são consistentes em diferentes amostras.
- **Aplicabilidade:** O modelo pode ser utilizado com segurança para classificar novos vinhos tintos com características físico-químicas semelhantes.

#### Limitações e Recomendações
- O modelo é específico para vinhos tintos e pode não generalizar para outros tipos de vinho.
- Recomenda-se atualização periódica do modelo com novos dados para manter a precisão.
- Para decisões críticas, o modelo deve ser usado como ferramenta de apoio, complementando avaliações sensoriais.

> O modelo desenvolvido atende ao objetivo proposto, fornecendo uma ferramenta eficiente, automatizada e precisa para classificação da qualidade de vinhos tintos.