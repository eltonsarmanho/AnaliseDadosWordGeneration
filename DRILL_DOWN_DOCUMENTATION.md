# 📊 Funcionalidade Drill-Down - Dashboard WordGen

## 🎯 Visão Geral

A funcionalidade de **Drill-Down Hierárquico** foi implementada na seção "Evolução Comparativa Hierárquica" do dashboard, permitindo navegação em três níveis:

```
🏠 ESCOLAS → 🏫 TURMAS → 👥 ALUNOS
```

## 🔧 Como Funciona

### **Nível 1: Escolas**
- **Visualização:** Gráfico de linhas mostrando a evolução média de Delta (Pós - Pré) por escola
- **Interação:** Clique em uma linha para navegar para as turmas dessa escola
- **Informações:** Hover mostra escola, fase, delta real e média geral

### **Nível 2: Turmas**
- **Visualização:** Gráfico de linhas das turmas da escola selecionada
- **Interação:** Clique em uma linha para ver os alunos dessa turma
- **Navegação:** Breadcrumb permite voltar ao nível de escolas

### **Nível 3: Alunos**
- **Visualização:** Evolução individual de cada aluno da turma selecionada
- **Informações:** Mostra a performance individual por fase
- **Navegação:** Breadcrumb permite navegar entre todos os níveis

## 🎛️ Controles e Funcionalidades

### **Breadcrumb Navigation**
```
[🏠 Escolas] [🏫 Nome da Escola] [👥 Nome da Turma]
```
- Botões clicáveis para navegar entre níveis
- Estado ativo destacado em azul

### **Opções Avançadas**
- ✅ **Agrupar nomes equivalentes de escolas:** Normaliza nomes similares
- ✅ **Preencher fases ausentes:** Completa dados faltantes com médias
- ⚙️ **Normalização z-score:** Visualização padronizada por fase
- 📊 **Ordenação por média:** Ordena legenda por performance

### **Interatividade**
- **Click-to-Drill:** Clique nas linhas dos gráficos para navegar
- **Hover Information:** Detalhes completos ao passar o mouse
- **State Management:** Estado persistente durante a navegação

## 🔍 Detalhes Técnicos

### **Gerenciamento de Estado**
```python
st.session_state.drill_level    # 'escola', 'turma', 'aluno'
st.session_state.selected_escola # Escola atualmente selecionada
st.session_state.selected_turma  # Turma atualmente selecionada
```

### **Captura de Eventos**
```python
clicked_data = st.plotly_chart(fig, on_select="rerun", key="unique_key")
```

### **Processamento Hierarchico**
1. **Filtragem progressiva:** Cada nível filtra os dados do anterior
2. **Agregação inteligente:** Médias calculadas por agrupamento
3. **Normalização opcional:** Z-score por fase quando habilitado

## 📈 Benefícios

### **Para Gestores Educacionais:**
- 🎯 **Análise Estratégica:** Visão macro das escolas
- 🔍 **Investigação Detalhada:** Drill-down até aluno individual
- 📊 **Comparação Justa:** Normalização por z-score

### **Para Professores:**
- 👥 **Foco na Turma:** Análise específica da classe
- 🎓 **Acompanhamento Individual:** Performance de cada aluno
- 📈 **Evolução Clara:** Tendências visuais por fase

### **Para Pesquisadores:**
- 📋 **Flexibilidade:** Múltiplas opções de visualização
- 🔬 **Granularidade:** Três níveis de análise
- 📊 **Dados Consistentes:** Tratamento inteligente de missing values

## 🚀 Exemplo de Uso

1. **Inicie** visualizando todas as escolas
2. **Identifique** uma escola com performance interessante
3. **Clique** na linha da escola para ver suas turmas
4. **Analise** qual turma tem melhor/pior desempenho
5. **Clique** na turma para ver alunos individuais
6. **Use** breadcrumbs para navegar de volta

## 🎨 Personalização Visual

- **Cores Dinâmicas:** Plotly colors automáticas
- **Markers:** Pontos em todas as linhas para clareza
- **Tooltips:** Informações completas no hover
- **Responsivo:** Layout adaptável ao container
- **Breadcrumbs:** Interface intuitiva de navegação

## 🔧 Manutenção e Extensões

### **Possíveis Melhorias Futuras:**
- 🎯 Filtros adicionais por performance
- 📊 Múltiplas métricas simultaneamente
- 💾 Export de dados filtrados
- 🔄 Refresh automático
- 📱 Melhor responsividade mobile

### **Estrutura do Código:**
- **Modular:** Função `criar_grafico_drill()` reutilizável
- **Limpo:** Separação clara entre níveis
- **Escalável:** Fácil adição de novos níveis
- **Eficiente:** Cache e otimizações Streamlit

---

**✨ A funcionalidade Drill-Down transforma análise estática em navegação interativa, permitindo insights desde visão geral até detalhes individuais!**