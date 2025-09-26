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
MATCH_DIR = os.path.join(os.path.dirname(__file__), 'Longitudinal')

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

def get_datasets():
    tde = load_csv(ARQ_TDE)
    vocab = load_csv(ARQ_VOC)
    for df in (tde, vocab):
        if 'NomeNorm' not in df.columns:
            df['NomeNorm'] = df['Nome'].apply(normalize_name)
        if 'Ano' not in df.columns:
            df['Ano'] = df['Turma'].apply(extract_year)
    return tde, vocab

def load_matching():
    resultados = {}
    if os.path.exists(MATCH_DIR):
        try:
            for filename in os.listdir(MATCH_DIR):
                if filename.startswith('matching_') and filename.endswith('.csv'):
                    file_path = os.path.join(MATCH_DIR, filename)
                    resultados[filename] = pd.read_csv(file_path)
        except Exception:
            pass
    return resultados
