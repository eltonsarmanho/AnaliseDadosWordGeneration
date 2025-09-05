# Pipeline TDE - WordGen Fase 2

## 📋 Visão Geral

Este módulo implementa o pipeline completo de análise dos dados do **Teste de Escrita (TDE)** do projeto WordGen - Fase 2. O TDE avalia a capacidade de escrita de palavras através de 40 questões específicas, organizadas por grupos de dificuldade.

## 🎯 Características do TDE

### Estrutura dos Dados
- **40 questões** de escrita de palavras (P1 a P40)
- **2 grupos de dificuldade** baseados na série escolar
- **Análise pré/pós-teste** com cálculo de mudanças
- **530 estudantes** após aplicação dos critérios de inclusão

### Grupos TDE
- **Grupo A (6º/7º anos)**: Palavras de dificuldade 1º-4º ano - 383 estudantes (72.3%)
- **Grupo B (8º/9º anos)**: Palavras de dificuldade 5º-9º ano - 147 estudantes (27.7%)

### Sistema de Pontuação
- **1 ponto**: Escrita correta da palavra
- **0 pontos**: Escrita incorreta ou erro
- **Vazio**: Questão não respondida

## 📁 Estrutura do Módulo

```
Modules/Fase2/TDE/
├── __init__.py                        # Inicializador do módulo
├── PipelineDataTDE.py                 # Pipeline principal - geração da tabela
├── GeradorDicionarioDadosTDE.py       # Gerador de dicionário de dados
├── PipelineTabelaBrutaTDE_CLI.py      # Interface de linha de comando
└── README.md                          # Esta documentação
```

## 🔧 Componentes

### 1. PipelineDataTDE.py
**Pipeline principal para processamento dos dados TDE**

- Carrega dados de pré-teste e pós-teste
- Aplica critérios de inclusão (80% questões respondidas)
- Calcula scores, deltas e percentuais
- Gera tabela consolidada com 251 colunas
- Salva em formato CSV e Excel

### 2. GeradorDicionarioDadosTDE.py
**Gerador de documentação detalhada**

- Cria dicionário de dados completo
- Documenta todas as 251 colunas
- Inclui metodologia e critérios
- Mapeia questões para palavras específicas
- Salva documentação em formato TXT

### 3. PipelineTabelaBrutaTDE_CLI.py
**Interface de linha de comando unificada**

- Comando `--gerar`: Executa pipeline completo
- Comando `--dicionario`: Gera documentação
- Comando `--resumo`: Mostra estatísticas detalhadas
- Comando `--preview`: Visualiza preview dos dados
- Comando `--help`: Exibe ajuda detalhada

## 🚀 Como Usar

### Instalação das Dependências
```bash
# Configurar ambiente Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

# Instalar dependências
pip install pandas numpy openpyxl
```

### Executar Pipeline Completo
```bash
# Navegar para o diretório do projeto
cd /caminho/para/AnaliseDadosWordGeneration

# Gerar tabela bruta TDE
python -m Modules.Fase2.TDE.PipelineTabelaBrutaTDE_CLI --gerar

# Gerar documentação
python -m Modules.Fase2.TDE.PipelineTabelaBrutaTDE_CLI --dicionario

# Ver estatísticas resumo
python -m Modules.Fase2.TDE.PipelineTabelaBrutaTDE_CLI --resumo

# Visualizar preview
python -m Modules.Fase2.TDE.PipelineTabelaBrutaTDE_CLI --preview
```

### Usar Módulos Individualmente
```python
# Importar funções específicas
from Modules.Fase2.TDE import gerar_tabela_tde, gerar_dicionario_tde

# Executar pipeline
tabela = gerar_tabela_tde()

# Gerar documentação
dicionario = gerar_dicionario_tde()
```

## 📊 Arquivos Gerados

### 1. Tabela Bruta TDE
- **CSV**: `Data/tabela_bruta_fase2_TDE_wordgen.csv`
- **Excel**: `Data/tabela_bruta_fase2_TDE_wordgen.xlsx`
- **Dimensões**: 530 registros × 251 colunas
- **Tamanho**: ~400KB (CSV), ~379KB (Excel)

### 2. Dicionário de Dados
- **Arquivo**: `Data/dicionario_dados_TDE_fase2.txt`
- **Conteúdo**: Documentação completa de todas as colunas
- **Tamanho**: ~6.9KB, 222 linhas

## 🏗️ Estrutura da Tabela Gerada

### Colunas de Identificação (5)
- `ID_Unico`: Identificador único (Nome + Turma)
- `Nome`: Nome completo do estudante
- `Escola`: Instituição de ensino
- `Turma`: Série/ano e turma
- `GrupoTDE`: Classificação automática (Grupo A/B)

