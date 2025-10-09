import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import get_datasets
import unicodedata, re, math
import numpy as np

st.set_page_config(page_title="Dashboard Longitudinal WordGen", layout="wide")

def normalizar_turma(turma_original: str) -> str:
    """Normaliza valores de turma para formato padrão (5° Ano, 6° Ano, etc.)"""
    if pd.isna(turma_original):
        return turma_original
    
    turma_str = str(turma_original).upper().strip()
    
    # Mapeamento de padrões para anos padronizados
    if any(x in turma_str for x in ['5', 'QUINTO']):
        return '5° Ano'
    elif any(x in turma_str for x in ['6', 'SEXTO']):
        return '6° Ano'
    elif any(x in turma_str for x in ['7', 'SETIMO', 'SÉTIMO']):
        return '7° Ano'
    elif any(x in turma_str for x in ['8', 'OITAVO']):
        return '8° Ano'
    elif any(x in turma_str for x in ['9', 'NONO']):
        return '9° Ano'
    else:
        # Se não conseguir identificar, mantém original
        return turma_original

@st.cache_data(show_spinner=False)
def load_data():
    """Carrega e normaliza os datasets principais (TDE e Vocabulário)."""
    tde, vocab = get_datasets()
    
    # Preservar turmas originais antes da normalização para contagem correta
    if 'Turma' in tde.columns:
        tde['Turma_Original'] = tde['Turma'].copy()
        tde['Turma'] = tde['Turma'].apply(normalizar_turma)
    
    if 'Turma' in vocab.columns:
        vocab['Turma_Original'] = vocab['Turma'].copy()
        vocab['Turma'] = vocab['Turma'].apply(normalizar_turma)
    
    return tde, vocab

# ================= LOAD DATA =================
tde_df, vocab_df = load_data()

PROVAS = {"TDE": tde_df, "VOCABULÁRIO": vocab_df}

# ================= SIDEBAR ===================
st.sidebar.title("📊 Dashboard Longitudinal - WordGen")
st.sidebar.markdown("""
**Este painel permite:**
- Filtrar por Escola / Turma / Fase / Prova
- Acompanhar evolução individual (pré x pós) por fase
""")
st.sidebar.markdown("---")
st.sidebar.header("Filtros")
prova_sel = st.sidebar.selectbox("Prova", list(PROVAS.keys()))
df = PROVAS[prova_sel]

# Fases (filtram os dados antes de definir escolas disponíveis)
fases = sorted(df['Fase'].dropna().unique())
fases_sel = st.sidebar.multiselect("Fase(s)", fases, default=fases)
if fases_sel:
    df = df[df['Fase'].isin(fases_sel)]

# Escolas (lista já considera filtro de fase)
escolas = sorted(df['Escola'].dropna().unique())
escola_sel = st.sidebar.multiselect("Escola(s)", escolas, default=[])
if escola_sel:
    df = df[df['Escola'].isin(escola_sel)]

# Turmas - Opção de agregação
st.sidebar.markdown("---")
agregar_turmas = st.sidebar.checkbox("🔄 Agregar turmas por ano", value=False, 
                                    help="Ative para agrupar turmas do mesmo ano (ex: 7° A, 7° B → 7° Ano)")

# Determinar que coluna de turma usar baseado na opção de agregação
if agregar_turmas:
    coluna_turma = 'Turma'  # Usa turmas normalizadas/agregadas
    turmas_disponiveis = sorted(df['Turma'].dropna().unique())
    label_turmas = "Turma(s) - Agregadas"
else:
    coluna_turma = 'Turma_Original'  # Usa turmas originais/separadas
    turmas_disponiveis = sorted(df['Turma_Original'].dropna().unique())
    label_turmas = "Turma(s) - Separadas"

turmas_sel = st.sidebar.multiselect(label_turmas, turmas_disponiveis)
if turmas_sel:
    df = df[df[coluna_turma].isin(turmas_sel)]

# Identificador anonimizado (para acompanhamento individual - LGPD)
ids_anonimizados = sorted(df['ID_Anonimizado'].dropna().unique())
id_anonimizado_sel = st.sidebar.selectbox(
    "🔒 Aluno (ID Anonimizado)", 
    ["<selecione>"] + ids_anonimizados,
    help="Formato: [Primeiras letras do ID] - [Iniciais do Nome]"
)

# ================= FUNÇÕES DE CÁLCULO DO TAMANHO DO EFEITO ==================
def calcular_d_cohen(df_in: pd.DataFrame, col_pre: str = 'Score_Pre', col_pos: str = 'Score_Pos') -> float:
    """Calcula d de Cohen para duas medidas (pré e pós) tratadas como grupos independentes.
    Retorna np.nan se não houver dados suficientes ou variância nula.
    Obs: Para medidas pareadas poderia-se usar d_av ou dz; aqui segue especificação do usuário.
    """
    if df_in is None or df_in.empty:
        return float('nan')
    pre = df_in[col_pre].dropna()
    pos = df_in[col_pos].dropna()
    n_pre, n_pos = len(pre), len(pos)
    if n_pre < 2 or n_pos < 2:
        return float('nan')
    m_pre, m_pos = pre.mean(), pos.mean()
    sd_pre, sd_pos = pre.std(ddof=1), pos.std(ddof=1)
    if (sd_pre == 0 and sd_pos == 0):
        return float('nan')
    pooled = math.sqrt(((n_pre - 1) * sd_pre**2 + (n_pos - 1) * sd_pos**2) / (n_pre + n_pos - 2)) if (n_pre + n_pos - 2) > 0 else float('nan')
    if pooled == 0 or np.isnan(pooled):
        return float('nan')
    return (m_pos - m_pre) / pooled

