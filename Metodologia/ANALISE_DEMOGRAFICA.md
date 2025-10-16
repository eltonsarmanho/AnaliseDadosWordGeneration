# Análise Demográfica - Documentação

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Estrutura de Dados](#estrutura-de-dados)
4. [Filtros Demográficos](#filtros-demográficos)
5. [Visualizações](#visualizações)
6. [Métricas e Estatísticas](#métricas-e-estatísticas)
7. [Uso no Dashboard](#uso-no-dashboard)

---

## 🎯 Visão Geral

A **Análise Demográfica** foi implementada para permitir a investigação de padrões e diferenças de performance entre diferentes perfis de estudantes, considerando variáveis como **sexo** e **idade**.

Esta funcionalidade é essencial para:
- Identificar disparidades de performance entre grupos demográficos
- Analisar se diferentes perfis de alunos respondem diferentemente às intervenções
- Fundamentar decisões pedagógicas baseadas em evidências
- Garantir equidade no processo educacional

---

## ✅ Funcionalidades Implementadas

### 1. Mapeamento de Datas de Aniversário
**Script:** `Modules/Preprocessamento/adicionar_data_aniversario.py`

- Lê dados de `Data/DadosGerais/*.csv`
- Normaliza nomes dos alunos para matching robusto
- Adiciona coluna `DataAniversario` aos arquivos longitudinais
- Taxa de sucesso: **91.2%** (TDE) e **90.7%** (Vocabulário)

**Exemplo de uso:**
```bash
cd /home/eltonss/Documents/VS\ CODE/AnaliseDadosWordGeneration
python Modules/Preprocessamento/adicionar_data_aniversario.py
```

### 2. Cálculo Automático de Idade
**Localização:** `Dashboard/app.py` (linhas 62-95)

Função: `calcular_idade(data_nasc, data_ref=None)`
- Suporta formatos: `DD/MM/YYYY` e `YYYY-MM-DD`
- Retorna idade em anos completos
- Retorna `None` se data inválida

**Exemplo:**
```python
idade = calcular_idade("17/03/2012")  # Retorna idade atual
idade = calcular_idade("17/03/2012", date(2023, 6, 15))  # Idade em data específica
```

### 3. Classificação em Faixas Etárias
**Localização:** `Dashboard/app.py` (linhas 97-112)

Função: `criar_faixas_etarias(idade)`

**Faixas definidas:**
- `< 10 anos`
- `10-11 anos`
- `12-13 anos`
- `14-15 anos`
- `≥ 16 anos`

---

## 📊 Estrutura de Dados

### Colunas Adicionadas

#### No CSV (TDE_longitudinal.csv e vocabulario_longitudinal.csv)
- `DataAniversario`: Data de nascimento do aluno (formato DD/MM/YYYY)

#### No DataFrame (computadas em tempo de execução)
- `Idade`: Idade em anos (int)
- `FaixaEtaria`: Classificação por faixa (string)

### Exemplo de Dados

| Nome | Sexo | DataAniversario | Idade | FaixaEtaria | Score_Pre | Score_Pos |
|------|------|----------------|-------|------------|-----------|-----------|
| João Silva | Masculino | 17/03/2012 | 12 | 12-13 anos | 45 | 67 |
| Maria Santos | Feminino | 05/08/2010 | 14 | 14-15 anos | 52 | 78 |

---

## 🎛️ Filtros Demográficos

### Localização
**Dashboard/app.py** (linhas 313-350)

### Filtros Disponíveis

#### 1. Filtro de Sexo
- **Tipo:** Multiselect
- **Valores:** Masculino, Feminino
- **Permite:** Selecionar um ou ambos os sexos

```python
if 'Sexo' in df.columns:
    sexos_disponiveis = sorted(df['Sexo'].dropna().unique())
    sexos_sel = st.multiselect("Sexo", sexos_disponiveis, default=sexos_disponiveis)
```

#### 2. Filtro de Faixa Etária
- **Tipo:** Multiselect
- **Valores:** 5 faixas predefinidas
- **Permite:** Selecionar uma ou mais faixas

```python
if 'FaixaEtaria' in df.columns:
    faixas_disponiveis = ['< 10 anos', '10-11 anos', '12-13 anos', '14-15 anos', '≥ 16 anos']
    faixas_sel = st.multiselect("Faixa Etária", faixas_disponiveis, default=faixas_disponiveis)
```

#### 3. Filtro de Idade Específica
- **Tipo:** Range Slider
- **Valores:** Mínimo e máximo dinâmicos do dataset
- **Permite:** Selecionar intervalo preciso de idades

```python
if 'Idade' in df.columns:
    idade_min = int(df['Idade'].min())
    idade_max = int(df['Idade'].max())
    idade_range = st.slider("Idade", idade_min, idade_max, (idade_min, idade_max))
```

---

## 📈 Visualizações

### Seção: Análise Demográfica
**Localização:** Dashboard/app.py (linhas 426-638)

### Estrutura
Organizada em **2 abas**:
1. **📊 Distribuição** - Análise descritiva dos dados
2. **📈 Performance por Perfil** - Análise comparativa de resultados

---

### Aba 1: Distribuição

#### Gráfico 1: Distribuição por Sexo
**Tipo:** Gráfico de Barras

**Características:**
- Mostra número de alunos únicos por sexo
- Exibe percentual em cada barra
- Cores: Masculino (azul), Feminino (vermelho)

**Informações:**
```
Quantidade absoluta
Percentual do total
```

**Exemplo de uso:**
- Verificar balanceamento de gênero na amostra
- Identificar viés de representação

---

#### Gráfico 2: Distribuição por Faixa Etária
**Tipo:** Gráfico de Barras Horizontal

**Características:**
- Mostra número de alunos únicos por faixa
- Exibe percentual em cada barra
- Cores: Escala de cores Viridis
- Eixo X rotacionado para melhor legibilidade

**Informações:**
```
Quantidade absoluta por faixa
Percentual do total
Ordenação cronológica das faixas
```

**Exemplo de uso:**
- Verificar distribuição etária dos participantes
- Identificar faixas com poucos dados

---

### Aba 2: Performance por Perfil

#### Análise 1: Performance por Sexo

**Gráfico:** Box Plot (Pré vs Pós-Teste)

**Características:**
- Compara Score_Pre e Score_Pos por sexo
- Cores: Pré-Teste (azul), Pós-Teste (vermelho)
- Mostra outliers
- Anotações com médias (μ) em cada box

**Estatísticas Complementares:**
```
Para cada sexo:
- Média Pré-Teste
- Média Pós-Teste
- Ganho absoluto
- Ganho percentual
```

**Exemplo de interpretação:**
```
Masculino:
- Pré: 45.30 | Pós: 67.20
- Ganho: 21.90 (48.3%)

Feminino:
- Pré: 47.80 | Pós: 69.50
- Ganho: 21.70 (45.4%)
```

---

#### Análise 2: Performance por Faixa Etária

**Gráfico:** Box Plot (Pré vs Pós-Teste)

**Características:**
- Compara Score_Pre e Score_Pos por faixa etária
- Cores: Pré-Teste (azul), Pós-Teste (vermelho)
- Mostra outliers
- Eixo X com faixas ordenadas cronologicamente

**Tabela de Estatísticas:**

| Faixa Etária | N Alunos | Pré (μ) | Pós (μ) | Ganho | Ganho % |
|--------------|----------|---------|---------|-------|---------|
| < 10 anos    | 45       | 42.30   | 61.20   | 18.90 | 44.7%   |
| 10-11 anos   | 123      | 46.50   | 68.30   | 21.80 | 46.9%   |
| 12-13 anos   | 89       | 48.70   | 70.10   | 21.40 | 43.9%   |

**Exemplo de uso:**
- Identificar se faixas etárias mais jovens/velhas têm desempenho diferente
- Verificar se a intervenção é igualmente efetiva para todas as idades

---

## 📊 Métricas e Estatísticas

### Métricas Calculadas

#### 1. Ganho Absoluto
```
Ganho = Média_Pós - Média_Pré
```

#### 2. Ganho Percentual
```
Ganho % = (Ganho / Média_Pré) × 100
```

#### 3. Distribuição
- Contagem de alunos únicos
- Percentual em relação ao total
- Estatísticas descritivas (média, mediana, quartis)

---

## 🖥️ Uso no Dashboard

### Fluxo de Trabalho

#### 1. Carregar Dashboard
```bash
cd Dashboard
streamlit run app.py
```

#### 2. Aplicar Filtros Gerais
- Selecionar Prova (TDE ou Vocabulário)
- Selecionar Fase(s)
- Selecionar Escola(s)
- Selecionar Turma(s)

#### 3. Aplicar Filtros Demográficos
- Selecionar Sexo(s) desejado(s)
- Selecionar Faixa(s) Etária(s)
- Ajustar range de idade específica

#### 4. Analisar Resultados
- Visualizar distribuição demográfica
- Comparar performance entre grupos
- Identificar padrões ou disparidades

---

## 🔍 Casos de Uso

### Caso 1: Análise de Equidade de Gênero
**Objetivo:** Verificar se há diferenças de performance entre meninos e meninas

**Passos:**
1. Não filtrar por sexo (manter ambos)
2. Navegar até "Performance por Sexo"
3. Comparar médias e ganhos
4. Avaliar magnitude das diferenças

**Interpretação:**
- Diferenças < 5% → Provavelmente não significativas
- Diferenças > 10% → Investigar causas

---

### Caso 2: Adequação Etária da Intervenção
**Objetivo:** Verificar se a intervenção é adequada para todas as faixas etárias

**Passos:**
1. Não filtrar por idade (manter todas as faixas)
2. Navegar até "Performance por Faixa Etária"
3. Observar ganhos percentuais
4. Identificar faixas com menor ganho

**Interpretação:**
- Ganhos uniformes → Intervenção adequada para todos
- Ganhos discrepantes → Considerar adaptações específicas

---

### Caso 3: Foco em Grupo Específico
**Objetivo:** Analisar apenas alunos de 12-13 anos do sexo masculino

**Passos:**
1. Filtrar Sexo: Masculino
2. Filtrar Faixa Etária: 12-13 anos
3. Visualizar todas as análises com esse subgrupo
4. Comparar com grupo completo

---

## 🚀 Melhorias Futuras

### Curto Prazo
- [ ] Adicionar testes estatísticos (t-test, ANOVA)
- [ ] Incluir intervalos de confiança nos gráficos
- [ ] Exportar relatórios demográficos em PDF

### Médio Prazo
- [ ] Análise de interação Sexo × Idade
- [ ] Gráficos de correlação entre idade e performance
- [ ] Predição de performance baseada em características demográficas

### Longo Prazo
- [ ] Machine Learning para identificar perfis de risco
- [ ] Dashboard de equidade educacional
- [ ] Comparações longitudinais de coortes

---

## 📝 Notas Técnicas

### Performance
- Cálculos de idade são feitos em tempo de execução (não armazenados)
- Filtros são aplicados diretamente ao DataFrame (eficiente)
- Visualizações usam Plotly (interativo e responsivo)

### Dados Faltantes
- Alunos sem DataAniversario: Excluídos das análises de idade
- Alunos sem Sexo: Excluídos das análises de gênero
- Dashboard exibe mensagens informativas quando dados não disponíveis

### Privacidade
- Dados de nome são usados apenas para matching
- Visualizações mostram apenas dados agregados
- Não há identificação individual nos gráficos

---

## 📚 Referências

- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Date/Time](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Cohen's d Effect Size](https://en.wikipedia.org/wiki/Effect_size#Cohen's_d)

---

**Última atualização:** 2024
**Autor:** Sistema de Análise de Dados WordGeneration
**Versão:** 1.0