### Colunas de Scores e Estatísticas (6)
- `Score_Pre`: Pontuação no pré-teste (0-40)
- `Score_Pos`: Pontuação no pós-teste (0-40)
- `Delta_Score`: Mudança na pontuação (Pós - Pré)
- `Questoes_Validas`: Número de questões respondidas
- `Percentual_Pre`: Percentual de acertos pré-teste
- `Percentual_Pos`: Percentual de acertos pós-teste

### Questões Individuais TDE (240)
Para cada questão P01-P40, há 3 colunas:
- `PXX_Pre_[PALAVRA]`: Resposta no pré-teste
- `PXX_Pos_[PALAVRA]`: Resposta no pós-teste  
- `PXX_Delta_[PALAVRA]`: Mudança (Pós - Pré)

## 📈 Estatísticas Principais

### Resultados Gerais
- **Total de estudantes**: 530
- **Score médio pré-teste**: 15.02 ± 7.13
- **Score médio pós-teste**: 10.66 ± 8.41
- **Delta médio**: -4.36 ± 8.42 (tendência de diminuição)

### Por Grupo TDE
**Grupo A (6º/7º anos) - N=383:**
- Score Pré: 15.21 ± 7.33
- Score Pós: 9.40 ± 8.41
- Delta médio: -5.81
- Melhorou: 84 (21.9%), Piorou: 275 (71.8%), Manteve: 24 (6.3%)

**Grupo B (8º/9º anos) - N=147:**
- Score Pré: 14.53 ± 6.57
- Score Pós: 13.95 ± 7.49
- Delta médio: -0.59
- Melhorou: 62 (42.2%), Piorou: 73 (49.7%), Manteve: 12 (8.2%)

### Ranking de Escolas (por Delta Score)
1. **EMEB PADRE ANCHIETA**: -1.29 (N=94)
2. **EMEB NATANAEL DA SILVA**: -1.62 (N=60)
3. **EMEF PADRE JOSÉ DOS SANTOS MOUSINHO**: -2.45 (N=56)
4. **EMEB PROFESSOR RICARDO VIEIRA DE LIMA**: -3.24 (N=187)
5. **EMEB PROFESSORA MARIA QUEIROZ FERRO**: -10.16 (N=133)

## ⚙️ Critérios de Processamento

### Inclusão de Dados
- Participação em **ambos** os testes (pré e pós)
- Pelo menos **80% das questões respondidas** (32/40)
- Dados de identificação válidos (Nome + Turma)

### Limpeza de Dados
- Conversão de valores para 0/1 (erro/acerto)
- Remoção de registros incompletos
- Padronização de identificadores únicos
- Filtro de qualidade dos dados

### Classificação de Grupos
- **Automática** baseada na série escolar
- 6º/7º anos → Grupo A (palavras básicas)
- 8º/9º anos → Grupo B (palavras avançadas)

## 🔍 Observações Importantes

### Tendências Identificadas
- **Diminuição geral** no desempenho TDE entre pré e pós-teste
- **Grupo B** teve melhor performance relativa que Grupo A
- **Variação significativa** entre escolas
- **42.2%** dos estudantes do Grupo B melhoraram vs **21.9%** do Grupo A

### Limitações
- Análise baseada apenas em presença/ausência de acertos
- Não inclui análise qualitativa dos tipos de erro
- Grupos definidos automaticamente por série
- Não considera fatores externos (frequência, contexto, etc.)

## 📝 Mapeamento das Questões

O arquivo `RespostaTED.json` contém o mapeamento completo das 40 questões TDE para as palavras específicas trabalhadas, organizadas por grupo de dificuldade.

## 🆘 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Verificar se está no diretório correto
cd /caminho/para/AnaliseDadosWordGeneration

# Verificar se o ambiente Python está ativo
source venv/bin/activate
```

### Erro: "FileNotFoundError"
```bash
# Verificar se os arquivos de dados existem
ls Data/Fase2/Pre/
ls Data/Fase2/Pos/
```

### Erro: "pandas not found"
```bash
# Instalar dependências
pip install pandas numpy openpyxl
```

## 📚 Arquivos Relacionados

- `Data/RespostaTED.json`: Mapeamento questões → palavras
- `Data/Fase2/Pre/Avaliação TDE II - RelaçãoCompletaAlunos.xlsx`: Dados pré-teste
- `Data/Fase2/Pos/Avaliação TDE II - RelaçãoCompletaAlunos.xlsx`: Dados pós-teste

---

**Autor**: Sistema de Análise WordGen  
**Projeto**: WordGen - Fase 2 - Teste de Escrita (TDE)  
**Data**: 2024  
**Versão**: 1.0.0
