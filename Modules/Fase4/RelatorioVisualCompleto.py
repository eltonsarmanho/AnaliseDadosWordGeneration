import os
import pathlib
from datetime import datetime
from typing import Dict, List
import base64
import io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
FIG_DIR = DATA_DIR / "figures"
CSV_PATH = DATA_DIR / "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_4.csv"
HTML_OUT = DATA_DIR / "relatorio_visual_wordgen.html"

FIG_HIST = FIG_DIR / "delta_medio_hist.png"
FIG_CATS = FIG_DIR / "categorias_mudanca_bar.png"
FIG_FOREST = FIG_DIR / "effect_size_forest.png"

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 120,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ======================
# Utilidades
# ======================

def _to_numeric_series(s: pd.Series) -> pd.Series:
    """Converte série para numérico tratando vírgula decimal e caracteres estranhos."""
    if s.dtype.kind in ("i", "f"):
        return s
    s = s.astype(str).str.replace("\u00A0", " ")  # NBSP
    s = s.str.replace(".", "", regex=False)  # remove separador milhar (se houver)
    s = s.str.replace(",", ".", regex=False)  # vírgula -> ponto
    s = s.str.replace(r"[^0-9\.-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")


def fig_to_base64(fig) -> str:
    """Converte uma figura matplotlib para string Base64."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return f"data:image/png;base64,{img_base64}"


def categorizar_mudanca_cohen(delta: float, baseline_sd: float) -> str:
    """Retorna a categoria de mudança segundo thresholds de Cohen, usando SD do pré (baseline)."""
    if not np.isfinite(baseline_sd) or baseline_sd <= 0:
        return "Sem Mudança Prática (±0.2 SD)"

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


# ======================
# Carregamento e limpeza
# ======================

def carregar_e_preparar() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {CSV_PATH}")

    # Lê como texto para tratar vírgulas/ruídos apenas nas colunas de interesse
    df = pd.read_csv(CSV_PATH, dtype=str)

    # Garante existência das colunas necessárias
    needed_cols = ["group", "total_pre_voc", "total_pos_voc"]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Colunas ausentes no CSV: {missing}")

    # Conversões para numérico
    df["total_pre_voc"] = _to_numeric_series(df["total_pre_voc"]) 
    df["total_pos_voc"] = _to_numeric_series(df["total_pos_voc"]) 

    # Limpeza: remover NaN/NULL nas colunas-chave e linhas sem grupo
    n_before = len(df)
    df = df.dropna(subset=["total_pre_voc", "total_pos_voc", "group"]).copy()
    # Normaliza espaços em branco no nome do grupo
    df["group"] = df["group"].astype(str).str.strip()

    # Delta e SD baseline
    df["delta_voc"] = df["total_pos_voc"] - df["total_pre_voc"]
    baseline_sd = float(df["total_pre_voc"].std(ddof=1))

    # Categoria de Cohen por aluno
    df["categoria_cohen"] = df["delta_voc"].apply(lambda x: categorizar_mudanca_cohen(x, baseline_sd))

    print(f"Registros antes da limpeza: {n_before}")
    print(f"Registros após a limpeza:  {len(df)}")
    print(f"SD(Pré) baseline:          {baseline_sd:.4f}")

    return df


# ======================
# Cálculos de indicadores
# ======================

def calcular_indicadores(df: pd.DataFrame) -> Dict[str, float]:
    baseline_sd = float(df["total_pre_voc"].std(ddof=1))
    delta_mean = float(df["delta_voc"].mean())

    es_global = np.nan
    if np.isfinite(baseline_sd) and baseline_sd > 0:
        es_global = delta_mean / baseline_sd

    return {
        "n_final": int(len(df)),
        "n_grupos": int(df["group"].nunique()),
        "media_pre": float(df["total_pre_voc"].mean()),
        "media_pos": float(df["total_pos_voc"].mean()),
        "delta_medio": delta_mean,
        "%_melhoraram": float((df["delta_voc"] > 0).mean() * 100.0),
        "%_pioraram": float((df["delta_voc"] < 0).mean() * 100.0),
        "%_mantiveram": float((df["delta_voc"] == 0).mean() * 100.0),
        "es_global": float(es_global) if np.isfinite(es_global) else float("nan"),
        "baseline_sd": baseline_sd,
    }


def resumo_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    baseline_sd = float(df["total_pre_voc"].std(ddof=1))
    grp = df.groupby("group", observed=False).agg(
        n=("group", "size"),
        pre_media=("total_pre_voc", "mean"),
        pos_media=("total_pos_voc", "mean"),
        delta_mean=("delta_voc", "mean"),
        delta_sd=("delta_voc", lambda s: np.std(s, ddof=1)),
    ).reset_index()

    grp["effect_size"] = np.where(baseline_sd > 0, grp["delta_mean"] / baseline_sd, np.nan)
    grp["se_d"] = np.where(baseline_sd > 0, (grp["delta_sd"] / np.sqrt(grp["n"])) / baseline_sd, np.nan)
    grp["ci_low"] = grp["effect_size"] - 1.96 * grp["se_d"]
    grp["ci_high"] = grp["effect_size"] + 1.96 * grp["se_d"]
    return grp


# ======================
# Gráficos (Base64)
# ======================

def gerar_histograma_delta(df: pd.DataFrame) -> str:
    """Gera histograma e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(7, 4))
    vals = df["delta_voc"].dropna()
    ax.hist(vals, bins=30, color="#6baed6", edgecolor="white")
    mean_val = float(vals.mean()) if len(vals) else 0.0

    ax.axvline(0, color="black", linestyle=":", linewidth=1)
    ax.axvline(mean_val, color="#e41a1c", linestyle="--", linewidth=1.5)
    ax.set_title("Distribuição dos Deltas (Pós - Pré)")
    ax.set_xlabel("Delta de Vocabulário")
    ax.set_ylabel("Frequência")
    ax.text(0.98, 0.92, f"Média: {mean_val:.2f}", transform=ax.transAxes, ha="right", va="center", fontsize=9,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
    fig.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_barras_categorias(df: pd.DataFrame, baseline_sd: float) -> str:
    """Gera gráfico de barras das categorias e retorna como Base64."""
    cat_order = [
        "Piora Grande (<-0.8 SD)",
        "Piora Média (-0.8 a -0.5 SD)",
        "Piora Pequena (-0.5 a -0.2 SD)",
        "Sem Mudança Prática (±0.2 SD)",
        "Melhora Pequena (0.2-0.5 SD)",
        "Melhora Média (0.5-0.8 SD)",
        "Melhora Grande (≥0.8 SD)",
    ]
    cores = {
        "Piora Grande (<-0.8 SD)": "#d73027",
        "Piora Média (-0.8 a -0.5 SD)": "#f46d43",
        "Piora Pequena (-0.5 a -0.2 SD)": "#fdae61",
        "Sem Mudança Prática (±0.2 SD)": "#fee08b",
        "Melhora Pequena (0.2-0.5 SD)": "#d9ef8b",
        "Melhora Média (0.5-0.8 SD)": "#a6d96a",
        "Melhora Grande (≥0.8 SD)": "#66bd63",
    }

    counts = df["categoria_cohen"].value_counts().reindex(cat_order).fillna(0).astype(int)
    total = counts.sum()
    pct = counts / total * 100.0 if total else counts

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(range(len(cat_order)), pct.values, color=[cores[c] for c in cat_order])
    ax.set_xticks(range(len(cat_order)))
    ax.set_xticklabels(cat_order, rotation=30, ha="right")
    ax.set_ylabel("% de alunos")
    ax.set_title("Categorias de Cohen (geral)")

    for rect, v in zip(bars, pct.values):
        ax.text(rect.get_x() + rect.get_width()/2, rect.get_height() + 0.5, f"{v:.1f}%",
                ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_forest_plot(grp: pd.DataFrame) -> str:
    """Gera forest plot e retorna como Base64."""
    # Ordena por ES
    data = grp.copy()
    data = data.sort_values("effect_size")

    y = np.arange(len(data))
    es = data["effect_size"].values
    ci_low = data["ci_low"].values
    ci_high = data["ci_high"].values

    fig, ax = plt.subplots(figsize=(7.5, max(4, 0.3 * len(data) + 1)))

    # IC horizontais
    ax.hlines(y=y, xmin=ci_low, xmax=ci_high, color="#999999", linewidth=2)

    # Pontos com destaque: |d|>=0.4 em verde; n pequeno (n<10) como círculo vazado
    colors = ["#238b45" if (isinstance(v, (float, int)) and np.isfinite(v) and abs(v) >= 0.4) else "#969696" for v in es]
    ns = data["n"].values
    for i, (xv, col, n) in enumerate(zip(es, colors, ns)):
        if not (isinstance(xv, (float, int)) and np.isfinite(xv)):
            continue
        if n < 10:
            ax.plot([xv], [i], marker="o", markersize=8, markerfacecolor="white", markeredgecolor=col, markeredgewidth=1.5)
        else:
            ax.plot([xv], [i], marker="o", markersize=7, color=col)

    # Linhas de referência
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.axvline(0.4, color="#238b45", linestyle=":", linewidth=1)
    ax.axvline(-0.4, color="#238b45", linestyle=":", linewidth=1)

    ax.set_yticks(y)
    ax.set_yticklabels(data["group"].values)
    ax.set_xlabel("Effect Size (Δ / SD Pré)")
    ax.set_title("Effect Size por Grupo (IC 95%)")

    # Ajusta limites x se possível
    finite_vals = np.array([v for v in np.concatenate([ci_low, ci_high]) if np.isfinite(v)])
    if finite_vals.size:
        xmin = min(np.min(finite_vals) - 0.05, -0.6)
        xmax = max(np.max(finite_vals) + 0.05, 1.0)
        ax.set_xlim(xmin, xmax)

    # Legenda explicativa
    legend_elems = [
        Line2D([0], [0], marker='o', color='w', label='|d| ≥ 0.4', markerfacecolor='#238b45', markeredgecolor='#238b45', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='|d| < 0.4', markerfacecolor='#969696', markeredgecolor='#969696', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='n < 10 (estimativa instável)', markerfacecolor='white', markeredgecolor='#666', markersize=8)
    ]
    ax.legend(handles=legend_elems, loc='lower right', frameon=False, fontsize=8)

    fig.tight_layout()
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


# ======================
# HTML Rendering
# ======================

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


def _interpretacao_contexto_html(grp: pd.DataFrame) -> str:
    rows = []
    for _, r in grp.sort_values("effect_size", ascending=False).iterrows():
        es = r["effect_size"]
        mag = interpretar_magnitude(es) if np.isfinite(es) else "Indefinido"
        ic = (r["ci_low"], r["ci_high"]) if np.isfinite(r["ci_low"]) and np.isfinite(r["ci_high"]) else (np.nan, np.nan)
        bench_hattie = "✓ Acima do benchmark (d≥0.4)" if (np.isfinite(es) and abs(es) >= 0.4) else "⚠ Abaixo do benchmark (d<0.4)"
        bench_vocab = "✓ Significativo em Vocabulário (d≥0.35)" if (np.isfinite(es) and abs(es) >= 0.35) else "⚠ Abaixo do threshold (d<0.35)"
        small_n_badge = "<span class='badge warn'>n pequeno (estimativa instável)</span>" if int(r.get('n', 0)) < 10 else ""

        rows.append(f"""
        <div class="grupo-item">
            <div class="grupo-titulo">{r['group']}: ES = {es:.3f} (n={int(r['n'])}) {small_n_badge}</div>
            <div class="grupo-detalhes">
                <span><strong>Magnitude:</strong> {mag}</span>
                <span><strong>IC 95%:</strong> [{ic[0]:.3f}, {ic[1]:.3f}]</span>
                <span>{bench_hattie}</span>
                <span>{bench_vocab}</span>
            </div>
        </div>
        """)

    return "\n".join(rows)


def gerar_html(df: pd.DataFrame, inds: Dict[str, float], grp: pd.DataFrame, 
               img_hist: str, img_cats: str, img_forest: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cards
    cards_html = "".join([
        _format_card("Registros", f"{inds['n_final']}", "alunos após limpeza"),
        _format_card("Total de grupos", f"{inds['n_grupos']}", "com dados válidos"),
        _format_card("Média Pré", f"{inds['media_pre']:.2f}"),
        _format_card("Média Pós", f"{inds['media_pos']:.2f}"),
        _format_card("Delta médio", f"{inds['delta_medio']:.2f}", "pontos"),
        _format_card("% Melhoraram", f"{inds['%_melhoraram']:.1f}%", theme="green"),
        _format_card("% Pioraram", f"{inds['%_pioraram']:.1f}%", theme="red"),
        _format_card("% Mantiveram", f"{inds['%_mantiveram']:.1f}%", theme="yellow"),
        _format_card("Effect Size global", f"{inds['es_global']:.3f}"),
    ])

    # Secção de interpretação por grupo
    interp_html = _interpretacao_contexto_html(grp)

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Relatório Visual WordGen - Vocabulário (Fase 4)</title>
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
        <div class="subtitle">Vocabulário – Fase 4 (TDE). Baseado em total_pre_voc, total_pos_voc e group.</div>
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
                <img src="{img_hist}" alt="Histograma de deltas" />
                <div class="caption">Distribuição dos deltas (pós - pré).</div>
            </div>
            <div class="fig">
                <img src="{img_cats}" alt="Categorias Cohen" />
                <div class="caption">Categorias de Cohen com base em SD do pré.</div>
            </div>
            <div class="fig">
                <img src="{img_forest}" alt="Forest plot ES por grupo" />
                <div class="caption">Effect Size por grupo (IC 95%). Linha tracejada: d = 0; Pontilhado: |d| = 0.4. Pontos vazados: n < 10 (estimativa instável).</div>
            </div>
        </div>

        <h2 class="section">Interpretação contextualizada dos effect sizes por grupo</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">Referências: Cohen (1988) – 0.2/0.5/0.8; Hattie (2009) – d≥0.4 como “bom resultado”; Vocabulário (Marulis & Neuman, 2010) – d≥0.35 significativo.</p>
            {interp_html}
        </div>

        <div class="foot-note">
            <p>Notas: ES global = Δ/SD(Pré). IC 95% via SE = SD(Δ)/√n / SD(Pré). Categorias Cohen baseadas em SD(Pré). Tudo calculado diretamente do CSV.</p>
        </div>
    </div>
</body>
</html>
"""
    return html


# ======================
# Main
# ======================

def main() -> pathlib.Path:
    print("Carregando e limpando dados do CSV...")
    df = carregar_e_preparar()

    print("Calculando indicadores globais e por grupo...")
    inds = calcular_indicadores(df)
    grp = resumo_por_grupo(df)

    print("Gerando gráficos em Base64...")
    img_hist = gerar_histograma_delta(df)
    img_cats = gerar_barras_categorias(df, inds["baseline_sd"])
    img_forest = gerar_forest_plot(grp)

    print("Renderizando HTML...")
    html = gerar_html(df, inds, grp, img_hist, img_cats, img_forest)
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Relatório gerado em: {HTML_OUT}")
    print("Todas as imagens foram incorporadas diretamente no HTML!")
    return HTML_OUT


if __name__ == "__main__":
    main()
