import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# ================= HEADER ====================
st.title("📊 Dashboard Longitudinal - WordGen")
st.markdown("""
Este painel permite:
- Filtrar por Escola / Turma / Fase / Prova
- Acompanhar evolução individual (pré x pós) por fase
""")

# ================= LOAD DATA =================
tde_df, vocab_df = load_data()

PROVAS = {"TDE": tde_df, "VOCABULÁRIO": vocab_df}

# ================= SIDEBAR ===================
st.sidebar.header("Filtros")
prova_sel = st.sidebar.selectbox("Prova", list(PROVAS.keys()))
df = PROVAS[prova_sel]

# Escolas (se vazio, mantém todas)
escolas = sorted(df['Escola'].dropna().unique())
escola_sel = st.sidebar.multiselect("Escola(s)", escolas, default=[])
if escola_sel:
    df = df[df['Escola'].isin(escola_sel)]

# Fases
fases = sorted(df['Fase'].dropna().unique())
fases_sel = st.sidebar.multiselect("Fase(s)", fases, default=fases)
if fases_sel:
    df = df[df['Fase'].isin(fases_sel)]

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

# Nome (para acompanhamento individual)
nomes = sorted(df['Nome'].dropna().unique())
nome_sel = st.sidebar.selectbox("Aluno (Nome Completo)", ["<selecione>"] + nomes)

# ================= OVERVIEW ==================
st.subheader("Resumo Filtrado")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", len(df))
col2.metric("Alunos únicos (Nome)", df['Nome'].nunique())
col3.metric("Escolas", df['Escola'].nunique())
# Contar turmas baseado na opção de agregação escolhida
turmas_count = df[coluna_turma].nunique()
turma_label = "Turmas (Agregadas)" if agregar_turmas else "Turmas (Separadas)"
col4.metric(turma_label, turmas_count)

# ================= EFFECT SIZE (COHEN'S D) ==================
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

def filtrar_dataset(base: pd.DataFrame) -> pd.DataFrame:
    df_f = base.copy()
    if escola_sel:
        df_f = df_f[df_f['Escola'].isin(escola_sel)]
    if fases_sel:
        df_f = df_f[df_f['Fase'].isin(fases_sel)]
    if turmas_sel:
        df_f = df_f[df_f['Turma'].isin(turmas_sel)]
    return df_f

