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
    mask_validos = work[cols_q].applymap(lambda x: x in (0, 1)).all(axis=1)
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


# ---------- Gráficos (Base64) ----------

def gerar_prepos_barras(pre_tot: pd.Series, pos_tot: pd.Series) -> str:
    """Gera gráfico de barras pré vs pós e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(8, 5))
    medias = [pre_tot.mean(), pos_tot.mean()]
    desvios = [pre_tot.std(ddof=1), pos_tot.std(ddof=1)]
    bars = ax.bar(["Pré", "Pós"], medias, yerr=desvios, capsize=6, color=["#7B68EE", "#4B0082"], alpha=0.9)
    ax.set_ylabel("Acertos (média ± DP)")
    ax.set_title("Comparação Pré vs Pós (acertos totais)")
    for b, m in zip(bars, medias):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(desvios)*0.05, f"{m:.2f}", ha="center", va="bottom")
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_scatter(pre_tot: pd.Series, pos_tot: pd.Series) -> str:
    """Gera gráfico de dispersão e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(7, 7))
    sns.scatterplot(x=pre_tot, y=pos_tot, s=18, alpha=0.5, edgecolor="none", ax=ax, color="#6A5ACD")
    lim_min = min(pre_tot.min(), pos_tot.min())
    lim_max = max(pre_tot.max(), pos_tot.max())
    ax.plot([lim_min, lim_max], [lim_min, lim_max], linestyle="--", color="#444", label="y=x")
    ax.set_xlabel("Pré (acertos)")
    ax.set_ylabel("Pós (acertos)")
    ax.set_title("Dispersão: Pré vs Pós por aluno")
    ax.legend()
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_delta_hist(delta: pd.Series) -> str:
    """Gera histograma de deltas e retorna como Base64."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(delta, bins=21, kde=True, color="#8A2BE2", ax=ax)
    ax.axvline(delta.mean(), color="red", linestyle="--", label=f"Δ médio = {delta.mean():.2f}")
    ax.set_xlabel("Δ (Pós - Pré)")
    ax.set_ylabel("Frequência")
    ax.set_title("Distribuição das diferenças individuais (Δ)")
    ax.legend()
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


def gerar_heatmap_questoes(df_pre: pd.DataFrame, df_pos: pd.DataFrame, cols_q: List[str]) -> str:
    """Gera heatmap das questões e retorna como Base64."""
    # Proporção de acertos por questão
    prop_pre = df_pre[cols_q].mean(axis=0)
    prop_pos = df_pos[cols_q].mean(axis=0)
    m = pd.DataFrame([prop_pre.values, prop_pos.values], index=["Pré", "Pós"], columns=cols_q)

    fig, ax = plt.subplots(figsize=(min(16, 0.35*len(cols_q)+4), 4.5))
    sns.heatmap(m, annot=False, cmap="Purples", vmin=0, vmax=1, cbar_kws={"label": "Proporção correta"}, ax=ax)
    ax.set_title("Proporção de acertos por questão (Pré vs Pós)")
    ax.set_xlabel("Questões")
    ax.set_ylabel("")
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
    sns.barplot(x=dados.values, y=dados.index, palette=cores, ax=ax)
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

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=perc.index, y=perc.values, palette="viridis", ax=ax)
    ax.set_ylabel("% de alunos")
    ax.set_xlabel("")
    ax.set_title("Distribuição de mudanças (padrão Cohen, SD do Pré)")
    ax.set_ylim(0, max(perc.max()*1.15, 10))
    ax.tick_params(axis='x', rotation=35)
    for i, v in enumerate(perc.values):
        ax.text(i, v + max(perc.max()*0.02, 0.5), f"{v:.1f}%", ha="center")
    # Linha de referência Hattie 0.4 e Vocabulário 0.35 como legenda explicativa no título
    plt.tight_layout()
    
    base64_str = fig_to_base64(fig)
    plt.close(fig)
    return base64_str


# ---------- HTML ----------

def gerar_html(indic: Dict[str, float], img_barras: str, img_scatter: str, 
               img_hist: str, img_heatmap: str, img_top: str, img_categ: str) -> str:
    d = indic.get("cohen_d_global", np.nan)
    d_txt = "NA" if pd.isna(d) else f"{d:.3f}"

    # Badges for benchmarks
    badge_hattie = "☑" if (not pd.isna(d) and d >= 0.4) else "☐"
    badge_vocab = "☑" if (not pd.isna(d) and d >= 0.35) else "☐"

    style = """
    <style>
      body { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; color: #1a1a1a; }
      header { background: linear-gradient(90deg, #6a11cb, #2575fc); color: white; padding: 28px 20px; }
      header h1 { margin: 0 0 6px 0; font-weight: 700; }
      header p { margin: 0; opacity: 0.95; }
      .container { padding: 18px 22px 40px; }
      .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 16px 0 10px; }
      .card { background: #ffffff; border: 1px solid #eee; border-radius: 12px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
      .card h3 { margin: 0 0 6px 0; font-size: 14px; color: #555; font-weight: 600; }
      .card .value { font-size: 22px; font-weight: 700; color: #4B0082; }
      section { margin-top: 24px; }
      section h2 { font-size: 18px; margin-bottom: 10px; color: #333; }
      figure { margin: 16px 0; }
      figure img { max-width: 100%; border-radius: 10px; border: 1px solid #eee; }
      figcaption { font-size: 12px; color: #666; margin-top: 6px; }
      .badges { display: flex; gap: 10px; margin-top: 6px; }
      .badge { display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 12px; border: 1px solid #ddd; background: #fafafa; }
      footer { margin-top: 30px; font-size: 12px; color: #666; }
    </style>
    """

    cards = f"""
    <div class="cards">
      <div class="card"><h3>Amostra</h3><div class="value">{indic['n']}</div></div>
      <div class="card"><h3>Média Pré ± DP</h3><div class="value">{indic['mean_pre']:.2f} ± {indic['std_pre']:.2f}</div></div>
      <div class="card"><h3>Média Pós ± DP</h3><div class="value">{indic['mean_pos']:.2f} ± {indic['std_pos']:.2f}</div></div>
      <div class="card"><h3>Δ médio (Pós - Pré)</h3><div class="value">{indic['mean_delta']:.2f}</div></div>
      <div class="card"><h3>Cohen d (global)</h3><div class="value">{d_txt}</div></div>
      <div class="card"><h3>Variação</h3><div class="value">{indic['%_improved']:.1f}% ↑ · {indic['%_unchanged']:.1f}% → · {indic['%_worsened']:.1f}% ↓</div></div>
    </div>
    """

    benchmarks = f"""
    <div class="card">
      <h3>Benchmarks educacionais</h3>
      <div class="badges">
        <span class="badge">Hattie 0.40: {badge_hattie}</span>
        <span class="badge">Vocabulário 0.35: {badge_vocab}</span>
        <span class="badge">Cohen d global: {d_txt}</span>
      </div>
      <p style="margin-top:6px; font-size: 13px; color:#444">Interpretação: valores ≥ 0.40 sugerem impacto educacional típico de boas intervenções gerais (Hattie). Para vocabulário, efeitos ≥ 0.35 são frequentemente relatados em meta-análises (Marulis & Neuman, 2010). Este relatório usa SD do pré como base de padronização.</p>
    </div>
    """

    html = f"""
    <!doctype html>
    <html lang=\"pt-br\">
    <head>
      <meta charset=\"utf-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>Relatório Visual WordGen – Fase 3</title>
      {style}
    </head>
    <body>
      <header>
        <h1>Vocabulário WordGen – Fase 3 (Pré vs Pós)</h1>
        <p>Relatório visual com indicadores, gráficos analíticos e benchmarks</p>
      </header>
      <div class="container">
        {cards}
        <section>
          <h2>Comparação geral e dispersão</h2>
          <figure>
            <img src="{img_barras}" alt="Médias Pré vs Pós" />
            <figcaption>Barra com média e desvio padrão por momento (Pré/Pós).</figcaption>
          </figure>
          <figure>
            <img src="{img_scatter}" alt="Dispersão Pré vs Pós" />
            <figcaption>Cada ponto representa um aluno. Linha tracejada indica referência y = x.</figcaption>
          </figure>
        </section>
        <section>
          <h2>Distribuição das mudanças</h2>
          <figure>
            <img src="{img_hist}" alt="Histograma de Δ" />
            <figcaption>Δ = acertos no Pós − acertos no Pré.</figcaption>
          </figure>
          <figure>
            <img src="{img_categ}" alt="Categorias Cohen" />
            <figcaption>Distribuição em categorias de mudança com base nos limiares de Cohen (SD do Pré).</figcaption>
          </figure>
        </section>
        <section>
          <h2>Diagnóstico por questão</h2>
          <figure>
            <img src="{img_heatmap}" alt="Heatmap por questão" />
            <figcaption>Proporção de acertos por questão no Pré e no Pós.</figcaption>
          </figure>
          <figure>
            <img src="{img_top}" alt="Top questões (melhoras/quedas)" />
            <figcaption>Questões com maiores ganhos e quedas em proporção de acertos.</figcaption>
          </figure>
        </section>
        <section>
          <h2>Análise com benchmarks educacionais</h2>
          {benchmarks}
        </section>
        <footer>
          <p>Notas: linhas com valores fora do domínio [0,1] ou com ausências em Qs foram removidas. IDs foram alinhados entre Pré e Pós para análise pareada.</p>
          <p>Referências: Cohen (1988); Hattie (2009); Marulis & Neuman (2010).</p>
        </footer>
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
    img_scatter = gerar_scatter(pre_tot, pos_tot)
    img_hist = gerar_delta_hist(delta)
    img_heatmap = gerar_heatmap_questoes(df_pre_a, df_pos_a, cols_q)
    img_top = gerar_top_questoes(df_pre_a, df_pos_a, cols_q)

    cat_df = categorizar_por_cohen(delta, indic["std_pre"])
    img_categ = gerar_categorias_bench(cat_df)

    print("Renderizando HTML...")
    html = gerar_html(indic, img_barras, img_scatter, img_hist, img_heatmap, img_top, img_categ)
    with open(saida_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Relatório salvo em: {saida_html}")
    print("Todas as imagens foram incorporadas diretamente no HTML!")
    return saida_html


if __name__ == "__main__":
    gerar_relatorio()
