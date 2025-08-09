import os
import pathlib
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Configuração de caminhos
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
EXCEL_NAME = "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_4.xlsx"
SHEET_NAME = "WG SSb (2024-2) - TDE, Vocabulá"

def carregar_dados():
    """Carrega e prepara os dados do Excel"""
    excel_path = DATA_DIR / EXCEL_NAME
    if not excel_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {excel_path}")
    
    df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)
    
    # Conversões e limpeza
    for c in ("total_pre_voc", "total_pos_voc"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["total_pre_voc", "total_pos_voc", "group"]).copy()

    # Ordenação customizada dos grupos para garantir a ordem cronológica (6o, 7o, ...)
    if 'group' in df.columns:
        df_sorted = df[['group']].copy().drop_duplicates()
        # Extrai o ano e a letra da turma para ordenação
        df_sorted['ano_sort'] = df_sorted['group'].str.extract(r'(\d+)').astype(int)
        df_sorted['turma_sort'] = df_sorted['group'].str.extract(r'ANO ([A-Z])')
        df_sorted = df_sorted.sort_values(['ano_sort', 'turma_sort'])
        
        # Cria uma ordem categórica para a coluna 'group'
        group_order = df_sorted['group'].tolist()
        df['group'] = pd.Categorical(df['group'], categories=group_order, ordered=True)
    
    # Métricas derivadas
    df["delta_voc"] = df["total_pos_voc"] - df["total_pre_voc"]
    baseline_sd = df["total_pre_voc"].std(ddof=1)
    
    return df, baseline_sd

def categorizar_mudanca_cohen(delta, baseline_sd):
    """Categorização baseada em Cohen's d"""
    pequeno = 0.2 * baseline_sd
    medio = 0.5 * baseline_sd
    grande = 0.8 * baseline_sd

    if delta >= grande:
        return "Melhora Grande (≥0.8 SD)"
    elif delta >= medio:
        return "Melhora Média (0.5-0.8 SD)"
    elif delta >= pequeno:
        return "Melhora Pequena (0.2-0.5 SD)"
    elif delta > -pequeno:
        return "Sem Mudança Prática (±0.2 SD)"
    elif delta > -medio:
        return "Piora Pequena (-0.5 a -0.2 SD)"
    elif delta > -grande:
        return "Piora Média (-0.8 a -0.5 SD)"
    else:
        return "Piora Grande (<-0.8 SD)"

def preparar_dados_grupo(df):
    """Prepara os dados para o gráfico de comparação por grupo"""
    # O groupby respeitará a ordem da coluna categórica 'group' definida em carregar_dados
    df_grupos = df.groupby('group', observed=False).agg({
        'total_pre_voc': 'mean',
        'total_pos_voc': 'mean',
        'delta_voc': 'mean'
    }).reset_index()
    
    # Renomear para manter compatibilidade
    df_grupos = df_grupos.rename(columns={
        'group': 'grupo',
        'total_pre_voc': 'pre_media',
        'total_pos_voc': 'pos_media',
        'delta_voc': 'delta_medio'
    })
    
    return df_grupos

def criar_grafico_pre_pos_grupo(df):
        """Cria gráfico de comparação pré vs pós por grupo (linha)"""
        df_grupos = preparar_dados_grupo(df)
        
        fig = go.Figure()
        
        # Pontos pré-teste
        fig.add_trace(go.Scatter(
            x=df_grupos['grupo'],
            y=df_grupos['pre_media'],
            mode='markers+lines',
            name='Pré-teste',
            marker=dict(size=10, color='red'),
            line=dict(color='red', dash='dash')
        ))
        
        # Pontos pós-teste
        fig.add_trace(go.Scatter(
            x=df_grupos['grupo'],
            y=df_grupos['pos_media'],
            mode='markers+lines',
            name='Pós-teste',
            marker=dict(size=10, color='blue'),
            line=dict(color='blue')
        ))
        
        # Setas de mudança
        for i, row in df_grupos.iterrows():
            fig.add_annotation(
                x=row['grupo'],
                y=row['pre_media'],
                ax=row['grupo'],
                ay=row['pos_media'],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if row['delta_medio'] > 0 else 'red'
            )
        
        fig.update_layout(
            title="Comparação Pré vs Pós-teste por Grupo",
            xaxis_title="Grupos",
            yaxis_title="Pontuação Média em Vocabulário",
            xaxis_tickangle=-45,
            height=600,
            template="plotly_white"
        )
        
        return fig

