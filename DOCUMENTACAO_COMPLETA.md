# Análise de Dados - WordGen - Doc### Fase 2 - Análise por Grupos Etários

**Objetivo**: Análise comparativa de vocabulário entre diferentes grupos etários.

**Características**:
- **Grupos**: 6º/7º anos vs 8º/9º anos
- **Dados**: Pré-teste e pós-teste com questões Q1-Q50
- **Domínio de valores**: 0 (erro), 1 (acerto parcial), 2 (acerto total), D/M (neutro)
- **Limpeza de dados**: Remove estudantes que participaram de apenas um teste
- **Filtros**: Apenas estudantes com pelo menos 80% das questões preenchidas

**Módulos disponíveis**:
- `PipelineData.py`: Pipeline de processamento e análise estatística
- `RelatorioVisualCompleto.py`: Geração de relatórios visuais completos em HTML
- `AnaliseVisual.py`: Análise visual interativa e geração de gráficos PNG

**Análises realizadas**:
1. **Taxa de acertos por palavra** - Mapeamento com RespostaVocabulario.json
2. **Distribuição de erros por palavra**
3. **Comparação intergrupos** - Desempenho 6º/7º vs 8º/9º anos
4. **Benchmarks educacionais** - Cohen, Hattie, Marulis & Neuman
5. **Estatística geral** - Comparação pré vs pós-teste por grupoa

## Visão Geral do Projeto

Este projeto realiza análises estatísticas completas dos dados do programa WordGen (Geração de Impacto em Vocabulário), comparando resultados de pré-teste e pós-teste em diferentes fases do programa educacional.

## Estrutura do Projeto

```
AnaliseDadosWordGeneration/
├── Data/                                    # Dados e resultados
│   ├── Fase2/                              # Dados da Fase 2
│   │   ├── Pre/                            # Pré-testes
│   │   └── Pos/                            # Pós-testes
│   ├── RespostaVocabulario.json            # Mapeamento questões-palavras
│   ├── pipeline_vocabulario_wordgen_fase2.txt     # Relatório Fase 2
│   ├── pipeline_vocabulario_wordgen_etapa3_fase3.txt  # Relatório Fase 3
│   └── [outros arquivos de dados e relatórios]
├── Modules/                                # Códigos de análise
│   ├── Fase2/
│   │   └── PipelineData.py                # Pipeline Fase 2
│   ├── Fase3/
│   │   ├── PipelineData.py                # Pipeline Fase 3
│   │   ├── AnaliseVisual.py               # Análises visuais
│   │   └── RelatorioVisualCompleto.py     # Relatórios visuais
│   └── Fase4/
│       ├── PipelineData.py                # Pipeline Fase 4
│       ├── AnaliseVisual.py               # Análises visuais
│       └── RelatorioVisualCompleto.py     # Relatórios visuais
└── [arquivos de configuração]
```

## Fases do Projeto

### Fase 2 - Análise por Grupos Etários (NOVO)

**Objetivo**: Analisar o desempenho em vocabulário separando estudantes em dois grupos etários.

**Características**:
- **Grupos**: 6º/7º anos vs 8º/9º anos
- **Dados**: Pré-teste e pós-teste com questões Q1-Q50
- **Domínio de valores**: 0 (erro), 1 (acerto parcial), 2 (acerto total), D/M (neutro)
- **Limpeza de dados**: Remove estudantes que participaram de apenas um teste
- **Filtros**: Apenas estudantes com pelo menos 80% das questões preenchidas

**Análises realizadas**:
1. **Taxa de acertos por palavra** - Mapeamento com RespostaVocabulario.json
2. **Distribuição de erros por palavra**
3. **Comparação intergrupos** - Desempenho 6º/7º vs 8º/9º anos
4. **Benchmarks educacionais** - Cohen, Hattie, Marulis & Neuman
5. **Estatística geral** - Comparação pré vs pós-teste por grupo

### Fase 3 - Análise com Benchmarks Educacionais Específicos

**Objetivo**: Análise detalhada com múltiplos frameworks de benchmarks educacionais.

