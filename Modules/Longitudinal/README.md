# Análise Longitudinal WordGen - Fases 2, 3 e 4

Este módulo realiza análise longitudinal dos dados do projeto WordGen, consolidando informações das Fases 2, 3 e 4 para TDE (Teste de Escrita) e Vocabulário.

## 🎯 Objetivo

Realizar análise longitudinal focada em:
- **Resumo demográfico geral** (número de participantes, escolas, perfil por gênero)
- **Número de acertos e melhorias** por escola e turma
- **Relatório visual HTML** seguindo o mesmo padrão das Fases 2 e 3
- **Foco em progressos positivos** (não evidenciando erros)

## 📁 Estrutura do Módulo

```
Modules/Longitudinal/
├── TDE/
│   └── PipelineDataLongitudinalTDE.py      # Pipeline de dados TDE
├── Vocabulario/
│   └── PipelineDataLongitudinalVocabulario.py  # Pipeline de dados Vocabulário
├── RelatorioVisualLongitudinal.py         # Gerador do relatório HTML
├── PipelinePrincipalLongitudinal.py       # Executor principal
└── Data/                                  # Dados e resultados gerados
    ├── dados_longitudinais_TDE.csv
    ├── dados_longitudinais_Vocabulario.csv
    ├── resumo_longitudinal_TDE.json
    ├── resumo_longitudinal_Vocabulario.json
    ├── relatorio_visual_longitudinal.html
    └── figures/                           # Gráficos gerados
```

## 🚀 Como Executar

### Execução Completa (Recomendado)
```bash
cd /caminho/para/AnaliseDadosWordGeneration
python Modules/Longitudinal/PipelinePrincipalLongitudinal.py
```

### Execução por Etapas
```bash
# 1. Pipeline TDE
python Modules/Longitudinal/TDE/PipelineDataLongitudinalTDE.py

# 2. Pipeline Vocabulário  
python Modules/Longitudinal/Vocabulario/PipelineDataLongitudinalVocabulario.py

# 3. Relatório Visual
python Modules/Longitudinal/RelatorioVisualLongitudinal.py
```

## 📊 Dados de Entrada

O módulo utiliza dados das seguintes pastas:
- `Data/Fase 2/Pre/` e `Data/Fase 2/Pos/`
- `Data/Fase 3/Pre/` e `Data/Fase 3/Pos/`
- `Data/Fase 4/Pre/` e `Data/Fase 4/Pos/`

### Arquivos necessários:
- `DadosTDE.csv` (pré e pós teste)
- `DadosVocabulario.csv` (pré e pós teste)

## 📈 Análises Realizadas

### 1. Resumo Demográfico
- Número total de participantes por fase
- Distribuição por escolas participantes
- Perfil de gênero (% meninos e meninas)
- Número de turmas envolvidas

### 2. Performance Longitudinal
- **Taxa de melhoria** por fase, escola e turma
- **Scores médios** pré e pós teste
- **Delta de melhorias** (pós - pré)
- **Evolução temporal** entre fases

### 3. Análise por Escola
- Ranking de performance por instituição
- Comparativo de melhorias entre escolas
- Identificação de melhores práticas

### 4. Visualizações Geradas
- Gráficos demográficos
- Evolução por fases
- Performance por escola
- Mapas de calor (heatmaps)
- Distribuição de melhorias

## 📋 Outputs Gerados

### 1. Arquivos CSV
- **`dados_longitudinais_TDE.csv`**: Dados consolidados TDE
- **`dados_longitudinais_Vocabulario.csv`**: Dados consolidados Vocabulário

### 2. Resumos JSON
- **`resumo_longitudinal_TDE.json`**: Estatísticas detalhadas TDE
- **`resumo_longitudinal_Vocabulario.json`**: Estatísticas detalhadas Vocabulário

### 3. Relatório HTML
- **`relatorio_visual_longitudinal.html`**: Relatório interativo completo

## 🎨 Padrão Visual

O relatório segue **exatamente o mesmo padrão visual** das Fases 2 e 3:
- Cores e tema consistentes
- Layout responsivo
- Gráficos interativos
- Cards informativos
- Estrutura hierárquica clara

## 📌 Características Especiais

### ✅ Foco Positivo
- Ênfase em **acertos e melhorias**
- **Não evidencia erros** ou falhas
- Destaque para progressos e sucessos

### 📊 Métricas Principais
- **Taxa de Melhoria**: % de estudantes que melhoraram
- **Delta Médio**: Diferença média entre pós e pré teste
- **Score Médio**: Pontuação média por fase
- **Distribuição Demográfica**: Perfil dos participantes

### 🔄 Continuidade Visual
- Mantém identidade visual das outras fases
- Usa mesma paleta de cores
- Estrutura HTML consistente
- Responsividade mantida

## 🛠️ Requisitos Técnicos

### Dependências Python
```
pandas
numpy
matplotlib
seaborn
scipy
pathlib
json
datetime
```

### Estrutura de Dados Esperada
- Colunas TDE: P1, P2, ..., P40 (questões)
- Colunas Vocabulário: Q1, Q2, ..., Q50 (questões)
- Metadados: Escola, Turma, Nome, Sexo, Idade

## 🔍 Tratamento de Erros

O pipeline é robusto e trata:
- **Dados faltantes**: Ignora registros incompletos
- **Formatos diferentes**: Adapta-se às variações da Fase 4
- **Correspondências**: Vincula pré e pós testes por nome/escola
- **Valores inválidos**: Filtra dados inconsistentes

## 📱 Como Visualizar os Resultados

1. **Abra o arquivo HTML** no navegador:
   ```
   file:///caminho/para/relatorio_visual_longitudinal.html
   ```

2. **Navegue pelas seções**:
   - Resumo Executivo
   - Perfil Demográfico  
   - Evolução por Fases
   - Performance por Escola
   - Mapa de Calor
   - Estatísticas Detalhadas

3. **Interprete os gráficos**:
   - Verde = Melhorias
   - Azul = Estabilidade
   - Vermelho = Oportunidades

## 📞 Suporte

Para questões ou problemas:
1. Verifique se todos os arquivos de dados estão presentes
2. Confirme que o ambiente Python está configurado
3. Execute o pipeline completo para garantir consistência
4. Consulte os logs de execução para detalhes de erros

---

**WordGen - Sistema de Análise Longitudinal**  
*Versão 1.0 - Setembro 2024*
