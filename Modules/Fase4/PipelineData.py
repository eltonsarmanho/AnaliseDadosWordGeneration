import pandas
import os
import sys
import pathlib
from scipy import stats
import numpy as np
from contextlib import redirect_stdout
import io

# Adiciona o diretório atual ao sys.path para permitir importações relativas
current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
print(f"Diretório atual: {current_dir}")
current_dir = str(current_dir) + '/Data'
nome = "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_4.xlsx"
arquivo_excel = os.path.join(current_dir, nome)
print(f"Arquivo Excel localizado: {arquivo_excel}")

# Buffer para capturar toda a saída
output_buffer = io.StringIO()

# Redirecionar stdout para capturar prints
original_stdout = sys.stdout

def capture_print(*args, **kwargs):
    """Função para capturar prints tanto no console quanto no buffer"""
    print(*args, **kwargs, file=original_stdout)  # Console
    print(*args, **kwargs, file=output_buffer)    # Buffer

# Substituir print temporariamente
sys.stdout = output_buffer

# Carregar as duas abas do arquivo Excel
capture_print("="*80)
capture_print("PIPELINE DE ANÁLISE - VOCABULÁRIO WORDGEN - ETAPA 4")
capture_print("="*80)
capture_print("Dados carregados com sucesso.")

df = pandas.read_excel(arquivo_excel, sheet_name='WG SSb (2024-2) - TDE, Vocabulá')
capture_print(f"Registros em df: {len(df)}")

# Converter colunas para float64
df['total_pre_voc'] = pandas.to_numeric(df['total_pre_voc'], errors='coerce')
df['total_pos_voc'] = pandas.to_numeric(df['total_pos_voc'], errors='coerce')

capture_print("\nApós conversão:")
capture_print(df[['total_pre_voc', 'total_pos_voc']].dtypes)
capture_print(f"Valores nulos em total_pre_voc: {df['total_pre_voc'].isnull().sum()}")
capture_print(f"Valores nulos em total_pos_voc: {df['total_pos_voc'].isnull().sum()}")

# Verificar registros antes da limpeza
capture_print(f"\nRegistros antes da limpeza: {len(df)}")

# Remover registros onde total_pre_voc ou total_pos_voc são NaN/nulos
df = df.dropna(subset=['total_pre_voc', 'total_pos_voc'])

# Verificar registros após a limpeza
capture_print(f"Registros após a limpeza: {len(df)}")
capture_print(f"Valores nulos restantes em total_pre_voc: {df['total_pre_voc'].isnull().sum()}")
capture_print(f"Valores nulos restantes em total_pos_voc: {df['total_pos_voc'].isnull().sum()}")

