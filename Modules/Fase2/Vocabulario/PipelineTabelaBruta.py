import pandas as pd
import os
import sys
import pathlib
from datetime import datetime
import json
import numpy as np

# Adiciona o diretório atual ao sys.path para permitir importações relativas
current_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
print(f"Diretório atual: {current_dir}")
data_dir = str(current_dir) + '/Data'

# Caminhos dos arquivos - Usando CSV
arquivo_pre = os.path.join(data_dir, 'Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.csv')
arquivo_pos = os.path.join(data_dir, 'Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (São Sebastião, WordGen, fase 2 - 2023.2).csv')
arquivo_respostas = os.path.join(data_dir, 'RespostaVocabulario.json')

print("="*80)
print("PIPELINE TABELA BRUTA - VOCABULÁRIO WORDGEN - FASE 2")
print("GERAÇÃO DE TABELA COM DADOS BRUTOS APÓS PRÉ-PROCESSAMENTO")
print("="*80)
print(f"Data/Hora de execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

def carregar_mapeamento_palavras():
    """Carrega o mapeamento das questões para palavras"""
    try:
        with open(arquivo_respostas, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # O arquivo é uma lista de objetos, vamos converter para dicionário
        mapeamento = {}
        for i, item in enumerate(data, 1):
            q_key = f'Q{i}'
            if q_key in item:
                palavra_trabalhada = item[q_key].get('Palavra Trabalhada', f'Palavra_{i}')
                mapeamento[str(i)] = palavra_trabalhada
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento de palavras: {e}")
        return {}

def converter_valor_questao(valor):
    """Converte valores das questões para formato numérico padronizado"""
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

def tem_questoes_validas(row, colunas_q):
    """Verifica se o estudante tem pelo menos 80% das questões respondidas"""
    valores_validos = 0
    for col in colunas_q:
        if col in row.index and not pd.isna(row[col]):
            valores_validos += 1
    return valores_validos >= 40  # Pelo menos 80% das questões preenchidas

def gerar_tabela_bruta():
    """Gera tabela com dados brutos após pré-processamento"""
    
    print("1. CARREGANDO DADOS...")
    df_pre = pd.read_csv(arquivo_pre)
    df_pos = pd.read_csv(arquivo_pos)
    
    # Carregar mapeamento de palavras
    mapeamento_palavras = carregar_mapeamento_palavras()
    print(f"   Mapeamento de palavras carregado: {len(mapeamento_palavras)} questões")
    
    print("2. APLICANDO PRÉ-PROCESSAMENTO...")
    
    # Colunas das questões
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
    
    # Criar identificador único baseado em Nome 
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
    
    print(f"   Após limpeza completa:")
    print(f"   Registros PRÉ: {len(df_pre_final)}")
    print(f"   Registros PÓS: {len(df_pos_final)}")
    print(f"   IDs finais: {len(ids_finais)}")
    
    print("3. CRIANDO TABELA CONSOLIDADA...")
    
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
        
        # Calcular scores totais
        score_pre = 0
        score_pos = 0
        questoes_validas = 0
        
        for col in colunas_q:
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
            'GrupoEtario': row_pre['GrupoEtario'],
            'Score_Pre': score_pre,
            'Score_Pos': score_pos,
            'Delta_Score': score_pos - score_pre,
            'Questoes_Validas': questoes_validas,
            'Percentual_Pre': (score_pre / (questoes_validas * 2)) * 100 if questoes_validas > 0 else 0,
            'Percentual_Pos': (score_pos / (questoes_validas * 2)) * 100 if questoes_validas > 0 else 0
        }
        
        # Adicionar respostas individuais das questões
        for i, col in enumerate(colunas_q, 1):
            if col in row_pre.index and col in row_pos.index:
                # Obter palavra correspondente
                palavra = mapeamento_palavras.get(str(i), f"Palavra_{i}")
                
                registro[f'Q{i:02d}_Pre_{palavra}'] = row_pre[col] if not pd.isna(row_pre[col]) else ''
                registro[f'Q{i:02d}_Pos_{palavra}'] = row_pos[col] if not pd.isna(row_pos[col]) else ''
                registro[f'Q{i:02d}_Delta_{palavra}'] = (row_pos[col] - row_pre[col]) if (not pd.isna(row_pre[col]) and not pd.isna(row_pos[col])) else ''
        
        tabela_bruta.append(registro)
    
    # Converter para DataFrame
    df_tabela = pd.DataFrame(tabela_bruta)
    
    print("4. CALCULANDO ESTATÍSTICAS RESUMO...")
    
    # Estatísticas por grupo etário
    print("\n   ESTATÍSTICAS POR GRUPO ETÁRIO:")
    for grupo in df_tabela['GrupoEtario'].unique():
        if grupo != 'Indefinido':
            dados_grupo = df_tabela[df_tabela['GrupoEtario'] == grupo]
            print(f"   {grupo}: N={len(dados_grupo)}, Média Pré={dados_grupo['Score_Pre'].mean():.2f}, Média Pós={dados_grupo['Score_Pos'].mean():.2f}")
    
    # Estatísticas por escola
    print("\n   ESTATÍSTICAS POR ESCOLA:")
    for escola in df_tabela['Escola'].unique():
        if escola != 'N/A':
            dados_escola = df_tabela[df_tabela['Escola'] == escola]
            print(f"   {escola}: N={len(dados_escola)}, Δ médio={dados_escola['Delta_Score'].mean():.2f}")
    
    print("5. SALVANDO TABELA...")
    
    # Salvar como CSV
    arquivo_csv = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.csv')
    df_tabela.to_csv(arquivo_csv, index=False, encoding='utf-8-sig')
    
    # Salvar como Excel
    arquivo_xlsx = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.xlsx')
    df_tabela.to_excel(arquivo_xlsx, index=False, engine='openpyxl')
    
    print("="*80)
    print("✅ TABELA BRUTA GERADA COM SUCESSO!")
    print("="*80)
    print(f"📁 Arquivo CSV: {arquivo_csv}")
    print(f"📁 Arquivo Excel: {arquivo_xlsx}")
    print(f"📊 Total de registros: {len(df_tabela)}")
    print(f"📋 Total de colunas: {len(df_tabela.columns)}")
    print("="*80)
    
    # Mostrar preview da tabela
    print("\n📋 PREVIEW DA TABELA (primeiras 5 linhas, colunas principais):")
    colunas_preview = ['Nome', 'Escola', 'Turma', 'GrupoEtario', 'Score_Pre', 'Score_Pos', 'Delta_Score', 'Questoes_Validas']
    print(df_tabela[colunas_preview].head().to_string(index=False))
    
    return df_tabela

def main():
    """Função principal do pipeline"""
    try:
        tabela = gerar_tabela_bruta()
        print(f"\n✅ Pipeline executado com sucesso!")
        print(f"🎯 Dados brutos processados e salvos em formato CSV e Excel")
        return tabela
    except Exception as e:
        print(f"\n❌ Erro durante execução do pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
