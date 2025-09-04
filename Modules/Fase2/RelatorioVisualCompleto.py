import os
import io
import base64
import pathlib
import json
from typing import List, Tuple, Dict, Any
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.switch_backend("Agg")
sns.set_theme(style="whitegrid")

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
FIG_DIR = DATA_DIR / "figures"

# Dados da Fase 2
ARQUIVO_PRE = DATA_DIR / "Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.xlsx"
ARQUIVO_POS = DATA_DIR / "Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).xlsx"
ARQUIVO_RESPOSTAS = DATA_DIR / "RespostaVocabulario.json"
OUTPUT_HTML = DATA_DIR / "relatorio_visual_wordgen_fase2.html"

# Figuras
FIG_GRUPOS_BARRAS = FIG_DIR / "fase2_grupos_barras.png"
FIG_PALAVRAS_TOP = FIG_DIR / "fase2_palavras_top.png"
FIG_COHEN_BENCHMARK = FIG_DIR / "fase2_cohen_benchmark.png"
FIG_INTERGRUPOS = FIG_DIR / "fase2_comparacao_intergrupos.png"
FIG_HEATMAP_ERROS_POS = FIG_DIR / "fase2_heatmap_erros_pos.png"
FIG_HEATMAP_ERROS_PRE = FIG_DIR / "fase2_heatmap_erros_pre.png"

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 120,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ======================
# Funções de utilidade
# ======================

def interpretar_cohen_d(d):
    """Interpreta o Cohen's d conforme benchmarks educacionais"""
    abs_d = abs(d)
    
    # Magnitude (Cohen, 1988)
    if abs_d >= 0.8:
        magnitude = "Grande"
    elif abs_d >= 0.5:
        magnitude = "Médio"
    elif abs_d >= 0.2:
        magnitude = "Pequeno"
    else:
        magnitude = "Negligível"
    
    # Benchmark educacional (Hattie, 2009)
    if abs_d >= 0.4:
        hattie_status = "Acima do benchmark (d≥0.4)"
    else:
        hattie_status = "Abaixo do benchmark (d≥0.4)"
    
    # Significativo para vocabulário (Marulis & Neuman, 2010)
    if abs_d >= 0.35:
        vocab_status = "Significativo para vocabulário (d≥0.35)"
    else:
        vocab_status = "Abaixo do threshold para vocabulário (d≥0.35)"
    
    return {
        'magnitude': magnitude,
        'hattie_status': hattie_status,
        'vocab_status': vocab_status
    }

def converter_valor_questao(valor):
    """Converte valores das questões para sistema numérico"""
    if pd.isna(valor):
        return np.nan
    
    valor_str = str(valor).strip().upper()
    
    if valor_str in ['0', '0.0']:
        return 0  # Erro
    elif valor_str in ['1', '1.0']:
        return 1  # Acerto parcial
    elif valor_str in ['2', '2.0']:
        return 2  # Acerto total
    elif valor_str in ['D', 'M']:
        return np.nan  # Neutro
    else:
        try:
            num_valor = float(valor_str)
            if num_valor == 0:
                return 0
            elif num_valor == 1:
                return 1
            elif num_valor == 2:
                return 2
            else:
                return np.nan
        except:
            return np.nan

