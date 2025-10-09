# 🎨 Visualização: Como Funcionam as Coortes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SISTEMA DE COORTES - WORDGEN                          │
│                    Rastreamento Longitudinal de Alunos                       │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                        O QUE SÃO COORTES?                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Coortes são GRUPOS de alunos baseados na FASE em que ENTRARAM no programa:

┌──────────────────────────────────────────────────────────────────────────┐
│  COORTE 1                                                                 │
│  ├─ Entrada: Fase 2 (primeira avaliação)                                 │
│  ├─ Trajetória: Fase 2 → Fase 3 → Fase 4                                │
│  ├─ Alunos: 2.231 (TDE) | 2.237 (Vocabulário)                           │
│  └─ Percentual: 81.5% (TDE) | 79.1% (Vocabulário)                       │
├──────────────────────────────────────────────────────────────────────────┤
│  COORTE 2                                                                 │
│  ├─ Entrada: Fase 3 (entrada tardia)                                     │
│  ├─ Trajetória: Fase 3 → Fase 4                                         │
│  ├─ Alunos: 448 (TDE) | 337 (Vocabulário)                               │
│  └─ Percentual: 16.4% (TDE) | 11.9% (Vocabulário)                       │
├──────────────────────────────────────────────────────────────────────────┤
│  COORTE 3                                                                 │
│  ├─ Entrada: Fase 4 (última entrada)                                     │
│  ├─ Trajetória: Fase 4 apenas                                           │
│  ├─ Alunos: 58 (TDE) | 254 (Vocabulário)                                │
│  └─ Percentual: 2.1% (TDE) | 9.0% (Vocabulário)                         │
└──────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                    EXEMPLO: TRAJETÓRIA DE ALUNOS                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

ALUNO A (Maria - ID: ABC123)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fase 2: Turma 7A → [PRIMEIRA PARTICIPAÇÃO] ✓
Fase 3: Turma 8A → [continua na mesma escola]
Fase 4: Turma 9A → [continua na mesma escola]

