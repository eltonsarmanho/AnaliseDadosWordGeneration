import pandas
import os
import sys
import pathlib
from scipy import stats
import numpy as np

# Adiciona o diretório atual ao sys.path para permitir importações relativas
current_dir = pathlib.Path(__file__).parent.resolve()
current_dir = str(current_dir) + '/Data'
nome = "RESULTADOS Geração Impacto (WordGen) - TDE, Vocabulário (2023-2, Fase 2).xlsx"
arquivo_excel = os.path.join(current_dir, nome)
print(f"Arquivo Excel localizado: {arquivo_excel}")
# Carregar as duas abas do arquivo Excel
df_pre = pandas.read_excel(arquivo_excel, sheet_name='2023-2 TDE pre')
df_pos = pandas.read_excel(arquivo_excel, sheet_name='2023-2 TDE pos')

print("Dados carregados com sucesso.")

# Verificar IDs em comum entre df_pre e df_pos
ids_pre = set(df_pre['id'])
ids_pos = set(df_pos['id'])
ids_comuns = ids_pre.intersection(ids_pos)

print(f"Total de IDs em df_pre: {len(ids_pre)}")
print(f"Total de IDs em df_pos: {len(ids_pos)}")
print(f"IDs em comum: {len(ids_comuns)}")
print(f"IDs únicos em df_pre: {len(ids_pre - ids_pos)}")
print(f"IDs únicos em df_pos: {len(ids_pos - ids_pre)}")

# Se quiser ver os IDs em comum
# print(f"Lista de IDs em comum: {sorted(list(ids_comuns))}")

# Filtrar os DataFrames para manter apenas os IDs em comum
df_pre_filtrado = df_pre[df_pre['id'].isin(ids_comuns)]
df_pos_filtrado = df_pos[df_pos['id'].isin(ids_comuns)]

print(f"\nApós filtrar por IDs em comum:")
print(f"Registros em df_pre_filtrado: {len(df_pre_filtrado)}")
print(f"Registros em df_pos_filtrado: {len(df_pos_filtrado)}")

#print(df_pre_filtrado.info())
#print(df_pos_filtrado.info())

# Descrição estatística dos dados pré-intervenção
print("\n" + "="*50)
print("DESCRIÇÃO ESTATÍSTICA - PRÉ-INTERVENÇÃO")
print("="*50)
print(df_pre_filtrado.describe())

# Descrição estatística dos dados pós-intervenção
print("\n" + "="*50)
print("DESCRIÇÃO ESTATÍSTICA - PÓS-INTERVENÇÃO")
print("="*50)
print(df_pos_filtrado.describe())

# Descrição estatística específica para as perguntas P1 a P40 e Score Final
colunas_interesse = [col for col in df_pre_filtrado.columns if col.startswith('P') or 'Score' in col or 'score' in col]