def criar_histograma_delta(df):
    """Cria histograma da distribuição dos deltas"""
    media_delta = df['delta_voc'].mean()
    
    fig = px.histogram(
        df, 
        x='delta_voc', 
        nbins=30,
        title="Distribuição dos Deltas",
        labels={'delta_voc': 'Delta (Pós - Pré)', 'count': 'Frequência'},
        color_discrete_sequence=['lightblue']
    )
    
    # Adicionar linha da média
    fig.add_vline(
        x=media_delta, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Média: {media_delta:.2f}",
        annotation_position="top"
    )
    
    # Linha do zero
    fig.add_vline(x=0, line_dash="dot", line_color="black", opacity=0.5)
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    return fig

def criar_forest_plot(df, baseline_sd):
    """Cria forest plot de Effect Size por grupo"""
    # Calcular estatísticas por grupo
    grp = df.groupby("group", observed=False).agg(
        n=("group", "size"),
        delta_mean=("delta_voc", "mean"),
        delta_sd=("delta_voc", lambda s: np.std(s, ddof=1)),
    ).reset_index()
    
    grp["effect_size"] = grp["delta_mean"] / baseline_sd
    grp["se_d"] = (grp["delta_sd"] / np.sqrt(grp["n"])) / baseline_sd
    grp["ci_low"] = grp["effect_size"] - 1.96 * grp["se_d"]
    grp["ci_high"] = grp["effect_size"] + 1.96 * grp["se_d"]
    grp = grp.sort_values("effect_size")
    
    # Cores: verde se ES >= 0.4, cinza caso contrário
    colors = ['#238b45' if abs(es) >= 0.4 else '#969696' for es in grp["effect_size"]]
    
    fig = go.Figure()
    
    # Pontos e intervalos de confiança
    fig.add_trace(go.Scatter(
        x=grp["effect_size"],
        y=grp["group"],
        mode="markers",
        marker=dict(color=colors, size=10),
        error_x=dict(
            type="data",
            array=grp["ci_high"] - grp["effect_size"],
            arrayminus=grp["effect_size"] - grp["ci_low"],
            visible=True,
            color="gray"
        ),
        showlegend=False
    ))
    
    # Linhas de referência
    fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=1)
    fig.add_vline(x=0.4, line_dash="dot", line_color="#238b45", line_width=1)
    fig.add_vline(x=-0.4, line_dash="dot", line_color="#238b45", line_width=1)
    
    fig.update_layout(
        title="Effect Size por Grupo (com IC 95%)",
        xaxis_title="Effect Size (Δ/SD Pré)",
        yaxis_title="Grupo",
        template="plotly_white",
        height=max(400, len(grp) * 25 + 100),
        xaxis=dict(range=[-0.5, 1.0])
    )
    
    return fig

