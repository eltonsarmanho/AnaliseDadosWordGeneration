# 📚 Índice da Documentação - Sistema de Coortes

Este índice organiza toda a documentação relacionada ao sistema de coortes do Dashboard WordGen.

---

## 🎯 Para Iniciantes

**Comece aqui se você é novo no projeto:**

1. **[GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md)** ⭐ **RECOMENDADO**
   - Visão geral em 5 minutos
   - O que é e como funciona
   - Como validar rapidamente
   - Troubleshooting comum

2. **[CONCEITO_COORTES.md](./CONCEITO_COORTES.md)**
   - Definição pedagógica de coortes
   - Por que usar coortes em estudos longitudinais
   - Exemplos práticos

---

## 🔧 Para Desenvolvedores

**Documentação técnica e implementação:**

1. **[VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md)** ⭐ **COMPLETO**
   - Documentação técnica completa
   - Todos os testes executados
   - Métricas de validação
   - Casos de uso validados
   - Como manter o sistema

2. **[CORRECAO_CONCEITO_COORTES.md](./CORRECAO_CONCEITO_COORTES.md)**
   - Histórico da correção (ano → fase)
   - Motivação para a mudança
   - Impactos da correção

---

## 🧪 Para Testes e Validação

**Garantindo qualidade do sistema:**

1. **`/Dashboard/test_coorte.py`** ⭐ **EXECUTE REGULARMENTE**
   - Suite de 6 testes automatizados
   - Valida toda a implementação
   - Como executar:
     ```bash
     cd Dashboard
     python test_coorte.py
     ```

2. **[VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md)** (Seção "Validação e Testes")
   - Resultados dos testes
   - Interpretação dos resultados
   - O que fazer se falhar

---

## 📊 Para Pesquisadores/Analistas

**Como usar coortes para análise de dados:**

1. **[GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md)** (Seção "Uso Pedagógico")
   - Perguntas que o sistema responde
   - Boas práticas de análise
   - Cuidados metodológicos

2. **[CONCEITO_COORTES.md](./CONCEITO_COORTES.md)**
   - Fundamentação teórica
   - Quando usar cada coorte
   - Limitações e vieses

---

## 🏗️ Arquitetura e Código

**Estrutura técnica do sistema:**

### Arquivos de Código

| Arquivo | Linha Chave | Função |
|---------|-------------|--------|
| `/Dashboard/data_loader.py` | 70-120 | `create_coorte_origem()` - Cria coluna de coorte |
| `/Dashboard/app.py` | 455-470 | Aplica filtro de coorte |
| `/Dashboard/app.py` | 409-431 | Expander explicativo sobre coortes |
| `/Dashboard/app.py` | 437-442 | Seletor de coorte (UI) |

### Fluxo de Dados

```
1. CSV carregado (TDE_longitudinal.csv, vocabulario_longitudinal.csv)
   ↓
2. data_loader.get_datasets()
   ↓
3. create_coorte_origem(df)
   - Identifica menor fase por ID_Unico
   - Mapeia fase → coorte (2→1, 3→2, 4→3)
   - Cria coluna Coorte_Origem
   ↓
4. app.py carrega dados com cache
   ↓
5. Usuário seleciona coorte no dashboard
   ↓
6. Filtro aplicado em df_drill_base
   ↓
7. Estatísticas calculadas e exibidas
```

---

## 📈 Histórico de Mudanças

### Principais Marcos

1. **Implementação Inicial**
   - Conceito de coorte baseado em **ano** (ex: 2023, 2024)
   - Problemas: não acompanhava trajetória individual

2. **Correção 1: Ano → Fase**
   - Mudança para **fase inicial** (Fase 2, 3, 4)
   - Doc: [CORRECAO_CONCEITO_COORTES.md](./CORRECAO_CONCEITO_COORTES.md)

3. **Correção 2: Turma → ID_Unico**
   - Rastreamento por **ID_Unico** (não turma)
   - Garante consistência longitudinal
   - Doc: [VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md)

4. **Validação Completa**
   - 6 testes automatizados
   - 100% de sucesso
   - Sistema em produção ✅

