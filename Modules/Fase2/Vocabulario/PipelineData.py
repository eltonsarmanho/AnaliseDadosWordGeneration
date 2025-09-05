import pandas as pd
import os
import sys
import pathlib
from scipy import stats
import numpy as np
from datetime import datetime
import io
import json

# Adiciona o diretório atual ao sys.path para permitir importações relativas
current_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
print(f"Diretório atual: {current_dir}")
data_dir = str(current_dir) + '/Data'

# Caminhos dos arquivos
arquivo_pre = os.path.join(data_dir, 'Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.xlsx')
arquivo_pos = os.path.join(data_dir, 'Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).xlsx')
arquivo_respostas = os.path.join(data_dir, 'RespostaVocabulario.json')

print(f"Arquivo PRÉ localizado: {arquivo_pre}")
print(f"Arquivo PÓS localizado: {arquivo_pos}")
print(f"Arquivo Respostas localizado: {arquivo_respostas}")

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
capture_print("PIPELINE DE ANÁLISE - VOCABULÁRIO WORDGEN - FASE 2")
capture_print("ANÁLISE POR GRUPOS ETÁRIOS COM BENCHMARKS EDUCACIONAIS")
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

def analisar_com_benchmarks(cohen_d, grupo_nome=""):
    """Análise detalhada com todos os benchmarks"""
    interpretacao = interpretar_effect_size_benchmarks(cohen_d)
    
    capture_print(f"\n2. ANÁLISE COM BENCHMARKS EDUCACIONAIS - {grupo_nome}")
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

def carregar_mapeamento_palavras():
    """Carrega o mapeamento de questões para palavras trabalhadas"""
    try:
        with open(arquivo_respostas, 'r', encoding='utf-8') as f:
            dados_respostas = json.load(f)
        
        mapeamento = {}
        for item in dados_respostas:
            for questao, info in item.items():
                mapeamento[questao] = info['Palavra Trabalhada']
        
        return mapeamento
    except Exception as e:
        capture_print(f"Erro ao carregar mapeamento de palavras: {e}")
        return {}