def analise_estatistica_vocabulario(df):
    """
    Análise estatística descritiva das colunas de vocabulário por grupo
    """
    capture_print("="*70)
    capture_print("ANÁLISE ESTATÍSTICA DESCRITIVA - VOCABULÁRIO")
    capture_print("="*70)
    
    # 1. ESTATÍSTICAS GERAIS (todos os grupos)
    capture_print("\n1. ESTATÍSTICAS GERAIS (TODOS OS GRUPOS)")
    capture_print("-"*50)
    
    colunas_interesse = ['total_pre_voc', 'total_pos_voc']
    desc_geral = df[colunas_interesse].describe()
    capture_print(desc_geral.round(2))
    
    # Adicionar algumas estatísticas extras
    capture_print(f"\nTotal de alunos analisados: {len(df)}")
    capture_print(f"Grupos únicos: {df['group'].unique()}")
    capture_print(f"Quantidade por grupo:\n{df['group'].value_counts().sort_index()}")
    
    # 2. COMPARAÇÃO PRÉ vs PÓS (geral)
    capture_print("\n2. COMPARAÇÃO PRÉ vs PÓS (GERAL)")
    capture_print("-"*50)
    
    # Calcular delta (melhora)
    df['delta_voc'] = df['total_pos_voc'] - df['total_pre_voc']
    
    media_pre = df['total_pre_voc'].mean()
    media_pos = df['total_pos_voc'].mean()
    media_delta = df['delta_voc'].mean()
    
    capture_print(f"Média PRÉ-teste:  {media_pre:.2f}")
    capture_print(f"Média PÓS-teste:  {media_pos:.2f}")
    capture_print(f"Diferença média:  {media_delta:.2f}")
    capture_print(f"Melhora %:        {(media_delta/media_pre)*100:.1f}%")
    
    # Distribuição das mudanças
    melhoraram = (df['delta_voc'] > 0).sum()
    pioraram = (df['delta_voc'] < 0).sum()
    mantiveram = (df['delta_voc'] == 0).sum()
    
    capture_print(f"\nDistribuição das mudanças:")
    capture_print(f"Melhoraram:  {melhoraram} ({100*melhoraram/len(df):.1f}%)")
    capture_print(f"Pioraram:    {pioraram} ({100*pioraram/len(df):.1f}%)")
    capture_print(f"Mantiveram:  {mantiveram} ({100*mantiveram/len(df):.1f}%)")
    
    # 3. ANÁLISE POR GRUPO
    capture_print("\n3. ANÁLISE DETALHADA POR GRUPO")
    capture_print("-"*50)
    
    grupos = df['group'].unique()
    resultados_grupo = []
    
    for grupo in sorted(grupos):
        df_grupo = df[df['group'] == grupo]
        n_alunos = len(df_grupo)
        
        if n_alunos == 0:
            continue
            
        capture_print(f"\nGRUPO: {grupo} (n={n_alunos})")
        capture_print("-" * 30)
        
        # Estatísticas do grupo
        stats_grupo = df_grupo[colunas_interesse].describe()
        capture_print(stats_grupo.round(2))
        
        # Comparação pré-pós no grupo
        pre_grupo = df_grupo['total_pre_voc'].mean()
        pos_grupo = df_grupo['total_pos_voc'].mean()
        delta_grupo = df_grupo['delta_voc'].mean()
        
        capture_print(f"\nMédia PRÉ:     {pre_grupo:.2f}")
        capture_print(f"Média PÓS:     {pos_grupo:.2f}")
        capture_print(f"Delta médio:   {delta_grupo:.2f}")
        capture_print(f"Melhora %:     {(delta_grupo/pre_grupo)*100:.1f}%")
        
        # Mudanças no grupo
        melhor_grupo = (df_grupo['delta_voc'] > 0).sum()
        pior_grupo = (df_grupo['delta_voc'] < 0).sum()
        igual_grupo = (df_grupo['delta_voc'] == 0).sum()
        
        capture_print(f"Melhoraram:    {melhor_grupo} ({100*melhor_grupo/n_alunos:.1f}%)")
        capture_print(f"Pioraram:      {pior_grupo} ({100*pior_grupo/n_alunos:.1f}%)")
        capture_print(f"Mantiveram:    {igual_grupo} ({100*igual_grupo/n_alunos:.1f}%)")
        
        # Guardar para comparação
        resultados_grupo.append({
            'grupo': grupo,
            'n_alunos': n_alunos,
            'media_pre': pre_grupo,
            'media_pos': pos_grupo,
            'delta_medio': delta_grupo,
            'melhora_perc': (delta_grupo/pre_grupo)*100,
            'prop_melhoraram': melhor_grupo/n_alunos
        })
    
    # 4. COMPARAÇÃO ENTRE GRUPOS
    # capture_print("\n4. RESUMO COMPARATIVO ENTRE GRUPOS")
    # capture_print("-"*50)
    
    df_resumo = pandas.DataFrame(resultados_grupo)
    # capture_print(df_resumo.round(2))
    
    # 5. TESTE ESTATÍSTICO BÁSICO
    capture_print("\n5. TESTE ESTATÍSTICO (PRÉ vs PÓS)")
    capture_print("-"*50)
    
    # Teste t pareado para toda a amostra
    from scipy.stats import ttest_rel, wilcoxon, shapiro
    
    # Teste de normalidade
    stat_norm_pre, p_norm_pre = shapiro(df['total_pre_voc'])
    stat_norm_pos, p_norm_pos = shapiro(df['total_pos_voc'])
    
    capture_print(f"Teste de normalidade (Shapiro-Wilk):")
    capture_print(f"PRÉ:  p-value = {p_norm_pre:.6f}")
    capture_print(f"PÓS:  p-value = {p_norm_pos:.6f}")
    
    # Escolher teste apropriado
    if p_norm_pre > 0.05 and p_norm_pos > 0.05:
        # Dados normais: teste t pareado
        stat, p_value = ttest_rel(df['total_pre_voc'], df['total_pos_voc'])
        capture_print(f"\nTeste t pareado:")
        capture_print(f"t-statistic: {stat:.4f}")
        capture_print(f"p-value: {p_value:.6f}")
    else:
        # Dados não normais: Wilcoxon
        stat, p_value = wilcoxon(df['total_pre_voc'], df['total_pos_voc'])
        capture_print(f"\nTeste Wilcoxon (dados não normais):")
        capture_print(f"W-statistic: {stat:.4f}")
        capture_print(f"p-value: {p_value:.6f}")
    
    # Interpretação
    alpha = 0.05
    if p_value < alpha:
        capture_print(f"\n✓ RESULTADO: Diferença estatisticamente significativa (p < {alpha})")
    else:
        capture_print(f"\n✗ RESULTADO: Diferença NÃO estatisticamente significativa (p ≥ {alpha})")
    
    # Tamanho do efeito (Cohen's d)
    pooled_std = np.sqrt((df['total_pre_voc'].var() + df['total_pos_voc'].var()) / 2)
    cohens_d = (df['total_pos_voc'].mean() - df['total_pre_voc'].mean()) / pooled_std
    
    capture_print(f"\nTamanho do efeito (Cohen's d): {cohens_d:.4f}")
    if abs(cohens_d) < 0.2:
        capture_print("Interpretação: Efeito pequeno")
    elif abs(cohens_d) < 0.5:
        capture_print("Interpretação: Efeito médio")
    else:
        capture_print("Interpretação: Efeito grande")
    
    return df_resumo

