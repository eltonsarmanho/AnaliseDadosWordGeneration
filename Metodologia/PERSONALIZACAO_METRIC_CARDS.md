# 🎨 Personalização dos Metric Cards - Dashboard WordGen

## 📋 Resumo das Alterações

Todos os metric cards do dashboard foram personalizados para seguir um padrão visual moderno e consistente, baseado no design com FontAwesome e cores RGB.

---

## ✨ Funcionalidade Criada

### Função `criar_metric_card()`

```python
def criar_metric_card(valor, titulo, icone, cor_box=(0, 123, 255), cor_fonte=(255, 255, 255)):
    """Cria um card métrico personalizado com ícone FontAwesome"""
```

**Parâmetros:**
- `valor`: Valor principal a ser exibido (número ou texto)
- `titulo`: Descrição/rótulo do card
- `icone`: Classe do ícone FontAwesome (ex: "fas fa-users")
- `cor_box`: Tupla RGB para cor de fundo (padrão: azul)
- `cor_fonte`: Tupla RGB para cor do texto (padrão: branco)

**Características:**
- Integração com FontAwesome 5.12.1 para ícones
- Design responsivo com border-radius arredondado
- Sombra suave para profundidade visual
- Tipografia hierárquica (valor grande, título pequeno)
- Opacidade controlada para melhor contraste

---

## 🎨 Cards Implementados

### 1. **Resumo Filtrado - Primeira Linha**

#### Card "Registros"
- **Ícone:** `fas fa-database` 📊
- **Cor:** Azul `rgb(52, 152, 219)`
- **Valor:** Total de registros no dataset filtrado

#### Card "Alunos Únicos"
- **Ícone:** `fas fa-users` 👥
- **Cor:** Verde `rgb(46, 204, 113)`
- **Valor:** Número de alunos únicos (ID_Unico)

#### Card "Escolas"
- **Ícone:** `fas fa-school` 🏫
- **Cor:** Roxo `rgb(155, 89, 182)`
- **Valor:** Número de escolas únicas

### 2. **Resumo Filtrado - Segunda Linha**

#### Card "Turmas"
- **Ícone:** `fas fa-chalkboard-teacher` 👨‍🏫
- **Cor:** Laranja `rgb(230, 126, 34)`
- **Valor:** Número de turmas (agregadas ou separadas)
- **Título Dinâmico:** Muda conforme opção de agregação

#### Card "Tamanho do Efeito (Cohen's d)"
- **Ícone:** `fas fa-chart-line` 📈
- **Cores Dinâmicas:**
  - **Verde** `rgb(40, 167, 69)` → Resultado excelente (ok_flag=True) ✅
  - **Amarelo** `rgb(255, 193, 7)` → Ponto de atenção (ok_flag=False) ⚠️
  - **Cinza** `rgb(108, 117, 125)` → Sem dados ℹ️
- **Valor:** d de Cohen calculado (formato: 0.XXX)
- **Informações Extras:**
  - Benchmark específico (TDE/Vocabulário)
  - Classificação geral (Trivial/Pequeno/Médio/Grande)

### 3. **Drill-Down: Estatísticas de Alunos por Turma**

Quando o usuário navega até o nível de alunos de uma turma específica:

#### Card "Total de Alunos"
- **Ícone:** `fas fa-user-graduate` 🎓
- **Cor:** Azul `rgb(52, 152, 219)`

#### Card "Delta Médio"
- **Ícone:** `fas fa-chart-bar` 📊
- **Cor:** Roxo `rgb(155, 89, 182)`
- **Formato:** 2 casas decimais

#### Card "Melhor Delta"
- **Ícone:** `fas fa-arrow-up` ⬆️
- **Cor:** Verde `rgb(46, 204, 113)`
- **Formato:** 2 casas decimais

#### Card "Pior Delta"
- **Ícone:** `fas fa-arrow-down` ⬇️
- **Cor:** Vermelho `rgb(231, 76, 60)`
- **Formato:** 2 casas decimais

---

## 🎯 Benefícios da Personalização

### 1. **Consistência Visual**
- Todos os cards seguem o mesmo padrão de design
- Paleta de cores harmoniosa e profissional
- Ícones intuitivos que reforçam o significado

### 2. **Ergonomia Melhorada**
- Hierarquia visual clara (valor → título)
- Cores com significado semântico (verde=positivo, vermelho=negativo)
- Sombras e opacidade para profundidade

### 3. **Responsividade**
- Cards se adaptam ao layout de colunas do Streamlit
- Fontes proporcionais e legíveis
- Padding consistente

### 4. **Acessibilidade**
- Contraste adequado entre texto e fundo
- Ícones como reforço visual da informação
- Tipografia legível (18-36px para valores)

---

## 🔧 Estrutura do HTML Gerado

```html
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css">

<p style='background-color: rgb(R, G, B, 0.85); 
          color: rgb(R, G, B, 0.95); 
          font-size: 28px; 
          font-weight: 700;
          border-radius: 10px; 
          padding: 20px 15px; 
          text-align: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
    <i class='ICONE fa-lg'></i> VALOR
    <br>
    <span style='font-size: 13px; font-weight: 400;'>TITULO</span>
</p>
```

---

## 📊 Paleta de Cores Utilizada

| Elemento | RGB | Hexadecimal | Uso |
|----------|-----|-------------|-----|
| Azul | `(52, 152, 219)` | `#3498db` | Registros, Total Alunos |
| Verde | `(46, 204, 113)` | `#2ecc71` | Alunos Únicos, Melhor Delta |
| Roxo | `(155, 89, 182)` | `#9b59b6` | Escolas, Delta Médio |
| Laranja | `(230, 126, 34)` | `#e67e22` | Turmas |
| Verde Escuro | `(40, 167, 69)` | `#28a745` | Cohen's d - Excelente |
| Amarelo | `(255, 193, 7)` | `#ffc107` | Cohen's d - Atenção |
| Cinza | `(108, 117, 125)` | `#6c757d` | Cohen's d - Sem Dados |
| Vermelho | `(231, 76, 60)` | `#e74c3c` | Pior Delta |

---

## 🚀 Implementação Técnica

### Substituição dos `st.metric()` nativos

**Antes:**
```python
col1.metric("Registros", len(df))
```

**Depois:**
```python
with col1:
    st.markdown(
        criar_metric_card(
            valor=len(df),
            titulo="Registros",
            icone="fas fa-database",
            cor_box=(52, 152, 219),
            cor_fonte=(255, 255, 255)
        ),
        unsafe_allow_html=True
    )
```

### Vantagens sobre `st.metric()` nativo
1. **Customização total** do design
2. **Ícones FontAwesome** integrados
3. **Cores personalizadas** por contexto
4. **Layout mais atraente** visualmente
5. **Maior controle** sobre tipografia e espaçamento

---

## 📝 Observações Importantes

1. **Dependência do FontAwesome**: Requer conexão à internet para carregar os ícones
2. **HTML Inline**: Usa `unsafe_allow_html=True` do Streamlit
3. **Responsividade**: Funciona bem em diferentes tamanhos de tela
4. **Manutenibilidade**: Função centralizada facilita mudanças futuras

---

## 🎓 Referências

- **FontAwesome 5.12.1**: https://fontawesome.com/v5.12/icons
- **Paleta Flat UI Colors**: Inspirada em flat design moderno
- **Streamlit HTML Components**: Documentação oficial do Streamlit

---

**Implementado por:** Elton Sarmanho  
**Data:** Outubro de 2025  
**Dashboard:** WordGen - Análise Longitudinal TDE/Vocabulário
