import pandas as pd
import os
import sys
import pathlib
from scipy import stats
import numpy as np
from datetime import datetime
import io
import json

# Configurar caminhos
current_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
data_dir = str(current_dir) + '/Data'
fase2_dir = os.path.join(data_dir, 'Fase2')
pre_dir = os.path.join(fase2_dir, 'Pre')
pos_dir = os.path.join(fase2_dir, 'Pos')
output_csv = os.path.join(data_dir, 'tabela_bruta_fase2_TDE_wordgen.csv')
output_excel = os.path.join(data_dir, 'tabela_bruta_fase2_TDE_wordgen.xlsx')
mapping_file = os.path.join(data_dir, 'RespostaTED.json')

# Caminhos dos arquivos TDE
arquivo_pre = os.path.join(pre_dir, 'Avaliação TDE II - RelaçãoCompletaAlunos.xlsx')
arquivo_pos = os.path.join(pos_dir, 'Avaliação TDE II - RelaçãoCompletaAlunos.xlsx')

print("="*80)
print("PIPELINE TABELA BRUTA - TDE WORDGEN - FASE 2")
print("TESTE DE ESCRITA - ANÁLISE PRÉ/PÓS-TESTE")
print("="*80)
print(f"Data/Hora de execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

def carregar_mapeamento_palavras_tde():
    """Carrega o mapeamento das questões TDE para palavras"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Separar por grupos
        mapeamento_a = {}  # Grupo A (6º/7º anos)
        mapeamento_b = {}  # Grupo B (8º/9º anos)
        
        for item in data:
            for pergunta_key, pergunta_data in item.items():
                if 'Pergunta' in pergunta_key:
                    numero = pergunta_key.split(' ')[1]
                    palavra = pergunta_data.get('Palavra Trabalhada', f'Palavra_{numero}')
                    grupo = pergunta_data.get('Grupo', 'A')
                    
                    if grupo == 'A':
                        mapeamento_a[f'P{numero}'] = palavra
                    else:
                        mapeamento_b[f'P{numero}'] = palavra
        
        return mapeamento_a, mapeamento_b
    except Exception as e:
        print(f"Erro ao carregar mapeamento TDE: {e}")
        return {}, {}

def converter_valor_tde(valor):
    """Converte valores TDE para formato numérico padronizado"""
    if pd.isna(valor):
        return np.nan
    
    # Converter para string para manipulação
    valor_str = str(valor).strip().upper()
    
    # Para TDE, valores são geralmente 0 (erro) ou 1 (acerto)
    if valor_str in ['0', '0.0']:
        return 0  # Erro
    elif valor_str in ['1', '1.0']:
        return 1  # Acerto
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
            else:
                return np.nan
        except:
            return np.nan

def classificar_grupo_tde(turma):
    """Classifica estudantes em grupos TDE baseado na turma"""
    turma_str = str(turma).upper()
    
    if '6º' in turma_str or '6°' in turma_str or '7º' in turma_str or '7°' in turma_str:
        return "Grupo A (6º/7º anos)"
    elif '8º' in turma_str or '8°' in turma_str or '9º' in turma_str or '9°' in turma_str:
        return "Grupo B (8º/9º anos)"
    else:
        return "Indefinido"

def tem_questoes_validas_tde(row, colunas_p):
    """Verifica se o estudante tem pelo menos 60% das questões TDE respondidas"""
    valores_validos = 0
    for col in colunas_p:
        if col in row.index and not pd.isna(row[col]):
            valores_validos += 1
    return valores_validos >= 24  # Pelo menos 60% das 40 questões

def gerar_tabela_bruta_tde():
    """Gera tabela com dados brutos TDE após pré-processamento"""
    
    print("1. CARREGANDO DADOS TDE...")
    df_pre = pd.read_excel(arquivo_pre)
    df_pos = pd.read_excel(arquivo_pos)
    
    # Carregar mapeamento de palavras
    mapeamento_a, mapeamento_b = carregar_mapeamento_palavras_tde()
    print(f"   Mapeamento Grupo A carregado: {len(mapeamento_a)} questões")
    print(f"   Mapeamento Grupo B carregado: {len(mapeamento_b)} questões")
    
    print("2. APLICANDO PRÉ-PROCESSAMENTO TDE...")
    
    # Colunas das questões TDE (P1 a P40)
    colunas_p = [f'P{i}' for i in range(1, 41)]
    
    # Aplicar conversão de valores
    for col in colunas_p:
        if col in df_pre.columns:
            df_pre[col] = df_pre[col].apply(converter_valor_tde)
        if col in df_pos.columns:
            df_pos[col] = df_pos[col].apply(converter_valor_tde)
    
    # Adicionar grupos TDE
    df_pre['GrupoTDE'] = df_pre['Turma'].apply(classificar_grupo_tde)
    df_pos['GrupoTDE'] = df_pos['Turma'].apply(classificar_grupo_tde)
    
    # Criar identificador único baseado em Nome + Turma
    df_pre['ID_Unico'] = df_pre['Nome'].astype(str) + "_" + df_pre['Turma'].astype(str)
    df_pos['ID_Unico'] = df_pos['Nome'].astype(str) + "_" + df_pos['Turma'].astype(str)
    
    # Filtrar apenas estudantes que participaram de ambos os testes
    ids_pre = set(df_pre['ID_Unico'])
    ids_pos = set(df_pos['ID_Unico'])
    ids_comuns = ids_pre.intersection(ids_pos)
    
    print(f"   Total de IDs em PRÉ: {len(ids_pre)}")
    print(f"   Total de IDs em PÓS: {len(ids_pos)}")
    print(f"   IDs em comum: {len(ids_comuns)}")
    
    # Filtrar DataFrames
    df_pre_filtrado = df_pre[df_pre['ID_Unico'].isin(ids_comuns)].copy()
    df_pos_filtrado = df_pos[df_pos['ID_Unico'].isin(ids_comuns)].copy()
    
    # Aplicar filtro de questões válidas (pelo menos 80% preenchidas)
    mask_pre = df_pre_filtrado.apply(lambda row: tem_questoes_validas_tde(row, colunas_p), axis=1)
    mask_pos = df_pos_filtrado.apply(lambda row: tem_questoes_validas_tde(row, colunas_p), axis=1)
    
    df_pre_filtrado = df_pre_filtrado[mask_pre]
    df_pos_filtrado = df_pos_filtrado[mask_pos]
    
    # Filtrar novamente por IDs comuns após limpeza
    ids_pre_limpo = set(df_pre_filtrado['ID_Unico'])
    ids_pos_limpo = set(df_pos_filtrado['ID_Unico'])
    ids_finais = ids_pre_limpo.intersection(ids_pos_limpo)
    
    df_pre_final = df_pre_filtrado[df_pre_filtrado['ID_Unico'].isin(ids_finais)]
    df_pos_final = df_pos_filtrado[df_pos_filtrado['ID_Unico'].isin(ids_finais)]
    
    print(f"   Após limpeza completa:")
    print(f"   Registros PRÉ: {len(df_pre_final)}")
    print(f"   Registros PÓS: {len(df_pos_final)}")
    print(f"   IDs finais: {len(ids_finais)}")
    
    print("3. CRIANDO TABELA CONSOLIDADA TDE...")
    
    # Criar tabela consolidada
    tabela_bruta = []
    
    # Ordenar por ID_Unico para garantir correspondência
    df_pre_final = df_pre_final.sort_values('ID_Unico')
    df_pos_final = df_pos_final.sort_values('ID_Unico')
    
    for _, row_pre in df_pre_final.iterrows():
        id_unico = row_pre['ID_Unico']
        
        # Encontrar correspondente no pós-teste
        pos_rows = df_pos_final[df_pos_final['ID_Unico'] == id_unico]
        if len(pos_rows) == 0:
            continue
            
        row_pos = pos_rows.iloc[0]
        
        # Determinar grupo e usar mapeamento correto
        grupo_tde = row_pre['GrupoTDE']
        if 'Grupo A' in grupo_tde:
            mapeamento = mapeamento_a
        else:
            mapeamento = mapeamento_b
        
        # Calcular scores TDE
        score_pre = 0
        score_pos = 0
        questoes_validas = 0
        
        for col in colunas_p:
            if col in row_pre.index and col in row_pos.index:
                val_pre = row_pre[col]
                val_pos = row_pos[col]
                
                if not pd.isna(val_pre) and not pd.isna(val_pos):
                    score_pre += val_pre
                    score_pos += val_pos
                    questoes_validas += 1
        
        # Criar registro consolidado
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
        
        # Adicionar respostas individuais das questões TDE
        for i, col in enumerate(colunas_p, 1):
            if col in row_pre.index and col in row_pos.index:
                # Obter palavra correspondente baseada no grupo
                palavra = mapeamento.get(col, f"Palavra_P{i}")
                
                registro[f'P{i:02d}_Pre_{palavra}'] = row_pre[col] if not pd.isna(row_pre[col]) else ''
                registro[f'P{i:02d}_Pos_{palavra}'] = row_pos[col] if not pd.isna(row_pos[col]) else ''
                registro[f'P{i:02d}_Delta_{palavra}'] = (row_pos[col] - row_pre[col]) if (not pd.isna(row_pre[col]) and not pd.isna(row_pos[col])) else ''
        
        tabela_bruta.append(registro)
    
    # Converter para DataFrame
    df_tabela = pd.DataFrame(tabela_bruta)
    
    print("4. CALCULANDO ESTATÍSTICAS RESUMO TDE...")
    
    # Estatísticas por grupo TDE
    print("\n   ESTATÍSTICAS POR GRUPO TDE:")
    for grupo in df_tabela['GrupoTDE'].unique():
        if grupo != 'Indefinido':
            dados_grupo = df_tabela[df_tabela['GrupoTDE'] == grupo]
            print(f"   {grupo}: N={len(dados_grupo)}, Média Pré={dados_grupo['Score_Pre'].mean():.2f}, Média Pós={dados_grupo['Score_Pos'].mean():.2f}")
    
    # Estatísticas por escola
    print("\n   ESTATÍSTICAS POR ESCOLA:")
    for escola in df_tabela['Escola'].unique():
        if escola != 'N/A':
            dados_escola = df_tabela[df_tabela['Escola'] == escola]
            print(f"   {escola}: N={len(dados_escola)}, Δ médio={dados_escola['Delta_Score'].mean():.2f}")
    
    print("5. SALVANDO TABELA TDE...")
    
    # Salvar como CSV
    df_tabela.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    # Salvar como Excel
    df_tabela.to_excel(output_excel, index=False, engine='openpyxl')
    
    print("="*80)
    print("✅ TABELA BRUTA TDE GERADA COM SUCESSO!")
    print("="*80)
    print(f"📁 Arquivo CSV: {output_csv}")
    print(f"📁 Arquivo Excel: {output_excel}")
    print(f"📊 Total de registros: {len(df_tabela)}")
    print(f"📋 Total de colunas: {len(df_tabela.columns)}")
    print("="*80)
    
    # Mostrar preview da tabela
    print("\n📋 PREVIEW DA TABELA TDE (primeiras 5 linhas, colunas principais):")
    colunas_preview = ['Nome', 'Escola', 'Turma', 'GrupoTDE', 'Score_Pre', 'Score_Pos', 'Delta_Score', 'Questoes_Validas']
    print(df_tabela[colunas_preview].head().to_string(index=False))
    
    return df_tabela

def main():
    """Função principal do pipeline TDE"""
    try:
        tabela = gerar_tabela_bruta_tde()
        print(f"\n✅ Pipeline TDE executado com sucesso!")
        print(f"🎯 Dados TDE processados e salvos em formato CSV e Excel")
        return tabela
    except Exception as e:
        print(f"\n❌ Erro durante execução do pipeline TDE: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()