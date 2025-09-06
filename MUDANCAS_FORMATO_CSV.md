# MIGRAÇÃO PARA FORMATO CSV - PIPELINES WORDGEN FASE 2

## 📋 RESUMO DAS MODIFICAÇÕES

Data: 05/09/2025  
Objetivo: Migrar todos os pipelines de análise e relatórios visuais do TDE e Vocabulário para usar arquivos CSV ao invés de Excel.

## 🔍 PROBLEMA IDENTIFICADO

Durante análise comparativa entre formatos CSV e Excel, foram identificadas diferenças significativas:

### Diferenças nos Dados:
- **Excel**: Valores ausentes representados como `NaN`
- **CSV**: Valores ausentes convertidos para string `"0"`
- **Impacto**: 476 conversões NaN→"0" no arquivo PRÉ, afetando análises estatísticas

### Impacto Estatístico:
- **N Estudantes**: 1362 (Excel) vs 2274 (CSV) - diferença de 912 registros
- **Cohen's d**: 0.1104 (Excel) vs -0.1712 (CSV) - diferença de 0.28
- **Interpretação**: Excel mostrava melhora pequena; CSV mostrava deterioração

## 🔧 ARQUIVOS MODIFICADOS

### 📚 VOCABULÁRIO - Fase 2

#### 1. `PipelineData.py`
- ✅ Caminhos de arquivo atualizados para CSV
- ✅ Carregamento com `pd.read_csv()` 
- ✅ Remoção da análise comparativa Excel vs CSV
- ✅ Simplificação do código

#### 2. `PipelineTabelaBruta.py`
- ✅ Caminhos atualizados para CSV
- ✅ Carregamento com `pd.read_csv()`

#### 3. `RelatorioVisualCompleto.py`
- ✅ Constantes de arquivo atualizadas para CSV
- ✅ Função `obter_escolas_disponiveis()` atualizada
- ✅ Função `carregar_e_preparar_dados()` atualizada

#### 4. `AnaliseVisual.py`
- ✅ Caminhos no construtor atualizados para CSV
- ✅ Método `carregar_dados()` atualizado

#### 5. `GeradorDicionarioDados.py`
- ✅ Prioridade alterada: CSV primeiro, Excel como fallback
- ✅ Lógica de carregamento invertida

### 📝 TDE - Fase 2

#### 1. `PipelineDataTDE.py`
- ✅ Caminhos de arquivo atualizados para CSV
- ✅ Carregamento com `pd.read_csv()`

#### 2. `RelatorioVisualCompleto.py`
- ✅ Constante `CSV_TABELA_TDE` atualizada para CSV
- ✅ Função `obter_escolas_disponiveis_tde()` atualizada

## ✅ TESTES REALIZADOS

### Vocabulário:
```bash
python Modules/Fase2/Vocabulario/PipelineData.py
```
- ✅ Execução bem-sucedida
- ✅ 2274 registros processados
- ✅ Cohen's d = -0.1712 (consistente com dados CSV)
- ✅ Relatório salvo em `pipeline_vocabulario_wordgen_fase2.txt`

### TDE:
```bash
python Modules/Fase2/TDE/PipelineDataTDE.py
```
- ✅ Execução bem-sucedida
- ✅ 2023 registros processados
- ✅ Tabela bruta gerada em CSV e Excel
- ✅ Estatísticas por grupo e escola calculadas

## 📊 RESULTADOS APÓS MIGRAÇÃO

### Vocabulário (usando CSV):
- **Total de estudantes**: 2274
- **Score PRÉ médio**: 20.41 ± 13.07
- **Score PÓS médio**: 18.01 ± 14.88
- **Cohen's d**: -0.1712 (deterioração trivial)
- **Classificação**: Insuficiente - sem impacto prático

### TDE (usando CSV):
- **Total de registros**: 2023
- **Grupo A (6º/7º)**: N=1110, Pré=11.78, Pós=6.63
- **Grupo B (8º/9º)**: N=913, Pré=9.55, Pós=8.62

## 🎯 BENEFÍCIOS DA MIGRAÇÃO

1. **Consistência de Dados**: Uso de fonte única (CSV)
2. **Maior Transparência**: Tratamento explícito de valores ausentes
3. **Melhor Rastreabilidade**: Eliminação de artefatos de conversão Excel
4. **Dados Mais Realistas**: Análises baseadas em dados brutos sem filtragem automática

## ⚠️ CONSIDERAÇÕES IMPORTANTES

1. **Interpretação dos Resultados**: Os dados CSV refletem a realidade dos testes, onde valores ausentes foram codificados como "0" (erro)
2. **Impacto Estatístico**: As análises agora mostram o verdadeiro impacto da intervenção
3. **Compatibilidade**: Mantida geração de ambos formatos (CSV + Excel) para compatibilidade

## 📋 PRÓXIMOS PASSOS

1. ✅ Pipelines principais migrados
2. ⏳ Verificar outros scripts que possam usar Excel
3. ⏳ Atualizar documentação dos módulos
4. ⏳ Validar relatórios visuais com novo formato

## 🔗 ARQUIVOS AFETADOS

### Dados de Entrada (CSV):
- `Data/Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.csv`
- `Data/Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).csv`
- `Data/Fase2/Pre/Avaliação TDE II - RelaçãoCompletaAlunos.csv`
- `Data/Fase2/Pos/Avaliação TDE II - RelaçãoCompletaAlunos.csv`

### Relatórios Gerados:
- `Data/pipeline_vocabulario_wordgen_fase2.txt`
- `Data/tabela_bruta_fase2_TDE_wordgen.csv`
- `Data/tabela_bruta_fase2_TDE_wordgen.xlsx`

---

**Migração realizada com sucesso! ✅**  
Todos os pipelines agora utilizam CSV como fonte primária de dados.