def classificar_geral(d: float) -> str:
    if np.isnan(d):
        return 'Sem dados'
    ad = abs(d)
    if ad < 0.2: return 'Trivial'
    if ad < 0.5: return 'Pequeno'
    if ad < 0.8: return 'Médio'
    return 'Grande'

def benchmark_especifico(d: float, prova: str) -> tuple[str, bool]:
    if np.isnan(d):
        return ('Sem dados', False)
    if prova == 'TDE':
        return ('Bom resultado' if d >= 0.40 else 'Ponto de atenção', d >= 0.40)
    # Vocabulário
    return ('Impacto significativo' if d >= 0.35 else 'Ponto de atenção', d >= 0.35)

# ================= FUNÇÕES DE CÁLCULO ==================
def calcular_d_cohen(df_in: pd.DataFrame, col_pre: str = 'Score_Pre', col_pos: str = 'Score_Pos') -> float:
    """Calcula d de Cohen para duas medidas (pré e pós) tratadas como grupos independentes.
    Retorna np.nan se não houver dados suficientes ou variância nula.
    """
    if df_in is None or df_in.empty:
        return float('nan')
    pre = df_in[col_pre].dropna()
    pos = df_in[col_pos].dropna()
    n_pre, n_pos = len(pre), len(pos)
    if n_pre < 2 or n_pos < 2:
        return float('nan')
    m_pre, m_pos = pre.mean(), pos.mean()
    sd_pre, sd_pos = pre.std(ddof=1), pos.std(ddof=1)
    if (sd_pre == 0 and sd_pos == 0):
        return float('nan')
    pooled = math.sqrt(((n_pre - 1) * sd_pre**2 + (n_pos - 1) * sd_pos**2) / (n_pre + n_pos - 2)) if (n_pre + n_pos - 2) > 0 else float('nan')
    if pooled == 0 or np.isnan(pooled):
        return float('nan')
    return (m_pos - m_pre) / pooled

def classificar_geral(d: float) -> str:
    if np.isnan(d):
        return 'Sem dados'
    ad = abs(d)
    if ad < 0.2: return 'Trivial'
    if ad < 0.5: return 'Pequeno'
    if ad < 0.8: return 'Médio'
    return 'Grande'

def benchmark_especifico(d: float, prova: str) -> tuple[str, bool]:
    if np.isnan(d):
        return ('Sem dados', False)
    if prova == 'TDE':
        return ('Bom resultado' if d >= 0.40 else 'Ponto de atenção', d >= 0.40)
    # Vocabulário
    return ('Impacto significativo' if d >= 0.35 else 'Ponto de atenção', d >= 0.35)

# ================= FUNÇÕES PARA CRIAR CARDS PERSONALIZADOS ==================
def criar_metric_card(valor, titulo, icone, cor_box=(0, 123, 255), cor_fonte=(255, 255, 255)):
    """Cria um card métrico personalizado com ícone FontAwesome"""
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    
    htmlstr = f"""<p style='background-color: rgb({cor_box[0]}, {cor_box[1]}, {cor_box[2]}, 0.85); 
                            color: rgb({cor_fonte[0]}, {cor_fonte[1]}, {cor_fonte[2]}, 0.95); 
                            font-size: 18px; 
                            font-weight: 600;
                            border-radius: 10px; 
                            padding: 20px 15px; 
                            text-align: center;
                            line-height: 1.4;
                            margin: 0;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <i class='{icone} fa-lg' style='margin-right: 10px;'></i> {valor}
                            <br><span style='font-size: 11px; 
                            font-weight: 300;
                            opacity: 0.9;
                            margin-top: 8px;
                            display: block;'>{titulo}</span></p>"""
    
    return lnk + htmlstr

# ================= OVERVIEW ==================
st.subheader("Resumo Filtrado")

# Primeira linha: métricas básicas
col1, col2, col3, col_turma, col_cohen= st.columns(5)

