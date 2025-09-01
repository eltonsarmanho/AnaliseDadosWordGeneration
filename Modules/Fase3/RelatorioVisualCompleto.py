# filepath: /home/eltonss/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/Fase3/RelatorioVisualCompleto.py
import os
import io
import base64
import pathlib
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.switch_backend("Agg")
sns.set_theme(style="whitegrid")

DATA_DIR = str(pathlib.Path(__file__).parent.parent.parent.resolve() / "Data")
FIG_DIR = os.path.join(DATA_DIR, "figures")
DEFAULT_PRE = os.path.join(DATA_DIR, "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_3_preTeste.csv")
DEFAULT_POS = os.path.join(DATA_DIR, "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_3_posTeste.csv")
OUTPUT_HTML = os.path.join(DATA_DIR, "relatorio_visual_wordgen_fase3.html")

# Figure paths
FIG_PREPOS_BARRAS = os.path.join(FIG_DIR, "fase3_prepos_barras.png")
FIG_PREPOS_SCATTER = os.path.join(FIG_DIR, "fase3_prepos_scatter.png")
FIG_DELTA_HIST = os.path.join(FIG_DIR, "fase3_delta_hist.png")
FIG_HEATMAP_Q = os.path.join(FIG_DIR, "fase3_heatmap_questoes.png")
FIG_TOP_Q = os.path.join(FIG_DIR, "fase3_top_questoes.png")
FIG_CATEG_BENCH = os.path.join(FIG_DIR, "fase3_categorias_bench.png")


