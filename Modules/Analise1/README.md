# Análise de Desempenho Agregado - WordGen

## Resumo da Análise

Este diretório contém análises agregadas detalhadas do desempenho em **TDE (Teste de Desempenho Escolar)** e **Vocabulário** considerando:

- **Fase 2**: Realizada em 2023
- **Fases 3 e 4**: Realizadas em 2024
- **Agregação multidimensional**: por ano escolar, fase, ano calendário e cruzamentos

## Principais Achados

### 📊 Desempenho Geral por Ano

**2023 (Fase 2):**
- **TDE**: Declínio significativo (d = -0.227, efeito pequeno negativo)
  - Pré-teste: 18.82 pontos → Pós-teste: 15.38 pontos
  - Delta médio: -3.44 pontos
- **Vocabulário**: Declínio leve (d = -0.169, efeito trivial negativo)
  - Pré-teste: 20.45 pontos → Pós-teste: 18.07 pontos  
  - Delta médio: -2.37 pontos

**2024 (Fases 3-4):**
- **TDE**: Melhoria leve (d = 0.059, efeito trivial positivo)
  - Pré-teste: 26.50 pontos → Pós-teste: 27.22 pontos
  - Delta médio: +0.72 pontos
- **Vocabulário**: Melhoria leve (d = 0.057, efeito trivial positivo)
  - Pré-teste: 21.28 pontos → Pós-teste: 21.77 pontos
  - Delta médio: +0.49 pontos

### 🎯 Padrões Detalhados por Ano Escolar (2023 vs 2024)

**Análise Geral (Todas as Fases):**
- **TDE**: 4.573 participantes, d = -0.092 (declínio trivial)
  - Melhoria: 29.8% | Declínio: 33.4% | Estável: 36.8%
- **Vocabulário**: 4.393 participantes, d = -0.084 (declínio trivial)
  - Melhoria: 44.5% | Declínio: 41.0% | Estável: 14.4%

**🏆 Melhores Desempenhos:**
- **TDE**: 2024 - 9º Ano (d = 0.100), 2024 - 7º Ano (d = 0.082)
- **Vocabulário**: Fase 4 (d = 0.089), 2024 - 6º Ano (d = 0.086)

**⚠️ Desempenhos Mais Preocupantes:**
- **TDE**: 2023 - 6º Ano (d = -0.443), 2023 - 7º Ano (d = -0.348)
- **Vocabulário**: 2023 - 8º Ano (d = -0.213), 2023 - 9º Ano (d = -0.171)

### 📈 Interpretação dos Resultados

1. **Contraste entre anos**: Houve uma **reversão de tendência** entre 2023 e 2024
   - 2023: Declínios em ambas as provas
   - 2024: Melhorias modestas em ambas as provas

2. **Magnitude dos efeitos**: Todos os efeitos são de pequena magnitude ou triviais
   - Nenhum atinge os benchmarks educacionais (TDE: d ≥ 0.40, Vocabulário: d ≥ 0.35)

3. **Padrão diferencial por série**: Os anos iniciais (6º-7º) foram mais afetados negativamente em 2023

## 📁 Arquivos Gerados

### Scripts de Análise
- **`gerar_relatorio_desempenho_agregado.py`**: Análise básica por ano e fase
- **`gerar_relatorio_expandido.py`**: Análise multidimensional completa (8 dimensões)
- **`gerar_resumo_executivo.py`**: Resumo visual com tabelas e insights estratégicos

### Relatórios TXT
- **`relatorio_desempenho_agregado_[timestamp].txt`**: Relatório básico (7.4 KB)
- **`relatorio_desempenho_expandido_[timestamp].txt`**: Relatório detalhado multidimensional (32.3 KB)  
- **`resumo_executivo_visual_[timestamp].txt`**: Tabela consolidada com insights (7.6 KB)
- **`README.md`**: Este resumo executivo

### Dimensões de Análise no Relatório Expandido
1. **Análise Geral**: Todas as fases consolidadas
2. **Por Ano Calendário**: 2023 vs 2024
3. **Por Fase**: Fases 2, 3 e 4 individualmente
4. **Por Ano de Turma**: 6º ao 9º ano
5. **Cruzamento Ano × Fase**: Combinações ano-fase
6. **Cruzamento Ano × Turma**: Performance por ano de turma em cada ano calendário
7. **Cruzamento Fase × Turma**: Performance por turma em cada fase
8. **Análise Tripla**: Ano × Fase × Turma (grupos com n ≥ 10)

### 🏆 Principais Descobertas

**Reversão de Tendência Positiva:**
- **TDE**: Melhoria de +0.287 pontos de efeito (de d=-0.227 para d=+0.059)
- **Vocabulário**: Melhoria de +0.227 pontos de efeito (de d=-0.169 para d=+0.057)

**Atingimento de Benchmarks:**
- **Nenhum grupo** atingiu os benchmarks educacionais estabelecidos
- TDE: 0/18 grupos ≥ 0.40 (0%)
- Vocabulário: 0/18 grupos ≥ 0.35 (0%)

**Distribuição de Resultados:**
- TDE: 29.8% melhoria | 33.4% declínio | 36.8% estável
- Vocabulário: 44.5% melhoria | 41.0% declínio | 14.4% estável

## 🔍 Recomendações Estratégicas

### 📈 Curto Prazo
1. **Focar intervenções** nos grupos 6º e 7º anos (maior declínio em 2023)
2. **Replicar estratégias** bem-sucedidas de 2024 (reversão positiva)
3. **Investigar fatores** específicos do 8º ano em Vocabulário (declínio persistente)

### 🔬 Médio Prazo
4. **Análise qualitativa** dos fatores de melhoria entre 2023-2024
5. **Estudo de caso** das escolas com melhor desempenho
6. **Desenvolver intervenções** específicas por ano escolar

### 📊 Longo Prazo
7. **Sistema de alerta precoce** para grupos de risco
8. **Benchmarks adaptativos** por contexto escolar
9. **Análise longitudinal individual** para trajetórias de aprendizagem

---
*Gerado automaticamente pelo Sistema de Análise WordGen*