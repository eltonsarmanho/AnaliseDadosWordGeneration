import pandas as pd
import unicodedata
import re
from pathlib import Path
import functools

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / 'Data'

ARQ_TDE = DATA_DIR / 'TDE_consolidado_fases_2_3_4.csv'
ARQ_VOC = DATA_DIR / 'vocabulario_consolidado_fases_2_3_4.csv'
MATCH_DIR = DATA_DIR / 'Longitudinal'

@functools.lru_cache(maxsize=4)
def load_csv(path: Path) -> pd.DataFrame:
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
    for f in MATCH_DIR.glob('matching_*_f*_f*.csv'):
        try:
            resultados[f.name] = pd.read_csv(f)
        except Exception:
            pass
    return resultados