def classificar_grupo_etario(turma):
    """Classifica estudantes em grupos etários"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
        return "6º/7º anos"
    elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
        return "8º/9º anos"
    else:
        return "Indefinido"

def carregar_mapeamento_palavras():
    """Carrega o mapeamento de questões para palavras"""
    try:
        with open(ARQUIVO_RESPOSTAS, 'r', encoding='utf-8') as f:
            dados_respostas = json.load(f)
        
        mapeamento = {}
        for item in dados_respostas:
            for questao, info in item.items():
                mapeamento[questao] = info['Palavra Trabalhada']
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento de palavras: {e}")
        return {}

def fig_to_base64(fig):
    """Converte uma figura matplotlib para string Base64"""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return f"data:image/png;base64,{img_base64}"

# ======================
# Funções de análise
# ======================

def carregar_e_preparar_dados():
    """Carrega e prepara os dados da Fase 2"""
    print("1. Carregando dados...")
    
    # Carregar dados
    df_pre = pd.read_excel(ARQUIVO_PRE)
    df_pos = pd.read_excel(ARQUIVO_POS)
    
    # Carregar mapeamento de palavras
    mapeamento_palavras = carregar_mapeamento_palavras()
    
    # Colunas de questões
    colunas_q = [f'Q{i}' for i in range(1, 51)]
    
    # Aplicar conversão de valores
    for col in colunas_q:
        if col in df_pre.columns:
            df_pre[col] = df_pre[col].apply(converter_valor_questao)
        if col in df_pos.columns:
            df_pos[col] = df_pos[col].apply(converter_valor_questao)
    
    # Adicionar grupos etários
    df_pre['GrupoEtario'] = df_pre['Turma'].apply(classificar_grupo_etario)
    df_pos['GrupoEtario'] = df_pos['Turma'].apply(classificar_grupo_etario)
    
    # Criar identificador único
    df_pre['ID_Unico'] = df_pre['Nome'].astype(str) + "_" + df_pre['Turma'].astype(str)
    df_pos['ID_Unico'] = df_pos['Nome'].astype(str) + "_" + df_pos['Turma'].astype(str)
    
    print("2. Limpando dados...")
    
    # Filtrar apenas estudantes que participaram de ambos os testes
    ids_pre = set(df_pre['ID_Unico'])
    ids_pos = set(df_pos['ID_Unico'])
    ids_comuns = ids_pre.intersection(ids_pos)
    
    df_pre_filtrado = df_pre[df_pre['ID_Unico'].isin(ids_comuns)].copy()
    df_pos_filtrado = df_pos[df_pos['ID_Unico'].isin(ids_comuns)].copy()
    
    # Função para verificar questões válidas
    def tem_questoes_validas(row):
        valores_validos = 0
        for col in colunas_q:
            if col in row.index and not pd.isna(row[col]):
                valores_validos += 1
        return valores_validos >= 40  # Pelo menos 80% das questões
    
    # Aplicar filtro
    mask_pre = df_pre_filtrado.apply(tem_questoes_validas, axis=1)
    mask_pos = df_pos_filtrado.apply(tem_questoes_validas, axis=1)
    
    df_pre_filtrado = df_pre_filtrado[mask_pre]
    df_pos_filtrado = df_pos_filtrado[mask_pos]
    
    # Filtrar novamente por IDs comuns após limpeza
    ids_pre_limpo = set(df_pre_filtrado['ID_Unico'])
    ids_pos_limpo = set(df_pos_filtrado['ID_Unico'])
    ids_finais = ids_pre_limpo.intersection(ids_pos_limpo)
    
    df_pre_final = df_pre_filtrado[df_pre_filtrado['ID_Unico'].isin(ids_finais)]
    df_pos_final = df_pos_filtrado[df_pos_filtrado['ID_Unico'].isin(ids_finais)]
    
    print(f"   Dados limpos: {len(df_pre_final)} estudantes")
    
    return df_pre_final, df_pos_final, colunas_q, mapeamento_palavras

def calcular_scores(df_pre_final, df_pos_final, colunas_q):
    """Calcula scores por estudante"""
    print("3. Calculando scores...")
    
    scores_data = []
    
    for _, row_pre in df_pre_final.iterrows():
        id_unico = row_pre['ID_Unico']
        grupo = row_pre['GrupoEtario']
        
        # Encontrar correspondente no pós-teste
        pos_rows = df_pos_final[df_pos_final['ID_Unico'] == id_unico]
        if len(pos_rows) == 0:
            continue
            
        row_pos = pos_rows.iloc[0]
        
        # Calcular scores
        score_pre = 0
        score_pos = 0
        questoes_validas = 0
        
        for col in colunas_q:
            if col in df_pre_final.columns and col in df_pos_final.columns:
                val_pre = row_pre[col]
                val_pos = row_pos[col]
                
                if not pd.isna(val_pre) and not pd.isna(val_pos):
                    score_pre += val_pre
                    score_pos += val_pos
                    questoes_validas += 1
        
        if questoes_validas >= 40:  # Pelo menos 80% das questões
            scores_data.append({
                'ID_Unico': id_unico,
                'GrupoEtario': grupo,
                'Score_Pre': score_pre,
                'Score_Pos': score_pos,
                'Delta': score_pos - score_pre,
                'N_Questoes': questoes_validas
            })
    
    return pd.DataFrame(scores_data)

def calcular_indicadores(scores_df, grupo_filtro=None):
    """Calcula indicadores estatísticos"""
    if grupo_filtro:
        dados = scores_df[scores_df['GrupoEtario'] == grupo_filtro]
    else:
        dados = scores_df
    
    if len(dados) == 0:
        return {}
    
    pre_scores = dados['Score_Pre']
    pos_scores = dados['Score_Pos']
    deltas = dados['Delta']
    
    # Estatísticas básicas
    indicadores = {
        'n': len(dados),
        'mean_pre': pre_scores.mean(),
        'std_pre': pre_scores.std(),
        'mean_pos': pos_scores.mean(),
        'std_pos': pos_scores.std(),
        'mean_delta': deltas.mean(),
        'std_delta': deltas.std()
    }
    
    # Cohen's d
    pooled_std = np.sqrt((pre_scores.var() + pos_scores.var()) / 2)
    indicadores['cohen_d'] = deltas.mean() / pooled_std if pooled_std > 0 else 0
    
    # Teste estatístico
    try:
        _, p_value = stats.wilcoxon(pre_scores, pos_scores, alternative='two-sided')
        indicadores['p_value'] = p_value
    except:
        indicadores['p_value'] = 1.0
    
    # Percentuais de mudança
    melhoraram = (deltas > 0).sum()
    pioraram = (deltas < 0).sum()
    mantiveram = (deltas == 0).sum()
    total = len(deltas)
    
    indicadores['perc_improved'] = (melhoraram / total) * 100
    indicadores['perc_worsened'] = (pioraram / total) * 100
    indicadores['perc_unchanged'] = (mantiveram / total) * 100
    
    return indicadores

def analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, grupo_filtro=None):
    """Analisa performance por palavra"""
    
    if grupo_filtro:
        df_pre_grupo = df_pre_final[df_pre_final['GrupoEtario'] == grupo_filtro]
        df_pos_grupo = df_pos_final[df_pos_final['GrupoEtario'] == grupo_filtro]
    else:
        df_pre_grupo = df_pre_final
        df_pos_grupo = df_pos_final
    
    palavras_data = []
    
    for col in colunas_q:
        if col in df_pre_grupo.columns and col in df_pos_grupo.columns:
            palavra = mapeamento_palavras.get(col, f"Palavra_{col}")
            
            valores_pre = df_pre_grupo[col].dropna()
            valores_pos = df_pos_grupo[col].dropna()
            
            if len(valores_pre) > 0 and len(valores_pos) > 0:
                # Taxa de acerto (≥1)
                acertos_pre = (valores_pre >= 1).sum()
                acertos_pos = (valores_pos >= 1).sum()
                
                taxa_pre = acertos_pre / len(valores_pre)
                taxa_pos = acertos_pos / len(valores_pos)
                melhora = taxa_pos - taxa_pre
                
                # Taxa de erro (=0)
                erros_pre = (valores_pre == 0).sum()
                erros_pos = (valores_pos == 0).sum()
                
                perc_erro_pre = erros_pre / len(valores_pre)
                perc_erro_pos = erros_pos / len(valores_pos)
                
                palavras_data.append({
                    'Questao': col,
                    'Palavra': palavra,
                    'Taxa_Pre': taxa_pre,
                    'Taxa_Pos': taxa_pos,
                    'Melhora': melhora,
                    'Perc_Erro_Pre': perc_erro_pre,
                    'Perc_Erro_Pos': perc_erro_pos
                })
    
    return pd.DataFrame(palavras_data)

# ======================
# Funções de visualização
# ======================

def plot_grupos_barras(scores_df):
    """Gráfico de barras comparando grupos"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    grupos = ['6º/7º anos', '8º/9º anos']
    cores = ['#3498db', '#e74c3c']
    
    # 1. Médias de scores
    ax = axes[0, 0]
    means_pre = []
    means_pos = []
    stds_pre = []
    stds_pos = []
    
    for grupo in grupos:
        data = scores_df[scores_df['GrupoEtario'] == grupo]
        means_pre.append(data['Score_Pre'].mean())
        means_pos.append(data['Score_Pos'].mean())
        stds_pre.append(data['Score_Pre'].std())
        stds_pos.append(data['Score_Pos'].std())
    
    x = np.arange(len(grupos))
    width = 0.35
    
    ax.bar(x - width/2, means_pre, width, yerr=stds_pre, label='Pré-teste', alpha=0.8, color=cores[0])
    ax.bar(x + width/2, means_pos, width, yerr=stds_pos, label='Pós-teste', alpha=0.8, color=cores[1])
    
    ax.set_xlabel('Grupos')
    ax.set_ylabel('Score Médio')
    ax.set_title('Comparação de Médias por Grupo')
    ax.set_xticks(x)
    ax.set_xticklabels(grupos)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Boxplot de deltas
    ax = axes[0, 1]
    deltas_data = [scores_df[scores_df['GrupoEtario'] == grupo]['Delta'] for grupo in grupos]
    bp = ax.boxplot(deltas_data, labels=grupos, patch_artist=True)
    
    for patch, cor in zip(bp['boxes'], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Mudança (Delta)')
    ax.set_title('Distribuição de Mudanças por Grupo')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    
    # 3. Tamanhos de amostra
    ax = axes[1, 0]
    sizes = [len(scores_df[scores_df['GrupoEtario'] == grupo]) for grupo in grupos]
    bars = ax.bar(grupos, sizes, color=cores, alpha=0.8)
    
    for bar, size in zip(bars, sizes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{size}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Número de Estudantes')
    ax.set_title('Tamanho das Amostras')
    ax.grid(True, alpha=0.3)
    
    # 4. Cohen's d por grupo
    ax = axes[1, 1]
    cohens_d = []
    for grupo in grupos:
        data = scores_df[scores_df['GrupoEtario'] == grupo]
        pre_scores = data['Score_Pre']
        pos_scores = data['Score_Pos']
        pooled_std = np.sqrt((pre_scores.var() + pos_scores.var()) / 2)
        d = (pos_scores.mean() - pre_scores.mean()) / pooled_std if pooled_std > 0 else 0
        cohens_d.append(d)
    
    bars = ax.bar(grupos, cohens_d, color=cores, alpha=0.8)
    
    # Linhas de referência
    ax.axhline(y=0.2, color='green', linestyle='--', alpha=0.7, label='Pequeno (0.2)')
    ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Médio (0.5)')
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Grande (0.8)')
    
    for bar, d in zip(bars, cohens_d):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{d:.3f}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel("Cohen's d")
    ax.set_title("Effect Size por Grupo")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_palavras_top(palavras_df_todos, palavras_df_grupo1, palavras_df_grupo2):
    """Top palavras com maior melhora - Layout simplificado 2x1"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. Top 20 palavras geral
    ax = axes[0]
    top_20 = palavras_df_todos.nlargest(20, 'Melhora')
    y_pos = np.arange(len(top_20))
    
    bars = ax.barh(y_pos, top_20['Melhora'], color='#3498db', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([p[:15] + '...' if len(p) > 15 else p for p in top_20['Palavra']])
    ax.set_xlabel('Melhora na Taxa de Acerto')
    ax.set_title('Top 20 Palavras - Melhora Geral')
    ax.grid(True, alpha=0.3)
    
    # 2. Comparação entre grupos - Top 15
    ax = axes[1]
    top_15_questoes = palavras_df_todos.nlargest(15, 'Melhora')['Questao']
    
    melhoras_g1 = []
    melhoras_g2 = []
    palavras_nomes = []
    
    for questao in top_15_questoes:
        palavra = palavras_df_todos[palavras_df_todos['Questao'] == questao]['Palavra'].iloc[0]
        palavras_nomes.append(palavra[:10] + '...' if len(palavra) > 10 else palavra)
        
        # Buscar melhora para cada grupo
        melhora_g1 = palavras_df_grupo1[palavras_df_grupo1['Questao'] == questao]['Melhora']
        melhora_g2 = palavras_df_grupo2[palavras_df_grupo2['Questao'] == questao]['Melhora']
        
        melhoras_g1.append(melhora_g1.iloc[0] if len(melhora_g1) > 0 else 0)
        melhoras_g2.append(melhora_g2.iloc[0] if len(melhora_g2) > 0 else 0)
    
    x = np.arange(len(palavras_nomes))
    width = 0.35
    
    ax.bar(x - width/2, melhoras_g1, width, label='6º/7º anos', color='#3498db', alpha=0.7)
    ax.bar(x + width/2, melhoras_g2, width, label='8º/9º anos', color='#e74c3c', alpha=0.7)
    
    ax.set_xlabel('Palavras')
    ax.set_ylabel('Melhora')
    ax.set_title('Comparação de Melhora - Top 15')
    ax.set_xticks(x)
    ax.set_xticklabels(palavras_nomes, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_cohen_benchmark(indicadores_geral, indicadores_grupo1, indicadores_grupo2):
    """Effect sizes com benchmarks"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Dados
    grupos = ['Geral', '6º/7º anos', '8º/9º anos']
    cohens_d = [
        indicadores_geral.get('cohen_d', 0),
        indicadores_grupo1.get('cohen_d', 0),
        indicadores_grupo2.get('cohen_d', 0)
    ]
    
    # Cores baseadas nos valores
    cores = []
    for d in cohens_d:
        abs_d = abs(d)
        if abs_d >= 0.6:
            cores.append('#28a745')  # Verde - Excelente
        elif abs_d >= 0.4:
            cores.append('#ffc107')  # Amarelo - Bom
        elif abs_d >= 0.35:
            cores.append('#fd7e14')  # Laranja - Adequado
        elif abs_d >= 0.2:
            cores.append('#6f42c1')  # Roxo - Marginal
        else:
            cores.append('#dc3545')  # Vermelho - Insuficiente
    
    # Gráfico de barras
    bars = ax.bar(grupos, cohens_d, color=cores, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Linhas de referência
    ax.axhline(y=0.2, color='green', linestyle='--', alpha=0.7, label='Cohen: Pequeno (0.2)')
    ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Cohen: Médio (0.5)')
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Cohen: Grande (0.8)')
    ax.axhline(y=0.35, color='purple', linestyle=':', alpha=0.7, label='Marulis: Significativo (0.35)')
    ax.axhline(y=0.4, color='blue', linestyle=':', alpha=0.7, label='Hattie: Bom (0.4)')
    
    # Valores nas barras
    for bar, d in zip(bars, cohens_d):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{d:.4f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_ylabel("Cohen's d")
    ax.set_title("Effect Sizes com Benchmarks Educacionais", fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_comparacao_intergrupos(scores_df):
    """Comparação detalhada entre grupos - Layout simplificado 2x1"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    grupos = ['6º/7º anos', '8º/9º anos']
    cores = ['#3498db', '#e74c3c']
    
    # 1. Distribuição de scores pré e pós combinados
    ax = axes[0]
    
    # Dados para cada grupo
    for i, grupo in enumerate(grupos):
        data_pre = scores_df[scores_df['GrupoEtario'] == grupo]['Score_Pre']
        data_pos = scores_df[scores_df['GrupoEtario'] == grupo]['Score_Pos']
        
        ax.hist(data_pre, alpha=0.4, label=f'{grupo} (Pré)', color=cores[i], bins=15, density=True)
        ax.hist(data_pos, alpha=0.6, label=f'{grupo} (Pós)', color=cores[i], bins=15, density=True, hatch='//')
    
    ax.set_xlabel('Scores')
    ax.set_ylabel('Densidade')
    ax.set_title('Distribuição de Scores Pré e Pós-teste')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Percentuais de melhoria
    ax = axes[1]
    melhorou = []
    piorou = []
    igual = []
    
    for grupo in grupos:
        data = scores_df[scores_df['GrupoEtario'] == grupo]
        total = len(data)
        
        melhorou.append((data['Delta'] > 0).sum() / total * 100)
        piorou.append((data['Delta'] < 0).sum() / total * 100)
        igual.append((data['Delta'] == 0).sum() / total * 100)
    
    x = np.arange(len(grupos))
    width = 0.25
    
    ax.bar(x - width, melhorou, width, label='Melhorou', color='#28a745', alpha=0.7)
    ax.bar(x, piorou, width, label='Piorou', color='#dc3545', alpha=0.7)
    ax.bar(x + width, igual, width, label='Igual', color='#6c757d', alpha=0.7)
    
    # Adicionar valores nas barras
    for i, (mel, pio, ig) in enumerate(zip(melhorou, piorou, igual)):
        ax.text(i - width, mel + 1, f'{mel:.1f}%', ha='center', va='bottom', fontsize=9)
        ax.text(i, pio + 1, f'{pio:.1f}%', ha='center', va='bottom', fontsize=9)
        ax.text(i + width, ig + 1, f'{ig:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Grupos')
    ax.set_ylabel('Percentual (%)')
    ax.set_title('Distribuição de Resultados')
    ax.set_xticks(x)
    ax.set_xticklabels(grupos)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_heatmap_erros_pos(palavras_df_grupo1, palavras_df_grupo2):
    """Heatmap de erros por palavra e grupo - Pós-teste"""
    # Selecionar top 20 palavras com maior melhora geral
    todas_palavras = pd.concat([palavras_df_grupo1, palavras_df_grupo2])
    palavras_geral = todas_palavras.groupby('Questao').agg({
        'Melhora': 'mean',
        'Palavra': 'first'
    }).reset_index()
    
    top_20_questoes = palavras_geral.nlargest(20, 'Melhora')['Questao']
    
    # Preparar dados para heatmap
    heatmap_data = []
    palavras_labels = []
    
    for questao in top_20_questoes:
        palavra = palavras_geral[palavras_geral['Questao'] == questao]['Palavra'].iloc[0]
        palavras_labels.append(palavra[:12] + '...' if len(palavra) > 12 else palavra)
        
        # Erros no pós-teste para cada grupo
        erro_g1 = palavras_df_grupo1[palavras_df_grupo1['Questao'] == questao]['Perc_Erro_Pos']
        erro_g2 = palavras_df_grupo2[palavras_df_grupo2['Questao'] == questao]['Perc_Erro_Pos']
        
        erro_g1_val = erro_g1.iloc[0] if len(erro_g1) > 0 else 0
        erro_g2_val = erro_g2.iloc[0] if len(erro_g2) > 0 else 0
        
        heatmap_data.append([erro_g1_val, erro_g2_val])
    
    heatmap_array = np.array(heatmap_data)
    
    fig, ax = plt.subplots(figsize=(8, 12))
    
    im = ax.imshow(heatmap_array, cmap='Reds', aspect='auto')
    
    # Configurar eixos
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['6º/7º anos', '8º/9º anos'])
    ax.set_yticks(range(len(palavras_labels)))
    ax.set_yticklabels(palavras_labels)
    ax.set_title('Percentual de Erros por Palavra e Grupo\n(Pós-teste - Top 20 palavras)', fontweight='bold')
    
    # Adicionar valores
    for i in range(len(palavras_labels)):
        for j in range(2):
            text = ax.text(j, i, f'{heatmap_array[i, j]:.2f}',
                         ha="center", va="center", 
                         color="white" if heatmap_array[i, j] > 0.5 else "black",
                         fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Percentual de Erros')
    plt.tight_layout()
    return fig

def plot_heatmap_erros_pre(palavras_df_grupo1, palavras_df_grupo2):
    """Heatmap de erros por palavra e grupo - Pré-teste"""
    # Selecionar top 20 palavras com maior melhora geral (mesma lista do pós-teste para comparação)
    todas_palavras = pd.concat([palavras_df_grupo1, palavras_df_grupo2])
    palavras_geral = todas_palavras.groupby('Questao').agg({
        'Melhora': 'mean',
        'Palavra': 'first'
    }).reset_index()
    
    top_20_questoes = palavras_geral.nlargest(20, 'Melhora')['Questao']
    
    # Preparar dados para heatmap
    heatmap_data = []
    palavras_labels = []
    
    for questao in top_20_questoes:
        palavra = palavras_geral[palavras_geral['Questao'] == questao]['Palavra'].iloc[0]
        palavras_labels.append(palavra[:12] + '...' if len(palavra) > 12 else palavra)
        
        # Erros no pré-teste para cada grupo
        erro_g1 = palavras_df_grupo1[palavras_df_grupo1['Questao'] == questao]['Perc_Erro_Pre']
        erro_g2 = palavras_df_grupo2[palavras_df_grupo2['Questao'] == questao]['Perc_Erro_Pre']
        
        erro_g1_val = erro_g1.iloc[0] if len(erro_g1) > 0 else 0
        erro_g2_val = erro_g2.iloc[0] if len(erro_g2) > 0 else 0
        
        heatmap_data.append([erro_g1_val, erro_g2_val])
    
    heatmap_array = np.array(heatmap_data)
    
    fig, ax = plt.subplots(figsize=(8, 12))
    
    im = ax.imshow(heatmap_array, cmap='Reds', aspect='auto')
    
    # Configurar eixos
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['6º/7º anos', '8º/9º anos'])
    ax.set_yticks(range(len(palavras_labels)))
    ax.set_yticklabels(palavras_labels)
    ax.set_title('Percentual de Erros por Palavra e Grupo\n(Pré-teste - Top 20 palavras)', fontweight='bold')
    
    # Adicionar valores
    for i in range(len(palavras_labels)):
        for j in range(2):
            text = ax.text(j, i, f'{heatmap_array[i, j]:.2f}',
                         ha="center", va="center", 
                         color="white" if heatmap_array[i, j] > 0.5 else "black",
                         fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Percentual de Erros')
    plt.tight_layout()
    return fig

# ======================
# Função de formatação de cards
# ======================

def format_card(label: str, value: str, extra: str = "", theme: str = "default") -> str:
    """Formata um card seguindo o padrão da Fase 3"""
    classes = {
        "default": "card",
        "green": "card green",
        "red": "card red",
        "yellow": "card yellow",
    }.get(theme, "card")
    
    return f"""
        <div class="{classes}">
            <div class="card-label">{label}</div>
            <div class="valor">{value}</div>
            <div class="desc">{extra}</div>
        </div>
    """

# ======================
# Geração do HTML
# ======================

def gerar_html_relatorio(indicadores_geral, indicadores_grupo1, indicadores_grupo2, 
                        palavras_df_todos, figuras_b64):
    """Gera o relatório HTML completo seguindo padrão da Fase 3"""
    
    # Cards seguindo o padrão da Fase 3
    cards_html = "".join([
        format_card("Registros", f"{indicadores_geral.get('n', 0)}", "alunos após limpeza"),
        format_card("Média Pré", f"{indicadores_geral.get('mean_pre', 0):.2f}"),
        format_card("Média Pós", f"{indicadores_geral.get('mean_pos', 0):.2f}"),
        format_card("Delta médio", f"{indicadores_geral.get('mean_delta', 0):+.2f}", "pontos"),
        format_card("% Melhoraram", f"{indicadores_geral.get('perc_improved', 0):.1f}%", theme="green"),
        format_card("% Pioraram", f"{indicadores_geral.get('perc_worsened', 0):.1f}%", theme="red"),
        format_card("% Mantiveram", f"{indicadores_geral.get('perc_unchanged', 0):.1f}%", theme="yellow"),
        format_card("Effect Size", f"{indicadores_geral.get('cohen_d', 0):.3f}"),
    ])
    
    # Interpretação dos grupos com análise completa
    def get_interpretacao_grupo(indicadores, nome_grupo):
        d = indicadores.get('cohen_d', 0)
        interpretacao = interpretar_cohen_d(d)
        
        return f"""
        <div class="grupo-item">
            <div class="grupo-titulo">{nome_grupo} (N={indicadores.get('n', 0)})</div>
            <div class="grupo-detalhes">
                <span>Média Pré: {indicadores.get('mean_pre', 0):.2f}</span>
                <span>Média Pós: {indicadores.get('mean_pos', 0):.2f}</span>
                <span>Delta: {indicadores.get('mean_delta', 0):+.2f}</span>
                <span>Cohen's d: {d:.3f}</span>
                <span>% Melhoraram: {indicadores.get('perc_improved', 0):.1f}%</span>
            </div>
            <div class="interpretacao-grupo">
                <p><strong>Magnitude:</strong> {interpretacao['magnitude']} (Cohen, 1988)</p>
                <p><strong>Benchmark Educacional:</strong> {interpretacao['hattie_status']} (Hattie, 2009)</p>
                <p><strong>Vocabulário:</strong> {interpretacao['vocab_status']} (Marulis & Neuman, 2010)</p>
            </div>
        </div>
        """
    
    interp_html = get_interpretacao_grupo(indicadores_grupo1, "6º/7º anos") + get_interpretacao_grupo(indicadores_grupo2, "8º/9º anos")

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Relatório Visual - WordGen Fase 2 - Vocabulário</title>
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
    .interpretacao-grupo {{ margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid var(--purple1); }}
    .interpretacao-grupo p {{ margin: 3px 0; font-size: 12px; }}
    .interpretacao-grupo strong {{ color: var(--purple1); }}

    .figs-heatmap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 10px; }}
    @media (max-width: 768px) {{ .figs-heatmap {{ grid-template-columns: 1fr; }} }}

    .foot-note {{ font-size: 12px; color: var(--muted); text-align: center; margin-top: 16px; }}

    .badge {{ display:inline-block; padding:2px 6px; border-radius:999px; font-size:11px; line-height:1.4; }}
    .badge.warn {{ background:#fff3cd; color:#7a6200; border:1px solid #ffe69c; }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Relatório Visual WordGen</div>
        <div class="subtitle">Vocabulário – Fase 2 (Grupos Etários: 6º/7º vs 8º/9º anos). Análise pareada por estudante.</div>
        <div class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</div>
    </div>

    <div class="container">
        <h2 class="section">Indicadores</h2>
        <div class="cards">
            {cards_html}
        </div>

        <h2 class="section">Gráficos</h2>
        <div class="figs">
            <div class="fig">
                <img src="{figuras_b64.get('grupos_barras', '')}" alt="Comparação de Grupos" />
                <div class="caption">Comparação de scores e distribuição de mudanças por grupo etário.</div>
            </div>
            <div class="fig">
                <img src="{figuras_b64.get('cohen_benchmark', '')}" alt="Cohen's d com Benchmarks" />
                <div class="caption">Effect sizes (Cohen's d) com referências de benchmarks educacionais.</div>
            </div>
            <div class="fig">
                <img src="{figuras_b64.get('palavras_top', '')}" alt="Top Palavras" />
                <div class="caption">Palavras com maior melhora na taxa de acerto.</div>
            </div>
            <div class="fig">
                <img src="{figuras_b64.get('comparacao_intergrupos', '')}" alt="Comparação Intergrupos" />
                <div class="caption">Comparação detalhada entre grupos etários.</div>
            </div>
        </div>

        <h2 class="section">Percentual de Erros por Palavra e Grupo</h2>
        <div class="figs-heatmap">
            <div class="fig">
                <img src="{figuras_b64.get('heatmap_erros_pre', '')}" alt="Heatmap de Erros Pré-teste" />
                <div class="caption">Percentual de erros no pré-teste (Top 20 palavras).</div>
            </div>
            <div class="fig">
                <img src="{figuras_b64.get('heatmap_erros_pos', '')}" alt="Heatmap de Erros Pós-teste" />
                <div class="caption">Percentual de erros no pós-teste (Top 20 palavras).</div>
            </div>
        </div>

        <h2 class="section">Interpretação contextualizada por grupo etário</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">Referências: Cohen (1988) – 0.2/0.5/0.8; Hattie (2009) – d≥0.4 como "bom resultado"; Vocabulário (Marulis & Neuman, 2010) – d≥0.35 significativo.</p>
            {interp_html}
        </div>

        <div class="foot-note">
            <p>Notas: ES = Effect Size (Cohen's d) = Δ/SD(Pré). Análise por grupos etários baseada na classificação de turmas. Dados filtrados para estudantes com participação completa (pré e pós-teste).</p>
        </div>
    </div>
</body>
</html>
"""
    return html

# ======================
# Função Principal
# ======================

def gerar_relatorio_completo():
    """Função principal que gera o relatório completo"""
    print("="*60)
    print("RELATÓRIO VISUAL WORDGEN - FASE 2 - Vocabulário")
    print("="*60)
    
    # Criar diretório de figuras
    os.makedirs(FIG_DIR, exist_ok=True)
    
    # 1. Carregar e preparar dados
    df_pre_final, df_pos_final, colunas_q, mapeamento_palavras = carregar_e_preparar_dados()
    
    # 2. Calcular scores
    scores_df = calcular_scores(df_pre_final, df_pos_final, colunas_q)
    
    # 3. Calcular indicadores
    print("4. Calculando indicadores...")
    indicadores_geral = calcular_indicadores(scores_df)
    indicadores_grupo1 = calcular_indicadores(scores_df, "6º/7º anos")
    indicadores_grupo2 = calcular_indicadores(scores_df, "8º/9º anos")
    
    # 4. Analisar palavras
    print("5. Analisando palavras...")
    palavras_df_todos = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras)
    palavras_df_grupo1 = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "6º/7º anos")
    palavras_df_grupo2 = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "8º/9º anos")
    
    # 5. Gerar figuras
    print("6. Gerando figuras...")
    
    # Figura 1: Comparação de grupos
    fig1 = plot_grupos_barras(scores_df)
    fig1.savefig(FIG_GRUPOS_BARRAS, dpi=150, bbox_inches='tight')
    plt.close(fig1)
    
    # Figura 2: Top palavras
    fig2 = plot_palavras_top(palavras_df_todos, palavras_df_grupo1, palavras_df_grupo2)
    fig2.savefig(FIG_PALAVRAS_TOP, dpi=150, bbox_inches='tight')
    plt.close(fig2)
    
    # Figura 3: Cohen's d com benchmarks
    fig3 = plot_cohen_benchmark(indicadores_geral, indicadores_grupo1, indicadores_grupo2)
    fig3.savefig(FIG_COHEN_BENCHMARK, dpi=150, bbox_inches='tight')
    plt.close(fig3)
    
    # Figura 4: Comparação intergrupos
    fig4 = plot_comparacao_intergrupos(scores_df)
    fig4.savefig(FIG_INTERGRUPOS, dpi=150, bbox_inches='tight')
    plt.close(fig4)
    
    # Figura 5: Heatmap de erros pós-teste
    fig5 = plot_heatmap_erros_pos(palavras_df_grupo1, palavras_df_grupo2)
    fig5.savefig(FIG_HEATMAP_ERROS_POS, dpi=150, bbox_inches='tight')
    plt.close(fig5)
    
    # Figura 6: Heatmap de erros pré-teste
    fig6 = plot_heatmap_erros_pre(palavras_df_grupo1, palavras_df_grupo2)
    fig6.savefig(FIG_HEATMAP_ERROS_PRE, dpi=150, bbox_inches='tight')
    plt.close(fig6)
    
    # 6. Converter figuras para Base64
    print("7. Convertendo figuras para Base64...")
    figuras_b64 = {}
    
    for nome, caminho in [
        ('grupos_barras', FIG_GRUPOS_BARRAS),
        ('palavras_top', FIG_PALAVRAS_TOP),
        ('cohen_benchmark', FIG_COHEN_BENCHMARK),
        ('comparacao_intergrupos', FIG_INTERGRUPOS),
        ('heatmap_erros_pos', FIG_HEATMAP_ERROS_POS),
        ('heatmap_erros_pre', FIG_HEATMAP_ERROS_PRE)
    ]:
        if caminho.exists():
            with open(caminho, 'rb') as f:
                img_data = f.read()
                img_b64 = base64.b64encode(img_data).decode('utf-8')
                figuras_b64[nome] = f"data:image/png;base64,{img_b64}"
    
    # 7. Gerar relatório HTML
    print("8. Gerando relatório HTML...")
    html_content = gerar_html_relatorio(
        indicadores_geral, indicadores_grupo1, indicadores_grupo2,
        palavras_df_todos, figuras_b64
    )
    
    # 8. Salvar HTML
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("="*60)
    print("✅ RELATÓRIO GERADO COM SUCESSO!")
    print(f"📁 Arquivo HTML: {OUTPUT_HTML}")
    print(f"📊 Figuras salvas em: {FIG_DIR}")
    print(f"👥 {indicadores_geral['n']} estudantes analisados")
    print(f"📈 Effect Size Geral: {indicadores_geral['cohen_d']:.4f}")
    print("="*60)
    
    return str(OUTPUT_HTML)

if __name__ == "__main__":
    gerar_relatorio_completo()
