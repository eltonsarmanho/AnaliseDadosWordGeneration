# Pré-processamento de Dados - WordGen

Este documento descreve as etapas detalhadas do pré-processamento dos dados coletados no projeto WordGen, incluindo dados de TDE (Teste de Desempenho Escolar) e Vocabulário, organizados por fases (2, 3 e 4) e momentos (Pré e Pós).

## Visão Geral

O pré-processamento é uma etapa fundamental para garantir a qualidade e consistência dos dados antes das análises estatísticas. O processo é dividido em **8 etapas principais** que são aplicadas sequencialmente aos dados brutos.

---

## **Pré-processamento Completo (8 etapas)**

### **2.1: Completar Dados Faltantes de Escola/Turma**

**Objetivo:** Identificar e corrigir registros com informações de escola ou turma ausentes ou inconsistentes.

**Processo:**
- **Identificação:** Buscar registros com valores nulos, vazios ou inconsistentes nos campos `Escola` e `Turma`
- **Correção por Contexto:** Utilizar informações de outros registros do mesmo participante (ID_Unico) para completar dados faltantes
- **Padronização:** Corrigir variações de grafia dos nomes das escolas
- **Validação:** Verificar se todas as combinações Escola-Turma são válidas e consistentes

**Critérios:**
- Registros sem escola ou turma são marcados para revisão
- Nomes de escolas são padronizados (ex: "EMEB Prof." vs "EMEB Professor")
- Turmas seguem formato padrão (ex: "6º ANO A", "7 ANO B")

**Exemplo de Correção:**
```
Antes: Escola = "", Turma = "6º ANO A"
Depois: Escola = "EMEB PROFESSOR RICARDO VIEIRA DE LIMA", Turma = "6º ANO A"
```

---

### **2.2: Remover Duplicados (Escola + Turma + Nome)**

**Objetivo:** Eliminar registros duplicados que podem comprometer a integridade das análises.

**Processo:**
- **Identificação:** Buscar combinações idênticas de `Escola + Turma + Nome`
- **Análise de Duplicatas:** Verificar se são duplicatas verdadeiras ou registros legítimos
- **Critério de Remoção:** Manter o registro mais completo (com mais dados preenchidos)
- **Registro de Ações:** Documentar quantas duplicatas foram removidas por escola/turma

**Critérios de Prioridade:**
1. Registro com mais questões respondidas
2. Registro com dados mais recentes
3. Registro com menor quantidade de valores faltantes

**Estatísticas Geradas:**
- Número total de duplicatas identificadas
- Duplicatas removidas por escola
- Percentual de duplicatas por fase

---

### **2.3: Converter Valores TDE (0=erro, 1=acerto parcial, 2=acerto completo)**

**Objetivo:** Padronizar a codificação das respostas do TDE seguindo o sistema de pontuação oficial.

**Sistema de Codificação:**
- **0 = Erro:** Resposta incorreta ou não respondida
- **1 = Acerto Parcial:** Resposta parcialmente correta (quando aplicável)
- **2 = Acerto Completo:** Resposta totalmente correta

**Processo:**
- **Mapeamento:** Converter respostas originais (texto, números diversos) para o sistema 0-1-2
- **Validação:** Verificar se todas as questões P01-P40 seguem a codificação
- **Correção:** Ajustar valores fora do padrão (ex: valores negativos, texto)
- **Documentação:** Registrar quantas conversões foram feitas por tipo

**Exemplos de Conversão:**
```
Antes: "Correto" → Depois: 2
Antes: "Parcial" → Depois: 1
Antes: "Errado" → Depois: 0
Antes: "" → Depois: 0
Antes: -1 → Depois: 0
```

---

### **2.4: Verificar Questões Válidas (≥25%) de Cada Registro de Participante**

**Objetivo:** Garantir que cada participante tenha respondido a um número mínimo de questões para validar sua participação.

**Critérios de Validação:**
- **TDE:** Mínimo de 10 questões respondidas (25% de 40 questões)
- **Vocabulário:** Mínimo de 13 questões respondidas (25% de 50 questões)
- **Aplicação:** Critério aplicado tanto para Pré quanto para Pós-teste

**Processo:**
- **Cálculo:** Contar questões com respostas válidas (não nulas/vazias) por participante
- **Classificação:** Marcar registros como válidos ou inválidos
- **Ação:** Remover ou marcar para revisão registros com participação insuficiente
- **Relatório:** Gerar estatísticas de participação por escola/turma

**Estatísticas Geradas:**
- Taxa de participação por escola
- Distribuição de questões respondidas
- Registros removidos por participação insuficiente

---

### **2.5: Padronizar Nomes de Colunas (ESCOLA→Escola, etc.)**

**Objetivo:** Uniformizar os nomes das colunas para facilitar processamento e análises.