COORTE: Coorte 1 (entrou na Fase 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALUNO B (João - ID: DEF456)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fase 2: [não participou]
Fase 3: Turma 8B → [PRIMEIRA PARTICIPAÇÃO] ✓
Fase 4: Turma 9C → [mudou de turma!]

COORTE: Coorte 2 (entrou na Fase 3)
       ↑ Mantém "Coorte 2" mesmo mudando de turma!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALUNO C (Ana - ID: GHI789)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fase 2: [não participou]
Fase 3: [não participou]
Fase 4: Turma 9D → [PRIMEIRA PARTICIPAÇÃO] ✓

COORTE: Coorte 3 (entrou na Fase 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


╔═══════════════════════════════════════════════════════════════════════════╗
║                    FLUXO DE PROCESSAMENTO                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

 ┌────────────────────────────────────────────────────────────────────────┐
 │  1. CARREGAMENTO DOS DADOS                                              │
 │     ↓                                                                   │
 │     TDE_longitudinal.csv + vocabulario_longitudinal.csv                 │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  2. IDENTIFICAÇÃO DA PRIMEIRA FASE (por ID_Unico)                       │
 │     ↓                                                                   │
 │     Para cada ID_Unico: encontrar MIN(Fase)                            │
 │     Exemplo: Maria (ABC123) → MIN(2, 3, 4) = 2                         │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  3. MAPEAMENTO FASE → COORTE                                           │
 │     ↓                                                                   │
 │     Fase 2 → "Coorte 1"                                                │
 │     Fase 3 → "Coorte 2"                                                │
 │     Fase 4 → "Coorte 3"                                                │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  4. APLICAÇÃO A TODOS OS REGISTROS DO ALUNO                            │
 │     ↓                                                                   │
 │     TODOS os registros de Maria (ABC123) recebem "Coorte 1"           │
 │     independente da fase/turma atual                                   │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  5. COLUNA COORTE_ORIGEM CRIADA ✓                                     │
 │     ↓                                                                   │
 │     Cada linha do dataset agora tem sua coorte definida                │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  6. FILTRO NO DASHBOARD                                                │
 │     ↓                                                                   │
 │     Usuário seleciona: "Coorte 1"                                      │
 │     Sistema filtra: df[df['Coorte_Origem'] == 'Coorte 1']             │
 └────────────────────────────────────────────────────────────────────────┘
                                  ↓
 ┌────────────────────────────────────────────────────────────────────────┐
 │  7. ESTATÍSTICAS CALCULADAS                                            │
 │     ↓                                                                   │
 │     Alunos únicos: df['ID_Anonimizado'].nunique()                      │
 │     Exemplo: "2.231 alunos" (Coorte 1 - TDE)                           │
 └────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                    COMPARAÇÃO: ANTES vs DEPOIS                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

ANTES (Sistema Incorreto):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Coorte baseada em TURMA ATUAL
❌ Aluno que muda de turma muda de coorte
❌ Não acompanha trajetória individual
❌ Impossível fazer análise longitudinal correta

Exemplo:
  João - Fase 2: Turma 7A → Coorte "7A"
  João - Fase 3: Turma 8B → Coorte "8B"  ← PROBLEMA!
  João - Fase 4: Turma 9C → Coorte "9C"  ← PROBLEMA!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEPOIS (Sistema Correto):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Coorte baseada em FASE DE ENTRADA
✅ Aluno mantém coorte mesmo mudando de turma
✅ Rastreamento por ID_Unico
✅ Análise longitudinal correta

Exemplo:
  João - Fase 2: Turma 7A → Coorte 1 (entrou na Fase 2)
  João - Fase 3: Turma 8B → Coorte 1 (mantém)
  João - Fase 4: Turma 9C → Coorte 1 (mantém)  ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


╔═══════════════════════════════════════════════════════════════════════════╗
║                    VALIDAÇÃO DO SISTEMA                                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

Execução de Testes (test_coorte.py):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ TESTE 1: Coluna Coorte_Origem existe            [✅ PASSOU]
✓ TESTE 2: Valores válidos (Coorte 1, 2, 3)      [✅ PASSOU]
✓ TESTE 3: Consistência por ID_Unico             [✅ PASSOU]
   → 0 inconsistências encontradas
✓ TESTE 4: Mapeamento fase → coorte correto      [✅ PASSOU]
✓ TESTE 5: Estatísticas de distribuição          [✅ PASSOU]
   TDE:        2.737 alunos (1: 2.231 | 2: 448 | 3: 58)
   Vocabulário: 2.828 alunos (1: 2.237 | 2: 337 | 3: 254)
✓ TESTE 6: Acompanhamento longitudinal           [✅ PASSOU]
   → ~45% dos alunos Coorte 1 têm dados em múltiplas fases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESULTADO: ✅ TODOS OS TESTES PASSARAM (6/6)
SISTEMA: ✅ VALIDADO E PRONTO PARA PRODUÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


╔═══════════════════════════════════════════════════════════════════════════╗
║                    USO NO DASHBOARD                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

Filtro de Coorte:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────────────────────────────────────┐
  │  🎓 Filtrar por Coorte: ▼                                   │
  │     ┌────────────────────────────────────────────────────┐ │
  │     │  • Todas                                           │ │
  │     │  • Coorte 1  (iniciaram na Fase 2)               │ │
  │     │  • Coorte 2  (iniciaram na Fase 3)               │ │
  │     │  • Coorte 3  (iniciaram na Fase 4)               │ │
  │     └────────────────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────────────────┘

Impacto do Filtro:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SEM FILTRO (Todas):
  ┌──────────────────────────────────────────────────────────────┐
  │  📊 Estatísticas Gerais                                      │
  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
  │  Total: 10 escolas / 2.737 alunos únicos                    │
  └──────────────────────────────────────────────────────────────┘

  COM FILTRO (Coorte 1):
  ┌──────────────────────────────────────────────────────────────┐
  │  📊 Estatísticas Gerais                                      │
  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
  │  Total: 10 escolas / 2.231 alunos únicos  ← MUDOU!          │
  └──────────────────────────────────────────────────────────────┘

  → Diferença: 506 alunos filtrados (Coorte 2 + Coorte 3)


╔═══════════════════════════════════════════════════════════════════════════╗
║                    CASOS DE USO PRÁTICOS                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. ANÁLISE DE TRAJETÓRIA COMPLETA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pergunta: "Quantos alunos completaram o programa desde o início?"

Passos:
  1. Selecionar: Coorte 1
  2. Selecionar: Fase 4
  3. Ver quantos alunos permanecem

Resultado: Identifica taxa de retenção


2. COMPARAÇÃO ENTRE COORTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pergunta: "Qual coorte teve melhor desempenho?"

Passos:
  1. Analisar Coorte 1 na Fase 4
  2. Analisar Coorte 2 na Fase 4
  3. Comparar médias de Score_Pos

Resultado: Identifica efeito de tempo de exposição


3. EFEITO DE MATURAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pergunta: "Houve efeito de maturação (idade)?"

Passos:
  1. Comparar Coorte 1 (Fase 2) vs Coorte 2 (Fase 3)
  2. Ambos na mesma fase atual
  3. Ver se há diferença de desempenho

Resultado: Controla efeito de idade vs efeito do programa


╔═══════════════════════════════════════════════════════════════════════════╗
║                    ARQUIVOS CHAVE                                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Código:
  📄 /Dashboard/data_loader.py      → Criação da coluna Coorte_Origem
  📄 /Dashboard/app.py               → Filtro e interface do dashboard
  📄 /Dashboard/test_coorte.py       → Testes automatizados

Documentação:
  📚 GUIA_RAPIDO_COORTES.md          → Referência rápida (5 min)
  📚 VALIDACAO_FINAL_COORTES.md      → Documentação completa
  📚 CONCEITO_COORTES.md             → Fundamentação teórica
  📚 INDEX_COORTES.md                → Índice de toda documentação
  📚 Este arquivo                    → Visualização didática


╔═══════════════════════════════════════════════════════════════════════════╗
║                    STATUS DO SISTEMA                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

   ✅ Implementação:  CONCLUÍDA
   ✅ Testes:         6/6 PASSARAM
   ✅ Documentação:   COMPLETA
   ✅ Validação:      APROVADA
   ✅ Produção:       PRONTO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Sistema de Coortes - WordGen Dashboard
   Versão: 1.0 | Status: ✅ PRODUÇÃO | Data: 2024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
