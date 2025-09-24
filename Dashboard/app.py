import streamlit as st
import pandas as pd
import plotly.express as px
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
# Contar turmas originais (antes da normalização) para mostrar quantidade real de classes
turmas_originais = df['Turma_Original'].nunique() if 'Turma_Original' in df.columns else df['Turma'].nunique()
col4.metric("Turmas", turmas_originais)

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
                     .applymap(style_delta, subset=['Delta'])
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
st.caption("Dashboard gerado automaticamente - WordGen • Utilize filtros na barra lateral para refinar a análise.")

