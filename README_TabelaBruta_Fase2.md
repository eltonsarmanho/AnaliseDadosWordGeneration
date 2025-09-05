# Pipeline Tabela Bruta - WordGen Fase 2

## Descrição

Este pipeline gera uma tabela consolidada com dados **brutos após pré-processamento** do projeto WordGen Fase 2. A tabela contém todos os dados limpos e organizados em formato tabular, pronta para análises personalizadas.

## Arquivos Gerados

### 📁 Principais
- `tabela_bruta_fase2_vocabulario_wordgen.csv` (1MB) - Tabela em formato CSV
- `tabela_bruta_fase2_vocabulario_wordgen.xlsx` (627KB) - Tabela em formato Excel
- `dicionario_dados_tabela_bruta_fase2.txt` (16KB) - Dicionário de dados completo

### 📊 Conteúdo da Tabela

**Total:** 1.362 registros × 161 colunas

#### Colunas de Identificação (11 colunas)
- `ID_Unico` - Identificador único (Nome + Turma)
- `Nome` - Nome completo do estudante
- `Escola` - Nome da escola
- `Turma` - Turma do estudante
- `GrupoEtario` - Classificação etária (6º/7º anos ou 8º/9º anos)
- `Score_Pre` - Pontuação total no pré-teste (0-100)
- `Score_Pos` - Pontuação total no pós-teste (0-100)
- `Delta_Score` - Diferença entre pós e pré-teste
- `Questoes_Validas` - Número de questões válidas respondidas
- `Percentual_Pre` - Percentual de acerto no pré-teste
- `Percentual_Pos` - Percentual de acerto no pós-teste

#### Colunas de Questões (150 colunas)
Para cada uma das 50 questões de vocabulário:
- `Q##_Pre_[palavra]` - Resposta no pré-teste (0, 1, 2, ou vazio)
- `Q##_Pos_[palavra]` - Resposta no pós-teste (0, 1, 2, ou vazio) 
- `Q##_Delta_[palavra]` - Diferença entre pós e pré-teste

**Legendas das respostas:**
- `0` = Erro
- `1` = Acerto parcial  
- `2` = Acerto total
- Vazio = Não respondido ou valor D/M

## Como Usar

### 🚀 Executar Pipeline Completo
```bash
# Gerar tabela + resumo + preview + dicionário
python Modules/Fase2/PipelineTabelaBrutaCLI.py --all
```

### 📝 Comandos Individuais
```bash
# Gerar apenas a tabela bruta
python Modules/Fase2/PipelineTabelaBrutaCLI.py --gerar

# Ver resumo estatístico
python Modules/Fase2/PipelineTabelaBrutaCLI.py --resumo

# Ver preview dos dados
python Modules/Fase2/PipelineTabelaBrutaCLI.py --preview

# Gerar dicionário de dados
python Modules/Fase2/PipelineTabelaBrutaCLI.py --dicionario

# Ver opções disponíveis
python Modules/Fase2/PipelineTabelaBrutaCLI.py --help
```

### 📊 Scripts Avançados
```bash
# Pipeline básico (sem CLI)
python Modules/Fase2/PipelineTabelaBruta.py

# Resumo executivo (sem CLI)
python Modules/Fase2/ResumoTabelaBruta.py

# Dicionário de dados (sem CLI)
python Modules/Fase2/GeradorDicionarioDados.py
```

## Dicionário de Dados

### 📖 Documentação Completa
O arquivo `dicionario_dados_tabela_bruta_fase2.txt` contém documentação detalhada de:

#### 📋 Estrutura Completa
- **Informações gerais:** Descrição do dataset, período, população
- **Distribuições:** Por escola, grupo etário, estatísticas descritivas
- **Colunas de identificação:** 11 colunas com dados do estudante e scores
- **Questões de vocabulário:** 150 colunas (50 questões × 3 tipos: Pre/Pos/Delta)
- **Lista completa das palavras:** Todas as 50 palavras com respostas corretas
- **Critérios de inclusão:** Regras de pré-processamento aplicadas
- **Transformações:** Como os dados foram limpos e padronizados
- **Estatísticas descritivas:** Médias, desvios, distribuições
- **Guia de uso:** Como analisar os dados, limitações, cuidados

#### 🔍 Exemplo de Documentação por Coluna
```
1. ID_Unico
   Tipo: Texto
   Descrição: Identificador único do estudante
   Detalhes: Formato: 'Nome_Turma' para evitar duplicatas

6. Score_Pre
   Tipo: Numérica
   Descrição: Pontuação total no pré-teste
   Detalhes: Faixa: 0-100 pontos (soma de Q1-Q50)
```

#### 📚 Documentação das Questões
```
Q01 - enorme
     Colunas: Q01_Pre_enorme, Q01_Pos_enorme, Q01_Delta_enorme
     Resposta correta: grande

Q02 - diretriz
     Colunas: Q02_Pre_diretriz, Q02_Pos_diretriz, Q02_Delta_diretriz
     Resposta correta: regra
```

### 💡 Codificação das Respostas
- **0** = Erro (resposta incorreta)
- **1** = Acerto parcial (resposta parcialmente correta)
- **2** = Acerto total (resposta completamente correta)
- **(vazio)** = Não respondido ou valor inválido (D/M no original)