**Padronizações Aplicadas:**
- **Capitalização:** Primeira letra maiúscula, demais minúsculas
- **Consistência:** Mesmo padrão em todas as fases e tipos de teste
- **Códigos:** Manter códigos padronizados para questões (P01-P40, Q01-Q50)

**Mapeamento de Colunas:**
```
ESCOLA → Escola
TURMA → Turma  
NOME → Nome
ID_UNICO → ID_Unico
SCORE_PRE → Score_Pre
SCORE_POS → Score_Pos
GrupoEtario → GrupoTDE (para TDE)
```

**Processo:**
- **Detecção:** Identificar variações nos nomes das colunas
- **Mapeamento:** Aplicar conversões padronizadas
- **Validação:** Verificar se todas as colunas essenciais estão presentes
- **Documentação:** Registrar alterações feitas

---

### **2.6: Classificar Grupos (A: 6º/7º, B: 8º/9º) - Somente para Efeito de Análise**

**Objetivo:** Criar grupos etários para facilitar análises comparativas entre diferentes níveis escolares.

**Classificação:**
- **Grupo A:** 6º e 7º anos do Ensino Fundamental
- **Grupo B:** 8º e 9º anos do Ensino Fundamental

**Processo:**
- **Extração:** Identificar o ano escolar a partir do campo `Turma`
- **Regex Utilizado:** `r'(\d+)(?:º|°|\s+(?:ano|ANO))'` para capturar variações
- **Classificação:** Aplicar regras de agrupamento
- **Validação:** Verificar classificações ambíguas ou incorretas

**Padrões Reconhecidos:**
```
"6º ANO A" → Grupo A
"6° ANO B" → Grupo A  
"7 ANO C" → Grupo A
"8º ANO A" → Grupo B
"9 ANO B" → Grupo B
```

**Campo Criado:**
- **TDE:** `GrupoTDE` (A ou B)
- **Vocabulário:** `GrupoVocabulario` (A ou B)

---

### **2.7: Criar IDs Únicos**

**Objetivo:** Garantir identificação única de cada participante para permitir análises longitudinais.

**Processo:**
- **Geração:** Criar identificador único baseado em `Escola + Turma + Nome`
- **Algoritmo:** Usar hash ou concatenação padronizada
- **Validação:** Verificar unicidade dos IDs gerados
- **Persistência:** Manter consistência entre fases e tipos de teste

**Formato do ID:**
```
Escola: "EMEB PROF RICARDO"
Turma: "6º ANO A"  
Nome: "JOÃO SILVA"
ID_Unico: "EMEB_PROF_RICARDO_6A_JOAO_SILVA"
```

**Tratamento de Casos Especiais:**
- Remoção de acentos e caracteres especiais
- Padronização de espaços
- Tratamento de nomes similares

---

### **2.8: Verificar Presença dos Alunos em Ambos os Testes (Pré e Pós)**

**Objetivo:** Identificar participantes que completaram tanto o pré-teste quanto o pós-teste, essencial para análises de ganho.

**Processo:**
- **Identificação:** Verificar presença do mesmo `ID_Unico` em dados Pré e Pós
- **Classificação:** Marcar registros como completos, apenas-pré ou apenas-pós
- **Ação:** Definir estratégias para registros incompletos
- **Relatório:** Gerar estatísticas de completude por escola/turma

**Categorias de Participação:**
- **Completa:** Participou de Pré E Pós (ideal para análises)
- **Apenas Pré:** Participou só do pré-teste
- **Apenas Pós:** Participou só do pós-teste
- **Ausente:** Não participou de nenhum

**Estatísticas Geradas:**
- Taxa de retenção por escola
- Distribuição de participação por grupo etário
- Análise de perdas entre Pré e Pós

**Critérios para Análises:**
- **Análises de Ganho:** Apenas participantes completos
- **Análises Descritivas:** Todos os participantes válidos
- **Análises Longitudinais:** Participantes presentes em múltiplas fases

---

## Validação Final

Após completar as 8 etapas, é realizada uma validação final que verifica:

1. **Integridade dos Dados:**
   - Todos os campos essenciais preenchidos
   - Valores dentro dos intervalos esperados
   - Consistência entre fases

2. **Qualidade dos Dados:**
   - Taxa de participação adequada
   - Distribuição equilibrada entre grupos
   - Ausência de outliers extremos

3. **Preparação para Análise:**
   - Estrutura padronizada
   - IDs únicos funcionais  
   - Dados prontos para consolidação

---

## Arquivos Gerados

O processo de pré-processamento gera os seguintes arquivos por fase:

- `tabela_bruta_fase{N}_TDE_wordgen.csv`
- `tabela_bruta_fase{N}_vocabulario_wordgen.csv`

E os arquivos consolidados:

- `TDE_consolidado_fases_2_3_4.csv`
- `vocabulario_consolidado_fases_2_3_4.csv`

Cada arquivo inclui todas as etapas de pré-processamento aplicadas e está pronto para análises estatísticas e geração de relatórios visuais.