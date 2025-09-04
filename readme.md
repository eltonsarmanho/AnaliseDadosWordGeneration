# Análise de Dados - WordGen (Geração de Impacto em Vocabulário)

## 📊 Descrição do Projeto

Este projeto realiza análises estatísticas completas dos dados do programa WordGen, comparando resultados de pré-teste e pós-teste em diferentes fases do programa educacional com foco em análise de vocabulário.

## 🎯 Objetivos

- **Fase 2**: Análise por grupos etários (6º/7º anos vs 8º/9º anos) com benchmarks educacionais
- **Fase 3**: Análise com benchmarks educacionais específicos  
- **Fase 4**: Análise consolidada final

## 🔧 Funcionalidades Principais

### Fase 2 - Análise por Grupos Etários (NOVO)
- ✅ Divisão de estudantes em grupos: 6º/7º anos e 8º/9º anos
- ✅ Análise de dados pré e pós-teste com filtros rigorosos
- ✅ Sistema de valores: 0 (erro), 1 (acerto parcial), 2 (acerto total), D/M (neutro)
- ✅ Taxa de acertos por palavra com mapeamento das questões Q1-Q50
- ✅ Distribuição de erros por palavra
- ✅ Comparação intergrupos de desempenho
- ✅ Benchmarks educacionais (Cohen, Hattie, Marulis & Neuman)
- ✅ Estatística geral e comparação pré vs pós-teste

### Análises Estatísticas Implementadas
- **Limpeza de dados**: Remove estudantes com dados incompletos
- **Testes de normalidade**: Shapiro-Wilk
- **Testes comparativos**: t-teste pareado / Wilcoxon
- **Effect size**: Cohen's d com interpretação por benchmarks
- **Análise por palavra**: Taxa de acerto e melhora individual

### Benchmarks Educacionais
- **Cohen (1988)**: Framework estatístico padrão
- **Hattie (2009)**: 800+ meta-análises educacionais  
- **Marulis & Neuman (2010)**: Específico para vocabulário

## 📁 Estrutura do Projeto

```
AnaliseDadosWordGeneration/
├── Data/                                    # Dados e resultados
│   ├── Fase2/                              # Dados Fase 2
│   ├── RespostaVocabulario.json            # Mapeamento questões
│   └── pipeline_vocabulario_wordgen_*.txt  # Relatórios gerados
├── Modules/                                # Códigos de análise
│   ├── Fase2/PipelineData.py              # 🆕 Pipeline Fase 2
│   ├── Fase3/PipelineData.py              # Pipeline Fase 3
│   └── Fase4/PipelineData.py              # Pipeline Fase 4
├── DOCUMENTACAO_COMPLETA.md               # 📖 Documentação detalhada
└── readme.md                              # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Dependências já instaladas: pandas, scipy, numpy, openpyxl
```

### Executar Análises
```bash
# Fase 2 - Análise por grupos etários (NOVO)
python Modules/Fase2/PipelineData.py

# Fase 3 - Benchmarks educacionais
python Modules/Fase3/PipelineData.py

# Fase 4 - Análise consolidada
python Modules/Fase4/PipelineData.py
```

## 📈 Resultados da Fase 2

### Resumo Executivo:
- **1.362 estudantes analisados** (após filtros de qualidade)
- **6º/7º anos**: 730 estudantes | **8º/9º anos**: 632 estudantes
- **Effect Size Geral**: d = 0.1104 (Classificação: INSUFICIENTE)
- **Significância**: p < 0.05 (estatisticamente significativo)
- **Interpretação**: Melhoria trivial sem impacto prático educacional

### Top 5 Palavras com Maior Melhora:
1. **status** (+10.6%)
2. **diretriz** (+9.4%)  
3. **década** (+9.0%)
4. **ambígua** (+7.4%)
5. **contribuiu** (+6.9%)

## 📋 Metodologia

### Limpeza de Dados
- Apenas estudantes presentes em pré E pós-teste
- Mínimo 40/50 questões válidas (80%)
- ID único: Nome + Turma (resolve homônimos)

### Sistema de Pontuação
- **0**: Erro completo
- **1**: Acerto parcial
- **2**: Acerto total
- **D/M**: Valores desconhecidos (tratados como neutros)

### Benchmarks Aplicados
- **d ≥ 0.6**: 🟢 Excelente
- **d ≥ 0.4**: 🟡 Bom resultado
- **d ≥ 0.35**: 🟠 Adequado (vocabulário)
- **d < 0.35**: 🔴 Insuficiente

## 📊 Arquivos Gerados

Cada pipeline gera relatórios detalhados:
- `Data/pipeline_vocabulario_wordgen_fase2.txt` - **Relatório Fase 2 (NOVO)**
- `Data/pipeline_vocabulario_wordgen_etapa3_fase3.txt` - Relatório Fase 3
- `Data/pipeline_vocabulario_wordgen_fase4.txt` - Relatório Fase 4

## 📚 Documentação

Para documentação completa, metodologia detalhada e referências científicas, consulte:
**[DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)**

## 🔬 Referências Científicas

1. Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences
2. Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses  
3. Marulis, L. M., & Neuman, S. B. (2010). Vocabulary intervention meta-analysis

## 🏗️ Desenvolvido Por

Pipeline da Fase 2 desenvolvido com base nos padrões das Fases 3 e 4, implementando análise por grupos etários com benchmarks educacionais específicos para vocabulário.

---
**Última atualização**: Setembro 2025 | **Status**: ✅ Fase 2 Concluída