def categorizar_mudanca_cohen(delta, baseline_sd):
    """
    Categorização baseada em Cohen's d (1988) - Effect Size
    Referência: Cohen, J. (1988). Statistical power analysis for the behavioral sciences
    
    Pequeno: 0.2 SD, Médio: 0.5 SD, Grande: 0.8 SD
    """
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

def analise_individual_mudanca(df):
    """
    Análise detalhada das mudanças individuais - geral e por grupo
    Usando categorização baseada em Cohen's Effect Size
    """
    capture_print("="*70)
    capture_print("ANÁLISE INDIVIDUAL DE MUDANÇA - VOCABULÁRIO (COHEN'S EFFECT SIZE)")
    capture_print("="*70)
    
    # Calcular delta se não existir
    if 'delta_voc' not in df.columns:
        df['delta_voc'] = df['total_pos_voc'] - df['total_pre_voc']
    
    # Calcular parâmetros para Cohen's d
    baseline_mean = df['total_pre_voc'].mean()
    baseline_sd = df['total_pre_voc'].std()
    
    capture_print(f"PARÂMETROS DE REFERÊNCIA (Cohen, 1988):")
    capture_print(f"Baseline mean: {baseline_mean:.2f}")
    capture_print(f"Baseline SD: {baseline_sd:.2f}")
    capture_print(f"Pequeno (0.2 SD): ±{0.2*baseline_sd:.2f}")
    capture_print(f"Médio (0.5 SD): ±{0.5*baseline_sd:.2f}")
    capture_print(f"Grande (0.8 SD): ±{0.8*baseline_sd:.2f}")
    
    # 1. ANÁLISE GERAL DAS MUDANÇAS INDIVIDUAIS
    capture_print("\n1. ANÁLISE GERAL DAS MUDANÇAS INDIVIDUAIS")
    capture_print("-"*50)
    
    # Estatísticas do delta
    capture_print("Estatísticas das mudanças (delta = pós - pré):")
    capture_print(df['delta_voc'].describe().round(2))
    
    # Categorização baseada em Cohen
    df['categoria_cohen'] = df['delta_voc'].apply(
        lambda x: categorizar_mudanca_cohen(x, baseline_sd)
    )
    
    capture_print(f"\nDistribuição das categorias (Cohen's Effect Size) (n={len(df)}):")
    cat_counts = df['categoria_cohen'].value_counts()
    
    # Ordenar categorias por magnitude
    ordem_categorias = [
        "Piora Grande (<-0.8 SD)",
        "Piora Média (-0.8 a -0.5 SD)", 
        "Piora Pequena (-0.5 a -0.2 SD)",
        "Sem Mudança Prática (±0.2 SD)",
        "Melhora Pequena (0.2-0.5 SD)",
        "Melhora Média (0.5-0.8 SD)",
        "Melhora Grande (≥0.8 SD)"
    ]
    
    for categoria in ordem_categorias:
        if categoria in cat_counts.index:
            count = cat_counts[categoria]
            capture_print(f"{categoria:30s}: {count:4d} ({100*count/len(df):5.1f}%)")
    
    # Effect sizes observados
    effect_size_medio = df['delta_voc'].mean() / baseline_sd
    capture_print(f"\nEffect Size médio observado: {effect_size_medio:.3f}")
    
    if abs(effect_size_medio) < 0.2:
        interpretacao = "Efeito trivial/negligível"
    elif abs(effect_size_medio) < 0.5:
        interpretacao = "Efeito pequeno"
    elif abs(effect_size_medio) < 0.8:
        interpretacao = "Efeito médio"
    else:
        interpretacao = "Efeito grande"
    
    capture_print(f"Interpretação Cohen: {interpretacao}")
    
    # 2. ANÁLISE INDIVIDUAL POR GRUPO
    capture_print("\n2. ANÁLISE INDIVIDUAL POR GRUPO")
    capture_print("-"*50)
    
    grupos = sorted(df['group'].unique())
    resultados_individuais = []
    
    for grupo in grupos:
        df_grupo = df[df['group'] == grupo]
        n_grupo = len(df_grupo)
        
        if n_grupo == 0:
            continue
            
        capture_print(f"\nGRUPO: {grupo} (n={n_grupo})")
        capture_print("-" * 40)
        
        # Estatísticas do delta no grupo
        capture_print("Estatísticas das mudanças no grupo:")
        desc_grupo = df_grupo['delta_voc'].describe().round(2)
        capture_print(desc_grupo)
        
        # Effect size do grupo
        effect_size_grupo = df_grupo['delta_voc'].mean() / baseline_sd
        capture_print(f"\nEffect Size do grupo: {effect_size_grupo:.3f}")
        
        # Categorias de mudança no grupo (Cohen)
        capture_print(f"\nDistribuição das categorias (Cohen):")
        cat_grupo = df_grupo['categoria_cohen'].value_counts()
        
        for categoria in ordem_categorias:
            if categoria in cat_grupo.index:
                count = cat_grupo[categoria]
                capture_print(f"{categoria:30s}: {count:3d} ({100*count/n_grupo:5.1f}%)")
        
        # Comparação com a média geral
        delta_medio_grupo = df_grupo['delta_voc'].mean()
        delta_medio_geral = df['delta_voc'].mean()
        
        capture_print(f"\nComparação com média geral:")
        capture_print(f"Média do grupo: {delta_medio_grupo:6.2f} (ES: {effect_size_grupo:.3f})")
        capture_print(f"Média geral:    {delta_medio_geral:6.2f} (ES: {effect_size_medio:.3f})")
        capture_print(f"Diferença:      {delta_medio_grupo - delta_medio_geral:+6.2f}")
        
        # Contagens por categoria Cohen
        melhora_grande = len(df_grupo[df_grupo['delta_voc'] >= 0.8*baseline_sd])
        melhora_media = len(df_grupo[(df_grupo['delta_voc'] >= 0.5*baseline_sd) & (df_grupo['delta_voc'] < 0.8*baseline_sd)])
        melhora_pequena = len(df_grupo[(df_grupo['delta_voc'] >= 0.2*baseline_sd) & (df_grupo['delta_voc'] < 0.5*baseline_sd)])
        sem_mudanca = len(df_grupo[(df_grupo['delta_voc'] > -0.2*baseline_sd) & (df_grupo['delta_voc'] < 0.2*baseline_sd)])
        piora_pequena = len(df_grupo[(df_grupo['delta_voc'] >= -0.5*baseline_sd) & (df_grupo['delta_voc'] <= -0.2*baseline_sd)])
        piora_media = len(df_grupo[(df_grupo['delta_voc'] >= -0.8*baseline_sd) & (df_grupo['delta_voc'] < -0.5*baseline_sd)])
        piora_grande = len(df_grupo[df_grupo['delta_voc'] < -0.8*baseline_sd])
        
        # Guardar resultados para comparação
        resultados_individuais.append({
            'grupo': grupo,
            'n_alunos': n_grupo,
            'delta_medio': delta_medio_grupo,
            'effect_size': effect_size_grupo,
            'delta_mediano': df_grupo['delta_voc'].median(),
            'delta_std': df_grupo['delta_voc'].std(),
            'melhora_grande_cohen': melhora_grande,
            'melhora_media_cohen': melhora_media,
            'melhora_pequena_cohen': melhora_pequena,
            'sem_mudanca_cohen': sem_mudanca,
            'piora_pequena_cohen': piora_pequena,
            'piora_media_cohen': piora_media,
            'piora_grande_cohen': piora_grande,
            'prop_melhoraram': len(df_grupo[df_grupo['delta_voc'] > 0]) / n_grupo,
            'prop_pioraram': len(df_grupo[df_grupo['delta_voc'] < 0]) / n_grupo,
            'prop_melhora_significativa': (melhora_pequena + melhora_media + melhora_grande) / n_grupo
        })
    
    # 3. RESUMO COMPARATIVO ENTRE GRUPOS
    # capture_print("\n3. RESUMO COMPARATIVO - MUDANÇAS INDIVIDUAIS (COHEN)")
    # capture_print("-"*50)
    
    df_comp_individual = pandas.DataFrame(resultados_individuais)
    
    # capture_print("\nResumo por grupo (Effect Size):")
    # capture_print(df_comp_individual[['grupo', 'n_alunos', 'delta_medio', 'effect_size', 'delta_mediano', 'delta_std', 
    #                           'prop_melhoraram', 'prop_melhora_significativa']].round(3))
    
    # capture_print("\nContagem de categorias Cohen por grupo:")
    # capture_print(df_comp_individual[['grupo', 'melhora_grande_cohen', 'melhora_media_cohen', 'melhora_pequena_cohen', 
    #                           'sem_mudanca_cohen', 'piora_pequena_cohen', 'piora_media_cohen', 'piora_grande_cohen']])
    
    # 4. TESTE ESTATÍSTICO ENTRE GRUPOS
    # capture_print("\n4. COMPARAÇÃO ESTATÍSTICA ENTRE GRUPOS")
    # capture_print("-"*50)
    
    if len(grupos) == 2:
        grupo1, grupo2 = grupos
        delta_g1 = df[df['group'] == grupo1]['delta_voc']
        delta_g2 = df[df['group'] == grupo2]['delta_voc']
        
        # Effect sizes por grupo
        es_g1 = delta_g1.mean() / baseline_sd
        es_g2 = delta_g2.mean() / baseline_sd
        
        capture_print(f"Effect Size por grupo:")
        capture_print(f"{grupo1}: {es_g1:.3f}")
        capture_print(f"{grupo2}: {es_g2:.3f}")
        capture_print(f"Diferença ES: {es_g1 - es_g2:.3f}")
        
        # Teste de normalidade
        from scipy.stats import shapiro, mannwhitneyu, ttest_ind
        
        _, p_norm_g1 = shapiro(delta_g1)
        _, p_norm_g2 = shapiro(delta_g2)
        
        capture_print(f"\nTeste de normalidade das mudanças:")
        capture_print(f"{grupo1}: p = {p_norm_g1:.6f}")
        capture_print(f"{grupo2}: p = {p_norm_g2:.6f}")
        
        # Escolher teste apropriado
        if p_norm_g1 > 0.05 and p_norm_g2 > 0.05:
            # Teste t independente
            stat, p_value = ttest_ind(delta_g1, delta_g2)
            capture_print(f"\nTeste t independente:")
            capture_print(f"t-statistic: {stat:.4f}")
        else:
            # Mann-Whitney U
            stat, p_value = mannwhitneyu(delta_g1, delta_g2, alternative='two-sided')
            capture_print(f"\nTeste Mann-Whitney U:")
            capture_print(f"U-statistic: {stat:.4f}")
        
        capture_print(f"p-value: {p_value:.6f}")
        
        if p_value < 0.05:
            capture_print(f"✓ Diferença significativa entre grupos (p < 0.05)")
        else:
            capture_print(f"✗ Diferença NÃO significativa entre grupos (p ≥ 0.05)")
        
        # Cohen's d entre grupos
        pooled_std = np.sqrt((delta_g1.var() + delta_g2.var()) / 2)
        cohens_d = (delta_g1.mean() - delta_g2.mean()) / pooled_std
        capture_print(f"\nTamanho do efeito entre grupos (Cohen's d): {cohens_d:.4f}")
        
        if abs(cohens_d) < 0.2:
            capture_print("Interpretação: Diferença trivial entre grupos")
        elif abs(cohens_d) < 0.5:
            capture_print("Interpretação: Diferença pequena entre grupos")
        elif abs(cohens_d) < 0.8:
            capture_print("Interpretação: Diferença média entre grupos")
        else:
            capture_print("Interpretação: Diferença grande entre grupos")
    
    # capture_print(f"\n" + "="*70)
    # capture_print("REFERÊNCIA CIENTÍFICA:")
    # capture_print("Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.)")
    # capture_print("Effect Size: Pequeno = 0.2, Médio = 0.5, Grande = 0.8")
    # capture_print("="*70)
    
    return df_comp_individual, df['categoria_cohen'].value_counts()