def criar_grafico_categorias_cohen(df, baseline_sd):
    """Cria gráfico de barras empilhadas das categorias Cohen por grupo"""
    # Aplicar categorização
    df['categoria_cohen'] = df['delta_voc'].apply(
        lambda x: categorizar_mudanca_cohen(x, baseline_sd)
    )
    
    # Tabela cruzada
    ctab = pd.crosstab(df["group"], df["categoria_cohen"])
    ctab_pct = ctab.div(ctab.sum(axis=1), axis=0) * 100
    
    # Ordem das categorias
    cat_order = [
        "Piora Grande (<-0.8 SD)",
        "Piora Média (-0.8 a -0.5 SD)",
        "Piora Pequena (-0.5 a -0.2 SD)",
        "Sem Mudança Prática (±0.2 SD)",
        "Melhora Pequena (0.2-0.5 SD)",
        "Melhora Média (0.5-0.8 SD)",
        "Melhora Grande (≥0.8 SD)",
    ]
    
    # Cores para as categorias
    cores = {
        "Piora Grande (<-0.8 SD)": "#d73027",
        "Piora Média (-0.8 a -0.5 SD)": "#f46d43",
        "Piora Pequena (-0.5 a -0.2 SD)": "#fdae61",
        "Sem Mudança Prática (±0.2 SD)": "#fee08b",
        "Melhora Pequena (0.2-0.5 SD)": "#d9ef8b",
        "Melhora Média (0.5-0.8 SD)": "#a6d96a",
        "Melhora Grande (≥0.8 SD)": "#66bd63",
    }
    
    fig = go.Figure()
    
    for categoria in cat_order:
        if categoria in ctab_pct.columns:
            fig.add_trace(go.Bar(
                name=categoria,
                x=ctab_pct.index,
                y=ctab_pct[categoria],
                marker_color=cores.get(categoria, 'gray')
            ))
    
    fig.update_layout(
        title="Categorias de Cohen por Grupo",
        xaxis_title="Grupo",
        yaxis_title="% de alunos",
        barmode="stack",
        template="plotly_white",
        height=500,
        xaxis=dict(tickangle=45),
        legend=dict(title="Categoria", orientation="v", x=1.02, y=1)
    )
    
    return fig

def calcular_resumo_insights(df, baseline_sd):
    """Calcula insights e estatísticas resumo"""
    n = len(df)
    media_pre = df["total_pre_voc"].mean()
    media_pos = df["total_pos_voc"].mean()
    delta_mean = df["delta_voc"].mean()
    pct_melhoraram = (df["delta_voc"] > 0).mean() * 100
    pct_pioraram = (df["delta_voc"] < 0).mean() * 100
    pct_mantiveram = (df["delta_voc"] == 0).mean() * 100
    effect_size_global = delta_mean / baseline_sd
    
    # Interpretação do ES
    if abs(effect_size_global) < 0.15:
        magnitude = "Trivial"
        contexto = "Sem impacto educacional detectável"
    elif abs(effect_size_global) < 0.35:
        magnitude = "Pequeno"
        contexto = "Mudança pequena mas relevante"
    elif abs(effect_size_global) < 0.65:
        magnitude = "Moderado"
        contexto = "Mudança substancial e importante"
    elif abs(effect_size_global) < 1.0:
        magnitude = "Grande"
        contexto = "Mudança grande e muito significativa"
    else:
        magnitude = "Muito Grande"
        contexto = "Mudança transformadora"
    
    # Grupos com ES acima de 0.4
    grp_stats = df.groupby('group', observed=False)['delta_voc'].mean() / baseline_sd
    grupos_acima_04 = grp_stats[grp_stats.abs() >= 0.4].index.tolist()
    
    # Top 3 e Bottom 3
    grp_sorted = grp_stats.sort_values(ascending=False)
    top_3 = [(grupo, es) for grupo, es in grp_sorted.head(3).items()]
    bottom_3 = [(grupo, es) for grupo, es in grp_sorted.tail(3).items()]
    
    return {
        'n': n,
        'media_pre': media_pre,
        'media_pos': media_pos,
        'delta_mean': delta_mean,
        'pct_melhoraram': pct_melhoraram,
        'pct_pioraram': pct_pioraram,
        'pct_mantiveram': pct_mantiveram,
        'effect_size_global': effect_size_global,
        'magnitude_global': magnitude,
        'contexto_global': contexto,
        'grupos_acima_04': grupos_acima_04,
        'top_3': top_3,
        'bottom_3': bottom_3
    }