def fig_to_base64(fig) -> str:
    """Converte uma figura matplotlib para string Base64."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return f"data:image/png;base64,{img_base64}"


def _ensure_fig_dir():
    os.makedirs(FIG_DIR, exist_ok=True)


def _read_csv_safe(path: str) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    # Last try without encoding to let pandas guess
    return pd.read_csv(path)


def detectar_coluna_id(df: pd.DataFrame) -> str:
    candidatos = [c for c in df.columns if c.lower() in {"id", "aluno_id", "student_id"}]
    if candidatos:
        return candidatos[0]
    # fallback: assume first column is ID if it's object-like and has many uniques
    primeira = df.columns[0]
    return primeira


def detectar_colunas_q(df: pd.DataFrame) -> List[str]:
    # Prefer exactly Q1..Q50 if available, keep only those present
    alvo = [f"Q{i}" for i in range(1, 51)]
    presentes = [c for c in alvo if c in df.columns]
    if presentes:
        return presentes
    # fallback: any column that matches Q\d+
    return [c for c in df.columns if c.upper().startswith("Q") and c[1:].isdigit()]


def limpar_validar_q(df: pd.DataFrame, cols_q: List[str]) -> pd.DataFrame:
    work = df.copy()
    # Coerce to numeric 0/1. Anything outside {0,1} -> NaN then drop rows with any NaN in Qs
    for c in cols_q:
        work[c] = pd.to_numeric(work[c], errors="coerce")
    # Domain check: only 0 or 1 allowed
    mask_validos = work[cols_q].map(lambda x: x in (0, 1)).all(axis=1)
    work = work[mask_validos]
    # Drop any residual NaNs in Qs
    work = work.dropna(subset=cols_q)
    return work


def alinhar_por_id(df_pre: pd.DataFrame, df_pos: pd.DataFrame, col_id: str, cols_q: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Deduplicate by ID keeping first
    df_pre = df_pre.drop_duplicates(subset=[col_id], keep="first")
    df_pos = df_pos.drop_duplicates(subset=[col_id], keep="first")

    ids_pre = set(df_pre[col_id].astype(str))
    ids_pos = set(df_pos[col_id].astype(str))
    ids_comuns = ids_pre.intersection(ids_pos)

    df_pre_f = df_pre[df_pre[col_id].astype(str).isin(ids_comuns)].copy()
    df_pos_f = df_pos[df_pos[col_id].astype(str).isin(ids_comuns)].copy()

    # Keep only Q columns (and id)
    df_pre_f = df_pre_f[[col_id] + cols_q]
    df_pos_f = df_pos_f[[col_id] + cols_q]

    # Sort by ID to align
    df_pre_f = df_pre_f.sort_values(by=col_id).reset_index(drop=True)
    df_pos_f = df_pos_f.sort_values(by=col_id).reset_index(drop=True)

    # Final sanity: ensure same order and same ids
    assert (df_pre_f[col_id].astype(str).values == df_pos_f[col_id].astype(str).values).all(), "IDs desalinham após ordenação"

    return df_pre_f, df_pos_f


def carregar_e_preparar(path_pre: str = DEFAULT_PRE, path_pos: str = DEFAULT_POS):
    df_pre_raw = _read_csv_safe(path_pre)
    df_pos_raw = _read_csv_safe(path_pos)

    col_id_pre = detectar_coluna_id(df_pre_raw)
    col_id_pos = detectar_coluna_id(df_pos_raw)
    # Renomear coluna ID para o mesmo nome
    df_pre_raw = df_pre_raw.rename(columns={col_id_pre: "ID"})
    df_pos_raw = df_pos_raw.rename(columns={col_id_pos: "ID"})

    cols_q_pre = detectar_colunas_q(df_pre_raw)
    cols_q_pos = detectar_colunas_q(df_pos_raw)
    cols_q = [c for c in cols_q_pre if c in cols_q_pos]

    if not cols_q:
        raise ValueError("Não foram encontradas colunas Q1..Q50 em comum nos CSVs de pré e pós.")

    df_pre = limpar_validar_q(df_pre_raw, cols_q)
    df_pos = limpar_validar_q(df_pos_raw, cols_q)

    df_pre_a, df_pos_a = alinhar_por_id(df_pre, df_pos, "ID", cols_q)

    # Totais por aluno
    pre_tot = df_pre_a[cols_q].sum(axis=1)
    pos_tot = df_pos_a[cols_q].sum(axis=1)
    delta = pos_tot - pre_tot

    meta = {
        "n_registros_pre_raw": len(df_pre_raw),
        "n_registros_pos_raw": len(df_pos_raw),
        "n_validos_pre": len(df_pre),
        "n_validos_pos": len(df_pos),
        "n_final": len(df_pre_a),
        "qtd_q": len(cols_q),
    }

    return df_pre_a, df_pos_a, pre_tot, pos_tot, delta, cols_q, meta


def indicadores(pre_tot: pd.Series, pos_tot: pd.Series, delta: pd.Series) -> Dict[str, float]:
    n = len(pre_tot)
    mean_pre = float(pre_tot.mean())
    std_pre = float(pre_tot.std(ddof=1)) if n > 1 else 0.0
    mean_pos = float(pos_tot.mean())
    std_pos = float(pos_tot.std(ddof=1)) if n > 1 else 0.0
    mean_delta = float(delta.mean())

    improved = (delta > 0).mean() * 100.0
    worsened = (delta < 0).mean() * 100.0
    unchanged = (delta == 0).mean() * 100.0

    d_global = mean_delta / std_pre if std_pre > 1e-12 else np.nan

    return {
        "n": n,
        "mean_pre": mean_pre,
        "std_pre": std_pre,
        "mean_pos": mean_pos,
        "std_pos": std_pos,
        "mean_delta": mean_delta,
        "%_improved": improved,
        "%_worsened": worsened,
        "%_unchanged": unchanged,
        "cohen_d_global": d_global,
    }


def categorizar_por_cohen(delta: pd.Series, sd_pre: float) -> pd.DataFrame:
    # Padronizar delta em unidades de desvio padrão do pré
    if sd_pre <= 1e-12:
        z = pd.Series(np.zeros(len(delta)), index=delta.index)
    else:
        z = delta / sd_pre

    def rotulo(v: float) -> str:
        if v <= -0.8:
            return "Piorou (grande)"
        if v <= -0.5:
            return "Piorou (médio)"
        if v <= -0.2:
            return "Piorou (pequeno)"
        if v < 0.2:
            return "Sem mudança"
        if v < 0.5:
            return "Melhorou (pequeno)"
        if v < 0.8:
            return "Melhorou (médio)"
        return "Melhorou (grande)"

    cats = z.apply(rotulo)
    return pd.DataFrame({"z": z, "categoria": cats})


# ---------- Utilidades ----------

def interpretar_magnitude(es: float) -> str:
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

# ---------- Gráficos (Base64) ----------

def gerar_prepos_barras(pre_tot: pd.Series, pos_tot: pd.Series) -> str:
    """Gera gráfico de barras pré vs pós e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(7, 4))
    medias = [pre_tot.mean(), pos_tot.mean()]
    desvios = [pre_tot.std(ddof=1), pos_tot.std(ddof=1)]
    bars = ax.bar(["Pré", "Pós"], medias, yerr=desvios, capsize=6, color=["#6baed6", "#2171b5"], alpha=0.9)
    ax.set_ylabel("Acertos (média ± DP)")
    ax.set_title("Comparação Pré vs Pós (acertos totais)")
    for b, m in zip(bars, medias):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(desvios)*0.05, f"{m:.2f}", ha="center", va="bottom")
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_delta_hist(delta: pd.Series) -> str:
    """Gera histograma de deltas e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(7, 4))
    vals = delta.dropna()
    ax.hist(vals, bins=30, color="#6baed6", edgecolor="white")
    mean_val = float(vals.mean()) if len(vals) else 0.0

    ax.axvline(0, color="black", linestyle=":", linewidth=1)
    ax.axvline(mean_val, color="#e41a1c", linestyle="--", linewidth=1.5)
    ax.set_title("Distribuição dos Deltas (Pós - Pré)")
    ax.set_xlabel("Delta de Vocabulário")
    ax.set_ylabel("Frequência")
    ax.text(0.98, 0.92, f"Média: {mean_val:.2f}", transform=ax.transAxes, ha="right", va="center", fontsize=9,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_top_questoes(df_pre: pd.DataFrame, df_pos: pd.DataFrame, cols_q: List[str], top_n: int = 10) -> str:
    """Gera gráfico das top questões e retorna como Base64."""
    prop_pre = df_pre[cols_q].mean(axis=0)
    prop_pos = df_pos[cols_q].mean(axis=0)
    delta_q = (prop_pos - prop_pre).sort_values(ascending=False)

    top_up = delta_q.head(top_n)
    top_down = delta_q.tail(top_n)

    fig, ax = plt.subplots(figsize=(10, 7))
    dados = pd.concat([top_up, top_down])
    cores = ["#2E8B57"]*len(top_up) + ["#B22222"]*len(top_down)
    
    # Cria um DataFrame para usar com seaborn sem warning
    plot_data = pd.DataFrame({
        'delta': dados.values,
        'questao': dados.index,
        'cor': cores
    })
    
    # Usa scatter + line para evitar warning do seaborn
    for i, (questao, delta, cor) in enumerate(zip(plot_data['questao'], plot_data['delta'], plot_data['cor'])):
        ax.barh(i, delta, color=cor, alpha=0.8)
    
    ax.set_yticks(range(len(plot_data)))
    ax.set_yticklabels(plot_data['questao'])
    ax.axvline(0, color="#333", linewidth=1)
    ax.set_xlabel("Δ proporção correta (Pós - Pré)")
    ax.set_ylabel("Questão")
    ax.set_title("Top questões: maiores melhorias e quedas")
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_categorias_bench(cat_df: pd.DataFrame) -> str:
    """Gera gráfico das categorias de benchmark e retorna como Base64."""
    ordem = [
        "Piorou (grande)", "Piorou (médio)", "Piorou (pequeno)",
        "Sem mudança",
        "Melhorou (pequeno)", "Melhorou (médio)", "Melhorou (grande)"
    ]
    cont = cat_df["categoria"].value_counts().reindex(ordem).fillna(0)
    perc = 100 * cont / cont.sum()
    
    cores = {
        "Piorou (grande)": "#d73027",
        "Piorou (médio)": "#f46d43", 
        "Piorou (pequeno)": "#fdae61",
        "Sem mudança": "#fee08b",
        "Melhorou (pequeno)": "#d9ef8b",
        "Melhorou (médio)": "#a6d96a",
        "Melhorou (grande)": "#66bd63",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Cria barras individuais para evitar warning do seaborn
    for i, (cat, val) in enumerate(zip(ordem, perc.values)):
        ax.bar(i, val, color=cores[cat], alpha=0.8)
    
    ax.set_xticks(range(len(ordem)))
    ax.set_xticklabels(ordem, rotation=30, ha="right")
    ax.set_ylabel("% de alunos")
    ax.set_title("Distribuição de mudanças (padrão Cohen, SD do Pré)")
    ax.set_ylim(0, max(perc.max()*1.15, 10))
    
    # Adiciona valores nas barras
    for i, v in enumerate(perc.values):
        ax.text(i, v + max(perc.max()*0.02, 0.5), f"{v:.1f}%", ha="center")
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


# ---------- HTML ----------

def _format_card(label: str, value: str, extra: str = "", theme: str = "default") -> str:
    theme_class = {
        "default": "card",
        "green": "card green",
        "red": "card red",
        "yellow": "card yellow",
    }.get(theme, "card")

    desc_html = f"<div class='desc'>{extra}</div>" if extra else ""
    return f"""
    <div class="{theme_class}">
        <div class="card-label">{label}</div>
        <div class="valor">{value}</div>
        {desc_html}
    </div>
    """


def _interpretacao_contexto_html(indic: Dict[str, float]) -> str:
    d = indic.get("cohen_d_global", np.nan)
    mag = interpretar_magnitude(d) if np.isfinite(d) else "Indefinido"
    
    bench_hattie = "✓ Acima do benchmark (d≥0.4)" if (np.isfinite(d) and abs(d) >= 0.4) else "⚠ Abaixo do benchmark (d<0.4)"
    bench_vocab = "✓ Significativo em Vocabulário (d≥0.35)" if (np.isfinite(d) and abs(d) >= 0.35) else "⚠ Abaixo do threshold (d<0.35)"

    return f"""
    <div class="grupo-item">
        <div class="grupo-titulo">Effect Size Global: d = {d:.3f} (n={indic['n']})</div>
        <div class="grupo-detalhes">
            <span><strong>Magnitude:</strong> {mag}</span>
            <span>{bench_hattie}</span>
            <span>{bench_vocab}</span>
        </div>
    </div>
    """


def gerar_html(indic: Dict[str, float], img_barras: str, img_hist: str, img_top: str, img_categ: str) -> str:
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cards seguindo o padrão da Fase4
    cards_html = "".join([
        _format_card("Registros", f"{indic['n']}", "alunos após limpeza"),
        _format_card("Média Pré", f"{indic['mean_pre']:.2f}"),
        _format_card("Média Pós", f"{indic['mean_pos']:.2f}"),
        _format_card("Delta médio", f"{indic['mean_delta']:.2f}", "pontos"),
        _format_card("% Melhoraram", f"{indic['%_improved']:.1f}%", theme="green"),
        _format_card("% Pioraram", f"{indic['%_worsened']:.1f}%", theme="red"),
        _format_card("% Mantiveram", f"{indic['%_unchanged']:.1f}%", theme="yellow"),
        _format_card("Effect Size global", f"{indic['cohen_d_global']:.3f}"),
    ])

    # Seção de interpretação seguindo o padrão da Fase4
    interp_html = _interpretacao_contexto_html(indic)

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Relatório Visual WordGen - Vocabulário (Fase 3)</title>
<style>
    :root {{
        --bg: #f5f6fa;
        --text: #2c3e50;
        --muted: #6b7280;
        --purple1: #6a11cb;
        --purple2: #8d36ff;
        --card-grad: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --green-grad: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        --red-grad: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        --yellow-grad: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
    }}
    body {{
        margin: 0; background: var(--bg); color: var(--text); font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }}
    .header {{
        background: linear-gradient(120deg, var(--purple1) 0%, var(--purple2) 100%);
        color: #fff; padding: 28px 18px; box-shadow: 0 2px 14px rgba(0,0,0,.12);
    }}
    .header .title {{
        font-size: 26px; font-weight: 700; margin: 0;
    }}
    .header .subtitle {{
        font-size: 14px; opacity: 0.95; margin-top: 6px;
    }}
    .header .timestamp {{
        font-size: 12px; opacity: 0.85; margin-top: 4px;
    }}
    .container {{
        max-width: 1200px; margin: 18px auto; background: #fff; border-radius: 12px; padding: 22px; box-shadow: 0 10px 24px rgba(0,0,0,.06);
    }}
    .cards {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-top: 16px;
    }}
    .card {{
        background: var(--card-grad); color: #fff; border-radius: 10px; padding: 14px; box-shadow: 0 4px 12px rgba(0,0,0,.12);
    }}
    .card.green {{ background: var(--green-grad); }}
    .card.red {{ background: var(--red-grad); }}
    .card.yellow {{ background: var(--yellow-grad); }}
    .card .card-label {{ font-size: 13px; opacity: 0.95; }}
    .card .valor {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
    .card .desc {{ font-size: 11px; opacity: 0.9; }}

    h2.section {{
        margin-top: 22px; font-size: 18px; border-left: 4px solid var(--purple1); padding-left: 10px; color: #1f2937;
    }}
    .figs {{ display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 10px; }}
    .fig {{ background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 8px; }}
    .fig img {{ width: 100%; height: auto; border-radius: 6px; }}
    .fig .caption {{ font-size: 12px; color: var(--muted); margin-top: 6px; text-align: center; }}

    .interp {{ background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 14px; }}
    .grupo-item {{ background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px 12px; margin: 10px 0; }}
    .grupo-titulo {{ font-weight: 600; }}
    .grupo-detalhes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 6px; color: #374151; font-size: 13px; margin-top: 6px; }}

    .foot-note {{ font-size: 12px; color: var(--muted); text-align: center; margin-top: 16px; }}

    .badge {{ display:inline-block; padding:2px 6px; border-radius:999px; font-size:11px; line-height:1.4; }}
    .badge.warn {{ background:#fff3cd; color:#7a6200; border:1px solid #ffe69c; }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Relatório Visual WordGen</div>
        <div class="subtitle">Vocabulário – Fase 3 (Pré vs Pós). Análise pareada por ID de aluno.</div>
        <div class="timestamp">Gerado em: {now}</div>
    </div>

    <div class="container">
        <h2 class="section">Indicadores</h2>
        <div class="cards">
            {cards_html}
        </div>

        <h2 class="section">Gráficos</h2>
        <div class="figs">
            <div class="fig">
                <img src="{img_barras}" alt="Comparação Pré vs Pós" />
                <div class="caption">Comparação das médias (Pré vs Pós) com desvio padrão.</div>
            </div>
            <div class="fig">
                <img src="{img_hist}" alt="Histograma de deltas" />
                <div class="caption">Distribuição dos deltas (pós - pré).</div>
            </div>
            <div class="fig">
                <img src="{img_categ}" alt="Categorias Cohen" />
                <div class="caption">Categorias de Cohen com base em SD do pré.</div>
            </div>
            <div class="fig">
                <img src="{img_top}" alt="Top questões" />
                <div class="caption">Questões com maiores ganhos e quedas em proporção de acertos.</div>
            </div>
        </div>

        <h2 class="section">Interpretação contextualizada do effect size</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">Referências: Cohen (1988) – 0.2/0.5/0.8; Hattie (2009) – d≥0.4 como "bom resultado"; Vocabulário (Marulis & Neuman, 2010) – d≥0.35 significativo.</p>
            {interp_html}
        </div>

        <div class="foot-note">
            <p>Notas: ES global = Δ/SD(Pré). Categorias Cohen baseadas em SD(Pré). Linhas com valores fora do domínio [0,1] ou com ausências em Qs foram removidas.</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def gerar_relatorio(path_pre: str = DEFAULT_PRE, path_pos: str = DEFAULT_POS, saida_html: str = OUTPUT_HTML) -> str:
    df_pre_a, df_pos_a, pre_tot, pos_tot, delta, cols_q, meta = carregar_e_preparar(path_pre, path_pos)

    print("FASE 3 - Pré/Pós")
    print(f"Registros brutos: PRE={meta['n_registros_pre_raw']}, POS={meta['n_registros_pos_raw']}")
    print(f"Válidos após limpeza: PRE={meta['n_validos_pre']}, POS={meta['n_validos_pos']}")
    print(f"IDs correspondentes e dados completos: N={meta['n_final']} | Qs utilizadas: {meta['qtd_q']}")

    indic = indicadores(pre_tot, pos_tot, delta)

    # Gerar gráficos em Base64
    print("Gerando gráficos em Base64...")
    img_barras = gerar_prepos_barras(pre_tot, pos_tot)
    img_hist = gerar_delta_hist(delta)
    img_top = gerar_top_questoes(df_pre_a, df_pos_a, cols_q)

    cat_df = categorizar_por_cohen(delta, indic["std_pre"])
    img_categ = gerar_categorias_bench(cat_df)

    print("Renderizando HTML...")
    html = gerar_html(indic, img_barras, img_hist, img_top, img_categ)
    with open(saida_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Relatório salvo em: {saida_html}")
    print("Todas as imagens foram incorporadas diretamente no HTML!")
    return saida_html


if __name__ == "__main__":
    gerar_relatorio()