if colunas_interesse:
    # Separar colunas P (booleanas) das colunas Score
    colunas_p = [col for col in colunas_interesse if col.startswith('P')]
    colunas_score = [col for col in colunas_interesse if 'Score' in col or 'score' in col]
    
    # Converter colunas P para booleano (0 = False, 1 ou 2 = True)
    df_pre_bool = df_pre_filtrado[colunas_p].copy()
    df_pos_bool = df_pos_filtrado[colunas_p].copy()
    
    for col in colunas_p:
        # Converter para numérico, valores não numéricos vão virar NaN
        df_pre_bool[col] = pandas.to_numeric(df_pre_filtrado[col], errors='coerce').fillna(0)
        df_pos_bool[col] = pandas.to_numeric(df_pos_filtrado[col], errors='coerce').fillna(0)
        
        # Converter para booleano (0 = False, qualquer valor > 0 = True)
        df_pre_bool[col] = (df_pre_bool[col] > 0).astype(int)
        df_pos_bool[col] = (df_pos_bool[col] > 0).astype(int)
    
    print("\n" + "="*60)
    print("ANÁLISE ESTATÍSTICA - PERGUNTAS BOOLEANAS (PRÉ)")
    print("="*60)
    print("Proporção de acertos por pergunta:")
    print(df_pre_bool.mean().round(3))
    print("\nTotal de acertos por pergunta:")
    print(df_pre_bool.sum())
    print(f"\nTotal de participantes: {len(df_pre_bool)}")
    
    print("\n" + "="*60)
    print("ANÁLISE ESTATÍSTICA - PERGUNTAS BOOLEANAS (PÓS)")
    print("="*60)
    print("Proporção de acertos por pergunta:")
    print(df_pos_bool.mean().round(3))
    print("\nTotal de acertos por pergunta:")
    print(df_pos_bool.sum())
    print(f"\nTotal de participantes: {len(df_pos_bool)}")
    
    # Análise dos Scores (se existirem)
    if colunas_score:
        print("\n" + "="*60)
        print("DESCRIÇÃO ESTATÍSTICA - SCORE FINAL")
        print("="*60)
        print("PRÉ-INTERVENÇÃO:")
        print(df_pre_filtrado[colunas_score].describe())
        print("\nPÓS-INTERVENÇÃO:")
        print(df_pos_filtrado[colunas_score].describe())
    
    # Comparação geral de desempenho
    # Ordenar os dataframes pelo ID para garantir correspondência
    df_pre_bool_sorted = df_pre_bool.set_index(df_pre_filtrado['id']).sort_index()
    df_pos_bool_sorted = df_pos_bool.set_index(df_pos_filtrado['id']).sort_index()
    
    acertos_pre = df_pre_bool_sorted.sum(axis=1)
    acertos_pos = df_pos_bool_sorted.sum(axis=1)
    
    print("\n" + "="*60)
    print("COMPARAÇÃO DE DESEMPENHO GERAL")
    print("="*60)
    print(f"Média de acertos PRÉ: {acertos_pre.mean():.2f} ± {acertos_pre.std():.2f}")
    print(f"Média de acertos PÓS: {acertos_pos.mean():.2f} ± {acertos_pos.std():.2f}")
    print(f"Diferença média: {(acertos_pos.mean() - acertos_pre.mean()):.2f}")
    
    # TESTES ESTATÍSTICOS PARA VERIFICAR MELHORA
    print("\n" + "="*60)
    print("TESTES ESTATÍSTICOS COMPARATIVOS DOS GRUPOS")
    print("="*60)
    
    # 1. Teste t pareado (Wilcoxon para dados não-normais)
    try:
        # Teste de normalidade (Shapiro-Wilk)
        stat_pre, p_pre = stats.shapiro(acertos_pre)
        stat_pos, p_pos = stats.shapiro(acertos_pos)
        
        print(f"Teste de Normalidade:")
        print(f"PRÉ - Shapiro-Wilk: p-value = {p_pre:.4f}")
        print(f"PÓS - Shapiro-Wilk: p-value = {p_pos:.4f}")
        
        # Se dados são normais (p > 0.05), usar teste t pareado
        if p_pre > 0.05 and p_pos > 0.05:
            t_stat, p_value = stats.ttest_rel(acertos_pos, acertos_pre)
            print(f"\nTeste t pareado:")
            print(f"t-statistic: {t_stat:.4f}")
            print(f"p-value: {p_value:.4f}")
        else:
            # Se não são normais, usar Wilcoxon
            w_stat, p_value = stats.wilcoxon(acertos_pos, acertos_pre, alternative='greater')
            print(f"\nTeste Wilcoxon (dados não-normais):")
            print(f"W-statistic: {w_stat:.4f}")
            print(f"p-value: {p_value:.4f}")
        
        # Interpretação do resultado
        alpha = 0.05
        if p_value < alpha:
            print(f"\n✓ RESULTADO: Há melhora estatisticamente significativa (p < {alpha})")
        else:
            print(f"\n✗ RESULTADO: Não há melhora estatisticamente significativa (p >= {alpha})")
            
    except Exception as e:
        print(f"Erro no teste estatístico: {e}")
    
    # 2. Tamanho do efeito (Cohen's d)
    try:
        diferenca = acertos_pos - acertos_pre
        cohen_d = diferenca.mean() / diferenca.std()
        print(f"\nTamanho do Efeito (Cohen's d): {cohen_d:.4f}")
        
        if abs(cohen_d) < 0.2:
            interpretacao = "pequeno"
        elif abs(cohen_d) < 0.5:
            interpretacao = "médio"
        elif abs(cohen_d) < 0.8:
            interpretacao = "grande"
        else:
            interpretacao = "muito grande"
        
        print(f"Interpretação: Efeito {interpretacao}")
        
    except Exception as e:
        print(f"Erro no cálculo do tamanho do efeito: {e}")
    
    # 3. Análise de melhora individual
    melhoraram = (acertos_pos > acertos_pre).sum()
    pioraram = (acertos_pos < acertos_pre).sum()
    mantiveram = (acertos_pos == acertos_pre).sum()
    
    print(f"\n" + "="*60)
    print("ANÁLISE INDIVIDUAL DE MUDANÇA")
    print("="*60)
    print(f"Participantes que melhoraram: {melhoraram} ({melhoraram/len(acertos_pre)*100:.1f}%)")
    print(f"Participantes que pioraram: {pioraram} ({pioraram/len(acertos_pre)*100:.1f}%)")
    print(f"Participantes que mantiveram: {mantiveram} ({mantiveram/len(acertos_pre)*100:.1f}%)")
    
    # 4. Análise por pergunta (quais perguntas mais melhoraram)
    print(f"\n" + "="*60)
    print("MELHORA POR PERGUNTA")
    print("="*60)
    melhora_por_pergunta = df_pos_bool_sorted.mean() - df_pre_bool_sorted.mean()
    melhora_por_pergunta_sorted = melhora_por_pergunta.sort_values(ascending=False)
    
    print("Top 10 perguntas com maior melhora:")
    for i, (pergunta, melhora) in enumerate(melhora_por_pergunta_sorted.head(10).items(), 1):
        print(f"{i:2d}. {pergunta}: +{melhora:.3f} ({melhora*100:.1f}%)")