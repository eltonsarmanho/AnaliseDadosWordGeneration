import pandas as pd
import unicodedata
import re
import sys
import os
import functools

# Configuração de paths para deploy EC2
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Caminhos dos arquivos de dados (relativos ao Dashboard)
ARQ_TDE = os.path.join(os.path.dirname(__file__), 'TDE_longitudinal.csv')
ARQ_VOC = os.path.join(os.path.dirname(__file__), 'vocabulario_longitudinal.csv')

@functools.lru_cache(maxsize=4)
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

def normalize_name(s: str) -> str:
    if pd.isna(s):
        return ''
    s = str(s).strip().upper()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = re.sub(r'\s+', ' ', s)
    return s

def extract_year(turma: str):
    if pd.isna(turma):
        return None
    t = str(turma).upper()
    m = re.search(r'(6|7|8|9)\s*(?:º|°)?\s*ANO', t)
    if m:
        return int(m.group(1))
    m2 = re.search(r'\b(6|7|8|9)\b', t)
    if m2:
        return int(m2.group(1))
    return None

def create_coorte_origem(df):
    """Cria coluna de Coorte_Origem baseada na primeira turma que cada aluno participou"""
    # Para cada ID_Unico, encontrar a menor fase (primeira participação)
    primeira_participacao = df.groupby('ID_Unico')['Fase'].min().reset_index()
    primeira_participacao = primeira_participacao.rename(columns={'Fase': 'Primeira_Fase'})
    
    # Merge para trazer primeira fase para cada registro
    df_temp = df.merge(primeira_participacao, on='ID_Unico', how='left')
    
    # Para cada aluno, pegar a turma da primeira fase como coorte
    coorte_map = {}
    for _, row in df_temp.iterrows():
        id_unico = row['ID_Unico']
        if id_unico not in coorte_map:
            # Buscar a turma da primeira fase deste aluno
            primeira_turma = df_temp[
                (df_temp['ID_Unico'] == id_unico) & 
                (df_temp['Fase'] == row['Primeira_Fase'])
            ]['Turma_Origem'].iloc[0]
            coorte_map[id_unico] = primeira_turma
    
    # Aplicar mapeamento
    df['Coorte_Origem'] = df['ID_Unico'].map(coorte_map)
    return df

def get_datasets():
    tde = load_csv(ARQ_TDE)
    vocab = load_csv(ARQ_VOC)
    
    # Processamento TDE
    if 'NomeNorm' not in tde.columns:
        tde['NomeNorm'] = tde['Nome'].apply(normalize_name)
    if 'Ano' not in tde.columns:
        tde['Ano'] = tde['Turma'].apply(extract_year)
    tde = create_coorte_origem(tde)
    
    # Processamento Vocabulário
    if 'NomeNorm' not in vocab.columns:
        vocab['NomeNorm'] = vocab['Nome'].apply(normalize_name)
    if 'Ano' not in vocab.columns:
        vocab['Ano'] = vocab['Turma'].apply(extract_year)
    vocab = create_coorte_origem(vocab)
    
    return tde, vocab