---

## 🔍 Documentação Relacionada

### Drill-Down e Interface

- **[INDEX_DRILL_DOWN.md](./INDEX_DRILL_DOWN.md)**
  - Visão geral do sistema de drill-down
  - Como o filtro de coorte se integra

- **[DRILL_DOWN_DOCUMENTATION.md](./DRILL_DOWN_DOCUMENTATION.md)**
  - Documentação técnica do drill-down
  - Ordem de aplicação de filtros

### Anonimização (LGPD)

- **[INDEX_ANONIMIZACAO.md](./INDEX_ANONIMIZACAO.md)**
  - Como IDs são anonimizados
  - Rastreamento longitudinal com LGPD

### Visualizações

- **[MELHORIA_BOXPLOT_MEDIA.md](./MELHORIA_BOXPLOT_MEDIA.md)**
  - Como boxplots são usados com coortes
  
- **[PROPOSTA_PARALLEL_COORDINATES.md](./PROPOSTA_PARALLEL_COORDINATES.md)**
  - Visualização alternativa de trajetórias por coorte

---

## 🎯 Casos de Uso Documentados

### 1. Validação Inicial
- **Documento:** [VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md) (Seção "Casos de Uso Validados")
- **Testes:** Caso 1, 2, 3, 4

### 2. Análise Longitudinal
- **Documento:** [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (Seção "Uso Pedagógico")
- **Pergunta:** "Quantos alunos completaram o programa desde o início?"

### 3. Comparação de Desempenho
- **Documento:** [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (Seção "Uso Pedagógico")
- **Pergunta:** "Qual coorte teve melhor desempenho?"

### 4. Análise de Retenção
- **Documento:** [VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md) (Teste 6)
- **Métrica:** ~45% dos alunos Coorte 1 têm dados em múltiplas fases

---

## 📞 FAQ Rápido

### "Como sei se o sistema está funcionando?"
→ Execute `python test_coorte.py` → Todos devem passar ✅

### "Por que o filtro não funciona?"
→ Veja [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (Seção "Troubleshooting")

### "Como interpretar os resultados?"
→ Veja [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (Seção "Uso Pedagógico")

### "Onde está o código?"
→ Veja tabela "Arquivos de Código" acima

### "Como validar após mudanças?"
→ Veja [VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md) (Seção "Manutenção e Debug")

---

## 📊 Estatísticas do Sistema

**Última validação:** 2024

| Métrica | Valor |
|---------|-------|
| Testes executados | 6/6 ✅ |
| Taxa de sucesso | 100% |
| Alunos TDE | 2.737 |
| Alunos Vocabulário | 2.828 |
| Coorte 1 (TDE) | 2.231 (81.5%) |
| Coorte 2 (TDE) | 448 (16.4%) |
| Coorte 3 (TDE) | 58 (2.1%) |
| Alunos com dados longitudinais | ~45% (Coorte 1) |

---

## 🚀 Início Rápido

**Para começar a usar:**

1. Leia [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (5 min)
2. Execute `python test_coorte.py` (1 min)
3. Abra o dashboard e teste o filtro de coorte (2 min)
4. ✅ Pronto! Sistema validado

**Para análise avançada:**

1. Leia [VALIDACAO_FINAL_COORTES.md](./VALIDACAO_FINAL_COORTES.md) (10 min)
2. Revise [CONCEITO_COORTES.md](./CONCEITO_COORTES.md) (5 min)
3. Explore casos de uso em [GUIA_RAPIDO_COORTES.md](./GUIA_RAPIDO_COORTES.md) (5 min)

---

## 🔄 Manutenção

**Cronograma sugerido:**

- **Diário:** Nenhuma ação necessária (sistema automático)
- **Após novos dados:** Executar `test_coorte.py`
- **Mensal:** Revisar estatísticas de distribuição
- **Trimestral:** Validar casos de uso com stakeholders
- **Anual:** Revisar documentação e atualizar se necessário

---

**Mantido por:** Equipe WordGen  
**Última atualização:** 2024  
**Status:** ✅ Sistema validado e em produção
