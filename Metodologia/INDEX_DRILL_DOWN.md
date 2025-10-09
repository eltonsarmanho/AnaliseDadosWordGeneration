# 🎯 Drill-Down com Coordenadas Paralelas - Guia Rápido

## 📌 O Que Foi Implementado

Uma visualização única e interativa de **coordenadas paralelas** usando **Altair**, que substitui o layout anterior de 3 colunas sincronizadas. Agora o usuário vê **um único gráfico por vez**, podendo alternar entre níveis de agregação (Escolas/Turmas/Alunos).

**✨ Versão Atual: 2.1** (com ajustes de UX e filtros otimizados)

---

## 🚀 Como Usar

### 1️⃣ **Acesse a Seção**
No dashboard, role até: **"Evolução Comparativa Hierárquica - Coordenadas Paralelas"**

### 2️⃣ **Configure o Contexto**
- **� Prova**: Use o filtro da **SIDEBAR** (TDE ou Vocabulário)
- **🎓 Coorte**: Todas, Coorte 1, 2 ou 3
  - 💡 **Clique em "ℹ️ O que são Coortes?"** para entender o conceito
- **🔍 Visualizar**: Escolas, Turmas ou Alunos

### 3️⃣ **Aplique Filtros (Opcional)**
- **🏫 Escolas**: Sempre visível
- **🎓 Turmas**: Aparece ao visualizar Turmas/Alunos
- **👨‍🎓 Alunos**: Aparece ao visualizar Alunos

### 4️⃣ **Interaja com o Gráfico**
- **Hover**: Ver detalhes de cada ponto
- **Brush Selection**: Arrastar para selecionar faixas de valores
- **Linha Vermelha**: Média geral (referência)

### 5️⃣ **Consulte Estatísticas**
4 cards abaixo do gráfico mostram:
- **N° Entidades**: Quantas escolas/turmas/alunos
- **Média**: Valor médio do indicador
- **Tendência**: Variação entre fases (📈/📉)
- **Variabilidade**: Desvio padrão

**Novo:** Um caption abaixo mostra **exatamente quais filtros** foram aplicados:
```
📊 Estatísticas calculadas com base nos filtros: Coorte 2, 3 escola(s), 5 turma(s)
```

---

## 🆕 O Que Há de Novo (v2.1)

### ✅ **Filtro de Prova Removido**
- Antes: Seletor "Tipo de Análise" (TDE/Vocabulário) na seção
- Agora: Usa o filtro **"Prova"** da sidebar
- **Benefício**: Menos redundância, interface mais limpa

### ✅ **Explicação de Coortes**
- Clique em **"ℹ️ O que são Coortes?"** para expandir
- Explicação clara: 
  - **Coorte 1**: Começaram na **Fase 2**
  - **Coorte 2**: Começaram na **Fase 3**
  - **Coorte 3**: Começaram na **Fase 4**
- Contexto educacional: Tempo de exposição ao programa, entrada escalonada
- Exemplos de trajetórias (Coorte 1: Fases 2→3→4, Coorte 2: 3→4, Coorte 3: apenas 4)
- **Benefício**: Usuários entendem que coortes = fase inicial, não ano calendário

### ✅ **Estatísticas Contextualizadas**
- Caption dinâmico mostra filtros ativos
- Transparência total sobre dados visualizados
- **Benefício**: Evita interpretações incorretas

### ✅ **Opção "Todas as Coortes"**
- Agora é possível ver todas as coortes juntas
- Útil para visão geral e comparações amplas
- **Benefício**: Mais flexibilidade analítica

---

## 💡 Casos de Uso

### 🏫 **Análise Regional (Escolas)**
```
Objetivo: Comparar escolas de uma região
1. Selecionar "Escolas"
2. Filtrar escolas de interesse
3. Identificar outliers (linhas que fogem da média)
```

### 🎓 **Foco Pedagógico (Turmas)**
```
Objetivo: Avaliar turmas de uma escola
1. Selecionar "Turmas"
2. Filtrar escola → turmas
3. Comparar evolução entre turmas
```

### 👨‍🎓 **Acompanhamento Individual (Alunos)**
```
Objetivo: Monitorar alunos específicos
1. Selecionar "Alunos"
2. Filtrar escola → turma → alunos
3. Comparar trajetórias individuais com média
```

---

## 🎨 Vantagens vs Versão Anterior

| Aspecto | Antes (3 Colunas) | Agora (Paralelas) |
|---------|-------------------|-------------------|
| **Layout** | 3 gráficos lado a lado | 1 gráfico centralizado |
| **Foco** | Disperso | Concentrado |
| **Filtros** | Replicados 3x | Únicos, contextuais |
| **Performance** | 3 renderizações | 1 renderização |
| **Comparação** | Difícil entre níveis | Seletor direto |

---

## 🔧 Detalhes Técnicos

### **Tecnologias**
- **Altair** (coordenadas paralelas)
- **Streamlit** (interface)
- **Pandas** (agregação de dados)
- **Plotly** (fallback se Altair não disponível)

### **Localização no Código**
```
Arquivo: /Dashboard/app.py
Linhas: ~397-750
```

### **Dependências**
```bash
pip install altair>=5.0 streamlit>=1.28 pandas>=2.0 plotly>=5.0
```

---

## ✅ Status

**CONCLUÍDO E VALIDADO** ✅

- Funcionalidade completa e testada
- Tratamento robusto de erros
- Performance otimizada
- UX intuitiva

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **`DRILL_DOWN_CONCLUIDO.md`** - Documentação técnica completa
- **`PROPOSTA_PARALLEL_COORDINATES.md`** - Design e justificativa
- **`REFATORACAO_COMPLETA_DRILL_DOWN.md`** - Histórico de mudanças

---

**Versão**: 2.0 | **Data**: Janeiro 2024 | **Autores**: IA + Elton Santos