def interpretar_effect_size_vocabulario(effect_size):
    """
    Interpretação contextualizada para desenvolvimento de vocabulário
    Baseado em: Marulis & Neuman (2010), Wright & Neuman (2014)
    """
    abs_es = abs(effect_size)
    
    if abs_es < 0.15:
        return {
            'magnitude': 'Trivial',
            'interpretacao': 'Mudança não significativa na prática',
            'contexto_educacional': 'Sem impacto educacional detectável'
        }
    elif abs_es < 0.35:
        return {
            'magnitude': 'Pequeno',
            'interpretacao': 'Mudança pequena mas educacionalmente relevante',
            'contexto_educacional': 'Ganho típico de intervenções escolares'
        }
    elif abs_es < 0.65:
        return {
            'magnitude': 'Moderado',
            'interpretacao': 'Mudança substancial e educacionalmente importante',
            'contexto_educacional': 'Ganho significativo - intervenção eficaz'
        }
    elif abs_es < 1.0:
        return {
            'magnitude': 'Grande',
            'interpretacao': 'Mudança grande e muito significativa',
            'contexto_educacional': 'Ganho excepcional - intervenção muito eficaz'
        }
    else:
        return {
            'magnitude': 'Muito Grande',
            'interpretacao': 'Mudança transformadora',
            'contexto_educacional': 'Ganho extraordinário - resultado raro'
        }