def criar_tabela_effect_sizes(df, baseline_sd):
    """Cria tabela HTML de effect sizes por grupo"""
    grp = df.groupby("group", observed=False).agg(
        n=("group", "size"),
        delta_mean=("delta_voc", "mean"),
        delta_sd=("delta_voc", lambda s: np.std(s, ddof=1)),
    ).reset_index()
    
    grp["effect_size"] = grp["delta_mean"] / baseline_sd
    grp["se_d"] = (grp["delta_sd"] / np.sqrt(grp["n"])) / baseline_sd
    grp["ci_low"] = grp["effect_size"] - 1.96 * grp["se_d"]
    grp["ci_high"] = grp["effect_size"] + 1.96 * grp["se_d"]
    
    def interpretar_magnitude(es):
        abs_es = abs(es)
        if abs_es < 0.15:
            return "Trivial"
        elif abs_es < 0.35:
            return "Pequeno"
        elif abs_es < 0.65:
            return "Moderado"
        elif abs_es < 1.0:
            return "Grande"
        else:
            return "Muito Grande"
    
    grp = grp.sort_values("effect_size", ascending=False)
    
    rows = []
    for _, r in grp.iterrows():
        magnitude = interpretar_magnitude(r["effect_size"])
        cor_linha = "#e8f5e8" if abs(r["effect_size"]) >= 0.4 else "#f8f8f8"
        
        rows.append(f"""
        <tr style="background-color: {cor_linha}">
            <td>{r['group']}</td>
            <td style='text-align:right'>{r['n']}</td>
            <td style='text-align:right'>{r['effect_size']:.3f}</td>
            <td style='text-align:right'>[{r['ci_low']:.3f}, {r['ci_high']:.3f}]</td>
            <td>{magnitude}</td>
        </tr>
        """)
    
    table_html = f"""
    <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
        <thead>
            <tr style="background-color: #4CAF50; color: white;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Grupo</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">n</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Effect Size</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">IC 95%</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Magnitude</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """
    
    return table_html

