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
output_csv = os.path.join(data_dir, 'tabela_bruta_fase3_TDE_wordgen.csv')
mapping_file = os.path.join(data_dir, 'RespostaTED.json')

# Caminhos dos arquivos TDE - CSV
arquivo_pre = os.path.join(pre_dir, 'DadosTDE.csv')
arquivo_pos = os.path.join(pos_dir, 'DadosTDE.csv')

print("="*80)
print("PIPELINE TDE - WORDGEN FASE 3")
print("="*80)
print(f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

def carregar_mapeamento_tde():
    """Carrega mapeamento das questões TDE"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mapeamento = {}
        for item in data:
            for pergunta_key, pergunta_data in item.items():
                if 'Pergunta' in pergunta_key:
                    numero = pergunta_key.split(' ')[1]
                    palavra = pergunta_data.get('Palavra Trabalhada', f'Palavra_{numero}')
                    mapeamento[f'P{numero}'] = palavra
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento: {e}")
        return {}

def converter_valor_tde(valor):
    """Converte valores TDE (0=erro, 1=acerto)"""
    if pd.isna(valor):
        return np.nan
    
    valor_str = str(valor).strip().upper()
    
    if valor_str in ['0', '0.0']:
        return 0
    elif valor_str in ['1', '1.0']:
        return 1
    else:
        try:
            num_valor = float(valor_str)
            return 1 if num_valor > 0 else 0
        except:
            return np.nan

def completar_dados_faltantes(df, nome_dataset):
    """
    Completa dados faltantes de Escola e/ou Turma para um aluno usando o registro mais próximo
    """
    print(f"   Verificando dados incompletos em {nome_dataset}...")
    registros_incompletos = 0
    registros_completados = 0
    
    for idx, row in df.iterrows():
        nome = str(row['Nome']).strip()
        escola_faltante = pd.isna(row['Escola']) or str(row['Escola']).strip() == '' or str(row['Escola']).strip().lower() == 'nan'
        turma_faltante = pd.isna(row['Turma']) or str(row['Turma']).strip() == '' or str(row['Turma']).strip().lower() == 'nan'
        
        if escola_faltante or turma_faltante:
            registros_incompletos += 1
            
            # Buscar registros do mesmo aluno com dados completos
            registros_mesmo_aluno = df[df['Nome'].str.strip() == nome]
            
            for _, reg_completo in registros_mesmo_aluno.iterrows():
                if reg_completo.name == idx:
                    continue
                    
                escola_completa = not (pd.isna(reg_completo['Escola']) or str(reg_completo['Escola']).strip() == '' or str(reg_completo['Escola']).strip().lower() == 'nan')
                turma_completa = not (pd.isna(reg_completo['Turma']) or str(reg_completo['Turma']).strip() == '' or str(reg_completo['Turma']).strip().lower() == 'nan')
                
                if escola_faltante and escola_completa:
                    df.at[idx, 'Escola'] = reg_completo['Escola']
                    registros_completados += 1
                    print(f"     Completado Escola para {nome}: {reg_completo['Escola']}")
                
                if turma_faltante and turma_completa:
                    df.at[idx, 'Turma'] = reg_completo['Turma']
                    registros_completados += 1
                    print(f"     Completado Turma para {nome}: {reg_completo['Turma']}")
                
                # Se ambos foram completados, parar a busca
                if not (escola_faltante and not escola_completa) and not (turma_faltante and not turma_completa):
                    break
    
    print(f"   {registros_incompletos} registros com dados incompletos encontrados")
    print(f"   {registros_completados} campos completados")
    return df

def remover_duplicados(df, nome_dataset):
    """
    Remove dados duplicados considerando Escola, Turma e Nome
    """
    print(f"   Verificando duplicados em {nome_dataset}...")
    len_inicial = len(df)
    
    # Identificar duplicados
    duplicados = df.duplicated(subset=['Escola', 'Turma', 'Nome'], keep='first')
    
    if duplicados.sum() > 0:
        print(f"     Encontrados {duplicados.sum()} registros duplicados:")
        for idx in df[duplicados].index:
            row = df.loc[idx]
            print(f"       - {row['Nome']} | {row['Escola']} | {row['Turma']}")
        
        # Remover duplicados
        df = df.drop_duplicates(subset=['Escola', 'Turma', 'Nome'], keep='first')
        print(f"     {len_inicial - len(df)} duplicados removidos")
    else:
        print(f"     Nenhum duplicado encontrado")
    
    return df

def verificar_questoes_validas(df, colunas_p, nome_dataset):
    """
    Remove registros que não possuem pelo menos 25% das questões (10 de 40)
    """
    print(f"   Verificando questões válidas em {nome_dataset}...")
    len_inicial = len(df)
    
    def tem_questoes_suficientes(row):
        questoes_validas = sum(1 for col in colunas_p if col in row.index and not pd.isna(row[col]) and str(row[col]).strip() != '')
        return questoes_validas >= 10  # Pelo menos 25% das questões (10 de 40)
    
    # Identificar registros com questões suficientes
    registros_validos = df.apply(tem_questoes_suficientes, axis=1)
    registros_invalidos = (~registros_validos).sum()
    
    if registros_invalidos > 0:
        print(f"     {registros_invalidos} registros com questões insuficientes encontrados")
        # Mostrar alguns exemplos
        for idx in df[~registros_validos].head(5).index:
            row = df.loc[idx]
            questoes_validas = sum(1 for col in colunas_p if col in row.index and not pd.isna(row[col]) and str(row[col]).strip() != '')
            print(f"       - {row['Nome']} | {row['Escola']} | {row['Turma']} | Questões: {questoes_validas}/40")
        
        # Remover registros inválidos
        df = df[registros_validos]
        print(f"     {len_inicial - len(df)} registros com questões insuficientes removidos")
    else:
        print(f"     Todos os registros possuem questões suficientes (≥25%)")
    
    return df

def classificar_grupo_tde(turma):
    """Classifica em Grupo A (6º/7º) ou B (8º/9º)"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
        return "Grupo A (6º/7º anos)"
    elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
        return "Grupo B (8º/9º anos)"
    else:
        return "Indefinido"

def main():
    """Pipeline principal TDE"""
    
    # 1. CARREGAR DADOS
    print("1. CARREGANDO DADOS...")
    df_pre = pd.read_csv(arquivo_pre)
    df_pos = pd.read_csv(arquivo_pos)
    mapeamento = carregar_mapeamento_tde()
    
    print(f"   PRÉ-teste: {len(df_pre)} registros")
    print(f"   PÓS-teste: {len(df_pos)} registros")
    print(f"   Mapeamento: {len(mapeamento)} questões")
    
    # 2. PRÉ-PROCESSAMENTO MELHORADO
    print("\n2. PRÉ-PROCESSAMENTO...")
    
    # Colunas TDE (P1 a P40)
    colunas_p = [f'P{i}' for i in range(1, 41)]
    
    # 2.1 Completar dados faltantes de Escola e/ou Turma
    print("\n2.1 COMPLETANDO DADOS FALTANTES...")
    df_pre = completar_dados_faltantes(df_pre, "PRÉ-teste")
    df_pos = completar_dados_faltantes(df_pos, "PÓS-teste")
    
    # 2.2 Remover duplicados
    print("\n2.2 REMOVENDO DUPLICADOS...")
    df_pre = remover_duplicados(df_pre, "PRÉ-teste")
    df_pos = remover_duplicados(df_pos, "PÓS-teste")
    
    # 2.3 Converter valores
    print("\n2.3 CONVERTENDO VALORES DAS QUESTÕES...")
    for col in colunas_p:
        if col in df_pre.columns:
            df_pre[col] = df_pre[col].apply(converter_valor_tde)
        if col in df_pos.columns:
            df_pos[col] = df_pos[col].apply(converter_valor_tde)
    
    # 2.4 Verificar questões válidas (mínimo 25% = 10 questões)
    print("\n2.4 VERIFICANDO QUESTÕES VÁLIDAS...")
    df_pre = verificar_questoes_validas(df_pre, colunas_p, "PRÉ-teste")
    df_pos = verificar_questoes_validas(df_pos, colunas_p, "PÓS-teste")
    
    # 2.5 Classificar grupos
    print("\n2.5 CLASSIFICANDO GRUPOS...")
    df_pre['GrupoTDE'] = df_pre['Turma'].apply(classificar_grupo_tde)
    df_pos['GrupoTDE'] = df_pos['Turma'].apply(classificar_grupo_tde)
    
    # 2.6 ID único
    print("\n2.6 CRIANDO IDs ÚNICOS...")
    df_pre['ID_Unico'] = df_pre['Nome'].astype(str) + "_" + df_pre['Escola'].astype(str) + "_" + df_pre['Turma'].astype(str)
    df_pos['ID_Unico'] = df_pos['Nome'].astype(str) + "_" + df_pos['Escola'].astype(str) + "_" + df_pos['Turma'].astype(str)
    
    # 2.7 Verificar presença em ambos os testes (PRÉ e PÓS)
    print("\n2.7 VERIFICANDO PRESENÇA EM AMBOS OS TESTES...")
    ids_pre = set(df_pre['ID_Unico'])
    ids_pos = set(df_pos['ID_Unico'])
    ids_comuns = ids_pre.intersection(ids_pos)
    
    print(f"   IDs no PRÉ-teste: {len(ids_pre)}")
    print(f"   IDs no PÓS-teste: {len(ids_pos)}")
    print(f"   IDs em ambos os testes: {len(ids_comuns)}")
    print(f"   IDs apenas no PRÉ: {len(ids_pre - ids_pos)}")
    print(f"   IDs apenas no PÓS: {len(ids_pos - ids_pre)}")
    
    # Mostrar alguns exemplos de registros que serão removidos
    if len(ids_pre - ids_pos) > 0:
        print("     Exemplos de registros apenas no PRÉ-teste (serão removidos):")
        for id_exemplo in list(ids_pre - ids_pos)[:3]:
            nome_exemplo = df_pre[df_pre['ID_Unico'] == id_exemplo]['Nome'].iloc[0]
            escola_exemplo = df_pre[df_pre['ID_Unico'] == id_exemplo]['Escola'].iloc[0]
            turma_exemplo = df_pre[df_pre['ID_Unico'] == id_exemplo]['Turma'].iloc[0]
            print(f"       - {nome_exemplo} | {escola_exemplo} | {turma_exemplo}")
    
    if len(ids_pos - ids_pre) > 0:
        print("     Exemplos de registros apenas no PÓS-teste (serão removidos):")
        for id_exemplo in list(ids_pos - ids_pre)[:3]:
            nome_exemplo = df_pos[df_pos['ID_Unico'] == id_exemplo]['Nome'].iloc[0]
            escola_exemplo = df_pos[df_pos['ID_Unico'] == id_exemplo]['Escola'].iloc[0]
            turma_exemplo = df_pos[df_pos['ID_Unico'] == id_exemplo]['Turma'].iloc[0]
            print(f"       - {nome_exemplo} | {escola_exemplo} | {turma_exemplo}")
    
    # Filtrar apenas registros presentes em ambos os testes
    df_pre = df_pre[df_pre['ID_Unico'].isin(ids_comuns)]
    df_pos = df_pos[df_pos['ID_Unico'].isin(ids_comuns)]
    
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
        score_pre = sum(row_pre[col] for col in colunas_p if not pd.isna(row_pre[col]))
        score_pos = sum(row_pos[col] for col in colunas_p if not pd.isna(row_pos[col]))
        questoes_validas = sum(1 for col in colunas_p if not pd.isna(row_pre[col]) and not pd.isna(row_pos[col]))
        
        # Registro base
        registro = {
            'ID_Unico': id_unico,
            'Nome': row_pre['Nome'],
            'Escola': row_pre.get('Escola', 'N/A'),
            'Turma': row_pre['Turma'],
            'GrupoTDE': row_pre['GrupoTDE'],
            'Score_Pre': score_pre,
            'Score_Pos': score_pos,
            'Delta_Score': score_pos - score_pre,
            'Questoes_Validas': questoes_validas,
            'Percentual_Pre': (score_pre / questoes_validas) * 100 if questoes_validas > 0 else 0,
            'Percentual_Pos': (score_pos / questoes_validas) * 100 if questoes_validas > 0 else 0
        }
        
        # Questões individuais
        for i, col in enumerate(colunas_p, 1):
            palavra = mapeamento.get(col, f"Palavra_P{i}")
            registro[f'P{i:02d}_Pre_{palavra}'] = row_pre[col] if not pd.isna(row_pre[col]) else ''
            registro[f'P{i:02d}_Pos_{palavra}'] = row_pos[col] if not pd.isna(row_pos[col]) else ''
            registro[f'P{i:02d}_Delta_{palavra}'] = (row_pos[col] - row_pre[col]) if (not pd.isna(row_pre[col]) and not pd.isna(row_pos[col])) else ''
        
        tabela_bruta.append(registro)
    
    df_tabela = pd.DataFrame(tabela_bruta)
    
    # 4. ESTATÍSTICAS
    print("\n4. ESTATÍSTICAS DOS DADOS:")
    print("="*50)
    
    print(f"TOTAL DE ESTUDANTES: {len(df_tabela)}")
    print(f"TOTAL DE COLUNAS: {len(df_tabela.columns)}")
    
    print("\nPOR GRUPO TDE:")
    for grupo in df_tabela['GrupoTDE'].unique():
        if grupo != 'Indefinido':
            dados = df_tabela[df_tabela['GrupoTDE'] == grupo]
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
    print("✅ PIPELINE TDE CONCLUÍDO!")
    print("="*80)
    print(f"📁 Arquivo gerado: {output_csv}")
    print(f"📊 Registros: {len(df_tabela)}")
    print(f"📋 Colunas: {len(df_tabela.columns)}")
    print("="*80)
    
    return df_tabela

if __name__ == "__main__":
    main()
