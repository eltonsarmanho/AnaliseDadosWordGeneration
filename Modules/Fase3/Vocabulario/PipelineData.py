import pandas as pd
import os
import sys
import pathlib
from scipy import stats
import numpy as np
from datetime import datetime
import json

# Configurar caminhos
current_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
data_dir = str(current_dir) + '/Data'
fase3_dir = os.path.join(data_dir, 'Fase 3')
pre_dir = os.path.join(fase3_dir, 'Pre')
pos_dir = os.path.join(fase3_dir, 'Pos')
output_csv = os.path.join(data_dir, 'tabela_bruta_fase3_vocabulario_wordgen.csv')
mapping_file = os.path.join(data_dir, 'RespostaVocabulario.json')

# Caminhos dos arquivos - CSV
arquivo_pre = os.path.join(pre_dir, 'DadosVocabulario.csv')
arquivo_pos = os.path.join(pos_dir, 'DadosVocabulario.csv')

print("="*80)
print("PIPELINE VOCABULÁRIO - WORDGEN FASE 3")
print("="*80)
print(f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

def carregar_mapeamento_vocabulario():
    """Carrega mapeamento das questões de vocabulário"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        mapeamento = {}
        for item in dados:
            for questao, info in item.items():
                mapeamento[questao] = info['Palavra Trabalhada']
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento: {e}")
        return {}

def converter_valor_vocabulario(valor):
    """Converte valores vocabulário (0=erro, 1=parcial, 2=acerto)"""
    if pd.isna(valor):
        return np.nan
    
    valor_str = str(valor).strip().upper()
    
    if valor_str in ['0', '0.0']:
        return 0
    elif valor_str in ['1', '1.0']:
        return 1
    elif valor_str in ['2', '2.0']:
        return 2
    else:
        try:
            num_valor = float(valor_str)
            if num_valor <= 0:
                return 0
            elif num_valor <= 1:
                return 1
            else:
                return 2
        except:
            return np.nan

def classificar_grupo_etario(turma):
    """Classifica em grupos etários"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
        return "6º/7º anos"
    elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
        return "8º/9º anos"
    else:
        return "Indefinido"

def main():
    """Pipeline principal Vocabulário"""
    
    # 1. CARREGAR DADOS
    print("1. CARREGANDO DADOS...")
    df_pre = pd.read_csv(arquivo_pre)
    df_pos = pd.read_csv(arquivo_pos)
    mapeamento = carregar_mapeamento_vocabulario()
    
    print(f"   PRÉ-teste: {len(df_pre)} registros")
    print(f"   PÓS-teste: {len(df_pos)} registros")
    print(f"   Mapeamento: {len(mapeamento)} questões")
    
    # 2. PRÉ-PROCESSAMENTO
    print("\n2. PRÉ-PROCESSAMENTO...")
    
    # Colunas vocabulário (Q1 a Q50)
    colunas_q = [f'Q{i}' for i in range(1, 51)]
    
    # Converter valores
    for col in colunas_q:
        if col in df_pre.columns:
            df_pre[col] = df_pre[col].apply(converter_valor_vocabulario)
        if col in df_pos.columns:
            df_pos[col] = df_pos[col].apply(converter_valor_vocabulario)
    
    # Classificar grupos
    df_pre['GrupoEtario'] = df_pre['Turma'].apply(classificar_grupo_etario)
    df_pos['GrupoEtario'] = df_pos['Turma'].apply(classificar_grupo_etario)
    
    # ID único
    df_pre['ID_Unico'] = df_pre['Nome'].astype(str) + "_" + df_pre['Turma'].astype(str)
    df_pos['ID_Unico'] = df_pos['Nome'].astype(str) + "_" + df_pos['Turma'].astype(str)
    
    # Filtrar IDs comuns
    ids_comuns = set(df_pre['ID_Unico']).intersection(set(df_pos['ID_Unico']))
    df_pre = df_pre[df_pre['ID_Unico'].isin(ids_comuns)]
    df_pos = df_pos[df_pos['ID_Unico'].isin(ids_comuns)]
    
    # Filtrar questões válidas (mínimo 40/50 = 80%)
    def tem_questoes_validas(row):
        validos = sum(1 for col in colunas_q if col in row.index and not pd.isna(row[col]))
        return validos >= 40
    
    df_pre = df_pre[df_pre.apply(tem_questoes_validas, axis=1)]
    df_pos = df_pos[df_pos.apply(tem_questoes_validas, axis=1)]
    
    # Filtrar novamente por IDs comuns
    ids_finais = set(df_pre['ID_Unico']).intersection(set(df_pos['ID_Unico']))
    df_pre = df_pre[df_pre['ID_Unico'].isin(ids_finais)]
    df_pos = df_pos[df_pos['ID_Unico'].isin(ids_finais)]
    
    print(f"   Registros finais: {len(df_pre)}")
    
    # 3. GERAR TABELA BRUTA
    print("\n3. GERANDO TABELA BRUTA...")
    
    df_pre = df_pre.sort_values('ID_Unico')
    df_pos = df_pos.sort_values('ID_Unico')
    
    tabela_bruta = []
    
    for _, row_pre in df_pre.iterrows():
        id_unico = row_pre['ID_Unico']
        row_pos = df_pos[df_pos['ID_Unico'] == id_unico].iloc[0]
        
        # Calcular scores
        score_pre = sum(row_pre[col] for col in colunas_q if not pd.isna(row_pre[col]))
        score_pos = sum(row_pos[col] for col in colunas_q if not pd.isna(row_pos[col]))
        questoes_validas = sum(1 for col in colunas_q if not pd.isna(row_pre[col]) and not pd.isna(row_pos[col]))
        
        # Registro base
        registro = {
            'ID_Unico': id_unico,
            'Nome': row_pre['Nome'],
            'Escola': row_pre.get('Escola', 'N/A'),
            'Turma': row_pre['Turma'],
            'GrupoEtario': row_pre['GrupoEtario'],
            'Score_Pre': score_pre,
            'Score_Pos': score_pos,
            'Delta_Score': score_pos - score_pre,
            'Questoes_Validas': questoes_validas,
            'Percentual_Pre': (score_pre / (questoes_validas * 2)) * 100 if questoes_validas > 0 else 0,  # Max = 2 por questão
            'Percentual_Pos': (score_pos / (questoes_validas * 2)) * 100 if questoes_validas > 0 else 0
        }
        
        # Questões individuais
        for i, col in enumerate(colunas_q, 1):
            palavra = mapeamento.get(col, f"Palavra_Q{i}")
            registro[f'Q{i:02d}_Pre_{palavra}'] = row_pre[col] if not pd.isna(row_pre[col]) else ''
            registro[f'Q{i:02d}_Pos_{palavra}'] = row_pos[col] if not pd.isna(row_pos[col]) else ''
            registro[f'Q{i:02d}_Delta_{palavra}'] = (row_pos[col] - row_pre[col]) if (not pd.isna(row_pre[col]) and not pd.isna(row_pos[col])) else ''
        
        tabela_bruta.append(registro)
    
    df_tabela = pd.DataFrame(tabela_bruta)
    
    # 4. ESTATÍSTICAS
    print("\n4. ESTATÍSTICAS DOS DADOS:")
    print("="*50)
    
    print(f"TOTAL DE ESTUDANTES: {len(df_tabela)}")
    print(f"TOTAL DE COLUNAS: {len(df_tabela.columns)}")
    
    print("\nPOR GRUPO ETÁRIO:")
    for grupo in df_tabela['GrupoEtario'].unique():
        if grupo != 'Indefinido':
            dados = df_tabela[df_tabela['GrupoEtario'] == grupo]
            print(f"  {grupo}:")
            print(f"    N: {len(dados)}")
            print(f"    Pré-teste: {dados['Score_Pre'].mean():.2f} ± {dados['Score_Pre'].std():.2f}")
            print(f"    Pós-teste: {dados['Score_Pos'].mean():.2f} ± {dados['Score_Pos'].std():.2f}")
            print(f"    Delta: {dados['Delta_Score'].mean():.2f} ± {dados['Delta_Score'].std():.2f}")
            
            # Teste t pareado
            t_stat, p_value = stats.ttest_rel(dados['Score_Pos'], dados['Score_Pre'])
            cohen_d = (dados['Score_Pos'].mean() - dados['Score_Pre'].mean()) / dados['Delta_Score'].std()
            print(f"    Teste t: t={t_stat:.3f}, p={p_value:.4f}")
            print(f"    Cohen's d: {cohen_d:.3f}")
    
    print("\nPOR ESCOLA:")
    for escola in df_tabela['Escola'].unique():
        if escola != 'N/A':
            dados = df_tabela[df_tabela['Escola'] == escola]
            print(f"  {escola}: N={len(dados)}, Δ={dados['Delta_Score'].mean():.2f}")
    
    print("\nPOR TURMA:")
    for turma in sorted(df_tabela['Turma'].unique()):
        dados = df_tabela[df_tabela['Turma'] == turma]
        print(f"  {turma}: N={len(dados)}, Δ={dados['Delta_Score'].mean():.2f}")
    
    # Estatísticas gerais
    print(f"\nESTATÍSTICAS GERAIS:")
    print(f"  Score Pré-teste: {df_tabela['Score_Pre'].mean():.2f} ± {df_tabela['Score_Pre'].std():.2f}")
    print(f"  Score Pós-teste: {df_tabela['Score_Pos'].mean():.2f} ± {df_tabela['Score_Pos'].std():.2f}")
    print(f"  Delta médio: {df_tabela['Delta_Score'].mean():.2f} ± {df_tabela['Delta_Score'].std():.2f}")
    
    # Teste t geral
    t_stat, p_value = stats.ttest_rel(df_tabela['Score_Pos'], df_tabela['Score_Pre'])
    cohen_d = (df_tabela['Score_Pos'].mean() - df_tabela['Score_Pre'].mean()) / df_tabela['Delta_Score'].std()
    print(f"  Teste t pareado: t={t_stat:.3f}, p={p_value:.4f}")
    print(f"  Cohen's d geral: {cohen_d:.3f}")
    
    # 5. SALVAR CSV
    print("\n5. SALVANDO TABELA...")
    df_tabela.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print("="*80)
    print("✅ PIPELINE VOCABULÁRIO CONCLUÍDO!")
    print("="*80)
    print(f"📁 Arquivo gerado: {output_csv}")
    print(f"📊 Registros: {len(df_tabela)}")
    print(f"📋 Colunas: {len(df_tabela.columns)}")
    print("="*80)
    
    return df_tabela

if __name__ == "__main__":
    main()