def gerar_relatorio_html(df, baseline_sd):
    """Gera o relatório HTML completo"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calcular insights
    insights = calcular_resumo_insights(df, baseline_sd)
    
    # Criar gráficos
    fig_pre_pos = criar_grafico_pre_pos_grupo(df)
    fig_delta = criar_histograma_delta(df)
    fig_forest = criar_forest_plot(df, baseline_sd)
    fig_categorias = criar_grafico_categorias_cohen(df, baseline_sd)
    
    # Converter gráficos para HTML
    grafico1_html = pyo.plot(fig_pre_pos, include_plotlyjs=False, output_type='div')
    grafico2_html = pyo.plot(fig_delta, include_plotlyjs=False, output_type='div')
    grafico3_html = pyo.plot(fig_forest, include_plotlyjs=False, output_type='div')
    grafico4_html = pyo.plot(fig_categorias, include_plotlyjs=False, output_type='div')
    
    # Criar tabela
    tabela_html = criar_tabela_effect_sizes(df, baseline_sd)
    
    # Função auxiliar para formatar lista de grupos
    def fmt_group_list(items):
        return ", ".join(items) if items else "Nenhum"
    
    # Template HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório Visual - Vocabulário WordGen</title>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #34495e;
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-top: 40px;
            }}
            h3 {{
                color: #7f8c8d;
                margin-top: 30px;
            }}
            .resumo {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }}
            .card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 18px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .card.green {{
                background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            }}
            .card.red {{
                background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
            }}
            .card.yellow {{
                background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
            }}
            .card h4 {{
                margin: 0 0 8px 0;
                font-size: 13px;
                opacity: 0.9;
            }}
            .card .valor {{
                font-size: 22px;
                font-weight: bold;
                margin: 4px 0;
            }}
            .card .desc {{
                font-size: 11px;
                opacity: 0.8;
            }}
            .insights {{
                background-color: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .insights ul {{
                list-style-type: none;
                padding: 0;
            }}
            .insights li {{
                background-color: white;
                margin: 10px 0;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            .small {{
                color: #7f8c8d;
                font-size: 0.9em;
                text-align: center;
                margin-top: 30px;
            }}
            .plotly-graph-div {{
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relatório Visual - Vocabulário WordGen</h1>
            <div class="small">Gerado em: {now}</div>
            
            <h2>Resumo</h2>
            <div class="resumo">
                <div class="card">
                    <h4>Amostra</h4>
                    <div class="valor">{insights['n']}</div>
                    <div class="desc">alunos</div>
                </div>
                <div class="card">
                    <h4>Médias</h4>
                    <div class="valor">Pré: {insights['media_pre']:.2f}</div>
                    <div class="desc">Pós: {insights['media_pos']:.2f}</div>
                </div>
                <div class="card">
                    <h4>Delta Médio</h4>
                    <div class="valor">{insights['delta_mean']:.2f}</div>
                    <div class="desc">mudança média</div>
                </div>
                <div class="card green">
                    <h4>% Melhoraram</h4>
                    <div class="valor">{insights['pct_melhoraram']:.1f}%</div>
                    <div class="desc">dos alunos</div>
                </div>
                <div class="card red">
                    <h4>% Pioraram</h4>
                    <div class="valor">{insights['pct_pioraram']:.1f}%</div>
                    <div class="desc">dos alunos</div>
                </div>
                <div class="card yellow">
                    <h4>% Mantiveram</h4>
                    <div class="valor">{insights['pct_mantiveram']:.1f}%</div>
                    <div class="desc">dos alunos</div>
                </div>
                <div class="card">
                    <h4>Effect Size Global</h4>
                    <div class="valor">{insights['effect_size_global']:.3f}</div>
                    <div class="desc">{insights['magnitude_global']}</div>
                </div>
                <div class="card">
                    <h4>Contexto</h4>
                    <div class="valor">Educacional</div>
                    <div class="desc">{insights['contexto_global']}</div>
                </div>
            </div>
            
            <h2>Gráficos</h2>
            
            <h3>Comparação Pré vs Pós por Grupo</h3>
            {grafico1_html}
            
            <h3>Distribuição dos Deltas</h3>
            {grafico2_html}
            
            <h3>Effect Size por Grupo</h3>
            {grafico3_html}
            
            <h3>Categorias de Cohen por Grupo</h3>
            {grafico4_html}
            
            <h2>Insights</h2>
            <div class="insights">
                <ul>
                    <li><strong>Grupos com ES ≥ 0.4 (benchmark Hattie):</strong> {fmt_group_list(insights['grupos_acima_04'])}</li>
                    <li><strong>Top 3 ES:</strong> {", ".join([f"{g} ({es:.3f})" for g, es in insights['top_3']])}</li>
                    <li><strong>Bottom 3 ES:</strong> {", ".join([f"{g} ({es:.3f})" for g, es in insights['bottom_3']])}</li>
                </ul>
            </div>
            
            <h2>Tabela de Effect Sizes</h2>
            {tabela_html}
            
            <div class="small">
                <p><strong>Observação:</strong> ES = Δ/SD(Pré). IC 95% via SE = SD(Δ)/√n / SD(Pré).</p>
                <p><strong>Interpretação:</strong> Trivial (<0.15), Pequeno (0.15-0.35), Moderado (0.35-0.65), Grande (0.65-1.0), Muito Grande (≥1.0)</p>
                <p><strong>Benchmark Educacional:</strong> Hattie (2009) considera ES ≥ 0.4 como "bom resultado educacional"</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Função principal"""
    print("🔍 Carregando dados...")
    df, baseline_sd = carregar_dados()
    print(f"✅ Dados carregados: {len(df)} alunos | SD(Pré)={baseline_sd:.3f}")
    
    print("📊 Gerando relatório visual...")
    html_content = gerar_relatorio_html(df, baseline_sd)
    
    # Salvar arquivo HTML
    html_path = DATA_DIR / "relatorio_visual_vocabulario.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Relatório HTML salvo em: {html_path}")
    print(f"🌐 Para visualizar, abra o arquivo no navegador:")
    print(f"   file://{html_path.absolute()}")
    
    return html_path

if __name__ == "__main__":
    main()
