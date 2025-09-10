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
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
FIG_DIR = DATA_DIR / "figures"

# Dados da Fase 2 - Usando CSV
ARQUIVO_PRE = DATA_DIR / "Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.csv"
ARQUIVO_POS = DATA_DIR / "Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).csv"
ARQUIVO_RESPOSTAS = DATA_DIR / "RespostaVocabulario.json"
OUTPUT_HTML = DATA_DIR / "relatorio_visual_wordgen_fase2.html"
ARQUIVO_PALAVRAS_ENSINADAS = DATA_DIR / "Fase2/PalavrasEnsinadasVocabulario.json"

# Figuras
FIG_GRUPOS_BARRAS = FIG_DIR / "fase2_grupos_barras.png"
FIG_PALAVRAS_TOP = FIG_DIR / "fase2_palavras_top.png"
FIG_INTERGRUPOS = FIG_DIR / "fase2_comparacao_intergrupos.png"
FIG_HEATMAP_ERROS_POS = FIG_DIR / "fase2_heatmap_erros_pos.png"
FIG_HEATMAP_ERROS_PRE = FIG_DIR / "fase2_heatmap_erros_pre.png"
FIG_ENSINADAS_VS_NAO = FIG_DIR / "fase2_ensinadas_vs_nao.png"

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

def obter_escolas_disponiveis():
    """Obtém a lista de escolas disponíveis nos dados"""
    try:
        df_pre = pd.read_csv(ARQUIVO_PRE)
        escolas = sorted(df_pre['Escola'].dropna().unique().tolist())
        return ["Todas"] + escolas
    except Exception as e:
        print(f"Erro ao carregar escolas: {e}")
        return ["Todas"]

