# 🎨 Nova Proposta: Parallel Coordinates com Altair

## 🎯 Visão Geral

Substituir as 3 colunas atuais por **UMA visualização de Coordenadas Paralelas** que mostra:
- Todas as trajetórias longitudinais (Fases 2, 3, 4)
- Filtros hierárquicos (Escola → Turma → Aluno)
- Interatividade com brushing/seleção
- Estatísticas dinâmicas

## 📊 Como Funciona

```
┌────────────────────────────────────────────────────────────┐
│ Tipo: [TDE ▼]        Coorte: [Coorte 1 ▼]                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│     Fase 2    │    Fase 3    │    Fase 4                 │
│       │       │       │       │       │                    │
│       │    ╱──┼───────┼───╲   │       │  ← Escola A       │
│       │  ╱    │       │     ╲─┼─      │                    │
│       ├─      ├─      ├─      │       │                    │
│       │╲      │ ╲     │  ╲    │       │  ← Turma 7A       │
│       │ ╲────┼──╲────┼───╲───┼       │                    │
│       │      │   ╲   │    ╲  │       │                    │
│       │      │    ╲──┼─────╲─┼       │  ← Aluno João     │
│       │      │       │       ╲│       │                    │
│                                                            │
│  [Cada linha = uma trajetória completa através das fases] │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ 🔽 Nível: [Escolas ▼]  (Escolas/Turmas/Alunos)           │
│ 🔽 Filtrar Escolas: [Multiselect...]                      │
│ 🔽 Filtrar Turmas: [Multiselect...] (se nível ≥ Turmas)  │
│ 🔽 Filtrar Alunos: [Multiselect...] (se nível = Alunos)  │
├────────────────────────────────────────────────────────────┤
│ 📊 Estatísticas da Seleção:                               │
│ ┌───────────┬───────────┬───────────┬───────────┐        │
│ │ N° Itens  │ Δ Médio   │ Tendência │ Variância │        │
│ │    15     │  +12.5    │    ↗      │   ±3.2    │        │
│ └───────────┴───────────┴───────────┴───────────┘        │
└────────────────────────────────────────────────────────────┘
```

## 💡 Vantagens

1. **Uma Visualização, Todo Contexto**
   - Todas as trajetórias visíveis simultaneamente
   - Padrões emergem naturalmente (clusters, outliers)
   - Comparação direta entre entidades

2. **Interatividade Nativa**
   - Brush/seleção em qualquer fase
   - Highlight automático
   - Zoom e pan

3. **Filtros Hierárquicos Progressivos**
   - Nível 1: Ver todas as escolas
   - Nível 2: Drill-down para turmas de escolas selecionadas
   - Nível 3: Drill-down para alunos de turmas selecionadas

4. **Densidade de Informação**
   - Pode mostrar 100+ trajetórias simultaneamente
   - Transparência para ver sobreposições
   - Cores para diferenciar grupos

## 🎨 Design da Interface

### Estrutura
```python
# Uma coluna principal
col_main = st.container()

with col_main:
    # 1. Seletores de contexto
    col_sel1, col_sel2 = st.columns(2)
    
    # 2. Gráfico principal de coordenadas paralelas
    st.altair_chart(chart_parallel)
    
    # 3. Controles de filtro hierárquico
    st.radio("Visualizar:", ["Escolas", "Turmas", "Alunos"])
    st.multiselect("Filtrar...")
    
    # 4. Cards de estatísticas
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
```

## 🔧 Implementação com Altair

### Características Técnicas

- **Altair**: Grammar of Graphics declarativo
- **Interatividade**: Seleção e brush nativos
- **Performance**: Otimizado para grandes datasets
- **Estilo**: Customizável e moderno

### Benefícios do Altair

1. **Sintaxe Declarativa**
   - Código mais limpo e legível
   - Menos linhas que Plotly
   - Mais intuitivo

2. **Interatividade Nativa**
   - Linked brushing sem código extra
   - Seleção multi-eixo
   - Tooltip rico

3. **Composição**
   - Fácil combinar múltiplas views
   - Layer, concat, facet nativos
   - Responsivo

## 📈 Comparação: Atual vs Proposto

| Aspecto | Atual (3 Colunas) | Proposto (Parallel) |
|---------|-------------------|---------------------|
| Espaço usado | ~2000px largura | ~1200px largura |
| Trajetórias visíveis | Limitado por coluna | Ilimitado (scrollável) |
| Comparação | Difícil (3 gráficos) | Imediata (1 gráfico) |
| Padrões | Não visível | Clusters evidentes |
| Outliers | Manual | Automático visual |
| Interatividade | Básica | Avançada (brush) |
| Performance | Boa | Excelente |
| Código | ~250 linhas | ~150 linhas |

## 🚀 Próximos Passos

1. Implementar gráfico de coordenadas paralelas com Altair
2. Adicionar sistema de filtros hierárquicos
3. Criar cards de estatísticas dinâmicas
4. Adicionar opções de customização (cores, espessura, etc.)
5. Implementar exportação de dados/gráfico

---

**Pronto para implementar?** 🚀
