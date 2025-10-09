# 📚 Conceito de Coortes - Explicação Corrigida

## 🎯 Definição Correta

**Coortes no contexto do programa WordGen representam grupos de alunos baseados na FASE em que iniciaram o programa, NÃO no ano calendário.**

---

## ✅ Conceito Correto

### **Coorte 1: Iniciaram na Fase 2**
- Primeira fase de avaliação do programa
- Trajetória **completa**: têm dados nas Fases 2, 3 e 4
- Maior tempo de exposição ao WordGen
- Exemplo: Aluno que entrou na Fase 2 e foi acompanhado até a Fase 4

### **Coorte 2: Iniciaram na Fase 3**
- Entraram no meio do estudo longitudinal
- Trajetória **parcial**: têm dados nas Fases 3 e 4
- Tempo médio de exposição ao WordGen
- Exemplo: Aluno que entrou na Fase 3 e foi acompanhado até a Fase 4

### **Coorte 3: Iniciaram na Fase 4**
- Última fase de entrada no programa
- Trajetória **inicial**: têm dados apenas na Fase 4
- Menor tempo de exposição ao WordGen
- Exemplo: Aluno que entrou apenas na Fase 4 (snapshot)

---

## 🔄 Correção Aplicada

### ❌ Versão INCORRETA (anterior)
```
Coortes representam grupos de alunos que iniciaram o programa em anos diferentes:
- Coorte 1: Alunos que iniciaram em 2022
- Coorte 2: Alunos que iniciaram em 2023
- Coorte 3: Alunos que iniciaram em 2024
```

### ✅ Versão CORRETA (atual)
```
Coortes representam grupos de alunos baseados na fase em que iniciaram o programa:
- Coorte 1: Alunos que começaram na Fase 2
- Coorte 2: Alunos que começaram na Fase 3
- Coorte 3: Alunos que começaram na Fase 4
```

---

## 💡 Por Que Essa Distinção É Importante?

### **1. Controle do Tempo de Exposição**
Analisar por coorte permite controlar o **efeito do tempo de programa**:
- Coorte 1: 3 fases de intervenção
- Coorte 2: 2 fases de intervenção
- Coorte 3: 1 fase (baseline ou controle)

### **2. Comparação Justa**
Comparar alunos que **iniciaram no mesmo ponto**:
- Evita viés de tempo de exposição
- Permite avaliar progresso relativo
- Facilita identificação de efeitos do programa

### **3. Análise Longitudinal Correta**
Entender a **trajetória** de cada grupo:
- Coorte 1: Evolução completa (2→3→4)
- Coorte 2: Evolução parcial (3→4)
- Coorte 3: Ponto inicial (4)

---

## 📊 Exemplos Práticos

### **Exemplo 1: Análise de Progresso**
**Pergunta**: Qual coorte teve maior ganho?

**Análise Correta**:
- Coorte 1: Comparar Fase 2 → Fase 4 (ganho total)
- Coorte 2: Comparar Fase 3 → Fase 4 (ganho parcial)
- Coorte 3: Apenas Fase 4 (não há ganho, apenas baseline)

**Conclusão**: Não podemos comparar ganhos diretamente entre coortes, pois têm trajetórias diferentes!

---

### **Exemplo 2: Identificação de Alunos em Risco**
**Pergunta**: Quais alunos estão abaixo da média na última fase?

**Análise Correta**:
- Filtrar por **Coorte 1** → Ver alunos com trajetória completa
- Identificar os que **não evoluíram** entre Fase 2 e 4
- Priorizar intervenção nesses casos

**Por quê?**: Coorte 1 tem contexto completo, permitindo avaliar se há problema de aprendizado ou apenas efeito de entrada tardia.

---

### **Exemplo 3: Comparação de Escolas**
**Pergunta**: Qual escola tem melhor desempenho?

**Análise Correta**:
- Filtrar por **Coorte 1** (trajetória completa)
- Comparar evolução das escolas na mesma coorte
- Evitar comparar escolas com composições de coorte diferentes

**Por quê?**: Escolas podem ter proporções diferentes de Coorte 1/2/3, afetando médias.

---

## 🔍 Dicas de Uso no Dashboard

### **Quando usar "Todas as Coortes":**
- Visão geral do programa
- Entender distribuição de alunos por fase inicial
- Identificar padrões gerais

### **Quando usar Coorte 1:**
- Análise de **evolução longitudinal completa**
- Avaliar **impacto total** do programa
- Estudos de **trajetória** individual

### **Quando usar Coorte 2:**
- Análise de **impacto parcial**
- Comparar com Coorte 1 para validar resultados
- Entender efeito de **entrada tardia**

### **Quando usar Coorte 3:**
- Baseline do programa
- Ponto de comparação inicial
- Identificar **efeito de seleção** (alunos que entraram apenas na última fase)

---

## 📋 Checklist de Validação

- [x] Informativo corrigido no código (`app.py`)
- [x] Help do seletor atualizado
- [x] Documentação técnica corrigida (`AJUSTES_DRILL_DOWN_V2.1.md`)
- [x] Guia rápido atualizado (`INDEX_DRILL_DOWN.md`)
- [x] Resumo executivo corrigido (`RESUMO_AJUSTES_V2.1.md`)
- [x] Documento explicativo criado (`CONCEITO_COORTES.md`)

---

## 🎓 Referências Metodológicas

### **Coortes em Estudos Longitudinais:**
Em pesquisas educacionais, **coortes** geralmente se referem a:
1. **Grupos de entrada**: Quando os participantes iniciaram o estudo
2. **Grupos de idade**: Nascidos no mesmo período (não é o caso aqui)
3. **Grupos de tratamento**: Quando receberam a intervenção

No caso do WordGen, usamos **coortes de entrada**, baseadas na **fase inicial**.

### **Por Que Não Usar Ano Calendário:**
- Alunos da mesma escola podem ter entrado em fases diferentes
- O ano calendário não reflete tempo de exposição ao programa
- A fase inicial é o marcador mais relevante para análises longitudinais

---

## 🚀 Impacto da Correção

### **Antes (Incorreto):**
- Usuários confundiam coorte com ano de entrada
- Análises consideravam tempo cronológico, não tempo de programa
- Comparações entre coortes eram enganosas

### **Agora (Correto):**
- Definição clara: coorte = fase inicial
- Análises consideram tempo de exposição ao programa
- Comparações entre coortes são informadas e apropriadas
- Usuários tomam decisões metodologicamente corretas

---

**Data da Correção**: Janeiro 2024  
**Versão**: 2.1.1  
**Status**: ✅ CORRIGIDO E VALIDADO

---