def analise_effect_size_contextualizada(df_comp_individual):
    """
    Análise contextualizada dos effect sizes por grupo
    """
    capture_print("\n" + "="*70)
    capture_print("INTERPRETAÇÃO CONTEXTUALIZADA DOS EFFECT SIZES")
    capture_print("="*70)
    
    capture_print("\nLITERATURA DE REFERÊNCIA:")
    capture_print("• Cohen (1988): d = 0.2 (pequeno), 0.5 (médio), 0.8 (grande)")
    capture_print("• Educação (Hattie, 2009): d = 0.4+ considerado 'bom resultado'")
    capture_print("• Vocabulário (Marulis & Neuman, 2010): d = 0.35+ 'educacionalmente significativo'")
    
    for _, grupo_data in df_comp_individual.iterrows():
        grupo = grupo_data['grupo']
        es = grupo_data['effect_size']
        n = grupo_data['n_alunos']
        
        interpretacao = interpretar_effect_size_vocabulario(es)
        
        capture_print(f"\n{grupo.upper()}: Effect Size = {es:.3f} (n={n})")
        capture_print(f"  Magnitude: {interpretacao['magnitude']}")
        capture_print(f"  Interpretação: {interpretacao['interpretacao']}")
        capture_print(f"  Contexto Educacional: {interpretacao['contexto_educacional']}")
        
        # Intervalo de confiança (aproximado)
        se_d = np.sqrt((n + n) / (n * n) + (es**2) / (2 * (n + n)))
        ic_lower = es - 1.96 * se_d
        ic_upper = es + 1.96 * se_d
        capture_print(f"  IC 95%: [{ic_lower:.3f}, {ic_upper:.3f}]")
        
        # Benchmarks educacionais
        if abs(es) >= 0.4:
            capture_print(f"  ✓ BENCHMARK HATTIE: Acima do threshold (d≥0.4)")
        else:
            capture_print(f"  ⚠ BENCHMARK HATTIE: Abaixo do threshold (d<0.4)")
            
        if abs(es) >= 0.35:
            capture_print(f"  ✓ VOCABULÁRIO: Educacionalmente significativo (d≥0.35)")
        else:
            capture_print(f"  ⚠ VOCABULÁRIO: Abaixo do threshold educacional (d<0.35)")
    
    return df_comp_individual