def interpretar_cohen_d(d):
    """Interpreta o Cohen's d conforme benchmarks educacionais com direção do efeito"""
    abs_d = abs(d)
    is_positive = d >= 0
    
    # Magnitude (Cohen, 1988)
    if abs_d >= 0.8:
        magnitude = "Grande"
    elif abs_d >= 0.5:
        magnitude = "Médio"
    elif abs_d >= 0.2:
        magnitude = "Pequeno"
    else:
        magnitude = "Negligível"
    
    # Benchmark educacional (Hattie, 2009) - considerando direção
    if abs_d >= 0.4:
        if is_positive:
            hattie_status = "✅ Acima do benchmark (d≥0.4) - Melhoria significativa"
        else:
            hattie_status = "🚨 Acima do benchmark (|d|≥0.4) - ALERTA: Deterioração significativa"
    else:
        if is_positive:
            hattie_status = "⚠️ Abaixo do benchmark (d<0.4) - Melhoria limitada"
        else:
            hattie_status = "ℹ️ Abaixo do benchmark (|d|<0.4) - Deterioração limitada"
    
    # Significativo para vocabulário (Marulis & Neuman, 2010) - considerando direção
    if abs_d >= 0.35:
        if is_positive:
            vocab_status = "✅ Significativo para vocabulário (d≥0.35) - Ganho relevante"
        else:
            vocab_status = "🚨 Significativo para vocabulário (|d|≥0.35) - ALERTA: Perda relevante"
    else:
        if is_positive:
            vocab_status = "⚠️ Abaixo do threshold (d<0.35) - Ganho limitado"
        else:
            vocab_status = "ℹ️ Abaixo do threshold (|d|<0.35) - Perda limitada"
    
    return {
        'magnitude': magnitude,
        'hattie_status': hattie_status,
        'vocab_status': vocab_status,
        'is_positive': is_positive,
        'interpretation_alert': "CRÍTICO" if (abs_d >= 0.5 and not is_positive) else "NORMAL"
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
    """Classifica estudantes em grupos etários individuais por ano"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str:
        return "6º ano"
    elif '7º' in turma_str or '7°' in turma_str:
        return "7º ano"
    elif '8º' in turma_str or '8°' in turma_str:
        return "8º ano"
    elif '9º' in turma_str or '9°' in turma_str:
        return "9º ano"
    else:
        return "Indefinido"

def carregar_mapeamento_palavras():
    """Carrega o mapeamento de questões para palavras e classifica se foram ensinadas"""
    try:
        # Carregar respostas das questões
        with open(ARQUIVO_RESPOSTAS, 'r', encoding='utf-8') as f:
            dados_respostas = json.load(f)
        
        # Carregar palavras ensinadas
        with open(ARQUIVO_PALAVRAS_ENSINADAS, 'r', encoding='utf-8') as f:
            dados_ensinadas = json.load(f)
        
        palavras_ensinadas = set(dados_ensinadas.get("Palavras Ensinadas", []))
        
        mapeamento = {}
        for item in dados_respostas:
            for questao, info in item.items():
                palavra = info['Palavra Trabalhada']
                foi_ensinada = palavra in palavras_ensinadas
                mapeamento[questao] = {
                    'palavra': palavra,
                    'ensinada': foi_ensinada
                }
        
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

def carregar_e_preparar_dados(escola_filtro=None):
    """Carrega e prepara os dados da Fase 2"""
    print("1. Carregando dados...")
    
    # Carregar dados
    df_pre = pd.read_csv(ARQUIVO_PRE)
    df_pos = pd.read_csv(ARQUIVO_POS)
    
    # Filtrar por escola se especificado
    if escola_filtro and escola_filtro != "Todas":
        print(f"   Filtrando por escola: {escola_filtro}")
        df_pre = df_pre[df_pre['Escola'] == escola_filtro].copy()
        df_pos = df_pos[df_pos['Escola'] == escola_filtro].copy()
    
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
        return valores_validos >= 25  # Pelo menos 25% das questões
    
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
        return {
            'n': 0,
            'mean_pre': 0,
            'std_pre': 0,
            'mean_pos': 0,
            'std_pos': 0,
            'mean_delta': 0,
            'std_delta': 0,
            'cohen_d': 0,
            'p_value': 1.0,
            'perc_improved': 0,
            'perc_worsened': 0,
            'perc_unchanged': 0
        }
    
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
            info_palavra = mapeamento_palavras.get(col, {'palavra': f"Palavra_{col}", 'ensinada': False})
            palavra = info_palavra['palavra']
            foi_ensinada = info_palavra['ensinada']
            
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
                    'Ensinada': foi_ensinada,
                    'Taxa_Pre': taxa_pre,
                    'Taxa_Pos': taxa_pos,
                    'Melhora': melhora,
                    'Perc_Erro_Pre': perc_erro_pre,
                    'Perc_Erro_Pos': perc_erro_pos
                })
    
    return pd.DataFrame(palavras_data)

def analisar_palavras_por_categoria(palavras_df):
    """Analisa performance separando palavras ensinadas das não ensinadas"""
    
    # Separar por categoria
    ensinadas = palavras_df[palavras_df['Ensinada'] == True]
    nao_ensinadas = palavras_df[palavras_df['Ensinada'] == False]
    
    resultados = {}
    
    for categoria, df_categoria in [('Ensinadas', ensinadas), ('Não Ensinadas', nao_ensinadas)]:
        if len(df_categoria) > 0:
            resultados[categoria] = {
                'n_palavras': len(df_categoria),
                'media_melhora': df_categoria['Melhora'].mean(),
                'media_taxa_pre': df_categoria['Taxa_Pre'].mean(),
                'media_taxa_pos': df_categoria['Taxa_Pos'].mean(),
                'media_erro_pre': df_categoria['Perc_Erro_Pre'].mean(),
                'media_erro_pos': df_categoria['Perc_Erro_Pos'].mean(),
                'top_melhoras': df_categoria.nlargest(10, 'Melhora')[['Palavra', 'Melhora', 'Taxa_Pre', 'Taxa_Pos']].to_dict('records')
            }
        else:
            resultados[categoria] = {
                'n_palavras': 0,
                'media_melhora': 0,
                'media_taxa_pre': 0,
                'media_taxa_pos': 0,
                'media_erro_pre': 0,
                'media_erro_pos': 0,
                'top_melhoras': []
            }
    
    return resultados
# ======================
# Funções de visualização
# ======================

def plot_grupos_barras(scores_df):
    """Gráfico de barras comparando grupos por anos individuais"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    grupos = ['6º ano', '7º ano', '8º ano', '9º ano']
    cores = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    
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
    
    ax.bar(x - width/2, means_pre, width, yerr=stds_pre, label='Pré-teste', alpha=0.8, color='#3498db')
    ax.bar(x + width/2, means_pos, width, yerr=stds_pos, label='Pós-teste', alpha=0.8, color='#e74c3c')
    
    ax.set_xlabel('Anos')
    ax.set_ylabel('Score Médio')
    ax.set_title('Comparação de Médias por Ano')
    ax.set_xticks(x)
    ax.set_xticklabels(grupos)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Boxplot de deltas
    ax = axes[0, 1]
    deltas_data = [scores_df[scores_df['GrupoEtario'] == grupo]['Delta'] for grupo in grupos]
    bp = ax.boxplot(deltas_data, tick_labels=grupos, patch_artist=True)
    
    for patch, cor in zip(bp['boxes'], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Mudança (Delta)')
    ax.set_title('Distribuição de Mudanças por Ano')
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

def plot_palavras_top(palavras_df_todos, palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano):
    """Top palavras com maior melhora - Comparação entre os 4 anos"""
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
    
    # 2. Comparação entre anos - Top 15
    ax = axes[1]
    top_15_questoes = palavras_df_todos.nlargest(15, 'Melhora')['Questao']
    
    melhoras_6ano = []
    melhoras_7ano = []
    melhoras_8ano = []
    melhoras_9ano = []
    palavras_nomes = []
    
    for questao in top_15_questoes:
        palavra = palavras_df_todos[palavras_df_todos['Questao'] == questao]['Palavra'].iloc[0]
        palavras_nomes.append(palavra[:10] + '...' if len(palavra) > 10 else palavra)
        
        # Buscar melhora para cada ano
        melhora_6 = palavras_df_6ano[palavras_df_6ano['Questao'] == questao]['Melhora']
        melhora_7 = palavras_df_7ano[palavras_df_7ano['Questao'] == questao]['Melhora']
        melhora_8 = palavras_df_8ano[palavras_df_8ano['Questao'] == questao]['Melhora']
        melhora_9 = palavras_df_9ano[palavras_df_9ano['Questao'] == questao]['Melhora']
        
        melhoras_6ano.append(melhora_6.iloc[0] if len(melhora_6) > 0 else 0)
        melhoras_7ano.append(melhora_7.iloc[0] if len(melhora_7) > 0 else 0)
        melhoras_8ano.append(melhora_8.iloc[0] if len(melhora_8) > 0 else 0)
        melhoras_9ano.append(melhora_9.iloc[0] if len(melhora_9) > 0 else 0)
    
    x = np.arange(len(palavras_nomes))
    width = 0.2
    
    ax.bar(x - 1.5*width, melhoras_6ano, width, label='6º ano', color='#3498db', alpha=0.7)
    ax.bar(x - 0.5*width, melhoras_7ano, width, label='7º ano', color='#2ecc71', alpha=0.7)
    ax.bar(x + 0.5*width, melhoras_8ano, width, label='8º ano', color='#e74c3c', alpha=0.7)
    ax.bar(x + 1.5*width, melhoras_9ano, width, label='9º ano', color='#f39c12', alpha=0.7)
    
    ax.set_xlabel('Palavras')
    ax.set_ylabel('Melhora')
    ax.set_title('Comparação de Melhora por Ano - Top 15')
    ax.set_xticks(x)
    ax.set_xticklabels(palavras_nomes, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_comparacao_intergrupos(scores_df):
    """Comparação detalhada entre anos - Layout 2x2 com densidades por ano"""
    fig = plt.figure(figsize=(15, 10))
    
    grupos = ['6º ano', '7º ano', '8º ano', '9º ano']
    cores = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    
    # 1. Distribuição de densidade - 6º ANO (superior esquerdo)
    ax1 = plt.subplot(2, 2, 1)
    
    # Dados do 6º ano
    data_pre_6 = scores_df[scores_df['GrupoEtario'] == grupos[0]]['Score_Pre']
    data_pos_6 = scores_df[scores_df['GrupoEtario'] == grupos[0]]['Score_Pos']
    
    if len(data_pre_6) > 0:
        ax1.hist(data_pre_6, alpha=0.5, label='Pré-teste', color=cores[0], bins=12, density=True)
        ax1.hist(data_pos_6, alpha=0.7, label='Pós-teste', color=cores[0], bins=12, density=True, hatch='//')
    
    ax1.set_xlabel('Scores', fontsize=11)
    ax1.set_ylabel('Densidade', fontsize=11)
    ax1.set_title('6º ano\nDistribuição de Densidade', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribuição de densidade - 7º ANO (superior direito)
    ax2 = plt.subplot(2, 2, 2)
    
    # Dados do 7º ano
    data_pre_7 = scores_df[scores_df['GrupoEtario'] == grupos[1]]['Score_Pre']
    data_pos_7 = scores_df[scores_df['GrupoEtario'] == grupos[1]]['Score_Pos']
    
    if len(data_pre_7) > 0:
        ax2.hist(data_pre_7, alpha=0.5, label='Pré-teste', color=cores[1], bins=12, density=True)
        ax2.hist(data_pos_7, alpha=0.7, label='Pós-teste', color=cores[1], bins=12, density=True, hatch='//')
    
    ax2.set_xlabel('Scores', fontsize=11)
    ax2.set_ylabel('Densidade', fontsize=11)
    ax2.set_title('7º ano\nDistribuição de Densidade', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribuição de densidade - 8º ANO (inferior esquerdo)
    ax3 = plt.subplot(2, 2, 3)
    
    # Dados do 8º ano
    data_pre_8 = scores_df[scores_df['GrupoEtario'] == grupos[2]]['Score_Pre']
    data_pos_8 = scores_df[scores_df['GrupoEtario'] == grupos[2]]['Score_Pos']
    
    if len(data_pre_8) > 0:
        ax3.hist(data_pre_8, alpha=0.5, label='Pré-teste', color=cores[2], bins=12, density=True)
        ax3.hist(data_pos_8, alpha=0.7, label='Pós-teste', color=cores[2], bins=12, density=True, hatch='//')
    
    ax3.set_xlabel('Scores', fontsize=11)
    ax3.set_ylabel('Densidade', fontsize=11)
    ax3.set_title('8º ano\nDistribuição de Densidade', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Distribuição de densidade - 9º ANO (inferior direito)
    ax4 = plt.subplot(2, 2, 4)
    
    # Dados do 9º ano
    data_pre_9 = scores_df[scores_df['GrupoEtario'] == grupos[3]]['Score_Pre']
    data_pos_9 = scores_df[scores_df['GrupoEtario'] == grupos[3]]['Score_Pos']
    
    if len(data_pre_9) > 0:
        ax4.hist(data_pre_9, alpha=0.5, label='Pré-teste', color=cores[3], bins=12, density=True)
        ax4.hist(data_pos_9, alpha=0.7, label='Pós-teste', color=cores[3], bins=12, density=True, hatch='//')
    
    ax4.set_xlabel('Scores', fontsize=11)
    ax4.set_ylabel('Densidade', fontsize=11)
    ax4.set_title('9º ano\nDistribuição de Densidade', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_heatmap_erros_pos(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano):
    """Heatmap de erros por palavra e ano - Pós-teste"""
    # Selecionar top 20 palavras com maior melhora geral
    todas_palavras = pd.concat([palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano])
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
        
        # Erros no pós-teste para cada ano
        erro_6 = palavras_df_6ano[palavras_df_6ano['Questao'] == questao]['Perc_Erro_Pos']
        erro_7 = palavras_df_7ano[palavras_df_7ano['Questao'] == questao]['Perc_Erro_Pos']
        erro_8 = palavras_df_8ano[palavras_df_8ano['Questao'] == questao]['Perc_Erro_Pos']
        erro_9 = palavras_df_9ano[palavras_df_9ano['Questao'] == questao]['Perc_Erro_Pos']
        
        erro_6_val = erro_6.iloc[0] if len(erro_6) > 0 else 0
        erro_7_val = erro_7.iloc[0] if len(erro_7) > 0 else 0
        erro_8_val = erro_8.iloc[0] if len(erro_8) > 0 else 0
        erro_9_val = erro_9.iloc[0] if len(erro_9) > 0 else 0
        
        heatmap_data.append([erro_6_val, erro_7_val, erro_8_val, erro_9_val])
    
    heatmap_array = np.array(heatmap_data)
    
    fig, ax = plt.subplots(figsize=(8, 12))
    
    im = ax.imshow(heatmap_array, cmap='Reds', aspect='auto')
    
    # Configurar eixos
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['6º ano', '7º ano', '8º ano', '9º ano'])
    ax.set_yticks(range(len(palavras_labels)))
    ax.set_yticklabels(palavras_labels)
    ax.set_title('Percentual de Erros por Palavra e Ano\n(Pós-teste - Top 20 palavras)', fontweight='bold')
    
    # Adicionar valores
    for i in range(len(palavras_labels)):
        for j in range(4):
            text = ax.text(j, i, f'{heatmap_array[i, j]:.2f}',
                         ha="center", va="center", 
                         color="white" if heatmap_array[i, j] > 0.5 else "black",
                         fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Percentual de Erros')
    plt.tight_layout()
    return fig

def plot_heatmap_erros_pre(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano):
    """Heatmap de erros por palavra e ano - Pré-teste"""
    # Selecionar top 20 palavras com maior melhora geral (mesma lista do pós-teste para comparação)
    todas_palavras = pd.concat([palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano])
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
        
        # Erros no pré-teste para cada ano
        erro_6 = palavras_df_6ano[palavras_df_6ano['Questao'] == questao]['Perc_Erro_Pre']
        erro_7 = palavras_df_7ano[palavras_df_7ano['Questao'] == questao]['Perc_Erro_Pre']
        erro_8 = palavras_df_8ano[palavras_df_8ano['Questao'] == questao]['Perc_Erro_Pre']
        erro_9 = palavras_df_9ano[palavras_df_9ano['Questao'] == questao]['Perc_Erro_Pre']
        
        erro_6_val = erro_6.iloc[0] if len(erro_6) > 0 else 0
        erro_7_val = erro_7.iloc[0] if len(erro_7) > 0 else 0
        erro_8_val = erro_8.iloc[0] if len(erro_8) > 0 else 0
        erro_9_val = erro_9.iloc[0] if len(erro_9) > 0 else 0
        
        heatmap_data.append([erro_6_val, erro_7_val, erro_8_val, erro_9_val])
    
    heatmap_array = np.array(heatmap_data)
    
    fig, ax = plt.subplots(figsize=(8, 12))
    
    im = ax.imshow(heatmap_array, cmap='Reds', aspect='auto')
    
    # Configurar eixos
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['6º ano', '7º ano', '8º ano', '9º ano'])
    ax.set_yticks(range(len(palavras_labels)))
    ax.set_yticklabels(palavras_labels)
    ax.set_title('Percentual de Erros por Palavra e Ano\n(Pré-teste - Top 20 palavras)', fontweight='bold')
    
    # Adicionar valores
    for i in range(len(palavras_labels)):
        for j in range(4):
            text = ax.text(j, i, f'{heatmap_array[i, j]:.2f}',
                         ha="center", va="center", 
                         color="white" if heatmap_array[i, j] > 0.5 else "black",
                         fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Percentual de Erros')
    plt.tight_layout()
    return fig

def plot_comparacao_ensinadas_vs_nao(palavras_df):
    """Compara performance de palavras ensinadas vs não ensinadas"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Separar dados
    ensinadas = palavras_df[palavras_df['Ensinada'] == True]
    nao_ensinadas = palavras_df[palavras_df['Ensinada'] == False]
    
    # 1. Comparação de médias de melhora
    ax = axes[0, 0]
    categorias = ['Ensinadas', 'Não Ensinadas']
    medias_melhora = [
        ensinadas['Melhora'].mean() if len(ensinadas) > 0 else 0,
        nao_ensinadas['Melhora'].mean() if len(nao_ensinadas) > 0 else 0
    ]
    
    bars = ax.bar(categorias, medias_melhora, color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax.set_ylabel('Melhora Média na Taxa de Acerto')
    ax.set_title('Comparação de Melhora\n(Palavras Ensinadas vs Não Ensinadas)')
    ax.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, medias_melhora):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{valor:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Comparação de taxas de erro (pré-teste)
    ax = axes[0, 1]
    erros_pre = [
        ensinadas['Perc_Erro_Pre'].mean() if len(ensinadas) > 0 else 0,
        nao_ensinadas['Perc_Erro_Pre'].mean() if len(nao_ensinadas) > 0 else 0
    ]
    
    bars = ax.bar(categorias, erros_pre, color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax.set_ylabel('Taxa de Erro Média (Pré-teste)')
    ax.set_title('Comparação de Erros no Pré-teste')
    ax.grid(True, alpha=0.3)
    
    for bar, valor in zip(bars, erros_pre):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{valor:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Comparação de taxas de erro (pós-teste)
    ax = axes[1, 0]
    erros_pos = [
        ensinadas['Perc_Erro_Pos'].mean() if len(ensinadas) > 0 else 0,
        nao_ensinadas['Perc_Erro_Pos'].mean() if len(nao_ensinadas) > 0 else 0
    ]
    
    bars = ax.bar(categorias, erros_pos, color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax.set_ylabel('Taxa de Erro Média (Pós-teste)')
    ax.set_title('Comparação de Erros no Pós-teste')
    ax.grid(True, alpha=0.3)
    
    for bar, valor in zip(bars, erros_pos):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{valor:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Top 10 palavras com maior melhora (ensinadas)
    ax = axes[1, 1]
    if len(ensinadas) > 0:
        top_ensinadas = ensinadas.nlargest(10, 'Melhora')
        y_pos = np.arange(len(top_ensinadas))
        
        bars = ax.barh(y_pos, top_ensinadas['Melhora'], color='#2ecc71', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([p[:12] + '...' if len(p) > 12 else p for p in top_ensinadas['Palavra']])
        ax.set_xlabel('Melhora na Taxa de Acerto')
        ax.set_title('Top 10 Palavras Ensinadas\ncom Maior Melhora')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Nenhuma palavra ensinada\nencontrada', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Top 10 Palavras Ensinadas')
    
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

def gerar_graficos_escola(escola_filtro=None):
    """Gera gráficos específicos para uma escola e retorna como base64"""
    
    # Carregar dados da escola
    df_pre_final, df_pos_final, colunas_q, mapeamento_palavras = carregar_e_preparar_dados(escola_filtro)
    scores_df = calcular_scores(df_pre_final, df_pos_final, colunas_q)
    
    if len(scores_df) == 0:
        return {}
    
    # Calcular indicadores
    indicadores_geral = calcular_indicadores(scores_df)
    indicadores_6ano = calcular_indicadores(scores_df, "6º ano")
    indicadores_7ano = calcular_indicadores(scores_df, "7º ano")
    indicadores_8ano = calcular_indicadores(scores_df, "8º ano")
    indicadores_9ano = calcular_indicadores(scores_df, "9º ano")
    
    # Analisar palavras
    palavras_df_todos = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras)
    palavras_df_6ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "6º ano")
    palavras_df_7ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "7º ano")
    palavras_df_8ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "8º ano")
    palavras_df_9ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "9º ano")
    
    # Gerar gráficos em memória
    graficos_b64 = {}
    
    # Gráfico 1: Comparação de grupos
    fig1 = plot_grupos_barras(scores_df)
    buffer1 = io.BytesIO()
    fig1.savefig(buffer1, format='png', dpi=150, bbox_inches='tight')
    buffer1.seek(0)
    img_b64 = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    graficos_b64['grupos_barras'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig1)
    buffer1.close()
    
    # Gráfico 2: Top palavras
    fig2 = plot_palavras_top(palavras_df_todos, palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    buffer2 = io.BytesIO()
    fig2.savefig(buffer2, format='png', dpi=150, bbox_inches='tight')
    buffer2.seek(0)
    img_b64 = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    graficos_b64['palavras_top'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig2)
    buffer2.close()
    
    # Gráfico 4: Comparação intergrupos
    fig4 = plot_comparacao_intergrupos(scores_df)
    buffer4 = io.BytesIO()
    fig4.savefig(buffer4, format='png', dpi=150, bbox_inches='tight')
    buffer4.seek(0)
    img_b64 = base64.b64encode(buffer4.getvalue()).decode('utf-8')
    graficos_b64['comparacao_intergrupos'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig4)
    buffer4.close()
    
    # Gráfico 5: Heatmap erros pós-teste
    fig5 = plot_heatmap_erros_pos(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    buffer5 = io.BytesIO()
    fig5.savefig(buffer5, format='png', dpi=150, bbox_inches='tight')
    buffer5.seek(0)
    img_b64 = base64.b64encode(buffer5.getvalue()).decode('utf-8')
    graficos_b64['heatmap_erros_pos'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig5)
    buffer5.close()
    
    # Gráfico 6: Heatmap erros pré-teste
    fig6 = plot_heatmap_erros_pre(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    buffer6 = io.BytesIO()
    fig6.savefig(buffer6, format='png', dpi=150, bbox_inches='tight')
    buffer6.seek(0)
    img_b64 = base64.b64encode(buffer6.getvalue()).decode('utf-8')
    graficos_b64['heatmap_erros_pre'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig6)
    buffer6.close()
    
    # Gráfico 7: Comparação de palavras ensinadas vs não ensinadas
    fig7 = plot_comparacao_ensinadas_vs_nao(palavras_df_todos)
    buffer7 = io.BytesIO()
    fig7.savefig(buffer7, format='png', dpi=150, bbox_inches='tight')
    buffer7.seek(0)
    img_b64 = base64.b64encode(buffer7.getvalue()).decode('utf-8')
    graficos_b64['comparacao_ensinadas_vs_nao'] = f"data:image/png;base64,{img_b64}"
    plt.close(fig7)
    buffer7.close()
    
    return graficos_b64

def gerar_dados_todas_escolas():
    """Gera dados para todas as escolas para o menu interativo"""
    escolas = obter_escolas_disponiveis()
    dados_escolas = {}
    
    print("📊 Calculando dados para todas as escolas...")
    
    for escola in escolas:
        try:
            print(f"   Processando: {escola}")
            
            # Carregar dados para esta escola
            escola_filtro = escola if escola != "Todas" else None
            df_pre_final, df_pos_final, colunas_q, mapeamento_palavras = carregar_e_preparar_dados(escola_filtro)
            
            if len(df_pre_final) == 0:
                continue
                
            # Calcular scores
            scores_df = calcular_scores(df_pre_final, df_pos_final, colunas_q)
            
            if len(scores_df) == 0:
                continue
            
            # Calcular indicadores
            indicadores_geral = calcular_indicadores(scores_df)
            indicadores_6ano = calcular_indicadores(scores_df, "6º ano")
            indicadores_7ano = calcular_indicadores(scores_df, "7º ano")
            indicadores_8ano = calcular_indicadores(scores_df, "8º ano")
            indicadores_9ano = calcular_indicadores(scores_df, "9º ano")
            
            # Gerar gráficos específicos para esta escola
            print(f"     Gerando gráficos para: {escola}")
            graficos = gerar_graficos_escola(escola_filtro)
            
            # Analisar palavras
            palavras_df_todos = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras)
            
            dados_escolas[escola] = {
                'indicadores_geral': indicadores_geral,
                'indicadores_6ano': indicadores_6ano,
                'indicadores_7ano': indicadores_7ano,
                'indicadores_8ano': indicadores_8ano,
                'indicadores_9ano': indicadores_9ano,
                'graficos': graficos,
                'top_palavras': palavras_df_todos.nlargest(10, 'Melhora')[['Palavra', 'Melhora']].to_dict('records') if len(palavras_df_todos) > 0 else []
            }
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {escola}: {e}")
            continue
    
    return dados_escolas

def gerar_html_relatorio_interativo():
    """Gera o relatório HTML interativo com menu de escolas"""
    
    # Gerar dados para todas as escolas (incluindo gráficos específicos)
    dados_escolas = gerar_dados_todas_escolas()
    
    # Usar os gráficos da escola "Todas" como padrão
    figuras_b64 = dados_escolas.get('Todas', {}).get('graficos', {})
    
    # Gerar HTML interativo
    return gerar_html_com_menu(dados_escolas, figuras_b64)

def gerar_html_com_menu(dados_escolas, figuras_b64):
    """Gera HTML com menu interativo para seleção de escolas"""
    
    # Converter dados para JSON
    import json
    dados_json = json.dumps(dados_escolas, ensure_ascii=False, indent=2)
    
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
    .menu-container {{
        background: #fff; margin: 18px auto; max-width: 1200px; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }}
    .menu-title {{
        font-size: 18px; font-weight: 600; margin-bottom: 12px; color: var(--purple1);
    }}
    .escola-select {{
        width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; background: #fff; cursor: pointer;
        transition: border-color 0.3s ease;
    }}
    .escola-select:focus {{
        outline: none; border-color: var(--purple1);
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
        <div class="title">Relatório Visual WordGen - Fase 2</div>
        <div class="subtitle">Vocabulário (Grupos Etários: 6º,7º, 8º, 9º anos). Análise pareada por estudante.</div>
        <div class="timestamp" id="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</div>
    </div>

    <div class="menu-container">
        <div class="menu-title">🏫 Selecionar Escola</div>
        <select class="escola-select" id="escolaSelect" onchange="atualizarDados()">
        </select>
    </div>

    <div class="container">
        <h2 class="section">📊 Indicadores Principais</h2>
        <div class="cards" id="cardsContainer">
        </div>

        <h2 class="section">📈 Análises Visuais</h2>
        <div class="figs">
            <div class="fig" id="grafico-grupos">
                <img src="{figuras_b64.get('grupos_barras', '')}" alt="Comparação de Grupos" />
                <div class="caption">Comparação de scores e distribuição de mudanças por grupo etário.</div>
            </div>
            <div class="fig" id="grafico-palavras">
                <img src="{figuras_b64.get('palavras_top', '')}" alt="Top Palavras" />
                <div class="caption">Palavras com maior melhora na taxa de acerto.</div>
            </div>
            <div class="fig" id="grafico-intergrupos">
                <img src="{figuras_b64.get('comparacao_intergrupos', '')}" alt="Comparação Intergrupos" />
                <div class="caption">Comparação detalhada entre grupos etários (Densidade separada por grupo + Distribuição de resultados embaixo).</div>
            </div>
        </div>

        <h2 class="section">Análise de Palavras Ensinadas vs. Não Ensinadas</h2>
        <div class="figs">
            <div class="fig" id="grafico-ensinadas-nao-ensinadas">
                <img src="{figuras_b64.get('comparacao_ensinadas_vs_nao', '')}" alt="Comparação Ensinadas vs Não Ensinadas" />
                <div class="caption">Comparativo de performance entre palavras que foram explicitamente ensinadas e as que não foram.</div>
            </div>
        </div>

        <h2 class="section">Percentual de Erros por Palavra e Grupo</h2>
        <div class="figs-heatmap">
            <div class="fig" id="grafico-heatmap-pre">
                <img src="{figuras_b64.get('heatmap_erros_pre', '')}" alt="Heatmap de Erros Pré-teste" />
                <div class="caption">Percentual de erros no pré-teste (Top 20 palavras).</div>
            </div>
            <div class="fig" id="grafico-heatmap-pos">
                <img src="{figuras_b64.get('heatmap_erros_pos', '')}" alt="Heatmap de Erros Pós-teste" />
                <div class="caption">Percentual de erros no pós-teste (Top 20 palavras).</div>
            </div>
        </div>

        <h2 class="section">Interpretação contextualizada por grupo etário</h2>
        <div class="interp">
            <p style="margin-top:0;color:#374151;">Referências: Cohen (1988) – 0.2/0.5/0.8; Hattie (2009) – d≥0.4 como "bom resultado"; Vocabulário (Marulis & Neuman, 2010) – d≥0.35 significativo.</p>
            <div id="interpretacaoContainer">
            </div>
        </div>

        <div class="foot-note">
            <p>Notas: ES = Effect Size (Cohen's d) = Δ/SD(Pré). Análise por grupos etários baseada na classificação de turmas. Dados filtrados para estudantes com participação completa (pré e pós-teste).</p>
        </div>
    </div>

<script>
const dadosEscolas = {dados_json};

function inicializar() {{
    const select = document.getElementById('escolaSelect');
    
    // Adicionar opções ao select
    Object.keys(dadosEscolas).forEach(escola => {{
        const option = document.createElement('option');
        option.value = escola;
        option.textContent = escola;
        select.appendChild(option);
    }});
    
    // Definir "Todas" como padrão
    select.value = 'Todas';
    atualizarDados();
}}

function atualizarDados() {{
    const escolaSelecionada = document.getElementById('escolaSelect').value;
    const dados = dadosEscolas[escolaSelecionada];
    
    if (!dados) return;
    
    atualizarCards(dados.indicadores_geral);
    atualizarInterpretacao(dados);
    atualizarGraficos(dados.graficos);
}}

function atualizarCards(indicadores) {{
    const container = document.getElementById('cardsContainer');
    const maxScore = 100;
    const meanPrePercent = (indicadores.mean_pre / maxScore * 100).toFixed(1);
    const meanPosPercent = (indicadores.mean_pos / maxScore * 100).toFixed(1);
    
    container.innerHTML = `
        <div class="card">
            <div class="card-label">Palavras Testadas</div>
            <div class="valor">50</div>
            <div class="desc">questões de vocabulário</div>
        </div>
        <div class="card">
            <div class="card-label">Pontuação Máxima</div>
            <div class="valor">100</div>
            <div class="desc">pontos (2 por questão)</div>
        </div>
        <div class="card">
            <div class="card-label">Registros</div>
            <div class="valor">${{indicadores.n}}</div>
            <div class="desc">alunos após limpeza</div>
        </div>
        <div class="card">
            <div class="card-label">Média Pré</div>
            <div class="valor">${{indicadores.mean_pre.toFixed(2)}}</div>
            <div class="desc">(${{meanPrePercent}}% da máxima)</div>
        </div>
        <div class="card">
            <div class="card-label">Média Pós</div>
            <div class="valor">${{indicadores.mean_pos.toFixed(2)}}</div>
            <div class="desc">(${{meanPosPercent}}% da máxima)</div>
        </div>
        <div class="card">
            <div class="card-label">Delta médio</div>
            <div class="valor">${{indicadores.mean_delta >= 0 ? '+' : ''}}${{indicadores.mean_delta.toFixed(2)}}</div>
            <div class="desc">pontos</div>
        </div>
        <div class="card green">
            <div class="card-label">% Melhoraram</div>
            <div class="valor">${{indicadores.perc_improved.toFixed(1)}}%</div>
        </div>
        <div class="card red">
            <div class="card-label">% Pioraram</div>
            <div class="valor">${{indicadores.perc_worsened.toFixed(1)}}%</div>
        </div>
        <div class="card yellow">
            <div class="card-label">% Mantiveram</div>
            <div class="valor">${{indicadores.perc_unchanged.toFixed(1)}}%</div>
        </div>
        <div class="card">
            <div class="card-label">Effect Size</div>
            <div class="valor">${{indicadores.cohen_d.toFixed(3)}}</div>
        </div>
    `;
}}

function atualizarInterpretacao(dados) {{
    const container = document.getElementById('interpretacaoContainer');
    
function interpretarCohenD(d) {{
    const absD = Math.abs(d);
    const isPositive = d >= 0;
    let magnitude, hattieStatus, vocabStatus;
    
    if (absD >= 0.8) magnitude = "Grande";
    else if (absD >= 0.5) magnitude = "Médio";
    else if (absD >= 0.2) magnitude = "Pequeno";
    else magnitude = "Negligível";
    
    // Benchmark Hattie com direção
    if (absD >= 0.4) {{
        hattieStatus = isPositive ? 
            "✅ Acima do benchmark (d≥0.4) - Melhoria significativa" : 
            "🚨 Acima do benchmark (|d|≥0.4) - ALERTA: Deterioração significativa";
    }} else {{
        hattieStatus = isPositive ? 
            "⚠️ Abaixo do benchmark (d<0.4) - Melhoria limitada" : 
            "ℹ️ Abaixo do benchmark (|d|<0.4) - Deterioração limitada";
    }}
    
    // Vocabulário com direção
    if (absD >= 0.35) {{
        vocabStatus = isPositive ? 
            "✅ Significativo para vocabulário (d≥0.35) - Ganho relevante" : 
            "🚨 Significativo para vocabulário (|d|≥0.35) - ALERTA: Perda relevante";
    }} else {{
        vocabStatus = isPositive ? 
            "⚠️ Abaixo do threshold (d<0.35) - Ganho limitado" : 
            "ℹ️ Abaixo do threshold (|d|<0.35) - Perda limitada";
    }}
    
    return {{ magnitude, hattieStatus, vocabStatus, isPositive }};
}}    function criarGrupoItem(indicadores, nomeGrupo) {{
        const d = indicadores.cohen_d;
        const interp = interpretarCohenD(d);
        
        return `
            <div class="grupo-item">
                <div class="grupo-titulo">${{nomeGrupo}} (N=${{indicadores.n}})</div>
                <div class="grupo-detalhes">
                    <span>Média Pré: ${{indicadores.mean_pre.toFixed(2)}}</span>
                    <span>Média Pós: ${{indicadores.mean_pos.toFixed(2)}}</span>
                    <span>Delta: ${{indicadores.mean_delta >= 0 ? '+' : ''}}${{indicadores.mean_delta.toFixed(2)}}</span>
                    <span>Cohen's d: ${{d.toFixed(3)}}</span>
                    <span>% Melhoraram: ${{indicadores.perc_improved.toFixed(1)}}%</span>
                </div>
                <div class="interpretacao-grupo">
                    <p><strong>Magnitude:</strong> ${{interp.magnitude}} (Cohen, 1988)</p>
                    <p><strong>Benchmark Educacional:</strong> ${{interp.hattieStatus}} (Hattie, 2009)</p>
                    <p><strong>Vocabulário:</strong> ${{interp.vocabStatus}} (Marulis & Neuman, 2010)</p>
                </div>
            </div>
        `;
    }}
    
    container.innerHTML = 
        criarGrupoItem(dados.indicadores_6ano, "6º ano") + 
        criarGrupoItem(dados.indicadores_7ano, "7º ano") +
        criarGrupoItem(dados.indicadores_8ano, "8º ano") + 
        criarGrupoItem(dados.indicadores_9ano, "9º ano");
}}

function atualizarGraficos(graficos) {{
    if (!graficos) return;
    
    // Atualizar cada gráfico se existir
    const atualizarImg = (id, src) => {{
        const img = document.querySelector(`#${{id}} img`);
        if (img && src) {{
            img.src = src;
        }}
    }};
    
    atualizarImg('grafico-grupos', graficos.grupos_barras);
    atualizarImg('grafico-palavras', graficos.palavras_top);
    atualizarImg('grafico-intergrupos', graficos.comparacao_intergrupos);
    atualizarImg('grafico-heatmap-pre', graficos.heatmap_erros_pre);
    atualizarImg('grafico-heatmap-pos', graficos.heatmap_erros_pos);
    atualizarImg('grafico-ensinadas-nao-ensinadas', graficos.comparacao_ensinadas_vs_nao);
}}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', inicializar);
</script>
</body>
</html>
"""
    return html

def gerar_html_relatorio(indicadores_geral, indicadores_6ano, indicadores_7ano, indicadores_8ano, indicadores_9ano, 
                        palavras_df_todos, figuras_b64, escola_filtro=None):
    """Gera o relatório HTML completo seguindo padrão da Fase 3"""
    
    # Definir título baseado na escola
    if escola_filtro and escola_filtro != "Todas":
        titulo_escola = f" - {escola_filtro}"
        subtitulo_escola = f"Escola: {escola_filtro}. "
    else:
        titulo_escola = ""
        subtitulo_escola = "Todas as escolas. "
    
    # Calcular pontuação máxima possível (50 questões × 2 pontos cada)
    max_score = 50 * 2  # 100 pontos máximos
    mean_pre_percent = (indicadores_geral.get('mean_pre', 0) / max_score) *  100
    mean_pos_percent = (indicadores_geral.get('mean_pos', 0) / max_score) *  100
    
    # Cards seguindo o padrão da Fase 3
    cards_html = "".join([
        format_card("Palavras Testadas", "50", "questões de vocabulário", theme="default"),
        format_card("Pontuação Máxima", "100", "pontos (2 por questão)", theme="default"),
        format_card("Registros", f"{indicadores_geral.get('n', 0)}", "alunos após limpeza"),
        format_card("Média Pré", f"{indicadores_geral.get('mean_pre', 0):.2f}", f"({mean_pre_percent:.1f}% da máxima)"),
        format_card("Média Pós", f"{indicadores_geral.get('mean_pos', 0):.2f}", f"({mean_pos_percent:.1f}% da máxima)"),
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
    
    interp_html = (get_interpretacao_grupo(indicadores_6ano, "6º ano") + 
                   get_interpretacao_grupo(indicadores_7ano, "7º ano") +
                   get_interpretacao_grupo(indicadores_8ano, "8º ano") + 
                   get_interpretacao_grupo(indicadores_9ano, "9º ano"))

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
    .menu-container {{
        background: #fff; margin: 18px auto; max-width: 1200px; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }}
    .menu-title {{
        font-size: 18px; font-weight: 600; margin-bottom: 12px; color: var(--purple1);
    }}
    .escola-select {{
        width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; background: #fff; cursor: pointer;
        transition: border-color 0.3s ease;
    }}
    .escola-select:focus {{
        outline: none; border-color: var(--purple1);
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
        <div class="title">Relatório Visual WordGen{titulo_escola}</div>
        <div class="subtitle">{subtitulo_escola}Vocabulário – Fase 2 (Grupos Etários: 6º/7º vs 8º/9º anos). Análise pareada por estudante.</div>
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
                <img src="{figuras_b64.get('palavras_top', '')}" alt="Top Palavras" />
                <div class="caption">Palavras com maior melhora na taxa de acerto.</div>
            </div>
            <div class="fig">
                <img src="{figuras_b64.get('comparacao_intergrupos', '')}" alt="Comparação Intergrupos" />
                <div class="caption">Comparação detalhada entre grupos etários (Densidade separada por grupo + Distribuição de resultados embaixo).</div>
            </div>
        </div>

        <h2 class="section">Análise de Palavras Ensinadas vs. Não Ensinadas</h2>
        <div class="figs">
            <div class="fig" id="grafico-ensinadas-nao-ensinadas">
                <img src="{figuras_b64.get('comparacao_ensinadas_vs_nao', '')}" alt="Comparação Ensinadas vs Não Ensinadas" />
                <div class="caption">Comparativo de performance entre palavras que foram explicitamente ensinadas e as que não foram.</div>
            </div>
        </div>

        <h2 class="section">Percentual de Erros por Palavra e Grupo</h2>
        <div class="figs-heatmap">
            <div class="fig" id="grafico-heatmap-pre">
                <img src="{figuras_b64.get('heatmap_erros_pre', '')}" alt="Heatmap de Erros Pré-teste" />
                <div class="caption">Percentual de erros no pré-teste (Top 20 palavras).</div>
            </div>
            <div class="fig" id="grafico-heatmap-pos">
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

def gerar_relatorio_completo(escola_filtro=None):
    """Função principal que gera o relatório completo"""
    escola_nome = escola_filtro if escola_filtro and escola_filtro != "Todas" else "Todas as Escolas"
    print("="*60)
    print(f"RELATÓRIO VISUAL WORDGEN - FASE 2 - {escola_nome}")
    print("="*60)
    
    # Criar diretório de figuras
    os.makedirs(FIG_DIR, exist_ok=True)
    
    # 1. Carregar e preparar dados
    df_pre_final, df_pos_final, colunas_q, mapeamento_palavras = carregar_e_preparar_dados(escola_filtro)
    
    # 2. Calcular scores
    scores_df = calcular_scores(df_pre_final, df_pos_final, colunas_q)
    
    # Verificar se há dados suficientes
    if len(scores_df) == 0:
        print("❌ ERRO: Nenhum dado válido encontrado após limpeza.")
        print("   Verifique se a escola especificada possui dados válidos.")
        return None
    
    print(f"   Scores calculados: {len(scores_df)} estudantes")
    
    # 3. Calcular indicadores
    print("4. Calculando indicadores...")
    indicadores_geral = calcular_indicadores(scores_df)
    indicadores_6ano = calcular_indicadores(scores_df, "6º ano")
    indicadores_7ano = calcular_indicadores(scores_df, "7º ano")
    indicadores_8ano = calcular_indicadores(scores_df, "8º ano")
    indicadores_9ano = calcular_indicadores(scores_df, "9º ano")
    
    # 4. Analisar palavras
    print("5. Analisando palavras...")
    palavras_df_todos = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras)
    palavras_df_6ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "6º ano")
    palavras_df_7ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "7º ano")
    palavras_df_8ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "8º ano")
    palavras_df_9ano = analisar_palavras(df_pre_final, df_pos_final, colunas_q, mapeamento_palavras, "9º ano")
    
    # 5. Gerar figuras
    print("6. Gerando figuras...")
    
    # Figura 1: Comparação de grupos
    fig1 = plot_grupos_barras(scores_df)
    fig1.savefig(FIG_GRUPOS_BARRAS, dpi=150, bbox_inches='tight')
    plt.close(fig1)
    
    # Figura 2: Top palavras
    fig2 = plot_palavras_top(palavras_df_todos, palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    fig2.savefig(FIG_PALAVRAS_TOP, dpi=150, bbox_inches='tight')
    plt.close(fig2)
    
    # Figura 4: Comparação intergrupos
    fig4 = plot_comparacao_intergrupos(scores_df)
    fig4.savefig(FIG_INTERGRUPOS, dpi=150, bbox_inches='tight')
    plt.close(fig4)
    
    # Figura 5: Heatmap de erros pós-teste
    fig5 = plot_heatmap_erros_pos(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    fig5.savefig(FIG_HEATMAP_ERROS_POS, dpi=150, bbox_inches='tight')
    plt.close(fig5)
    
    # Figura 6: Heatmap de erros pré-teste
    fig6 = plot_heatmap_erros_pre(palavras_df_6ano, palavras_df_7ano, palavras_df_8ano, palavras_df_9ano)
    fig6.savefig(FIG_HEATMAP_ERROS_PRE, dpi=150, bbox_inches='tight')
    plt.close(fig6)
    
    # Figura 7: Comparação de palavras ensinadas vs não ensinadas
    fig7 = plot_comparacao_ensinadas_vs_nao(palavras_df_todos)
    fig7.savefig(FIG_ENSINADAS_VS_NAO, dpi=150, bbox_inches='tight')
    plt.close(fig7)
    
    # 6. Converter figuras para Base64
    print("7. Convertendo figuras para Base64...")
    figuras_b64 = {}
    
    for nome, caminho in [
        ('grupos_barras', FIG_GRUPOS_BARRAS),
        ('palavras_top', FIG_PALAVRAS_TOP),
        ('comparacao_intergrupos', FIG_INTERGRUPOS),
        ('heatmap_erros_pos', FIG_HEATMAP_ERROS_POS),
        ('heatmap_erros_pre', FIG_HEATMAP_ERROS_PRE),
        ('comparacao_ensinadas_vs_nao', FIG_ENSINADAS_VS_NAO)
    ]:
        if caminho.exists():
            with open(caminho, 'rb') as f:
                img_data = f.read()
                img_b64 = base64.b64encode(img_data).decode('utf-8')
                figuras_b64[nome] = f"data:image/png;base64,{img_b64}"
    
    # 7. Gerar relatório HTML
    print("8. Gerando relatório HTML...")
    html_content = gerar_html_relatorio(
        indicadores_geral, indicadores_6ano, indicadores_7ano, indicadores_8ano, indicadores_9ano,
        palavras_df_todos, figuras_b64, escola_filtro
    )
    
    # 8. Definir nome do arquivo baseado na escola
    if escola_filtro and escola_filtro != "Todas":
        # Limpar nome da escola para nome de arquivo
        escola_limpa = escola_filtro.replace(" ", "_").replace("/", "_").replace(".", "")
        output_file = DATA_DIR / f"relatorio_visual_wordgen_fase2_{escola_limpa}.html"
    else:
        output_file = OUTPUT_HTML
    
    # 9. Salvar HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("="*60)
    print("✅ RELATÓRIO GERADO COM SUCESSO!")
    print(f"📁 Arquivo HTML: {output_file}")
    print(f"📊 Figuras salvas em: {FIG_DIR}")
    print(f"👥 {indicadores_geral['n']} estudantes analisados")
    print(f"📈 Effect Size Geral: {indicadores_geral['cohen_d']:.4f}")
    print("="*60)
    
    return str(output_file)

def gerar_relatorios_todas_escolas():
    """Gera relatórios para todas as escolas individualmente"""
    escolas = obter_escolas_disponiveis()
    
    print("="*60)
    print("GERANDO RELATÓRIOS PARA TODAS AS ESCOLAS")
    print("="*60)
    
    arquivos_gerados = []
    
    for escola in escolas:
        try:
            print(f"\n🏫 Processando: {escola}")
            arquivo = gerar_relatorio_completo(escola)
            arquivos_gerados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao processar {escola}: {e}")
    
    print("\n" + "="*60)
    print("✅ TODOS OS RELATÓRIOS GERADOS!")
    print("="*60)
    print("📁 Arquivos gerados:")
    for arquivo in arquivos_gerados:
        print(f"   • {arquivo}")
    print("="*60)
    
    return arquivos_gerados

if __name__ == "__main__":
    import sys
    
    # Interface de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--todas-escolas":
            gerar_relatorios_todas_escolas()
        elif sys.argv[1] == "--escola":
            if len(sys.argv) > 2:
                escola = sys.argv[2]
                escolas_disponiveis = obter_escolas_disponiveis()
                if escola in escolas_disponiveis:
                    arquivo_gerado = gerar_relatorio_completo(escola)
                    print(f"✅ Relatório salvo: {arquivo_gerado}")
                    print(f"📊 Escola: {escola}")
                else:
                    print(f"❌ Escola '{escola}' não encontrada.")
                    print("🏫 Escolas disponíveis:")
                    for esc in escolas_disponiveis:
                        print(f"   • {esc}")
            else:
                print("❌ Especifique o nome da escola após --escola")
        elif sys.argv[1] == "--interativo":
            print("🔄 Gerando relatório interativo...")
            html_content = gerar_html_relatorio_interativo()
            arquivo_saida = "/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Data/relatorio_visual_wordgen_fase2_interativo.html"
            
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Relatório interativo salvo: {arquivo_saida}")
            print(f"🌐 Abra o arquivo em um navegador para usar o menu de seleção")
        elif sys.argv[1] == "--listar-escolas":
            escolas = obter_escolas_disponiveis()
            print("🏫 Escolas disponíveis:")
            for escola in escolas:
                print(f"   • {escola}")
        else:
            print("❌ Opção inválida.")
            print("📋 Uso:")
            print("   python RelatorioVisualCompleto.py                   # Todas as escolas")
            print("   python RelatorioVisualCompleto.py --todas-escolas   # Todas separadamente")
            print("   python RelatorioVisualCompleto.py --escola 'NOME'   # Escola específica")
            print("   python RelatorioVisualCompleto.py --interativo      # Menu interativo")
            print("   python RelatorioVisualCompleto.py --listar-escolas  # Listar escolas")
    else:
        # Padrão: gerar relatório geral (todas as escolas)
        arquivo_gerado = gerar_relatorio_completo()
        print(f"✅ Relatório salvo: {arquivo_gerado}")
        print(f"📊 Amostra: Todas as escolas")
