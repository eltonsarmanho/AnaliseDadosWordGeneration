import pandas
import os
import sys
import pathlib
from scipy import stats
import numpy as np
from datetime import datetime
import io

# Adiciona o diretório atual ao sys.path para permitir importações relativas
current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
print(f"Diretório atual: {current_dir}")
current_dir = str(current_dir) + '/Data'
nome = "RESULTADOS_WordGen_TDE_Vocabulario_2024-1_Fase_3.xlsx"
arquivo_excel = os.path.join(current_dir, nome)
print(f"Arquivo Excel localizado: {arquivo_excel}")

# Buffer para capturar toda a saída
output_buffer = io.StringIO()
original_stdout = sys.stdout

def capture_print(*args, **kwargs):
    """Função para capturar prints tanto no console quanto no buffer"""
    print(*args, **kwargs, file=original_stdout)  # Console
    print(*args, **kwargs, file=output_buffer)    # Buffer

# Substituir print temporariamente
sys.stdout = output_buffer

# Iniciar relatório
capture_print("="*80)
capture_print("PIPELINE DE ANÁLISE - VOCABULÁRIO WORDGEN - ETAPA 3")
capture_print("BENCHMARKS EDUCACIONAIS ESPECÍFICOS")
capture_print("="*80)
capture_print(f"Data/Hora de execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
capture_print("="*80)

def interpretar_effect_size_benchmarks(effect_size):
    """
    Interpretação baseada em múltiplos benchmarks educacionais
    
    Referências:
    - Cohen (1988): Statistical Power Analysis for the Behavioral Sciences
    - Hattie (2009): Visible Learning: A Synthesis of Over 800 Meta-Analyses
    - Marulis & Neuman (2010): The effects of vocabulary intervention on young children's word learning
    """
    abs_es = abs(effect_size)
    
    # Classificação primária (Cohen)
    if abs_es < 0.2:
        cohen_categoria = "Trivial"
        cohen_descricao = "Diferença praticamente imperceptível"
    elif abs_es < 0.5:
        cohen_categoria = "Pequeno"
        cohen_descricao = "Detectável por observador treinado"
    elif abs_es < 0.8:
        cohen_categoria = "Médio"
        cohen_descricao = "Diferença visível ao olho nu"
    else:
        cohen_categoria = "Grande"
        cohen_descricao = "Diferença óbvia para qualquer pessoa"
    
    # Benchmark Hattie (2009) - Educação
    if abs_es >= 0.6:
        hattie_categoria = "Excelente"
        hattie_status = "✓✓"
        hattie_cor = "🟢"
    elif abs_es >= 0.4:
        hattie_categoria = "Bom Resultado"
        hattie_status = "✓"
        hattie_cor = "🟡"
    else:
        hattie_categoria = "Abaixo do Esperado"
        hattie_status = "⚠"
        hattie_cor = "🔴"
    
    # Benchmark Marulis & Neuman (2010) - Vocabulário
    if abs_es >= 0.50:
        vocabulario_categoria = "Substancial"
        vocabulario_status = "✓✓"
        vocabulario_cor = "🟢"
    elif abs_es >= 0.35:
        vocabulario_categoria = "Educacionalmente Significativo"
        vocabulario_status = "✓"
        vocabulario_cor = "🟡"
    else:
        vocabulario_categoria = "Não Significativo"
        vocabulario_status = "⚠"
        vocabulario_cor = "🔴"
    
    # Classificação final integrada
    if abs_es >= 0.6:
        classificacao_final = "EXCELENTE"
        impacto_educacional = "Transformador - resultado excepcional"
    elif abs_es >= 0.4:
        classificacao_final = "BOM"
        impacto_educacional = "Substancial - intervenção eficaz"
    elif abs_es >= 0.35:
        classificacao_final = "ADEQUADO"
        impacto_educacional = "Moderado - ganho educacional detectável"
    elif abs_es >= 0.2:
        classificacao_final = "MARGINAL"
        impacto_educacional = "Pequeno - ganho limitado"
    else:
        classificacao_final = "INSUFICIENTE"
        impacto_educacional = "Trivial - sem impacto prático"
    
    return {
        'effect_size': effect_size,
        'abs_effect_size': abs_es,
        'cohen_categoria': cohen_categoria,
        'cohen_descricao': cohen_descricao,
        'hattie_categoria': hattie_categoria,
        'hattie_status': hattie_status,
        'hattie_cor': hattie_cor,
        'vocabulario_categoria': vocabulario_categoria,
        'vocabulario_status': vocabulario_status,
        'vocabulario_cor': vocabulario_cor,
        'classificacao_final': classificacao_final,
        'impacto_educacional': impacto_educacional
    }

def apresentar_benchmarks():
    """Apresenta os frameworks teóricos dos benchmarks"""
    capture_print("\n1. FRAMEWORKS TEÓRICOS E BENCHMARKS")
    capture_print("-"*60)
    
    capture_print("COHEN (1988) - Statistical Power Analysis:")
    capture_print("  📊 Base científica: >100.000 citações")
    capture_print("  • d = 0.2: Pequeno (detectável por especialista)")
    capture_print("  • d = 0.5: Médio (visível ao olho nu)")
    capture_print("  • d = 0.8: Grande (óbvio para qualquer pessoa)")
    
    capture_print("\nHATTIE (2009) - Visible Learning (Educação):")
    capture_print("  📊 Base: 800+ meta-análises educacionais")
    capture_print("  • d ≥ 0.6: 🟢 Excelente resultado educacional")
    capture_print("  • d ≥ 0.4: 🟡 Bom resultado educacional (threshold)")
    capture_print("  • d < 0.4: 🔴 Abaixo do esperado para educação")
    
    capture_print("\nMARULIS & NEUMAN (2010) - Vocabulário Específico:")
    capture_print("  📊 Base: Meta-análise com 67 estudos de vocabulário")
    capture_print("  • d ≥ 0.50: 🟢 Substancial para vocabulário")
    capture_print("  • d ≥ 0.35: 🟡 Educacionalmente significativo")
    capture_print("  • d < 0.35: 🔴 Não significativo para vocabulário")

def analisar_com_benchmarks(cohen_d):
    """Análise detalhada com todos os benchmarks"""
    interpretacao = interpretar_effect_size_benchmarks(cohen_d)
    
    capture_print(f"\n2. ANÁLISE COM BENCHMARKS EDUCACIONAIS")
    capture_print("-"*60)
    
    capture_print(f"Effect Size observado: {interpretacao['effect_size']:.4f}")
    capture_print(f"Effect Size absoluto: {interpretacao['abs_effect_size']:.4f}")
    
    capture_print(f"\nCLASSIFICAÇÃO FINAL: {interpretacao['classificacao_final']}")
    capture_print(f"Impacto educacional: {interpretacao['impacto_educacional']}")
    
    capture_print(f"\nBENCHMARKS APLICADOS:")
    capture_print(f"┌─────────────────────────────────────────────────────────┐")
    capture_print(f"│ COHEN (1988)                                            │")
    capture_print(f"│ Categoria: {interpretacao['cohen_categoria']:<20} │")
    capture_print(f"│ Descrição: {interpretacao['cohen_descricao']:<35} │")
    capture_print(f"├─────────────────────────────────────────────────────────┤")
    capture_print(f"│ HATTIE (2009) - EDUCAÇÃO                               │")
    capture_print(f"│ Status: {interpretacao['hattie_cor']} {interpretacao['hattie_categoria']:<25} {interpretacao['hattie_status']:<5} │")
    capture_print(f"├─────────────────────────────────────────────────────────┤")
    capture_print(f"│ MARULIS & NEUMAN (2010) - VOCABULÁRIO                  │")
    capture_print(f"│ Status: {interpretacao['vocabulario_cor']} {interpretacao['vocabulario_categoria']:<25} {interpretacao['vocabulario_status']:<5} │")
    capture_print(f"└─────────────────────────────────────────────────────────┘")
    
    return interpretacao

def recomendacoes_baseadas_benchmarks(interpretacao):
    """Gerar recomendações baseadas nos benchmarks"""
    capture_print(f"\n3. RECOMENDAÇÕES BASEADAS EM EVIDÊNCIAS")
    capture_print("-"*60)
    
    classificacao = interpretacao['classificacao_final']
    effect_size = interpretacao['abs_effect_size']
    
    if classificacao == "EXCELENTE":
        capture_print("🎯 ESTRATÉGIA: MANUTENÇÃO E EXPANSÃO")
        capture_print("✅ Resultado excepcional - acima de todos os benchmarks")
        capture_print("📈 Ações recomendadas:")
        capture_print("   • Documentar e sistematizar a metodologia aplicada")
        capture_print("   • Replicar a intervenção em outros contextos")
        capture_print("   • Treinar outros educadores com base nesta experiência")
        capture_print("   • Publicar resultados como modelo de referência")
        
    elif classificacao == "BOM":
        capture_print("🎯 ESTRATÉGIA: OTIMIZAÇÃO E CONSOLIDAÇÃO")
        capture_print("✅ Bom resultado educacional - atende benchmark Hattie")
        capture_print("📈 Ações recomendadas:")
        capture_print("   • Manter a metodologia atual")
        capture_print("   • Buscar pequenos ajustes para alcançar d≥0.6")
        capture_print("   • Monitorar sustentabilidade dos ganhos")
        capture_print("   • Considerar intensificação da intervenção")
        
    elif classificacao == "ADEQUADO":
        capture_print("🎯 ESTRATÉGIA: INTENSIFICAÇÃO MODERADA")
        capture_print("⚠️ Resultado adequado para vocabulário, mas abaixo do ideal educacional")
        capture_print("📈 Ações recomendadas:")
        capture_print("   • Aumentar frequência ou duração da intervenção")
        capture_print("   • Adicionar componentes complementares")
        capture_print("   • Revisar adequação ao público-alvo")
        capture_print("   • Meta: alcançar d≥0.4 (benchmark Hattie)")
        
    elif classificacao == "MARGINAL":
        capture_print("🎯 ESTRATÉGIA: REVISÃO METODOLÓGICA")
        capture_print("⚠️ Ganho detectável mas insuficiente para impacto educacional")
        capture_print("📈 Ações recomendadas:")
        capture_print("   • Revisar fundamentação teórica da intervenção")
        capture_print("   • Avaliar adequação ao contexto e idade")
        capture_print("   • Considerar mudanças metodológicas significativas")
        capture_print("   • Investigar fatores contextuais limitantes")
        
    else:  # INSUFICIENTE
        capture_print("🎯 ESTRATÉGIA: REFORMULAÇÃO COMPLETA")
        capture_print("❌ Resultado insuficiente - sem impacto educacional detectável")
        capture_print("📈 Ações recomendadas:")
        capture_print("   • Reformular completamente a intervenção")
        capture_print("   • Revisar pressupostos teóricos")
        capture_print("   • Considerar intervenções alternativas")
        capture_print("   • Avaliar pré-requisitos e condições de implementação")
    
    # Comparação com literatura
    capture_print(f"\n4. CONTEXTO NA LITERATURA CIENTÍFICA")
    capture_print("-"*60)
    
    if effect_size >= 0.6:
        capture_print("📚 Seu resultado está no TOP 25% dos estudos educacionais")
        capture_print("🏆 Resultado comparável aos melhores programas de vocabulário")
        
    elif effect_size >= 0.4:
        capture_print("📚 Seu resultado está acima da média dos estudos educacionais")
        capture_print("👍 Resultado superior a muitos programas escolares padrão")
        
    elif effect_size >= 0.35:
        capture_print("📚 Seu resultado está na média dos estudos de vocabulário")
        capture_print("💡 Resultado típico de intervenções educacionais eficazes")
        
    elif effect_size >= 0.2:
        capture_print("📚 Seu resultado está abaixo da média desejável")
        capture_print("⚠️ Muitos estudos reportam efeitos maiores")
        
    else:
        capture_print("📚 Seu resultado está significativamente abaixo da literatura")
        capture_print("🔍 Revisão metodológica é altamente recomendada")

# Carregar dados
df_pre = pandas.read_excel(arquivo_excel, sheet_name='pre')
df_pos = pandas.read_excel(arquivo_excel, sheet_name='pos')

capture_print("Dados carregados com sucesso.")

# Verificar IDs em comum entre df_pre e df_pos
ids_pre = set(df_pre['id'])
ids_pos = set(df_pos['id'])
ids_comuns = ids_pre.intersection(ids_pos)

capture_print(f"\nVERIFICAÇÃO DOS DADOS:")
capture_print(f"Total de IDs em df_pre: {len(ids_pre)}")
capture_print(f"Total de IDs em df_pos: {len(ids_pos)}")
capture_print(f"IDs em comum: {len(ids_comuns)}")

# Filtrar os DataFrames para manter apenas os IDs em comum
df_pre_filtrado = df_pre[df_pre['id'].isin(ids_comuns)]
df_pos_filtrado = df_pos[df_pos['id'].isin(ids_comuns)]

capture_print(f"\nApós filtrar por IDs em comum:")
capture_print(f"Registros em df_pre_filtrado: {len(df_pre_filtrado)}")
capture_print(f"Registros em df_pos_filtrado: {len(df_pos_filtrado)}")

# Descrição estatística dos dados
capture_print("\n" + "="*60)
capture_print("DESCRIÇÃO ESTATÍSTICA - PRÉ-INTERVENÇÃO")
capture_print("="*60)
capture_print(df_pre_filtrado.describe())

capture_print("\n" + "="*60)
capture_print("DESCRIÇÃO ESTATÍSTICA - PÓS-INTERVENÇÃO")
capture_print("="*60)
capture_print(df_pos_filtrado.describe())

# Análise das perguntas Q1 a Q40
colunas_interesse = [col for col in df_pre_filtrado.columns if col.startswith('Q') or 'Score' in col or 'score' in col]

if colunas_interesse:
    # Separar colunas Q (booleanas) das colunas Score
    colunas_q = [col for col in colunas_interesse if col.startswith('Q')]
    colunas_score = [col for col in colunas_interesse if 'Score' in col or 'score' in col]
    
    # Converter colunas Q para booleano
    df_pre_bool = df_pre_filtrado[colunas_q].copy()
    df_pos_bool = df_pos_filtrado[colunas_q].copy()
    
    for col in colunas_q:
        df_pre_bool[col] = pandas.to_numeric(df_pre_filtrado[col], errors='coerce').fillna(0)
        df_pos_bool[col] = pandas.to_numeric(df_pos_filtrado[col], errors='coerce').fillna(0)
        df_pre_bool[col] = (df_pre_bool[col] > 0).astype(int)
        df_pos_bool[col] = (df_pos_bool[col] > 0).astype(int)
    
    # capture_print("\n" + "="*60)
    # capture_print("ANÁLISE ESTATÍSTICA - PERGUNTAS BOOLEANAS (PRÉ)")
    # capture_print("="*60)
    # capture_print("Proporção de acertos por pergunta:")
    # capture_print(df_pre_bool.mean().round(3))
    # capture_print("\nTotal de acertos por pergunta:")
    # capture_print(df_pre_bool.sum())
    # capture_print(f"\nTotal de participantes: {len(df_pre_bool)}")
    
    # capture_print("\n" + "="*60)
    # capture_print("ANÁLISE ESTATÍSTICA - PERGUNTAS BOOLEANAS (PÓS)")
    # capture_print("="*60)
    # capture_print("Proporção de acertos por pergunta:")
    # capture_print(df_pos_bool.mean().round(3))
    # capture_print("\nTotal de acertos por pergunta:")
    # capture_print(df_pos_bool.sum())
    # capture_print(f"\nTotal de participantes: {len(df_pos_bool)}")
    
    # Análise dos Scores
    if colunas_score:
        capture_print("\n" + "="*60)
        capture_print("DESCRIÇÃO ESTATÍSTICA - SCORE FINAL")
        capture_print("="*60)
        capture_print("PRÉ-INTERVENÇÃO:")
        capture_print(df_pre_filtrado[colunas_score].describe())
        capture_print("\nPÓS-INTERVENÇÃO:")
        capture_print(df_pos_filtrado[colunas_score].describe())
    
    # Comparação geral de desempenho
    df_pre_bool_sorted = df_pre_bool.set_index(df_pre_filtrado['id']).sort_index()
    df_pos_bool_sorted = df_pos_bool.set_index(df_pos_filtrado['id']).sort_index()
    
    acertos_pre = df_pre_bool_sorted.sum(axis=1)
    acertos_pos = df_pos_bool_sorted.sum(axis=1)
    
    capture_print("\n" + "="*60)
    capture_print("COMPARAÇÃO DE DESEMPENHO GERAL")
    capture_print("="*60)
    capture_print(f"Média de acertos PRÉ: {acertos_pre.mean():.2f} ± {acertos_pre.std():.2f}")
    capture_print(f"Média de acertos PÓS: {acertos_pos.mean():.2f} ± {acertos_pos.std():.2f}")
    capture_print(f"Diferença média: {(acertos_pos.mean() - acertos_pre.mean()):.2f}")
    
    # Apresentar benchmarks teóricos
    apresentar_benchmarks()
    
    # TESTES ESTATÍSTICOS
    capture_print("\n" + "="*80)
    capture_print("TESTES ESTATÍSTICOS COMPARATIVOS")
    capture_print("="*80)
    
    # 1. Teste de normalidade e teste pareado
    try:
        stat_pre, p_pre = stats.shapiro(acertos_pre)
        stat_pos, p_pos = stats.shapiro(acertos_pos)
        
        capture_print(f"Teste de Normalidade (Shapiro-Wilk):")
        capture_print(f"PRÉ - p-value = {p_pre:.6f}")
        capture_print(f"PÓS - p-value = {p_pos:.6f}")
        
        if p_pre > 0.05 and p_pos > 0.05:
            t_stat, p_value = stats.ttest_rel(acertos_pos, acertos_pre)
            capture_print(f"\nTeste t pareado (dados normais):")
            capture_print(f"t-statistic: {t_stat:.4f}")
            capture_print(f"p-value: {p_value:.6f}")
        else:
            w_stat, p_value = stats.wilcoxon(acertos_pos, acertos_pre, alternative='greater')
            capture_print(f"\nTeste Wilcoxon (dados não-normais):")
            capture_print(f"W-statistic: {w_stat:.4f}")
            capture_print(f"p-value: {p_value:.6f}")
        
        alpha = 0.05
        if p_value < alpha:
            capture_print(f"\n✓ RESULTADO: Há melhora estatisticamente significativa (p < {alpha})")
        else:
            capture_print(f"\n✗ RESULTADO: Não há melhora estatisticamente significativa (p >= {alpha})")
            
    except Exception as e:
        capture_print(f"Erro no teste estatístico: {e}")
    
    # 2. Cálculo do Cohen's d corrigido
    try:
        diferenca = acertos_pos - acertos_pre
        # Cohen's d corrigido: usar desvio padrão pooled
        pooled_std = np.sqrt((acertos_pre.var() + acertos_pos.var()) / 2)
        cohen_d = diferenca.mean() / pooled_std
        
        capture_print(f"\n" + "="*80)
        capture_print("CÁLCULO DO EFFECT SIZE (COHEN'S d)")
        capture_print("="*80)
        capture_print(f"Diferença média: {diferenca.mean():.4f}")
        capture_print(f"Desvio padrão pooled: {pooled_std:.4f}")
        capture_print(f"Cohen's d: {cohen_d:.4f}")
        
        # Análise com benchmarks educacionais
        interpretacao = analisar_com_benchmarks(cohen_d)
        
        # Gerar recomendações
        recomendacoes_baseadas_benchmarks(interpretacao)
        
    except Exception as e:
        capture_print(f"Erro no cálculo do Cohen's d: {e}")
    
    # 3. Análise de melhora individual
    melhoraram = (acertos_pos > acertos_pre).sum()
    pioraram = (acertos_pos < acertos_pre).sum()
    mantiveram = (acertos_pos == acertos_pre).sum()
    
    capture_print(f"\n" + "="*60)
    capture_print("ANÁLISE INDIVIDUAL DE MUDANÇA")
    capture_print("="*60)
    capture_print(f"Participantes que melhoraram: {melhoraram} ({melhoraram/len(acertos_pre)*100:.1f}%)")
    capture_print(f"Participantes que pioraram: {pioraram} ({pioraram/len(acertos_pre)*100:.1f}%)")
    capture_print(f"Participantes que mantiveram: {mantiveram} ({mantiveram/len(acertos_pre)*100:.1f}%)")
    
    # 4. Análise por pergunta
    capture_print(f"\n" + "="*60)
    capture_print("MELHORA POR PERGUNTA")
    capture_print("="*60)
    melhora_por_pergunta = df_pos_bool_sorted.mean() - df_pre_bool_sorted.mean()
    melhora_por_pergunta_sorted = melhora_por_pergunta.sort_values(ascending=False)
    
    capture_print("Top 10 perguntas com maior melhora:")
    for i, (pergunta, melhora) in enumerate(melhora_por_pergunta_sorted.head(10).items(), 1):
        capture_print(f"{i:2d}. {pergunta}: +{melhora:.3f} ({melhora*100:.1f}%)")
    
    capture_print("\nTop 5 perguntas com menor melhora (ou piora):")
    for i, (pergunta, melhora) in enumerate(melhora_por_pergunta_sorted.tail(5).items(), 1):
        capture_print(f"{i:2d}. {pergunta}: {melhora:+.3f} ({melhora*100:+.1f}%)")

# Referências científicas
capture_print(f"\n" + "="*80)
capture_print("REFERÊNCIAS CIENTÍFICAS")
capture_print("="*80)
capture_print("Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.).")
capture_print("Lawrence Erlbaum Associates.")
capture_print("")
capture_print("Hattie, J. (2009). Visible Learning: A Synthesis of Over 800 Meta-Analyses")
capture_print("Relating to Achievement. Routledge.")
capture_print("")
capture_print("Marulis, L. M., & Neuman, S. B. (2010). The effects of vocabulary intervention")
capture_print("on young children's word learning: A meta-analysis. Review of Educational")
capture_print("Research, 80(3), 300-335.")

# Timestamp final
capture_print(f"\n" + "="*80)
capture_print(f"PIPELINE DE ANÁLISE ETAPA 3 FINALIZADA")
capture_print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
capture_print(f"="*80)

# Restaurar stdout
sys.stdout = original_stdout

# Salvar arquivo TXT
output_txt_path = os.path.join(str(pathlib.Path(__file__).parent.parent.parent.resolve()) + '/Data', 'pipeline_vocabulario_wordgen_etapa3_fase3.txt')

with open(output_txt_path, 'w', encoding='utf-8') as f:
    f.write(output_buffer.getvalue())

print(f"\n" + "="*80)
print(f"ETAPA 3 - ANÁLISE COM BENCHMARKS EDUCACIONAIS SALVA EM:")
print(f"{output_txt_path}")
print(f"="*80)

print(f"\nArquivos gerados:")
print(f"• Relatório completo ETAPA 3 (TXT): {output_txt_path}")
print(f"\nAnálise concluída com benchmarks educacionais específicos!")