Vou explicar detalhadamente cada etapa da análise estatística implementada:

## 1. **TESTE DE NORMALIDADE (Shapiro-Wilk)**

```python
stat_pre, p_pre = stats.shapiro(acertos_pre)
stat_pos, p_pos = stats.shapiro(acertos_pos)
```

**O que faz:**
- Testa se os dados seguem uma distribuição normal
- **H₀**: Os dados seguem distribuição normal
- **H₁**: Os dados NÃO seguem distribuição normal

**Interpretação:**
- Se **p-value > 0.05**: Dados são normais ✓
- Se **p-value ≤ 0.05**: Dados NÃO são normais ✗

**Por que é importante:**
- Determina qual teste estatístico usar posteriormente
- Dados normais → Teste t pareado
- Dados não-normais → Teste Wilcoxon

---

## 2. **TESTES PARA VERIFICAR MELHORA**

### **Teste t Pareado (para dados normais)**
```python
t_stat, p_value = stats.ttest_rel(acertos_pos, acertos_pre)
```

**O que faz:**
- Compara as médias de dois grupos relacionados (mesmo participante antes e depois)
- **H₀**: Não há diferença entre pré e pós (média_pós = média_pré)
- **H₁**: Há diferença entre pré e pós (média_pós ≠ média_pré)

### **Teste Wilcoxon (para dados não-normais)**
```python
w_stat, p_value = stats.wilcoxon(acertos_pos, acertos_pre, alternative='greater')
```

**O que faz:**
- Versão não-paramétrica do teste t pareado
- Compara medianas em vez de médias
- `alternative='greater'` testa se pós > pré

**Interpretação de ambos:**
- Se **p-value < 0.05**: Há melhora estatisticamente significativa ✓
- Se **p-value ≥ 0.05**: NÃO há melhora estatisticamente significativa ✗

---

## 3. **TAMANHO DO EFEITO (Cohen's d)**

```python
diferenca = acertos_pos - acertos_pre
cohen_d = diferenca.mean() / diferenca.std()
```

**O que mede:**
- A **magnitude prática** da melhora (não apenas se é significativa)
- Quantifica "o quão grande" é a diferença

**Interpretação:**
- **|d| < 0.2**: Efeito pequeno
- **0.2 ≤ |d| < 0.5**: Efeito médio  
- **0.5 ≤ |d| < 0.8**: Efeito grande
- **|d| ≥ 0.8**: Efeito muito grande

**Exemplo prático:**
- p-value = 0.001 (significativo) + Cohen's d = 0.1 → Melhora estatisticamente significativa mas **praticamente irrelevante**
- p-value = 0.001 + Cohen's d = 0.8 → Melhora significativa e **praticamente importante**

---

## 4. **ANÁLISE INDIVIDUAL DE MUDANÇA**

```python
melhoraram = (acertos_pos > acertos_pre).sum()
pioraram = (acertos_pos < acertos_pre).sum()
mantiveram = (acertos_pos == acertos_pre).sum()
```

**O que mostra:**
- **Quantos participantes** individualmente melhoraram, pioraram ou mantiveram
- **Porcentagem** de cada categoria

**Utilidade:**
- Complementa a análise de médias
- Pode revelar padrões como:
  - "A média melhorou, mas 40% dos alunos pioraram"
  - "70% dos alunos melhoraram consistentemente"

---

## 5. **ANÁLISE POR PERGUNTA**

```python
melhora_por_pergunta = df_pos_bool.mean() - df_pre_bool.mean()
melhora_por_pergunta_sorted = melhora_por_pergunta.sort_values(ascending=False)
```

**O que faz:**
- Calcula a melhora em cada pergunta específica (P1, P2, ..., P40)
- Ordena da maior para menor melhora

**Interpretação:**
- **Valores positivos**: Pergunta teve melhora (mais acertos no pós-teste)
- **Valores negativos**: Pergunta teve piora (menos acertos no pós-teste)
- **Valores próximos de zero**: Pouca mudança

**Utilidade pedagógica:**
- Identifica **quais conteúdos** a intervenção foi mais eficaz
- Mostra **áreas que precisam de reforço** (perguntas que não melhoraram)
- Permite **ajustes futuros** na intervenção

---

## **EXEMPLO DE INTERPRETAÇÃO COMPLETA:**

```
Teste de Normalidade:
PRÉ - Shapiro-Wilk: p-value = 0.0234  → Não normal
PÓS - Shapiro-Wilk: p-value = 0.0156  → Não normal

Teste Wilcoxon: p-value = 0.0034  → Melhora significativa ✓

Tamanho do Efeito (Cohen's d): 0.67  → Efeito grande

Análise Individual:
- 85% melhoraram
- 10% pioraram  
- 5% mantiveram

Top 3 perguntas com maior melhora:
1. P15: +0.45 (45% mais acertos)
2. P23: +0.38 (38% mais acertos)
3. P07: +0.33 (33% mais acertos)
```

**Conclusão:** A intervenção foi **estatisticamente significativa** e **praticamente relevante**, com melhora substancial na maioria dos participantes, especialmente nas habilidades avaliadas pelas perguntas P15, P23 e P07.