**Características**:
- Dados estruturados em formato específico
- Análise de effect size (Cohen's d)
- Interpretação baseada em literatura científica

### Fase 4 - Análise Consolidada

**Objetivo**: Análise final consolidada dos resultados do programa.

**Características**:
- Dados agregados finais
- Validação de resultados

## Metodologia de Análise

### 1. Limpeza e Preparação dos Dados

#### Fase 2 - Processo Específico:
```python
# Conversão de valores das questões
0, '0', '0.0' → 0 (Erro)
1, '1', '1.0' → 1 (Acerto parcial)  
2, '2', '2.0' → 2 (Acerto total)
'D', 'M' → NaN (Neutro - valores desconhecidos)
```

#### Filtros aplicados:
- Apenas estudantes presentes em ambos os testes (pré e pós)
- Mínimo de 40 questões válidas (80% das 50 questões)
- Identificação única: Nome + Turma (para lidar com homônimos)

#### Classificação de grupos etários:
```python
def classificar_grupo_etario(turma):
    if '6º' in turma or '6°' in turma or '7º' in turma or '7°' in turma:
        return "6º/7º anos"
    elif '8º' in turma or '8°' in turma or '9º' in turma or '9°' in turma:
        return "8º/9º anos"
```

### 2. Análises Estatísticas

#### Testes de Normalidade:
- **Shapiro-Wilk**: Para verificar distribuição normal dos dados
- **Escolha do teste**: t-teste pareado (normal) vs Wilcoxon (não-normal)

#### Effect Size (Cohen's d):
```python
# Cálculo do Cohen's d corrigido
diferenca = scores_pos - scores_pre
pooled_std = sqrt((scores_pre.var() + scores_pos.var()) / 2)
cohen_d = diferenca.mean() / pooled_std
```

### 3. Benchmarks Educacionais

#### Framework Teórico:

**Cohen (1988) - Statistical Power Analysis:**
- d = 0.2: Pequeno (detectável por especialista)
- d = 0.5: Médio (visível ao olho nu)  
- d = 0.8: Grande (óbvio para qualquer pessoa)

**Hattie (2009) - Visible Learning (800+ meta-análises educacionais):**
- d ≥ 0.6: 🟢 Excelente resultado educacional
- d ≥ 0.4: 🟡 Bom resultado educacional (threshold)
- d < 0.4: 🔴 Abaixo do esperado para educação

**Marulis & Neuman (2010) - Vocabulário Específico (67 estudos):**
- d ≥ 0.50: 🟢 Substancial para vocabulário
- d ≥ 0.35: 🟡 Educacionalmente significativo
- d < 0.35: 🔴 Não significativo para vocabulário

#### Classificação Final Integrada:
- **EXCELENTE** (d ≥ 0.6): Transformador - resultado excepcional
- **BOM** (d ≥ 0.4): Substancial - intervenção eficaz
- **ADEQUADO** (d ≥ 0.35): Moderado - ganho educacional detectável
- **MARGINAL** (d ≥ 0.2): Pequeno - ganho limitado
- **INSUFICIENTE** (d < 0.2): Trivial - sem impacto prático

### 4. Análise por Palavra/Questão

#### Mapeamento de Questões para Palavras:
Utiliza o arquivo `RespostaVocabulario.json` que mapeia cada questão (Q1-Q50) para a palavra trabalhada correspondente.

#### Métricas calculadas:
- **Taxa de acerto**: Proporção de respostas ≥ 1 (acertos parciais + totais)
- **Distribuição de erros**: Contagem de respostas = 0
- **Melhora**: Diferença entre taxa pós-teste e pré-teste
- **Ranking**: Top 10 palavras com maior melhora e 5 com menor melhora

## Resultados da Fase 2

### Resumo Geral:
- **Total analisado**: 1.362 estudantes
- **6º/7º anos**: 730 estudantes
- **8º/9º anos**: 632 estudantes

### Effect Sizes observados:
- **6º/7º anos**: Cohen's d = 0.1140 (INSUFICIENTE)
- **8º/9º anos**: Cohen's d = 0.1184 (INSUFICIENTE)  
- **Geral**: Cohen's d = 0.1104 (INSUFICIENTE)

### Interpretação:
Embora estatisticamente significativas (p < 0.05), as melhorias são **triviais** segundo todos os benchmarks educacionais, indicando que a intervenção teve impacto prático limitado na Fase 2.

### Palavras com maior melhora (Geral):
1. **status** (Q30): +10.6%
2. **diretriz** (Q2): +9.4%
3. **década** (Q3): +9.0%
4. **ambígua** (Q13): +7.4%
5. **contribuiu** (Q23): +6.9%

## Como Executar as Análises

### Pré-requisitos:
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install pandas scipy numpy openpyxl
```

### Executar Pipeline Fase 2:
```bash
cd /home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration
python Modules/Fase2/PipelineData.py
```

### Executar Relatório Visual Completo Fase 2:
```bash
python Modules/Fase2/RelatorioVisualCompleto.py
```

### Executar Análise Visual Interativa Fase 2:
```bash
python Modules/Fase2/AnaliseVisual.py
```

### Executar Pipeline Fase 3:
```bash
python Modules/Fase3/PipelineData.py
```

### Executar Pipeline Fase 4:
```bash
python Modules/Fase4/PipelineData.py
```

## Arquivos de Saída

### Fase 2:
- **Texto**: `Data/pipeline_vocabulario_wordgen_fase2.txt`
- **HTML**: `Data/relatorio_visual_wordgen_fase2.html`
- **Figuras**: `Data/figures/fase2_*.png` (múltiplos gráficos PNG)

### Fase 3 e 4:
- `Data/pipeline_vocabulario_wordgen_etapa3_fase3.txt`
- `Data/pipeline_vocabulario_wordgen_fase4.txt`

## Referências Científicas

1. **Cohen, J. (1988)**. Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.

2. **Hattie, J. (2009)**. Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement. Routledge.

3. **Marulis, L. M., & Neuman, S. B. (2010)**. The effects of vocabulary intervention on young children's word learning: A meta-analysis. Review of Educational Research, 80(3), 300-335.

## Notas Técnicas

### Decisões Metodológicas:
- **ID único**: Nome + Turma para lidar com homônimos
- **Threshold de validade**: 80% das questões preenchidas
- **Teste estatístico**: Wilcoxon para dados não-normais
- **Effect size**: Cohen's d com desvio padrão pooled

### Limitações:
- Dados faltantes tratados como neutros (NaN)
- Análise limitada a estudantes com dados completos
- Resultados dependem da qualidade do mapeamento questão-palavra

### Futuras Melhorias:
- Análise longitudinal entre fases
- Correlação com variáveis demográficas
- Análise de retenção do aprendizado
- Validação cruzada dos resultados
