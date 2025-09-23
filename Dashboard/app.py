import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import get_datasets
import unicodedata, re

st.set_page_config(page_title="Dashboard Longitudinal WordGen", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    """Carrega apenas os datasets principais (TDE e Vocabulário)."""
    tde, vocab = get_datasets()
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

# Turmas (dependente de escolas/fases)
turmas = sorted(df['Turma'].dropna().unique())
turmas_sel = st.sidebar.multiselect("Turma(s)", turmas)
if turmas_sel:
    df = df[df['Turma'].isin(turmas_sel)]

# Nome (para acompanhamento individual)
nomes = sorted(df['Nome'].dropna().unique())
nome_sel = st.sidebar.selectbox("Aluno (Nome Completo)", ["<selecione>"] + nomes)

# ================= OVERVIEW ==================
st.subheader("Resumo Filtrado")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", len(df))
col2.metric("Alunos únicos (Nome)", df['Nome'].nunique())
col3.metric("Escolas", df['Escola'].nunique())
col4.metric("Turmas", df['Turma'].nunique())

# Scores agregados por fase
if not df.empty:
    agg_fase = (df.groupby('Fase')
                  .agg(Score_Pre=('Score_Pre','mean'),
                       Score_Pos=('Score_Pos','mean'),
                       N=('Nome','nunique'))
                  .reset_index())
    fig_fase = px.bar(
        agg_fase,
        x='Fase',
        y=['Score_Pre','Score_Pos'],
        barmode='group',
        title='Média Pré-Teste vs Pós-Teste por Fase',
        labels={'value':'Score','variable':'Teste', 'Score_Pre':'Pré-Teste','Score_Pos':'Pós-Teste'}
    )
    # Renomear legendas explicitamente (wide-form mantém nomes originais das colunas)
    rename_map = {'Score_Pre':'Pré-Teste','Score_Pos':'Pós-Teste'}
    fig_fase.for_each_trace(lambda tr: tr.update(name=rename_map.get(tr.name, tr.name),
                                                 legendgroup=rename_map.get(tr.name, tr.name)))
    st.plotly_chart(fig_fase, use_container_width=True)

    # ---------------- EVOLUÇÃO AGRUPADA POR ESCOLA (Plotly Line) ----------------
    st.markdown("### Evolução Comparativa entre Escolas")
    st.caption("Cada linha representa a média de Delta (Pós - Pré) da escola por fase. Passe o mouse para ver detalhes.")

    with st.expander("Opções avançadas de visualização", expanded=False):
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

    df_lin = df.copy()
    df_lin['Delta'] = df_lin['Score_Pos'] - df_lin['Score_Pre']
    if agrupar:
        df_lin['Escola_Base'] = df_lin['Escola'].apply(normaliza_escola)
    else:
        df_lin['Escola_Base'] = df_lin['Escola']

    agrup_mean = (df_lin.groupby(['Escola_Base','Fase'])['Delta']
                        .mean()
                        .reset_index())
    # Reindex para preencher fases faltantes se necessário
    if preencher_faltantes:
        fases_ord = sorted(set(fases_sel))
        todas = pd.MultiIndex.from_product([agrup_mean['Escola_Base'].unique(), fases_ord], names=['Escola_Base','Fase'])
        agrup_mean = (agrup_mean.set_index(['Escola_Base','Fase'])
                                   .reindex(todas)
                                   .reset_index())
    # Preencher valores faltantes com média da fase
    if preencher_faltantes:
        fase_means = agrup_mean.groupby('Fase')['Delta'].transform(lambda s: s.fillna(s.mean()))
        agrup_mean['Delta'] = agrup_mean['Delta'].fillna(fase_means)

    # Remover escolas com menos de 2 valores não nulos
    valid_counts = agrup_mean.dropna(subset=['Delta']).groupby('Escola_Base')['Delta'].count()
    keep_escolas = valid_counts[valid_counts >= 2].index
    agrup_mean = agrup_mean[agrup_mean['Escola_Base'].isin(keep_escolas)]

    if agrup_mean.empty:
        st.info("Sem dados suficientes para plotar linhas.")
    else:
        # Ordena legenda por média se solicitado
        media_por_escola = agrup_mean.groupby('Escola_Base')['Delta'].mean()
        if ordenar:
            ordem = media_por_escola.sort_values(ascending=False).index
        else:
            ordem = sorted(media_por_escola.index)
        agrup_mean['Escola_Base'] = pd.Categorical(agrup_mean['Escola_Base'], categories=ordem, ordered=True)

        # Normalização opcional apenas para a visualização
        if normalizar:
            agrup_mean['Delta_Vis'] = agrup_mean.groupby('Fase')['Delta'].transform(lambda c: (c - c.mean())/c.std(ddof=0) if c.std(ddof=0) not in (0,None) else 0)
            y_col = 'Delta_Vis'
            y_label = 'Delta (z-score)'
        else:
            y_col = 'Delta'
            y_label = 'Delta (Pós - Pré)'

        agrup_mean['Fase'] = pd.Categorical(agrup_mean['Fase'], categories=sorted(set(fases_sel)), ordered=True)

        # Adicionar média geral para hover
        media_geral = agrup_mean.groupby('Escola_Base')['Delta'].transform('mean')
        agrup_mean['Media_Geral_Delta'] = media_geral

        # customdata para hover (Escola Base, Delta real, Média Geral real)
        agrup_mean = agrup_mean.sort_values(['Escola_Base','Fase'])
        custom_cols = ['Escola_Base','Delta','Media_Geral_Delta']

        # Criar coluna numérica para eixo ordinal
        fase_map = {'2':2,'3':3,'4':4}
        agrup_mean['FaseNum'] = agrup_mean['Fase'].astype(str).map(fase_map)

        fig_lines = px.line(
            agrup_mean,
            x='FaseNum', y=y_col, color='Escola_Base',
            category_orders={'Escola_Base': list(ordem)},
            custom_data=custom_cols,
            markers=True,
            labels={'FaseNum':'Fase','Escola_Base':'Escola', y_col: y_label}
        )
        hover_label_name = y_label
        fig_lines.update_traces(
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Fase: %{x}<br>'
                + hover_label_name + ': %{y:.2f}<br>'
                'Delta Real: %{customdata[1]:.2f}<br>'
                'Média Geral Delta: %{customdata[2]:.2f}<extra></extra>'
            ),
            opacity=0.8
        )
        fig_lines.update_layout(
            legend_title_text='Escola',
            yaxis_title=y_label,
            xaxis=dict(tickmode='array', tickvals=[2,3,4], ticktext=['2','3','4'], title='Fase')
        )
        st.plotly_chart(fig_lines, use_container_width=True)

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
        st.dataframe(df_show, use_container_width=True)

        # Linha evolução
        long = (df_ind.melt(id_vars=['Fase'], value_vars=['Score_Pre','Score_Pos'],
                            var_name='Momento', value_name='Score')
                       .replace({'Score_Pre':'Pré','Score_Pos':'Pós'}))
        fig_line = px.line(long, x='Fase', y='Score', color='Momento', markers=True,
                           title=f'Evolução Pré vs Pós - {nome_sel}')
        st.plotly_chart(fig_line, use_container_width=True)

        # Deltas
        fig_delta = px.bar(df_show, x='Fase', y='Delta', title='Delta (Pós - Pré) por Fase',
                           text='Delta')
        st.plotly_chart(fig_delta, use_container_width=True)
else:
    st.info("Selecione um aluno para ver evolução individual.")

# (Seção de continuidade longitudinal removida conforme solicitação do usuário)

# ================= DISTRIBUIÇÃO DE DELTAS ==================
st.subheader("Distribuição de Deltas (Pós - Pré)")
if not df.empty:
    df['Delta'] = df['Score_Pos'] - df['Score_Pre']
    fig_hist = px.histogram(df, x='Delta', nbins=30, title='Distribuição dos Deltas', marginal='rug')
    st.plotly_chart(fig_hist, use_container_width=True)

    agg_turma = (df.groupby('Turma')
                   .agg(Media_Delta=('Delta','mean'), N=('Nome','nunique'))
                   .reset_index() 
                   .sort_values('Media_Delta', ascending=False))
    st.markdown("**Média de Delta por Turma (top 20)**")
    st.dataframe(agg_turma.head(20), use_container_width=True)

# ================= FOOTER ==================
st.markdown("---")
st.caption("Dashboard gerado automaticamente - WordGen • Utilize filtros na barra lateral para refinar a análise.")