def converter_valor_questao(valor):
    """Converte valores das questões para sistema numérico"""
    if pd.isna(valor):
        return np.nan
    
    # Converter para string para manipulação
    valor_str = str(valor).strip().upper()
    
    # Valores conhecidos
    if valor_str in ['0', '0.0']:
        return 0  # Erro
    elif valor_str in ['1', '1.0']:
        return 1  # Acerto parcial
    elif valor_str in ['2', '2.0']:
        return 2  # Acerto total
    elif valor_str in ['D', 'M']:
        return np.nan  # Neutro (valores desconhecidos)
    else:
        # Tentar converter para número
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
    """Classifica estudantes em grupos etários baseado na turma"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
        return "6º/7º anos"
    elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
        return "8º/9º anos"
    else:
        return "Indefinido"

# Carregar dados
capture_print("CARREGANDO DADOS...")
df_pre = pd.read_excel(arquivo_pre)
df_pos = pd.read_excel(arquivo_pos)

# Carregar mapeamento de palavras
mapeamento_palavras = carregar_mapeamento_palavras()
capture_print(f"Mapeamento de palavras carregado: {len(mapeamento_palavras)} questões")

# Preparar dados
capture_print("INICIANDO LIMPEZA DOS DADOS...")

# Converter colunas Q1-Q50 para valores numéricos
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

# Criar identificador único baseado em Nome + Turma (para lidar com homônimos)
df_pre['ID_Unico'] = df_pre['Nome'].astype(str) + "_" + df_pre['Turma'].astype(str)
df_pos['ID_Unico'] = df_pos['Nome'].astype(str) + "_" + df_pos['Turma'].astype(str)

# Filtrar apenas estudantes que participaram de ambos os testes
ids_pre = set(df_pre['ID_Unico'])
ids_pos = set(df_pos['ID_Unico'])
ids_comuns = ids_pre.intersection(ids_pos)

capture_print(f"Total de IDs em PRÉ: {len(ids_pre)}")
capture_print(f"Total de IDs em PÓS: {len(ids_pos)}")
capture_print(f"IDs em comum: {len(ids_comuns)}")

# Filtrar DataFrames
df_pre_filtrado = df_pre[df_pre['ID_Unico'].isin(ids_comuns)].copy()
df_pos_filtrado = df_pos[df_pos['ID_Unico'].isin(ids_comuns)].copy()

# Função para verificar questões válidas
def tem_questoes_validas(row, colunas_q):
    valores_validos = 0
    for col in colunas_q:
        if col in row.index and not pd.isna(row[col]):
            valores_validos += 1
    return valores_validos >= 40  # Pelo menos 80% das questões preenchidas

# Aplicar filtro de questões válidas
mask_pre = df_pre_filtrado.apply(lambda row: tem_questoes_validas(row, colunas_q), axis=1)
mask_pos = df_pos_filtrado.apply(lambda row: tem_questoes_validas(row, colunas_q), axis=1)

df_pre_filtrado = df_pre_filtrado[mask_pre]
df_pos_filtrado = df_pos_filtrado[mask_pos]

# Filtrar novamente por IDs comuns após limpeza
ids_pre_limpo = set(df_pre_filtrado['ID_Unico'])
ids_pos_limpo = set(df_pos_filtrado['ID_Unico'])
ids_finais = ids_pre_limpo.intersection(ids_pos_limpo)

df_pre_final = df_pre_filtrado[df_pre_filtrado['ID_Unico'].isin(ids_finais)]
df_pos_final = df_pos_filtrado[df_pos_filtrado['ID_Unico'].isin(ids_finais)]

capture_print(f"Após limpeza completa:")
capture_print(f"Registros PRÉ: {len(df_pre_final)}")
capture_print(f"Registros PÓS: {len(df_pos_final)}")
capture_print(f"IDs finais: {len(ids_finais)}")

# Verificar distribuição dos grupos
capture_print(f"\nDISTRIBUIÇÃO DOS GRUPOS ETÁRIOS:")
grupos_pre = df_pre_final['GrupoEtario'].value_counts()
grupos_pos = df_pos_final['GrupoEtario'].value_counts()

for grupo in grupos_pre.index:
    capture_print(f"{grupo}: PRÉ={grupos_pre[grupo]}, PÓS={grupos_pos.get(grupo, 0)}")

# Apresentar benchmarks teóricos
apresentar_benchmarks()

# Função para analisar um grupo específico
def analisar_grupo(df_pre_grupo, df_pos_grupo, grupo_nome):
    """Analisa um grupo específico de estudantes"""
    capture_print(f"\n" + "="*80)
    capture_print(f"ANÁLISE DO GRUPO: {grupo_nome}")
    capture_print("="*80)
    
    if len(df_pre_grupo) == 0:
        capture_print(f"Nenhum dado disponível para o grupo {grupo_nome}")
        return {'grupo': grupo_nome, 'n_estudantes': 0}
    
    capture_print(f"Total de estudantes: {len(df_pre_grupo)}")
    
    # Calcular pontuação total para cada estudante
    scores_pre = []
    scores_pos = []
    
    for _, row_pre in df_pre_grupo.iterrows():
        id_unico = row_pre['ID_Unico']
        
        # Encontrar correspondente no pós-teste
        pos_rows = df_pos_grupo[df_pos_grupo['ID_Unico'] == id_unico]
        if len(pos_rows) == 0:
            continue
            
        row_pos = pos_rows.iloc[0]
        
        # Calcular scores
        score_pre = 0
        score_pos = 0
        questoes_validas = 0
        
        for col in colunas_q:
            if col in df_pre_grupo.columns and col in df_pos_grupo.columns:
                val_pre = row_pre[col]
                val_pos = row_pos[col]
                
                if not pd.isna(val_pre) and not pd.isna(val_pos):
                    score_pre += val_pre
                    score_pos += val_pos
                    questoes_validas += 1
        
        if questoes_validas >= 40:  # Pelo menos 80% das questões
            scores_pre.append(score_pre)
            scores_pos.append(score_pos)
    
    if len(scores_pre) == 0:
        capture_print("Nenhum estudante com dados válidos suficientes")
        return {'grupo': grupo_nome, 'n_estudantes': 0}
    
    scores_pre = np.array(scores_pre)
    scores_pos = np.array(scores_pos)
    
    capture_print(f"Estudantes com dados válidos: {len(scores_pre)}")
    capture_print(f"Score médio PRÉ: {scores_pre.mean():.2f} ± {scores_pre.std():.2f}")
    capture_print(f"Score médio PÓS: {scores_pos.mean():.2f} ± {scores_pos.std():.2f}")
    capture_print(f"Diferença média: {(scores_pos.mean() - scores_pre.mean()):.2f}")
    
    # Teste estatístico
    cohen_d = 0
    p_value = 1
    
    if len(scores_pre) > 3:
        try:
            # Verificar normalidade
            _, p_pre = stats.shapiro(scores_pre)
            _, p_pos = stats.shapiro(scores_pos)
            
            if p_pre > 0.05 and p_pos > 0.05:
                t_stat, p_value = stats.ttest_rel(scores_pos, scores_pre)
                capture_print(f"Teste t pareado: t={t_stat:.4f}, p={p_value:.6f}")
            else:
                w_stat, p_value = stats.wilcoxon(scores_pos, scores_pre, alternative='greater')
                capture_print(f"Teste Wilcoxon: W={w_stat:.4f}, p={p_value:.6f}")
            
            # Cohen's d
            diferenca = scores_pos - scores_pre
            pooled_std = np.sqrt((scores_pre.var() + scores_pos.var()) / 2)
            cohen_d = diferenca.mean() / pooled_std if pooled_std > 0 else 0
            
            capture_print(f"Cohen's d: {cohen_d:.4f}")
            
            # Análise com benchmarks
            analisar_com_benchmarks(cohen_d, grupo_nome)
            
            # Significância estatística
            if p_value < 0.05:
                capture_print(f"✓ Melhora estatisticamente significativa (p < 0.05)")
            else:
                capture_print(f"✗ Melhora não significativa estatisticamente (p >= 0.05)")
                
        except Exception as e:
            capture_print(f"Erro na análise estatística: {e}")
    
    # Análise por palavra/questão
    capture_print(f"\n--- ANÁLISE POR PALAVRA/QUESTÃO - {grupo_nome} ---")
    
    resultados_palavras = []
    
    for col in colunas_q:
        if col in df_pre_grupo.columns and col in df_pos_grupo.columns:
            palavra = mapeamento_palavras.get(col, f"Palavra_{col}")
            
            # Filtrar valores válidos
            valores_pre = df_pre_grupo[col].dropna()
            valores_pos = df_pos_grupo[col].dropna()
            
            if len(valores_pre) > 0 and len(valores_pos) > 0:
                # Taxa de acerto (considerando 1 e 2 como acertos)
                acertos_pre = (valores_pre >= 1).sum()
                acertos_pos = (valores_pos >= 1).sum()
                
                taxa_pre = acertos_pre / len(valores_pre)
                taxa_pos = acertos_pos / len(valores_pos)
                
                # Distribuição de erros
                erros_pre = (valores_pre == 0).sum()
                erros_pos = (valores_pos == 0).sum()
                
                melhora = taxa_pos - taxa_pre
                
                resultados_palavras.append({
                    'Questao': col,
                    'Palavra': palavra,
                    'Taxa_Pre': taxa_pre,
                    'Taxa_Pos': taxa_pos,
                    'Melhora': melhora,
                    'Erros_Pre': erros_pre,
                    'Erros_Pos': erros_pos
                })
    
    # Ordenar por melhora
    resultados_palavras.sort(key=lambda x: x['Melhora'], reverse=True)
    
    capture_print("Top 10 palavras com maior melhora:")
    for i, resultado in enumerate(resultados_palavras[:10], 1):
        capture_print(f"{i:2d}. {resultado['Palavra']:<15} ({resultado['Questao']}): "
                     f"Pré={resultado['Taxa_Pre']:.3f} → Pós={resultado['Taxa_Pos']:.3f} "
                     f"(+{resultado['Melhora']:+.3f})")
    
    capture_print("\nTop 5 palavras com menor melhora:")
    for i, resultado in enumerate(resultados_palavras[-5:], 1):
        capture_print(f"{i:2d}. {resultado['Palavra']:<15} ({resultado['Questao']}): "
                     f"Pré={resultado['Taxa_Pre']:.3f} → Pós={resultado['Taxa_Pos']:.3f} "
                     f"({resultado['Melhora']:+.3f})")
    
    return {
        'grupo': grupo_nome,
        'n_estudantes': len(scores_pre),
        'score_pre_media': scores_pre.mean() if len(scores_pre) > 0 else 0,
        'score_pos_media': scores_pos.mean() if len(scores_pos) > 0 else 0,
        'cohen_d': cohen_d,
        'p_value': p_value,
        'palavras_resultados': resultados_palavras
    }

# Analisar cada grupo
resultados_grupos = []

for grupo in ["6º/7º anos", "8º/9º anos"]:
    df_pre_grupo = df_pre_final[df_pre_final['GrupoEtario'] == grupo]
    df_pos_grupo = df_pos_final[df_pos_final['GrupoEtario'] == grupo]
    
    resultado = analisar_grupo(df_pre_grupo, df_pos_grupo, grupo)
    resultados_grupos.append(resultado)

# Comparação intergrupos
capture_print(f"\n" + "="*80)
capture_print("COMPARAÇÃO INTERGRUPOS")
capture_print("="*80)

if len(resultados_grupos) >= 2:
    grupo1 = resultados_grupos[0]
    grupo2 = resultados_grupos[1]
    
    capture_print(f"GRUPO {grupo1['grupo']}:")
    capture_print(f"  N = {grupo1['n_estudantes']}")
    capture_print(f"  Score PRÉ = {grupo1['score_pre_media']:.2f}")
    capture_print(f"  Score PÓS = {grupo1['score_pos_media']:.2f}")
    capture_print(f"  Cohen's d = {grupo1['cohen_d']:.4f}")
    
    capture_print(f"\nGRUPO {grupo2['grupo']}:")
    capture_print(f"  N = {grupo2['n_estudantes']}")
    capture_print(f"  Score PRÉ = {grupo2['score_pre_media']:.2f}")
    capture_print(f"  Score PÓS = {grupo2['score_pos_media']:.2f}")
    capture_print(f"  Cohen's d = {grupo2['cohen_d']:.4f}")
    
    # Comparar Cohen's d entre grupos
    diff_cohen = abs(grupo1['cohen_d'] - grupo2['cohen_d'])
    capture_print(f"\nDIFERENÇA NO EFFECT SIZE: {diff_cohen:.4f}")
    
    if grupo1['cohen_d'] > grupo2['cohen_d']:
        capture_print(f"Grupo {grupo1['grupo']} apresentou maior effect size")
    elif grupo2['cohen_d'] > grupo1['cohen_d']:
        capture_print(f"Grupo {grupo2['grupo']} apresentou maior effect size")
    else:
        capture_print("Ambos os grupos apresentaram effect size similar")

# Análise geral (todos os estudantes)
capture_print(f"\n" + "="*80)
capture_print("ANÁLISE GERAL - TODOS OS ESTUDANTES")
capture_print("="*80)

resultado_geral = analisar_grupo(df_pre_final, df_pos_final, "TODOS")

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
capture_print(f"PIPELINE DE ANÁLISE FASE 2 FINALIZADA")
capture_print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
capture_print(f"="*80)

# Restaurar stdout
sys.stdout = original_stdout

# Salvar arquivo TXT
output_txt_path = os.path.join(data_dir, 'pipeline_vocabulario_wordgen_fase2.txt')

with open(output_txt_path, 'w', encoding='utf-8') as f:
    f.write(output_buffer.getvalue())

print(f"\n" + "="*80)
print(f"FASE 2 - ANÁLISE POR GRUPOS ETÁRIOS SALVA EM:")
print(f"{output_txt_path}")
print(f"="*80)

print(f"\nArquivos gerados:")
print(f"• Relatório completo FASE 2 (TXT): {output_txt_path}")
print(f"\nAnálise concluída com separação por grupos etários e benchmarks educacionais!")