### 📊 Estatísticas Incluídas
- **468 linhas** de documentação
- **161 colunas** documentadas
- **50 questões** mapeadas com palavras
- **Estatísticas descritivas** completas
- **Guias de uso** e limitações

---

### 👥 Distribuição por Grupo Etário
- **6º/7º anos:** 730 estudantes (53.6%)
- **8º/9º anos:** 632 estudantes (46.4%)

### 🏫 Distribuição por Escola
- **EMEB PROFESSOR RICARDO VIEIRA DE LIMA:** 551 estudantes (40.5%)
- **EMEB PROFESSORA MARIA QUEIROZ FERRO:** 291 estudantes (21.4%)
- **EMEB PADRE ANCHIETA:** 206 estudantes (15.1%)
- **EMEF PADRE JOSÉ DOS SANTOS MOUSINHO:** 189 estudantes (13.9%)
- **EMEB NATANAEL DA SILVA:** 125 estudantes (9.2%)

### 📈 Performance Geral
- **Score Pré-teste:** Média 26.49 (DP: 8.68)
- **Score Pós-teste:** Média 27.47 (DP: 9.17)
- **Melhoria Média:** +0.99 pontos (DP: 6.00)

### 📊 Distribuição de Mudanças
- **Melhoraram:** 751 estudantes (55.1%)
- **Pioraram:** 501 estudantes (36.8%)
- **Mantiveram:** 110 estudantes (8.1%)

## Exemplos de Análises

### 📋 Carregar dados em Python
```python
import pandas as pd

# Carregar tabela
df = pd.read_csv('Data/tabela_bruta_fase2_vocabulario_wordgen.csv', encoding='utf-8-sig')

# Ver informações básicas
print(f"Total de estudantes: {len(df)}")
print(df.columns.tolist())  # Ver todas as colunas
```

### 🔍 Análises por Escola
```python
# Filtrar por escola específica
escola_dados = df[df['Escola'] == 'EMEB PADRE ANCHIETA']

# Calcular estatísticas
print(f"Melhoria média: {escola_dados['Delta_Score'].mean():.2f}")
```

### 📚 Análise de Palavras Específicas
```python
# Analisar palavra "enorme" (Q01)
pre_enorme = df['Q01_Pre_enorme']
pos_enorme = df['Q01_Pos_enorme']
delta_enorme = df['Q01_Delta_enorme']

# Calcular taxa de melhoria
melhorias = (delta_enorme > 0).sum()
print(f"Estudantes que melhoraram em 'enorme': {melhorias}")
```

### 👥 Comparação entre Grupos Etários
```python
grupo1 = df[df['GrupoEtario'] == '6º/7º anos']
grupo2 = df[df['GrupoEtario'] == '8º/9º anos']

print(f"Grupo 6º/7º: {grupo1['Score_Pre'].mean():.2f} → {grupo1['Score_Pos'].mean():.2f}")
print(f"Grupo 8º/9º: {grupo2['Score_Pre'].mean():.2f} → {grupo2['Score_Pos'].mean():.2f}")
```

## Pré-processamento Aplicado

### ✅ Critérios de Inclusão
1. **Participação completa:** Estudante deve ter dados em pré E pós-teste
2. **Questões válidas:** Pelo menos 40/50 questões respondidas (80%)
3. **Dados limpos:** Valores D/M convertidos para NaN, números padronizados

### 🔄 Transformações
- **Valores das questões:** 0 (erro) → 1 (parcial) → 2 (total)
- **Grupos etários:** Baseado na turma (6º/7º vs 8º/9º anos)
- **ID único:** Nome + Turma para evitar duplicatas
- **Scores:** Soma das pontuações de todas as questões válidas

### 📉 Dados Removidos
- **Original:** 2.405 registros
- **Após limpeza:** 1.362 registros (56.5% mantidos)
- **Principal motivo:** Participação incompleta (só pré OU só pós-teste)

## Palavras Analisadas (Primeiras 10)

1. **Q01:** enorme
2. **Q02:** diretriz  
3. **Q03:** década
4. **Q04:** isolar-se
5. **Q05:** depreciativos
6. **Q06:** abandonou
7. **Q07:** exibição
8. **Q08:** dramática
9. **Q09:** suspensos
10. **Q10:** libere

## Estrutura dos Arquivos

```
Data/
├── tabela_bruta_fase2_vocabulario_wordgen.csv    # Tabela principal
├── tabela_bruta_fase2_vocabulario_wordgen.xlsx   # Versão Excel
├── dicionario_dados_tabela_bruta_fase2.txt       # Dicionário de dados
└── Fase2/
    ├── Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.xlsx
    └── Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (...).xlsx
```

## Requisitos

- Python 3.8+
- pandas
- openpyxl (para Excel)
- numpy

## Logs e Debugging

O pipeline gera logs detalhados mostrando:
- ✅ Dados carregados e processados
- 📊 Estatísticas de limpeza
- 🔍 Distribuições por grupo e escola  
- 💾 Arquivos gerados com tamanhos

---

**Criado em:** 2025-09-04  
**Versão:** 1.0  
**Última atualização:** 2025-09-04 17:06
