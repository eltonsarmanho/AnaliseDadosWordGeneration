# 🎯 Guia Rápido: Sistema de Coortes - WordGen Dashboard

## O que é?

Um **sistema de rastreamento longitudinal** que agrupa alunos pela **fase em que entraram no programa WordGen**.

---

## 📊 3 Coortes Principais

| Coorte | Entrada | Trajetória Possível | Alunos (TDE) | Alunos (Vocab) |
|--------|---------|---------------------|--------------|----------------|
| **Coorte 1** | Fase 2 | Fases 2 → 3 → 4 | 2.231 (81.5%) | 2.237 (79.1%) |
| **Coorte 2** | Fase 3 | Fases 3 → 4 | 448 (16.4%) | 337 (11.9%) |
| **Coorte 3** | Fase 4 | Fase 4 apenas | 58 (2.1%) | 254 (9.0%) |

---

## 🔑 Conceito Chave

**IMPORTANTE:** A coorte é determinada pela **primeira fase** em que o aluno aparece nos dados, independentemente de mudanças de turma.

### Exemplo:
- **João** aparece pela primeira vez na **Fase 2** (Turma A)
- Na **Fase 3**, João muda para **Turma B**
- **João sempre será "Coorte 1"**, mesmo mudando de turma

---

## 🛠️ Como Funciona Tecnicamente

### 1. Criação da Coluna (`data_loader.py`)

```python
def create_coorte_origem(df):
    # 1. Encontrar menor fase por ID_Unico
    primeira_fase = df.groupby('ID_Unico')['Fase'].min()
    
    # 2. Mapear fase → coorte
    # Fase 2 → Coorte 1
    # Fase 3 → Coorte 2
    # Fase 4 → Coorte 3
    
    # 3. Aplicar para TODOS os registros do aluno
    df['Coorte_Origem'] = ...
```

### 2. Aplicação do Filtro (`app.py`)

```python
# Usuário seleciona coorte
if coorte_drill != 'Todas':
    # Filtrar dados
    df_drill_base = df_drill_base[df_drill_base['Coorte_Origem'] == coorte_drill]
    
    # Calcular estatísticas (número de alunos únicos afetados)
    n_alunos = df_drill_filtrado['ID_Anonimizado'].nunique()
```

---

## ✅ Como Validar

### Teste Rápido (Terminal)

```bash
cd Dashboard
python test_coorte.py
```

**Resultado esperado:**
```
✅ TODOS OS TESTES CONCLUÍDOS
```

### Teste Manual (Dashboard)

1. Abrir dashboard
2. Ir para "Evolução Comparativa Hierárquica"
3. Selecionar "Coorte 1"
4. Verificar se o card mostra **~2.200 alunos** (TDE)
5. Mudar para "Todas"
6. Verificar se o card mostra **~2.700 alunos** (TDE)

Se os números mudarem → ✅ **Funcionando!**

---

## 🐛 Troubleshooting

### Problema: Filtro não funciona

**Sintomas:**
- Seletor de coorte não muda o número de alunos
- Card sempre mostra o mesmo valor

**Solução:**
1. Verificar se warning aparece (coluna não encontrada)
2. Inspecionar dataframe:
   ```python
   from data_loader import get_datasets
   tde, _ = get_datasets()
   print('Coorte_Origem' in tde.columns)  # Deve ser True
   print(tde['Coorte_Origem'].unique())   # Deve mostrar ['Coorte 1', 'Coorte 2', 'Coorte 3']
   ```

### Problema: Aluno em múltiplas coortes

**Sintomas:**
- Mesmo ID_Unico aparece em diferentes coortes
- Teste 3 de `test_coorte.py` falha

**Solução:**
1. Verificar se `create_coorte_origem` foi modificada
2. Recarregar dados (limpar cache):
   ```python
   import streamlit as st
   st.cache_data.clear()
   ```

### Problema: Coorte incorreta para a fase