# EXECUTAR TODAS AS ANÁLISES
capture_print("\n" + "="*80)
capture_print("INICIANDO ANÁLISES COMPLETAS")
capture_print("="*80)

# Executar a análise descritiva
df_resumo_grupos = analise_estatistica_vocabulario(df)

# Executar análise individual de mudança
capture_print("\n" + "="*70)
df_comp_individual, cat_mudanca_geral = analise_individual_mudanca(df)

# Executar análise contextualizada dos effect sizes
df_comp_contextualizada = analise_effect_size_contextualizada(df_comp_individual)

# Adicionar timestamp final
from datetime import datetime
capture_print(f"\n" + "="*80)
capture_print(f"ANÁLISE COMPLETA FINALIZADA")
capture_print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
capture_print(f"="*80)

# Restaurar stdout
sys.stdout = original_stdout

# Salvar toda a saída em arquivo de texto
output_txt_path = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'analise_completa_vocabulario_wordgen.txt')

with open(output_txt_path, 'w', encoding='utf-8') as f:
    f.write(output_buffer.getvalue())

print(f"\n" + "="*80)
print(f"ANÁLISE COMPLETA SALVA EM:")
print(f"{output_txt_path}")
print(f"="*80)

# Salvar também os CSVs
output_path = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'resumo_estatistico_vocabulario.csv')
df_resumo_grupos.to_csv(output_path, index=False)

output_individual = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'analise_individual_mudanca.csv')
df_comp_individual.to_csv(output_individual, index=False)

output_contextualizada = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'analise_effect_size_contextualizada.csv')
df_comp_contextualizada.to_csv(output_contextualizada, index=False)

output_categorias = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'categorias_mudanca.csv')
cat_mudanca_geral.to_csv(output_categorias)

print(f"\nArquivos salvos:")
print(f"• Relatório completo (TXT): {output_txt_path}")
print(f"• Resumo por grupo (CSV): {output_path}")
print(f"• Análise individual (CSV): {output_individual}")
print(f"• Effect sizes contextualizados (CSV): {output_contextualizada}")
print(f"• Categorias de mudança (CSV): {output_categorias}")