with col1:
    st.markdown(
        criar_metric_card(
            valor=len(df),
            titulo="Registros",
            icone="fas fa-database",
            cor_box=(52, 152, 219),  # Azul
            cor_fonte=(255, 255, 255)
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        criar_metric_card(
            valor=df['ID_Unico'].nunique(),
            titulo="Alunos Únicos",
            icone="fas fa-users",
            cor_box=(46, 204, 113),  # Verde
            cor_fonte=(255, 255, 255)
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        criar_metric_card(
            valor=df['Escola'].nunique(),
            titulo="Escolas",
            icone="fas fa-school",
            cor_box=(155, 89, 182),  # Roxo
            cor_fonte=(255, 255, 255)
        ),
        unsafe_allow_html=True
    )

# Segunda linha: Turmas + Card do Tamanho do Efeito
#col_turma, col_cohen = st.columns([1, 2])

with col_turma:
    # Contar turmas baseado na opção de agregação escolhida
    turmas_count = df[coluna_turma].nunique()
    turma_label = "Turmas Agregadas" if agregar_turmas else "Turmas Separadas"
    
    st.markdown(
        criar_metric_card(
            valor=turmas_count,
            titulo=turma_label,
            icone="fas fa-chalkboard-teacher",
            cor_box=(230, 126, 34),  # Laranja
            cor_fonte=(255, 255, 255)
        ),
        unsafe_allow_html=True
    )

with col_cohen:
    # ================= TAMANHO DO EFEITO (COHEN'S D) - CARD SIMPLES ==================
    # Calcular d de Cohen
    d_val = calcular_d_cohen(df)
    prova_norm = 'TDE' if prova_sel.upper().startswith('TDE') else 'VOCAB'
    cls_espec, ok_flag = benchmark_especifico(d_val, prova_norm if prova_norm=='TDE' else 'VOCAB')
    geral_cls = classificar_geral(d_val)

    # Determinar cores e ícone baseado no resultado
    if ok_flag:
        cor_box = (40, 167, 69)  # Verde
        cor_fonte = (255, 255, 255)
        icone = "fas fa-check-circle"
    elif not np.isnan(d_val):
        cor_box = (255, 193, 7)  # Amarelo/Âmbar
        cor_fonte = (0, 0, 0)
        icone = "fas fa-exclamation-triangle"
    else:
        cor_box = (108, 117, 125)  # Cinza
        cor_fonte = (255, 255, 255)
        icone = "fas fa-info-circle"

    val_str = '—' if np.isnan(d_val) else f"{d_val:.3f}"
    
    # Criar card seguindo o mesmo padrão dos outros
    st.markdown(
        criar_metric_card(
            valor=val_str,
            titulo="Tamanho do Efeito",
            icone=icone,
            cor_box=cor_box,
            cor_fonte=cor_fonte
        ),
        unsafe_allow_html=True
    )



def filtrar_dataset(base: pd.DataFrame) -> pd.DataFrame:
    df_f = base.copy()
    if escola_sel:
        df_f = df_f[df_f['Escola'].isin(escola_sel)]
    if fases_sel:
        df_f = df_f[df_f['Fase'].isin(fases_sel)]
    if turmas_sel:
        df_f = df_f[df_f['Turma'].isin(turmas_sel)]
    return df_f



# Distribuição de scores por fase usando boxplot
if not df.empty:
    # Transformar dados para formato longo para o boxplot
    df_boxplot = df.melt(
        id_vars=['Fase'], 
        value_vars=['Score_Pre', 'Score_Pos'],
        var_name='Momento', 
        value_name='Score'
    )
    # Renomear para nomes mais amigáveis
    df_boxplot['Momento'] = df_boxplot['Momento'].replace({
        'Score_Pre': 'Pré-Teste',
        'Score_Pos': 'Pós-Teste'
    })
    
    # Criar boxplot com média visível
    fig_fase = px.box(
        df_boxplot,
        x='Fase',
        y='Score',
        color='Momento',
        title='Distribuição Pré-Teste vs Pós-Teste por Fase (com Média)',
        labels={'Score': 'Score', 'Momento': 'Teste'},
        points='outliers'  # Mostra apenas outliers como pontos
    )
    
    # Adicionar linhas tracejadas de média para cada grupo
    # Calcular médias por Fase e Momento
    medias = df_boxplot.groupby(['Fase', 'Momento'])['Score'].mean().reset_index()
    medias = medias.rename(columns={'Score': 'Media'})
    
    # Cores para combinar com o boxplot (padrão plotly)
    cores_momento = {
        'Pré-Teste': '#636EFA',  # Azul
        'Pós-Teste': '#EF553B'   # Vermelho/Laranja
    }
    
    # Obter as fases únicas para definir a largura das linhas
    fases = sorted(df_boxplot['Fase'].unique())
    primeira_fase = fases[0] if len(fases) > 0 else None
    
    # Adicionar linhas tracejadas de média para cada fase e momento
    for fase in fases:
        for momento in ['Pré-Teste', 'Pós-Teste']:
            media_valor = medias[(medias['Fase'] == fase) & (medias['Momento'] == momento)]['Media'].values
            if len(media_valor) > 0:
                media_valor = float(media_valor[0])
                
                # Calcular offset para posicionar as linhas lado a lado (como os boxplots)
                # O offset varia dependendo se é Pré ou Pós-Teste
                offset = -0.2 if momento == 'Pré-Teste' else 0.2
                x_pos = fase + offset
                
                # Determinar se deve mostrar legenda (apenas para a primeira fase)
                mostrar_legenda = bool(fase == primeira_fase)
                
                fig_fase.add_trace(
                    go.Scatter(
                        x=[x_pos - 0.15, x_pos + 0.15],  # Linha horizontal com largura de 0.3
                        y=[media_valor, media_valor],
                        mode='lines',
                        line=dict(
                            color=cores_momento.get(momento, '#000000'),
                            width=2,
                            dash='dash'
                        ),
                        name=f'Média {momento}' if mostrar_legenda else None,
                        showlegend=mostrar_legenda,
                        hovertemplate=f'<b>Média {momento}</b><br>Fase: {fase}<br>Média: {media_valor:.2f}<extra></extra>'
                    )
                )
    
    fig_fase.update_layout(
        legend_title_text='Legenda',
        showlegend=True,
        hovermode='closest'
    )
    st.plotly_chart(fig_fase, use_container_width=True)

    # ---------------- EVOLUÇÃO COMPARATIVA HIERÁRQUICA (COORDENADAS PARALELAS) ----------------
    st.markdown("### Evolução Comparativa Hierárquica - Coordenadas Paralelas")
    st.caption("Visualize trajetórias longitudinais através das fases. Cada linha representa uma entidade (Escola/Turma/Aluno) evoluindo ao longo do tempo.")

    # Inicializar estados
    if 'nivel_visualizacao' not in st.session_state:
        st.session_state.nivel_visualizacao = 'Escolas'
    if 'escolas_filtradas' not in st.session_state:
        st.session_state.escolas_filtradas = []
    if 'turmas_filtradas' not in st.session_state:
        st.session_state.turmas_filtradas = []

    # Informativo sobre Coortes
    with st.expander("ℹ️ O que são Coortes?", expanded=False):
        st.markdown("""
        **Coortes representam grupos de alunos baseados na fase em que iniciaram o programa WordGen:**
        
        - **Coorte 1**: Alunos que **começaram na Fase 2** (primeira fase de avaliação)
        - **Coorte 2**: Alunos que **começaram na Fase 3** (entraram mais tarde no programa)
        - **Coorte 3**: Alunos que **começaram na Fase 4** (última fase de entrada)
        
        💡 **Por que separar por coorte?**  
        Cada coorte teve **diferentes tempos de exposição** ao programa WordGen e representa **momentos distintos** 
        de entrada no estudo longitudinal. Analisar por coorte permite:
        
        - Comparar alunos que iniciaram em **fases equivalentes**
        - Controlar o **efeito do tempo de programa** nas análises
        - Entender diferenças entre grupos que **entraram em momentos diferentes**
        
        📊 **Exemplo prático**:
        - Coorte 1 tem dados em Fases 2, 3 e 4 (trajetória completa)
        - Coorte 2 tem dados em Fases 3 e 4 (trajetória parcial)
        - Coorte 3 tem dados apenas na Fase 4 (snapshot inicial)
        
        🔍 **Dica**: Selecione "Todas" para visão geral ou uma coorte específica para análise focada.
        """)

    # Seletores de contexto (REDUZIDO - removido Tipo de Análise)
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        coorte_drill = st.selectbox(
            "🎓 Filtrar por Coorte:",
            options=['Todas', 'Coorte 1', 'Coorte 2', 'Coorte 3'],
            key='drill_coorte_selector',
            help="Coorte 1: iniciaram na Fase 2 | Coorte 2: iniciaram na Fase 3 | Coorte 3: iniciaram na Fase 4"
        )
    with col_sel2:
        nivel_viz = st.selectbox(
            "🔍 Nível de Visualização:",
            options=['Escolas', 'Turmas', 'Alunos'],
            key='nivel_visualizacao_selector',
            help="Escolha o nível de agregação dos dados"
        )
        st.session_state.nivel_visualizacao = nivel_viz

    # Preparar dados base usando a prova selecionada na SIDEBAR
    df_drill_base = df.copy()  # Usa o df já filtrado pela sidebar (prova, fases, escolas, turmas)
    
    # Filtrar por coorte se selecionado (e se a coluna existir)
    if coorte_drill != 'Todas':
        # Verificar quais colunas de coorte existem (prioridade: anonimizado > origem > padrão)
        if 'coorte_anonimizado' in df_drill_base.columns:
            col_coorte = 'coorte_anonimizado'
        elif 'Coorte_Origem' in df_drill_base.columns:
            col_coorte = 'Coorte_Origem'
        elif 'Coorte' in df_drill_base.columns:
            col_coorte = 'Coorte'
        else:
            st.warning(f"⚠️ Coluna de coorte não encontrada. Colunas disponíveis: {list(df_drill_base.columns)}")
            col_coorte = None
        
        if col_coorte:
            df_drill_base = df_drill_base[df_drill_base[col_coorte] == coorte_drill].copy()
    
    # Determinar colunas
    colunas_validas = True
    
    if 'escola_anonimizado' in df_drill_base.columns:
        col_escola = 'escola_anonimizado'
    elif 'Escola' in df_drill_base.columns:
        col_escola = 'Escola'
    else:
        st.error("❌ Coluna de escola não encontrada")
        colunas_validas = False
    
    if colunas_validas:
        if 'turma_anonimizado' in df_drill_base.columns:
            col_turma = 'turma_anonimizado'
        elif 'Turma' in df_drill_base.columns:
            col_turma = 'Turma'
        else:
            st.error("❌ Coluna de turma não encontrada")
            colunas_validas = False
    
    if colunas_validas:
        if 'aluno_anonimizado' in df_drill_base.columns:
            col_aluno = 'aluno_anonimizado'
        elif 'ID_Anonimizado' in df_drill_base.columns:
            col_aluno = 'ID_Anonimizado'
        elif 'Nome' in df_drill_base.columns:
            col_aluno = 'Nome'
        else:
            st.error("❌ Coluna de aluno não encontrada")
            colunas_validas = False
    
    if colunas_validas:
        if 'fase' in df_drill_base.columns:
            col_fase = 'fase'
        elif 'Fase' in df_drill_base.columns:
            col_fase = 'Fase'
        else:
            st.error("❌ Coluna de fase não encontrada")
            colunas_validas = False
    
    if colunas_validas:
        if 'Score_Pos' in df_drill_base.columns and 'Score_Pre' in df_drill_base.columns:
            df_drill_base['Delta'] = df_drill_base['Score_Pos'] - df_drill_base['Score_Pre']
            metrica_col = 'Delta'
        elif 'pontuacao_total' in df_drill_base.columns:
            metrica_col = 'pontuacao_total'
        else:
            st.error("❌ Colunas de pontuação não encontradas")
            colunas_validas = False

    if not colunas_validas:
        st.info("⚠️ A visualização não está disponível para esta configuração de dados.")
    elif df_drill_base.empty:
        coorte_texto = coorte_drill if coorte_drill != 'Todas' else 'filtros selecionados'
        st.warning(f"⚠️ Nenhum dado disponível para {prova_sel} com {coorte_texto}.")
    else:
        st.markdown("---")
        
        # Criar visualização de coordenadas paralelas usando Altair
        try:
            import altair as alt
            
            # Preparar dados baseado no nível de visualização
            if nivel_viz == 'Escolas':
                col_agrupamento = col_escola
                label_entidade = 'Escola'
            elif nivel_viz == 'Turmas':
                col_agrupamento = col_turma
                label_entidade = 'Turma'
            else:  # Alunos
                col_agrupamento = col_aluno
                label_entidade = 'Aluno'
            
            # Agregar dados por entidade e fase
            df_viz = df_drill_base.groupby([col_agrupamento, col_fase])[metrica_col].mean().reset_index()
            df_viz = df_viz.rename(columns={col_agrupamento: 'Entidade', col_fase: 'Fase', metrica_col: 'Valor'})
            
            # Filtros hierárquicos
            st.markdown("#### 🔽 Filtros Hierárquicos")
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                todas_escolas = sorted(df_drill_base[col_escola].dropna().unique())
                escolas_selecionadas = st.multiselect(
                    "🏫 Filtrar Escolas:",
                    options=todas_escolas,
                    default=st.session_state.escolas_filtradas if st.session_state.escolas_filtradas else [],
                    key='filtro_escolas_parallel'
                )
                st.session_state.escolas_filtradas = escolas_selecionadas
            
            # Aplicar filtro de escolas
            df_drill_filtrado = df_drill_base.copy()
            if escolas_selecionadas:
                df_drill_filtrado = df_drill_filtrado[df_drill_filtrado[col_escola].isin(escolas_selecionadas)]
            
            with col_filtro2:
                turmas_selecionadas = []  # Inicializar para evitar erro no caption posterior
                if nivel_viz in ['Turmas', 'Alunos']:
                    todas_turmas = sorted(df_drill_filtrado[col_turma].dropna().unique())
                    turmas_selecionadas = st.multiselect(
                        "🎓 Filtrar Turmas:",
                        options=todas_turmas,
                        default=st.session_state.turmas_filtradas if st.session_state.turmas_filtradas else [],
                        key='filtro_turmas_parallel',
                        disabled=not escolas_selecionadas
                    )
                    st.session_state.turmas_filtradas = turmas_selecionadas
                    
                    if turmas_selecionadas:
                        df_drill_filtrado = df_drill_filtrado[df_drill_filtrado[col_turma].isin(turmas_selecionadas)]
                else:
                    st.info("👈 Disponível ao visualizar Turmas ou Alunos")
            
            with col_filtro3:
                alunos_selecionados = []  # Inicializar para evitar erro no caption posterior
                if nivel_viz == 'Alunos':
                    todos_alunos = sorted(df_drill_filtrado[col_aluno].dropna().unique())
                    alunos_selecionados = st.multiselect(
                        "👨‍🎓 Filtrar Alunos:",
                        options=todos_alunos[:50],  # Limitar a 50 para performance
                        key='filtro_alunos_parallel',
                        disabled=not turmas_selecionadas
                    )
                    
                    if alunos_selecionados:
                        df_drill_filtrado = df_drill_filtrado[df_drill_filtrado[col_aluno].isin(alunos_selecionados)]
                else:
                    st.info("👈 Disponível ao visualizar Alunos")
            
            # Reagregar dados após filtros
            df_viz = df_drill_filtrado.groupby([col_agrupamento, col_fase])[metrica_col].mean().reset_index()
            df_viz = df_viz.rename(columns={col_agrupamento: 'Entidade', col_fase: 'Fase', metrica_col: 'Valor'})
            
            if df_viz.empty:
                st.warning("⚠️ Nenhum dado disponível com os filtros selecionados.")
            else:
                # Criar gráfico de coordenadas paralelas com Altair
                st.markdown(f"#### 📊 Trajetórias de {label_entidade}s ao Longo das Fases")
                
                # Pivot para formato wide (necessário para parallel coordinates)
                df_wide = df_viz.pivot(index='Entidade', columns='Fase', values='Valor').reset_index()
                
                # Criar lista de colunas de fase disponíveis
                fases_disponiveis = [col for col in df_wide.columns if col != 'Entidade']
                
                if len(fases_disponiveis) < 2:
                    st.warning("⚠️ Necessário pelo menos 2 fases para visualização de trajetórias.")
                else:
                    # Transformar para formato longo novamente para Altair
                    df_plot = df_viz.copy()
                    df_plot['Fase'] = df_plot['Fase'].astype(str)
                    
                    # Criar gráfico com Altair
                    brush = alt.selection_interval(encodings=['y'])
                    
                    base = alt.Chart(df_plot).mark_line(
                        point=True,
                        strokeWidth=2,
                        opacity=0.6
                    ).encode(
                        x=alt.X('Fase:O', axis=alt.Axis(title='Fase', labelAngle=0)),
                        y=alt.Y('Valor:Q', axis=alt.Axis(title=f'{metrica_col}')),
                        color=alt.Color('Entidade:N', legend=None if len(df_plot['Entidade'].unique()) > 15 else alt.Legend(title=label_entidade)),
                        detail='Entidade:N',
                        tooltip=[
                            alt.Tooltip('Entidade:N', title=label_entidade),
                            alt.Tooltip('Fase:O', title='Fase'),
                            alt.Tooltip('Valor:Q', title=metrica_col, format='.2f')
                        ],
                        opacity=alt.condition(brush, alt.value(0.8), alt.value(0.2))
                    ).properties(
                        width=800,
                        height=500,
                        title=f'Evolução de {label_entidade}s: {prova_sel} - {coorte_drill}'
                    ).add_params(brush)
                    
                    # Adicionar linha de média
                    media_por_fase = df_plot.groupby('Fase')['Valor'].mean().reset_index()
                    
                    linha_media = alt.Chart(media_por_fase).mark_line(
                        strokeWidth=4,
                        color='red',
                        strokeDash=[5, 5]
                    ).encode(
                        x='Fase:O',
                        y='Valor:Q'
                    )
                    
                    pontos_media = alt.Chart(media_por_fase).mark_point(
                        size=150,
                        color='red',
                        shape='diamond'
                    ).encode(
                        x='Fase:O',
                        y='Valor:Q',
                        tooltip=[
                            alt.Tooltip('Fase:O', title='Fase'),
                            alt.Tooltip('Valor:Q', title='Média', format='.2f')
                        ]
                    )
                    
                    chart_final = (base + linha_media + pontos_media).configure_axis(
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_title(
                        fontSize=16,
                        anchor='start'
                    )
                    
                    st.altair_chart(chart_final, use_container_width=True)
                    
                    # Estatísticas da seleção
                    st.markdown("#### 📈 Estatísticas da Seleção")
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    n_entidades = df_viz['Entidade'].nunique()
                    
                    # Contar alunos únicos nos dados filtrados (importante para ver impacto do filtro de coorte)
                    n_alunos_unicos = df_drill_filtrado[col_aluno].nunique() if col_aluno in df_drill_filtrado.columns else 0
                    
                    media_geral = df_viz['Valor'].mean()
                    
                    # Calcular tendência (comparar primeira e última fase)
                    fases_ord = sorted(df_viz['Fase'].unique())
                    if len(fases_ord) >= 2:
                        primeira_fase = df_viz[df_viz['Fase'] == fases_ord[0]]['Valor'].mean()
                        ultima_fase = df_viz[df_viz['Fase'] == fases_ord[-1]]['Valor'].mean()
                        tendencia = ultima_fase - primeira_fase
                        tendencia_icon = "📈" if tendencia > 0 else "📉" if tendencia < 0 else "➡️"
                    else:
                        tendencia = 0
                        tendencia_icon = "➡️"
                    
                    variancia = df_viz['Valor'].std()
                    
                    with col_stat1:
                        # Mostrar número de entidades E número de alunos únicos
                        valor_card1 = f"{n_entidades} / {n_alunos_unicos}"
                        titulo_card1 = f"{label_entidade}s / Alunos"
                        
                        st.markdown(
                            criar_metric_card(
                                valor=valor_card1,
                                titulo=titulo_card1,
                                icone="fas fa-layer-group",
                                cor_box=(52, 152, 219),
                                cor_fonte=(255, 255, 255)
                            ),
                            unsafe_allow_html=True
                        )
                    
                    with col_stat2:
                        st.markdown(
                            criar_metric_card(
                                valor=f"{media_geral:.2f}",
                                titulo=f"{metrica_col} Médio",
                                icone="fas fa-chart-line",
                                cor_box=(46, 204, 113),
                                cor_fonte=(255, 255, 255)
                            ),
                            unsafe_allow_html=True
                        )
                    
                    with col_stat3:
                        st.markdown(
                            criar_metric_card(
                                valor=f"{tendencia_icon} {tendencia:+.2f}",
                                titulo="Tendência",
                                icone="fas fa-arrow-trend-up" if tendencia > 0 else "fas fa-arrow-trend-down",
                                cor_box=(155, 89, 182),
                                cor_fonte=(255, 255, 255)
                            ),
                            unsafe_allow_html=True
                        )
                    
                    with col_stat4:
                        st.markdown(
                            criar_metric_card(
                                valor=f"±{variancia:.2f}",
                                titulo="Variabilidade",
                                icone="fas fa-chart-area",
                                cor_box=(230, 126, 34),
                                cor_fonte=(255, 255, 255)
                            ),
                            unsafe_allow_html=True
                        )
                    
                    # Informativo sobre os dados das estatísticas
                    filtros_ativos = []
                    if coorte_drill != 'Todas':
                        filtros_ativos.append(f"**{coorte_drill}**")
                    if escolas_selecionadas:
                        filtros_ativos.append(f"**{len(escolas_selecionadas)} escola(s)**")
                    if nivel_viz in ['Turmas', 'Alunos'] and turmas_selecionadas:
                        filtros_ativos.append(f"**{len(turmas_selecionadas)} turma(s)**")
                    if nivel_viz == 'Alunos' and alunos_selecionados:
                        filtros_ativos.append(f"**{len(alunos_selecionados)} aluno(s)**")
                    
                    if filtros_ativos:
                        st.caption(f"📊 Estatísticas calculadas com base nos filtros: {', '.join(filtros_ativos)}")
                    else:
                        st.caption(f"📊 Estatísticas calculadas com todos os dados de **{prova_sel}**")
        
        except ImportError:
            st.error("❌ Biblioteca Altair não encontrada. Instale com: `pip install altair`")
            st.info("💡 Usando visualização alternativa com Plotly...")
            
            # Fallback para Plotly se Altair não estiver disponível
            if nivel_viz == 'Escolas':
                col_agrupamento = col_escola
            elif nivel_viz == 'Turmas':
                col_agrupamento = col_turma
            else:
                col_agrupamento = col_aluno
            
            df_viz = df_drill_base.groupby([col_agrupamento, col_fase])[metrica_col].mean().reset_index()
            
            fig = px.line(
                df_viz,
                x=col_fase,
                y=metrica_col,
                color=col_agrupamento,
                markers=True,
                title=f'Evolução - {nivel_viz}'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ================= ANÁLISE GRANULAR POR QUESTÃO ==================
st.markdown("### Análise Granular por Questão")
st.caption("Análise detalhada do desempenho por questão específica, mostrando evolução e competências melhor assimiladas.")

if not df.empty:
    # Identificar colunas de questões (Q1_Pre, Q1_Pos, Q2_Pre, Q2_Pos, etc.)
    questao_cols = [col for col in df.columns if col.startswith('Q') and ('_Pre' in col or '_Pos' in col)]
    
    if questao_cols:
        # Extrair números das questões disponíveis
        questoes_nums = set()
        for col in questao_cols:
            if '_Pre' in col:
                q_num = col.split('_Pre')[0]
                questoes_nums.add(q_num)
        
        questoes_nums = sorted(list(questoes_nums), key=lambda x: int(x[1:]))  # Ordenar Q1, Q2, Q3...
        
        # 1. Calcular percentual de acerto por questão
        analise_questoes = []
        
        for q_num in questoes_nums:
            col_pre = f"{q_num}_Pre"
            col_pos = f"{q_num}_Pos"
            
            if col_pre in df.columns and col_pos in df.columns:
                # Calcular percentuais (assumindo que 1 = acerto, 0 = erro)
                pct_pre = (df[col_pre].sum() / df[col_pre].count()) * 100 if df[col_pre].count() > 0 else 0
                pct_pos = (df[col_pos].sum() / df[col_pos].count()) * 100 if df[col_pos].count() > 0 else 0
                variacao = pct_pos - pct_pre
                
                analise_questoes.append({
                    'Questão': q_num,
                    '% Acerto Pré': pct_pre,
                    '% Acerto Pós': pct_pos,
                    'Variação (%)': variacao
                })
        
        if analise_questoes:
            df_analise = pd.DataFrame(analise_questoes)
            
            # 2. Tabela de Evolução por Competência (ordenada pela maior variação)
            df_analise_sorted = df_analise.sort_values('Variação (%)', ascending=False)
            
            st.markdown("#### Tabela de Evolução por Competência")
            st.caption("Questões ordenadas pela maior variação (melhoria) no percentual de acerto")
            
            # Formatação da tabela com cores
            def style_variacao(val):
                if pd.isna(val):
                    return ''
                elif val > 0:
                    return 'background-color: #e8f5e8; color: #2d5016; font-weight: bold'  # Verde
                elif val < 0:
                    return 'background-color: #fdf2f2; color: #721c24; font-weight: bold'  # Vermelho
                else:
                    return 'background-color: #f1f3f4; color: #495057; font-weight: bold'  # Cinza
            
            styled_analise = (df_analise_sorted.style
                             .map(style_variacao, subset=['Variação (%)'])
                             .format({
                                 '% Acerto Pré': '{:.1f}%',
                                 '% Acerto Pós': '{:.1f}%',
                                 'Variação (%)': '{:+.1f}%'
                             }))
            
            st.dataframe(styled_analise, use_container_width=True)
            # 3. Gráfico de Evolução por Questão
            st.markdown("#### Gráfico de Evolução por Questão")
            st.caption("Comparação visual do desempenho pré vs pós por questão. Linhas conectam os percentuais, mostrando a evolução.")
            
            # Preparar dados para o gráfico lollipop
            df_lollipop = df_analise.copy()
            df_lollipop = df_lollipop.sort_values('Variação (%)', ascending=True)  # Melhor variação no topo
            
            # Criar gráfico lollipop usando plotly
            fig_lollipop = go.Figure()
            
            # Adicionar linhas conectoras
            for i, row in df_lollipop.iterrows():
                fig_lollipop.add_trace(go.Scatter(
                    x=[row['% Acerto Pré'], row['% Acerto Pós']],
                    y=[row['Questão'], row['Questão']],
                    mode='lines',
                    line=dict(color='lightgray', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Adicionar pontos do Pré-teste
            fig_lollipop.add_trace(go.Scatter(
                x=df_lollipop['% Acerto Pré'],
                y=df_lollipop['Questão'],
                mode='markers',
                marker=dict(color='#dc3545', size=8),
                name='Pré-Teste',
                hovertemplate='<b>%{y}</b><br>Pré-Teste: %{x:.1f}%<extra></extra>'
            ))
            
            # Adicionar pontos do Pós-teste
            fig_lollipop.add_trace(go.Scatter(
                x=df_lollipop['% Acerto Pós'],
                y=df_lollipop['Questão'],
                mode='markers',
                marker=dict(color='#28a745', size=8),
                name='Pós-Teste',
                hovertemplate='<b>%{y}</b><br>Pós-Teste: %{x:.1f}%<extra></extra>'
            ))
            
            # Adicionar linha horizontal separando questões com variação positiva/neutra das negativas
            # Encontrar a posição da linha divisória (entre variação >= 0 e < 0)
            questoes_positivas = df_lollipop[df_lollipop['Variação (%)'] >= 0]
            questoes_negativas = df_lollipop[df_lollipop['Variação (%)'] < 0]
            
            if len(questoes_negativas) > 0 and len(questoes_positivas) > 0:
                # Encontrar a posição entre a última questão negativa e a primeira positiva
                ultima_negativa_idx = df_lollipop[df_lollipop['Variação (%)'] < 0].index[-1]
                primeira_positiva_idx = df_lollipop[df_lollipop['Variação (%)'] >= 0].index[0]
                
                # Como os dados estão ordenados por variação crescente, a linha vai entre essas posições
                posicao_linha = (df_lollipop.index.get_loc(ultima_negativa_idx) + 
                               df_lollipop.index.get_loc(primeira_positiva_idx)) / 2
                
                # Adicionar linha horizontal
                fig_lollipop.add_hline(
                    y=posicao_linha,
                    line_dash="dash",
                    line_color="orange",
                    line_width=2,
                    opacity=0.7,
                    annotation_text="Limite Melhoria/Declínio",
                    annotation_position="top right",
                    annotation_font_size=12,
                    annotation_font_color="orange"
                )
            
            fig_lollipop.update_layout(
                title='Evolução do Percentual de Acerto por Questão',
                xaxis_title='Percentual de Acerto (%)',
                yaxis_title='Questão',
                showlegend=True,
                height=max(400, len(questoes_nums) * 25),  # Altura dinâmica baseada no número de questões
                margin=dict(l=80, r=20, t=60, b=40)
            )
            
            st.plotly_chart(fig_lollipop, use_container_width=True)
            
            # Insights adicionais
            with st.expander("💡 Análise Granular", expanded=False):
                melhor_questao = df_analise_sorted.iloc[0]
                pior_questao = df_analise_sorted.iloc[-1]
                media_variacao = df_analise['Variação (%)'].mean()
                
                st.markdown(f"""
                **📈 Maior Melhoria:** {melhor_questao['Questão']} com variação de **{melhor_questao['Variação (%)']:+.1f}%**
                
                **📉 Menor Melhoria:** {pior_questao['Questão']} com variação de **{pior_questao['Variação (%)']:+.1f}%**
                
                **📊 Variação Média:** **{media_variacao:+.1f}%** entre todas as questões
                
                **🎯 Questões com Melhoria Significativa (>10% na variação):** {len(df_analise[df_analise['Variação (%)'] > 10])} questões
                
                **⚠️ Questões com Declínio:** {len(df_analise[df_analise['Variação (%)'] < 0])} questões
                """)
        else:
            st.info("Não foram encontradas questões com dados válidos para análise.")
    else:
        st.info("Dataset não contém colunas de questões individuais (Q1_Pre, Q1_Pos, etc.).")
else:
    st.info("Nenhum dado disponível para análise granular.")

# ================= EVOLUÇÃO INDIVIDUAL ==================
st.subheader("Evolução Individual (Pré vs Pós por Fase)")
if id_anonimizado_sel and id_anonimizado_sel != "<selecione>":
    df_ind = df[df['ID_Anonimizado'] == id_anonimizado_sel].sort_values('Fase')
    if df_ind.empty:
        st.info("Aluno não encontrado com filtros atuais.")
    else:
        # Tabela detalhada
        df_show = df_ind[['Fase','Escola','Turma','Score_Pre','Score_Pos']].copy()
        df_show['Delta'] = df_show['Score_Pos'] - df_show['Score_Pre']
        # Renomear colunas para nomes mais amigáveis
        df_show = df_show.rename(columns={
            'Score_Pre': 'Pré-Teste',
            'Score_Pos': 'Pós-Teste'
        })
        
        # Função para estilizar a coluna Delta com cores melhoradas e fonte em negrito
        def style_delta(val):
            if pd.isna(val):
                return ''
            elif val > 0:
                return 'background-color: #e8f5e8; color: #2d5016; font-weight: bold; border-left: 4px solid #28a745'  # Verde mais suave
            elif val == 0:
                return 'background-color: #f1f3f4; color: #495057; font-weight: bold; border-left: 4px solid #6c757d'  # Cinza neutro
            else:  # val < 0
                return 'background-color: #fdf2f2; color: #721c24; font-weight: bold; border-left: 4px solid #dc3545'  # Vermelho mais suave
        
        # Aplicar estilo à tabela com formatação de números
        styled_df = (df_show.style
                     .map(style_delta, subset=['Delta'])
                     .format({
                         'Pré-Teste': '{:.1f}',
                         'Pós-Teste': '{:.1f}',
                         'Delta': '{:+.1f}'  # Formato com sinal + ou -
                     }))
        st.dataframe(styled_df, use_container_width=True)

        # Gráficos lado a lado: Pré/Pós-Teste e Delta
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de Pré-Teste vs Pós-Teste (sem Delta)
            long_scores = (df_ind.melt(id_vars=['Fase'], value_vars=['Score_Pre','Score_Pos'],
                                      var_name='Momento', value_name='Score')
                                 .replace({'Score_Pre':'Pré-Teste','Score_Pos':'Pós-Teste'}))
            
            fig_scores = px.line(long_scores, x='Fase', y='Score', color='Momento', markers=True,
                               title=f'Evolução Pré vs Pós - {id_anonimizado_sel}',
                               labels={'Momento': 'Teste'})
            
            # Configurar eixo X com ticks discretos
            fig_scores.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=[2, 3, 4],
                    ticktext=['2', '3', '4'],
                    title='Fase'
                )
            )
            st.plotly_chart(fig_scores, use_container_width=True)
        
        with col2:
            # Gráfico somente do Delta
            df_delta = df_ind.copy()
            df_delta['Delta'] = df_delta['Score_Pos'] - df_delta['Score_Pre']
            
            fig_delta = px.line(df_delta, x='Fase', y='Delta', markers=True,
                              title=f'Evolução Delta - {id_anonimizado_sel}',
                              labels={'Delta': 'Delta (Pós - Pré)'})
            
            # Configurar eixo X com ticks discretos e adicionar linha zero de referência
            fig_delta.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=[2, 3, 4],
                    ticktext=['2', '3', '4'],
                    title='Fase'
                )
            )
            # Adicionar linha horizontal no zero para referência
            fig_delta.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            st.plotly_chart(fig_delta, use_container_width=True)

        # Deltas
        # fig_delta = px.bar(df_show, x='Fase', y='Delta', title='Delta (Pós - Pré) por Fase',
        #                    text='Delta')
        # st.plotly_chart(fig_delta, use_container_width=True)
else:
    st.info("Selecione um aluno para ver evolução individual.")

# (Seção de continuidade longitudinal removida conforme solicitação do usuário)
# (Seção de distribuição de deltas removida conforme solicitação do usuário)

# ================= FOOTER ==================
st.markdown("---")
st.caption("Dashboard desenvolvido por Elton Sarmanho • Utilize filtros na barra lateral para refinar a análise.")