**Sintomas:**
- Aluno que começou na Fase 2 está como "Coorte 2"
- Teste 4 de `test_coorte.py` falha

**Solução:**
1. Verificar mapeamento em `create_coorte_origem`:
   ```python
   # Deve ser:
   Fase 2 → Coorte 1
   Fase 3 → Coorte 2
   Fase 4 → Coorte 3
   ```
2. Reprocessar dados se necessário

---

## 📚 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `data_loader.py` | Cria coluna `Coorte_Origem` |
| `app.py` | Aplica filtro de coorte |
| `test_coorte.py` | Valida implementação |
| `VALIDACAO_FINAL_COORTES.md` | Documentação completa |
| Este arquivo | Referência rápida |

---

## 🔄 Manutenção

### Quando Revalidar

- ✅ Após adicionar novos dados
- ✅ Após modificar `create_coorte_origem`
- ✅ Após mudanças na estrutura de dados
- ✅ Mensalmente (rotina)

### Como Revalidar

```bash
# 1. Executar testes
cd Dashboard
python test_coorte.py

# 2. Se todos passarem ✅ → OK
# 3. Se algum falhar ❌ → Investigar

# 4. Verificar distribuição
python -c "
from data_loader import get_datasets
tde, _ = get_datasets()
print(tde.groupby('Coorte_Origem')['ID_Unico'].nunique())
"
```

---

## 📈 Uso Pedagógico

### Perguntas que o Sistema Responde

1. **"Quantos alunos completaram o programa desde o início?"**
   - Selecionar Coorte 1 + Fase 4
   - Ver quantos alunos permanecem

2. **"Qual coorte teve melhor desempenho?"**
   - Comparar médias de Score_Pos entre coortes
   - Usar drill-down para detalhar por escola/turma

3. **"Houve efeito de maturação?"**
   - Comparar Coorte 1 (Fase 2) vs Coorte 2 (Fase 3) na mesma fase
   - Controlar efeito de idade/exposição prévia

4. **"Qual a taxa de retenção do programa?"**
   - Contar alunos Coorte 1 em Fase 2 vs Fase 4
   - Identificar dropout

---

## 💡 Dicas de Análise

### ✅ Boas Práticas

- **Compare coortes na mesma fase** para isolar efeito do programa
- **Use Coorte 1 para análise longitudinal completa**
- **Combine filtros** (coorte + escola + turma) para análise granular
- **Documente decisões** de exclusão de coortes específicas

### ⚠️ Cuidados

- **Não compare coortes diferentes em fases diferentes** sem ajustar
- **Considere efeitos de confounding** (idade, contexto, etc.)
- **Verifique tamanho amostral** (Coorte 3 é pequena: n=58 TDE, n=254 Vocab)
- **Atenção à evasão** (~50% da Coorte 1 tem dados em múltiplas fases)

---

## 🎓 Referências Conceituais

**O que é um Estudo de Coorte?**
> Pesquisa longitudinal que acompanha um grupo de indivíduos ao longo do tempo, compartilhando uma característica comum (neste caso, fase de entrada no programa).

**Vantagens:**
- ✅ Permite análise de mudanças intra-indivíduo
- ✅ Controla variáveis de confusão temporais
- ✅ Identifica padrões de desenvolvimento/aprendizagem
- ✅ Separa efeito do programa de efeitos contextuais

**Limitações:**
- ⚠️ Evasão/atrito amostral
- ⚠️ Efeitos de maturação
- ⚠️ Mudanças contextuais entre fases
- ⚠️ Comparabilidade entre coortes

---

## 📞 Contato/Suporte

**Em caso de dúvidas:**
1. Consultar `VALIDACAO_FINAL_COORTES.md` (documentação completa)
2. Executar `test_coorte.py` para diagnosticar problemas
3. Verificar logs do dashboard para warnings/erros
4. Inspecionar dados diretamente via Python (exemplos acima)

---

**Última atualização:** 2024  
**Status:** ✅ Sistema validado e em produção  
**Versão:** 1.0