with st.expander('Tamanho do Efeito (d de Cohen)', expanded=True):
    # Usa o dataset filtrado atual (df) conforme PROVA selecionada
    d_val = calcular_d_cohen(df)
    prova_norm = 'TDE' if prova_sel.upper().startswith('TDE') else 'VOCAB'
    cls_espec, ok_flag = benchmark_especifico(d_val, prova_norm if prova_norm=='TDE' else 'VOCAB')
    geral_cls = classificar_geral(d_val)

    def card_unico(color_bg: str, titulo: str, valor: float, cls: str, geral: str, ok: bool):
        val_str = '—' if np.isnan(valor) else f"{valor:.2f}"
        icon = '✅' if ok else ('⚠️' if not np.isnan(valor) else '')
        html = f"""
        <div style='background:{color_bg};padding:14px 18px;border-radius:10px;margin-bottom:6px;'>
          <span style='font-weight:650;font-size:15px;'>{titulo}</span><br>
          <span style='font-size:30px;font-weight:700;'>{val_str}</span> {icon}<br>
          <span style='font-size:13px;'>Benchmark: {cls} • Geral: {geral}</span>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    cor = '#1b7837' if ok_flag else '#fdb863'
    titulo_card = f"{prova_sel} - d de Cohen"
    card_unico(cor, titulo_card, d_val, cls_espec, geral_cls, ok_flag)

    st.caption('Critérios: TDE ≥ 0.40 (Hattie, 2009); Vocabulário ≥ 0.35 (Marulis & Neuman, 2010); Geral (Cohen, 1988): 0.2 pequeno, 0.5 médio, 0.8 grande. Valores negativos indicam queda.')

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
    
    fig_fase = px.box(
        df_boxplot,
        x='Fase',
        y='Score',
        color='Momento',
        title='Distribuição Pré-Teste vs Pós-Teste por Fase',
        labels={'Score': 'Score', 'Momento': 'Teste'},
        points='outliers'  # Mostra apenas outliers como pontos
    )
    fig_fase.update_layout(
        legend_title_text='Teste',
        showlegend=True
    )
    st.plotly_chart(fig_fase, use_container_width=True)

    # ---------------- EVOLUÇÃO AGRUPADA POR ESCOLA (Plotly Line) ----------------
    st.markdown("### Evolução Comparativa Hierárquica (Drill-Down)")
    st.caption("Cada linha representa a média de Delta (Pós - Pré) por fase. **Clique em uma linha** para navegar: Escola → Turma → Aluno.")

    # Estado do drill-down usando session_state
    if 'drill_level' not in st.session_state:
        st.session_state.drill_level = 'escola'
    if 'selected_escola' not in st.session_state:
        st.session_state.selected_escola = None
    if 'selected_turma' not in st.session_state:
        st.session_state.selected_turma = None
    if 'analise_tipo' not in st.session_state:
        st.session_state.analise_tipo = None
    if 'selected_coorte' not in st.session_state:
        st.session_state.selected_coorte = None

    # Breadcrumb navigation - Sistema Híbrido
    if st.session_state.drill_level == 'escola':
        col_nav1 = st.columns([1])[0]
        with col_nav1:
            st.button("🏠 Escolas", type="primary", disabled=True)
    elif st.session_state.drill_level == 'escolha_analise':
        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button("🏠 Escolas", type="secondary"):
                st.session_state.drill_level = 'escola'
                st.session_state.selected_escola = None
                st.session_state.analise_tipo = None
                st.rerun()
        with col_nav2:
            st.button(f"🏫 {st.session_state.selected_escola}", type="primary", disabled=True)
    else:
        # Navegação para níveis mais profundos
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 2])
        with col_nav1:
            if st.button("🏠 Escolas", type="secondary"):
                st.session_state.drill_level = 'escola'
                st.session_state.selected_escola = None
                st.session_state.analise_tipo = None
                st.session_state.selected_turma = None
                st.session_state.selected_coorte = None
                st.rerun()
        
        with col_nav2:
            if st.session_state.selected_escola and st.button(f"🏫 {st.session_state.selected_escola}", type="secondary"):
                st.session_state.drill_level = 'escolha_analise'
                st.session_state.selected_turma = None
                st.session_state.selected_coorte = None
                st.rerun()
        
        with col_nav3:
            if st.session_state.analise_tipo:
                tipo_icon = "👥" if st.session_state.analise_tipo == 'coorte' else "📊"
                tipo_nome = "Coortes" if st.session_state.analise_tipo == 'coorte' else "Turmas"
                st.button(f"{tipo_icon} {tipo_nome}", type="primary" if st.session_state.drill_level in ['coorte', 'serie'] else "secondary", disabled=True)
        
        with col_nav4:
            if st.session_state.selected_coorte:
                st.button(f"🎓 {st.session_state.selected_coorte}", type="primary", disabled=True)
            elif st.session_state.selected_turma:
                st.button(f"� {st.session_state.selected_turma}", type="primary", disabled=True)

    with st.expander("Opções avançadas de visualização", expanded=False):
        st.info("💡 **Nova funcionalidade**: Use o filtro '🔄 Agregar turmas por ano' na barra lateral para controlar como as turmas são exibidas no drill-down.")
        agrupar = st.checkbox("Agrupar nomes equivalentes de escolas", value=True, help="Normaliza acentos, caixa e remove termos comuns.")
        preencher_faltantes = st.checkbox("Preencher fases ausentes com média da fase", value=True)
        normalizar = st.checkbox("Mostrar valores normalizados (z-score por fase)", value=False, help="Z-score é uma medida de distância para a média de um conjunto de dados. Valores positivos indicam acima da média, negativos abaixo. Útil para comparar tendências entre escolas com diferentes níveis de desempenho.")
        ordenar = st.checkbox("Ordenar legenda por média de Delta (desc)", value=True)

    def normaliza_escola(nome: str) -> str:
        if pd.isna(nome):
            return nome
        s = unicodedata.normalize('NFD', nome)
        s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn').upper()
        s = re.sub(r"[^A-Z0-9 ]+", " ", s)
        s = re.sub(r"\b(EMEB|EMEF|EME|ESCOLA MUNICIPAL|ESC MUNICIPAL|ESC MUN|ESCOLA)\b", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def criar_grafico_drill(df_data, agrupamento_col, titulo, y_col, y_label, 
                           custom_cols, nivel_drill, click_callback=None):
        """Função auxiliar para criar gráficos de drill-down"""
        if df_data.empty:
            st.info(f"Sem dados suficientes para plotar {titulo.lower()}.")
            return None
            
        # Ordenar por média se solicitado
        if ordenar:
            media_por_grupo = df_data.groupby(agrupamento_col)['Delta'].mean()
            ordem = media_por_grupo.sort_values(ascending=False).index
        else:
            ordem = sorted(df_data[agrupamento_col].unique())
        
        df_data[agrupamento_col] = pd.Categorical(df_data[agrupamento_col], 
                                                  categories=ordem, ordered=True)
        df_data = df_data.sort_values([agrupamento_col, 'Fase'])
        
        # Criar coluna numérica para eixo ordinal
        fase_map = {'2':2,'3':3,'4':4}
        df_data['FaseNum'] = df_data['Fase'].astype(str).map(fase_map)
        
        fig = px.line(
            df_data,
            x='FaseNum', y=y_col, color=agrupamento_col,
            category_orders={agrupamento_col: list(ordem)},
            custom_data=custom_cols,
            markers=True,
            labels={'FaseNum':'Fase', agrupamento_col: titulo.split()[0], y_col: y_label},
            title=titulo
        )
        
        # Template de hover adaptativo baseado no tipo de drill
        if nivel_drill == 'coorte' and len(custom_cols) >= 4:
            hover_template = (
                f'<b>%{{customdata[0]}}</b><br>'
                'Fase: %{x}<br>'
                f'{y_label}: %{{y:.2f}}<br>'
                'Delta Real: %{customdata[1]:.2f}<br>'
                'Média Geral Delta: %{customdata[2]:.2f}<br>'
                'Nº Alunos: %{customdata[3]}<extra></extra>'
            )
        else:
            hover_template = (
                f'<b>%{{customdata[0]}}</b><br>'
                'Fase: %{x}<br>'
                f'{y_label}: %{{y:.2f}}<br>'
                'Delta Real: %{customdata[1]:.2f}<br>'
                'Média Geral Delta: %{customdata[2]:.2f}<extra></extra>'
            )
        
        fig.update_traces(hovertemplate=hover_template, opacity=0.8)
        fig.update_layout(
            legend_title_text=titulo.split()[0],
            yaxis_title=y_label,
            xaxis=dict(tickmode='array', tickvals=[2,3,4], ticktext=['2','3','4'], title='Fase'),
            clickmode='event+select'
        )
        
        return fig

    # Preparar dados base
    df_lin = df.copy()
    df_lin['Delta'] = df_lin['Score_Pos'] - df_lin['Score_Pre']
    if agrupar:
        df_lin['Escola_Base'] = df_lin['Escola'].apply(normaliza_escola)
    else:
        df_lin['Escola_Base'] = df_lin['Escola']
    
    # Adicionar coluna de turma baseada na escolha do usuário
    df_lin['Turma_Drill'] = df_lin[coluna_turma]

    # Normalização opcional
    if normalizar:
        y_col = 'Delta_Vis'
        y_label = 'Delta (z-score)'
    else:
        y_col = 'Delta'
        y_label = 'Delta (Pós - Pré)'

    # Lógica do drill-down híbrido baseada no nível atual
    if st.session_state.drill_level == 'escola':
        # NÍVEL 1: ESCOLAS
        st.markdown("#### 🏠 Análise por Escola")
        st.caption("Clique em uma linha para ver as turmas dessa escola")
        
        agrup_mean = (df_lin.groupby(['Escola_Base','Fase'])['Delta']
                            .mean()
                            .reset_index())
        
        # Reindex para preencher fases faltantes se necessário
        if preencher_faltantes:
            fases_ord = sorted(set(fases_sel))
            todas = pd.MultiIndex.from_product([agrup_mean['Escola_Base'].unique(), fases_ord], 
                                             names=['Escola_Base','Fase'])
            agrup_mean = (agrup_mean.set_index(['Escola_Base','Fase'])
                                   .reindex(todas)
                                   .reset_index())
            # Preencher valores faltantes com média da fase
            fase_means = agrup_mean.groupby('Fase')['Delta'].transform(lambda s: s.fillna(s.mean()))
            agrup_mean['Delta'] = agrup_mean['Delta'].fillna(fase_means)

        # Remover escolas com menos de 2 valores não nulos
        valid_counts = agrup_mean.dropna(subset=['Delta']).groupby('Escola_Base')['Delta'].count()
        keep_escolas = valid_counts[valid_counts >= 2].index
        agrup_mean = agrup_mean[agrup_mean['Escola_Base'].isin(keep_escolas)]

        if not agrup_mean.empty:
            # Normalização opcional apenas para a visualização
            if normalizar:
                agrup_mean['Delta_Vis'] = agrup_mean.groupby('Fase')['Delta'].transform(
                    lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

            agrup_mean['Fase'] = pd.Categorical(agrup_mean['Fase'], 
                                              categories=sorted(set(fases_sel)), ordered=True)
            
            # Adicionar média geral para hover
            media_geral = agrup_mean.groupby('Escola_Base')['Delta'].transform('mean')
            agrup_mean['Media_Geral_Delta'] = media_geral
            
            custom_cols = ['Escola_Base','Delta','Media_Geral_Delta']
            
            fig_escolas = criar_grafico_drill(
                agrup_mean, 'Escola_Base', 'Evolução por Escola', 
                y_col, y_label, custom_cols, 'escola'
            )
            
            if fig_escolas:
                # Capturar cliques no gráfico
                clicked_data = st.plotly_chart(fig_escolas, use_container_width=True, 
                                             on_select="rerun", key="escola_chart")
                
                # Processar seleção de escola - Redirecionar para escolha de análise
                if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
                    selected_point = clicked_data['selection']['points'][0]
                    if 'customdata' in selected_point:
                        escola_selecionada = selected_point['customdata'][0]
                        st.session_state.selected_escola = escola_selecionada
                        st.session_state.drill_level = 'escolha_analise'
                        st.rerun()

    elif st.session_state.drill_level == 'escolha_analise':
        # NÍVEL 2: ESCOLHA DE TIPO DE ANÁLISE
        st.markdown(f"#### 🏫 Escola: {st.session_state.selected_escola}")
        st.markdown("**Escolha o tipo de análise:**")
        
        col_analise1, col_analise2 = st.columns(2)
        
        with col_analise1:
            if st.button("👥 **Análise de Coortes**\n(Evolução Longitudinal)", key="btn_coorte", help="Acompanha o mesmo grupo de alunos ao longo do tempo", use_container_width=True):
                st.session_state.analise_tipo = 'coorte'
                st.session_state.drill_level = 'coorte'
                st.rerun()
            st.caption("🎯 Para medir a evolução de um mesmo grupo de alunos")
        
        with col_analise2:
            if st.button("📊 **Análise de Turmas**\n(Por Fase)", key="btn_serie", help="Analisa turmas ao longo das fases", use_container_width=True):
                st.session_state.analise_tipo = 'serie'
                st.session_state.drill_level = 'serie'
                st.rerun()
            st.caption("📈 Para analisar turmas por fase")

    elif st.session_state.drill_level == 'coorte':
        # NÍVEL 3A: ANÁLISE DE COORTES
        st.markdown(f"#### 👥 Análise de Coortes - {st.session_state.selected_escola}")
        st.caption("Cada linha representa uma coorte de origem. Clique para ver alunos individuais da coorte.")
        
        # Filtrar dados da escola selecionada
        df_escola = df_lin[df_lin['Escola_Base'] == st.session_state.selected_escola]
        
        if not df_escola.empty and 'Coorte_Origem' in df_escola.columns:
            # Agrupar por coorte e fase, calculando média do Delta e contando alunos
            agrup_coorte = (df_escola.groupby(['Coorte_Origem','Fase'])
                                   .agg({'Delta': 'mean', 'ID_Unico': 'nunique'})
                                   .reset_index())
            agrup_coorte = agrup_coorte.rename(columns={'ID_Unico': 'Num_Alunos'})
            
            if preencher_faltantes:
                fases_ord = sorted(set(fases_sel))
                todas_coortes = pd.MultiIndex.from_product([agrup_coorte['Coorte_Origem'].unique(), fases_ord], 
                                                         names=['Coorte_Origem','Fase'])
                agrup_coorte = (agrup_coorte.set_index(['Coorte_Origem','Fase'])
                                          .reindex(todas_coortes)
                                          .reset_index())
                fase_means = agrup_coorte.groupby('Fase')['Delta'].transform(lambda s: s.fillna(s.mean()))
                agrup_coorte['Delta'] = agrup_coorte['Delta'].fillna(fase_means)
                # Preencher número de alunos como 0 para fases faltantes
                agrup_coorte['Num_Alunos'] = agrup_coorte['Num_Alunos'].fillna(0)

            # Filtrar coortes com dados suficientes
            valid_counts = agrup_coorte.dropna(subset=['Delta']).groupby('Coorte_Origem')['Delta'].count()
            keep_coortes = valid_counts[valid_counts >= 1].index
            agrup_coorte = agrup_coorte[agrup_coorte['Coorte_Origem'].isin(keep_coortes)]
            
            if not agrup_coorte.empty:
                if normalizar:
                    agrup_coorte['Delta_Vis'] = agrup_coorte.groupby('Fase')['Delta'].transform(
                        lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

                agrup_coorte['Fase'] = pd.Categorical(agrup_coorte['Fase'], 
                                                    categories=sorted(set(fases_sel)), ordered=True)
                
                media_geral = agrup_coorte.groupby('Coorte_Origem')['Delta'].transform('mean')
                agrup_coorte['Media_Geral_Delta'] = media_geral
                
                custom_cols = ['Coorte_Origem','Delta','Media_Geral_Delta','Num_Alunos']
                
                fig_coortes = criar_grafico_drill(
                    agrup_coorte, 'Coorte_Origem', 'Evolução por Coorte de Origem', 
                    y_col, y_label, custom_cols, 'coorte'
                )
                
                if fig_coortes:
                    clicked_data = st.plotly_chart(fig_coortes, use_container_width=True, 
                                                 on_select="rerun", key="coorte_chart")
                    
                    if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
                        selected_point = clicked_data['selection']['points'][0]
                        if 'customdata' in selected_point:
                            coorte_selecionada = selected_point['customdata'][0]
                            st.session_state.selected_coorte = coorte_selecionada
                            st.session_state.drill_level = 'alunos_coorte'
                            st.rerun()
            else:
                st.info("Sem dados suficientes de coortes para esta escola.")
        else:
            st.info("Dados de coorte não disponíveis para esta escola.")

    elif st.session_state.drill_level == 'serie':
        # NÍVEL 3B: ANÁLISE DE TURMAS (IMPLEMENTAÇÃO TRADICIONAL)
        st.markdown(f"#### 📊 Turmas da Escola: {st.session_state.selected_escola}")
        st.caption("Clique em uma linha para ver os alunos dessa turma")
        
        # Filtrar dados da escola selecionada
        df_escola = df_lin[df_lin['Escola_Base'] == st.session_state.selected_escola]
        
        if not df_escola.empty:
            agrup_turma = (df_escola.groupby(['Turma_Drill','Fase'])['Delta']
                                  .mean()
                                  .reset_index())
            # Renomear para manter compatibilidade com o resto do código
            agrup_turma = agrup_turma.rename(columns={'Turma_Drill': 'Turma'})
            
            if preencher_faltantes:
                fases_ord = sorted(set(fases_sel))
                todas_turmas = pd.MultiIndex.from_product([agrup_turma['Turma'].unique(), fases_ord], 
                                                        names=['Turma','Fase'])
                agrup_turma = (agrup_turma.set_index(['Turma','Fase'])
                                        .reindex(todas_turmas)
                                        .reset_index())
                fase_means = agrup_turma.groupby('Fase')['Delta'].transform(lambda s: s.fillna(s.mean()))
                agrup_turma['Delta'] = agrup_turma['Delta'].fillna(fase_means)

            valid_counts = agrup_turma.dropna(subset=['Delta']).groupby('Turma')['Delta'].count()
            keep_turmas = valid_counts[valid_counts >= 1].index
            agrup_turma = agrup_turma[agrup_turma['Turma'].isin(keep_turmas)]
            
            if not agrup_turma.empty:
                if normalizar:
                    agrup_turma['Delta_Vis'] = agrup_turma.groupby('Fase')['Delta'].transform(
                        lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

                agrup_turma['Fase'] = pd.Categorical(agrup_turma['Fase'], 
                                                   categories=sorted(set(fases_sel)), ordered=True)
                
                media_geral = agrup_turma.groupby('Turma')['Delta'].transform('mean')
                agrup_turma['Media_Geral_Delta'] = media_geral
                
                custom_cols = ['Turma','Delta','Media_Geral_Delta']
                
                fig_turmas = criar_grafico_drill(
                    agrup_turma, 'Turma', 'Evolução por Turma', 
                    y_col, y_label, custom_cols, 'turma'
                )
                
                if fig_turmas:
                    clicked_data = st.plotly_chart(fig_turmas, use_container_width=True, 
                                                 on_select="rerun", key="turma_serie_chart")
                    
                    if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
                        selected_point = clicked_data['selection']['points'][0]
                        if 'customdata' in selected_point:
                            turma_selecionada = selected_point['customdata'][0]
                            st.session_state.selected_turma = turma_selecionada
                            st.session_state.drill_level = 'alunos_turma'
                            st.rerun()
            else:
                st.info("Sem dados suficientes de turmas para esta escola.")
        else:
            st.info("Escola selecionada não possui dados.")

    elif st.session_state.drill_level == 'alunos_coorte':
        # NÍVEL 4: ALUNOS DA COORTE
        st.markdown(f"#### 🎓 Alunos da Coorte: {st.session_state.selected_coorte}")
        st.caption("Evolução individual de cada aluno da coorte selecionada")
        
        # Filtrar dados da escola, coorte selecionada
        df_coorte = df_lin[
            (df_lin['Escola_Base'] == st.session_state.selected_escola) & 
            (df_lin['Coorte_Origem'] == st.session_state.selected_coorte)
        ]
        
        if not df_coorte.empty:
            agrup_aluno = (df_coorte.groupby(['Nome','Fase'])['Delta']
                                   .mean()
                                   .reset_index())
            
            if not agrup_aluno.empty:
                if normalizar:
                    agrup_aluno['Delta_Vis'] = agrup_aluno.groupby('Fase')['Delta'].transform(
                        lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

                agrup_aluno['Fase'] = pd.Categorical(agrup_aluno['Fase'], 
                                                   categories=sorted(set(fases_sel)), ordered=True)
                
                media_geral = agrup_aluno.groupby('Nome')['Delta'].transform('mean')
                agrup_aluno['Media_Geral_Delta'] = media_geral
                
                custom_cols = ['Nome','Delta','Media_Geral_Delta']
                
                fig_alunos = criar_grafico_drill(
                    agrup_aluno, 'Nome', 'Evolução Individual por Aluno da Coorte', 
                    y_col, y_label, custom_cols, 'aluno'
                )
                
                if fig_alunos:
                    st.plotly_chart(fig_alunos, use_container_width=True, key="alunos_coorte_chart")
            else:
                st.info("Sem dados suficientes de alunos para esta coorte.")
        else:
            st.info("Coorte selecionada não possui dados.")

    elif st.session_state.drill_level == 'alunos_turma':
        # NÍVEL 4: ALUNOS DA TURMA (GRÁFICO DE BARRAS)
        st.markdown(f"#### 👥 Alunos da Turma: {st.session_state.selected_turma}")
        st.caption("Delta individual de cada aluno da turma (gráfico de barras)")
        
        # Filtrar dados da escola e turma selecionadas
        df_turma_alunos = df_lin[
            (df_lin['Escola_Base'] == st.session_state.selected_escola) & 
            (df_lin['Turma_Drill'] == st.session_state.selected_turma)
        ]
        
        if not df_turma_alunos.empty:
            # Agrupar por aluno, calculando média do Delta por aluno
            agrup_aluno_turma = (df_turma_alunos.groupby('Nome')['Delta']
                                               .mean()
                                               .sort_values(ascending=False)
                                               .reset_index())
            
            if not agrup_aluno_turma.empty:
                # Reordenar para maior delta primeiro (descrescente)
                agrup_aluno_turma = agrup_aluno_turma.sort_values('Delta', ascending=True)  # Ascending=True para que o maior apareça no topo
                
                # Criar gráfico de barras horizontais
                fig_barras = go.Figure()
                
                # Definir cores baseadas no valor do Delta
                cores = ['#28a745' if delta >= 0 else '#dc3545' for delta in agrup_aluno_turma['Delta']]
                
                fig_barras.add_trace(go.Bar(
                    x=agrup_aluno_turma['Delta'],
                    y=agrup_aluno_turma['Nome'],
                    orientation='h',  # Orientação horizontal
                    marker_color=cores,
                    text=agrup_aluno_turma['Delta'].round(2),
                    textposition='auto',
                    hovertemplate=(
                        '<b>%{y}</b><br>' +
                        'Delta: %{x:.2f}<br>' +
                        '<extra></extra>'
                    )
                ))
                
                fig_barras.update_layout(
                    title=f"Delta Individual dos Alunos - {st.session_state.selected_turma}",
                    xaxis_title="Delta (Pós - Pré)",
                    yaxis_title="Alunos",
                    showlegend=False,
                    height=max(400, len(agrup_aluno_turma) * 25)  # Altura dinâmica baseada no número de alunos
                )
                
                # Adicionar linha vertical no zero (para gráfico horizontal)
                fig_barras.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.7)
                
                st.plotly_chart(fig_barras, use_container_width=True)
                
                # Estatísticas resumidas
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total de Alunos", len(agrup_aluno_turma))
                col2.metric("Delta Médio", f"{agrup_aluno_turma['Delta'].mean():.2f}")
                col3.metric("Melhor Delta", f"{agrup_aluno_turma['Delta'].max():.2f}")
                col4.metric("Pior Delta", f"{agrup_aluno_turma['Delta'].min():.2f}")
                
            else:
                st.info("Sem dados suficientes de alunos para esta turma.")
        else:
            st.info("Turma selecionada não possui dados.")

    elif st.session_state.drill_level == 'turma':
        # NÍVEL 2: TURMAS
        st.markdown(f"#### 🏫 Turmas da Escola: {st.session_state.selected_escola}")
        st.caption("Clique em uma linha para ver os alunos dessa turma")
        
        # Filtrar dados da escola selecionada
        df_escola = df_lin[df_lin['Escola_Base'] == st.session_state.selected_escola]
        
        if not df_escola.empty:
            agrup_turma = (df_escola.groupby(['Turma_Drill','Fase'])['Delta']
                                  .mean()
                                  .reset_index())
            # Renomear para manter compatibilidade com o resto do código
            agrup_turma = agrup_turma.rename(columns={'Turma_Drill': 'Turma'})
            
            if preencher_faltantes:
                fases_ord = sorted(set(fases_sel))
                todas_turmas = pd.MultiIndex.from_product([agrup_turma['Turma'].unique(), fases_ord], 
                                                        names=['Turma','Fase'])
                agrup_turma = (agrup_turma.set_index(['Turma','Fase'])
                                        .reindex(todas_turmas)
                                        .reset_index())
                fase_means = agrup_turma.groupby('Fase')['Delta'].transform(lambda s: s.fillna(s.mean()))
                agrup_turma['Delta'] = agrup_turma['Delta'].fillna(fase_means)

            valid_counts = agrup_turma.dropna(subset=['Delta']).groupby('Turma')['Delta'].count()
            keep_turmas = valid_counts[valid_counts >= 1].index
            agrup_turma = agrup_turma[agrup_turma['Turma'].isin(keep_turmas)]
            
            if not agrup_turma.empty:
                if normalizar:
                    agrup_turma['Delta_Vis'] = agrup_turma.groupby('Fase')['Delta'].transform(
                        lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

                agrup_turma['Fase'] = pd.Categorical(agrup_turma['Fase'], 
                                                   categories=sorted(set(fases_sel)), ordered=True)
                
                media_geral = agrup_turma.groupby('Turma')['Delta'].transform('mean')
                agrup_turma['Media_Geral_Delta'] = media_geral
                
                custom_cols = ['Turma','Delta','Media_Geral_Delta']
                
                fig_turmas = criar_grafico_drill(
                    agrup_turma, 'Turma', 'Evolução por Turma', 
                    y_col, y_label, custom_cols, 'turma'
                )
                
                if fig_turmas:
                    clicked_data = st.plotly_chart(fig_turmas, use_container_width=True, 
                                                 on_select="rerun", key="turma_chart")
                    
                    if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
                        selected_point = clicked_data['selection']['points'][0]
                        if 'customdata' in selected_point:
                            turma_selecionada = selected_point['customdata'][0]
                            st.session_state.selected_turma = turma_selecionada
                            st.session_state.drill_level = 'aluno'
                            st.rerun()
            else:
                st.info("Sem dados suficientes de turmas para esta escola.")
        else:
            st.info("Escola selecionada não possui dados.")

    elif st.session_state.drill_level == 'aluno':
        # NÍVEL 3: ALUNOS
        st.markdown(f"#### 👥 Alunos da Turma: {st.session_state.selected_turma}")
        st.caption("Evolução individual de cada aluno")
        
        # Filtrar dados da escola e turma selecionadas
        df_turma = df_lin[
            (df_lin['Escola_Base'] == st.session_state.selected_escola) & 
            (df_lin['Turma_Drill'] == st.session_state.selected_turma)
        ]
        
        if not df_turma.empty:
            agrup_aluno = (df_turma.groupby(['Nome','Fase'])['Delta']
                                  .mean()
                                  .reset_index())
            
            if not agrup_aluno.empty:
                if normalizar:
                    agrup_aluno['Delta_Vis'] = agrup_aluno.groupby('Fase')['Delta'].transform(
                        lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)

                agrup_aluno['Fase'] = pd.Categorical(agrup_aluno['Fase'], 
                                                   categories=sorted(set(fases_sel)), ordered=True)
                
                media_geral = agrup_aluno.groupby('Nome')['Delta'].transform('mean')
                agrup_aluno['Media_Geral_Delta'] = media_geral
                
                custom_cols = ['Nome','Delta','Media_Geral_Delta']
                
                fig_alunos = criar_grafico_drill(
                    agrup_aluno, 'Nome', 'Evolução por Aluno', 
                    y_col, y_label, custom_cols, 'aluno'
                )
                
                if fig_alunos:
                    st.plotly_chart(fig_alunos, use_container_width=True, key="aluno_chart")
            else:
                st.info("Sem dados suficientes de alunos para esta turma.")
        else:
            st.info("Turma selecionada não possui dados.")

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
if nome_sel and nome_sel != "<selecione>":
    df_ind = df[df['Nome'] == nome_sel].sort_values('Fase')
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
                               title=f'Evolução Pré vs Pós - {nome_sel}',
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
                              title=f'Evolução Delta - {nome_sel}',
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

