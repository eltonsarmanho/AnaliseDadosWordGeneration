#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LongitudinalMatching
====================
Objetivo: Identificar e quantificar alunos que aparecem em múltiplas fases (2→3, 3→4) 
para TDE e Vocabulário usando os arquivos consolidados já pré-processados.

Abordagem de Identificação (sem usar ID_Unico):
1. Normalização de Nome (upper, remover acentos, colapsar espaços)
2. Chave primária: NomeNormalizado + Escola
3. Progressão esperada de série (Turma) é tolerada (ex: 6º→7º, 7º→8º, 8º→9º). Não é exigido
   que a turma seja idêntica, apenas que a progressão não seja regressiva absurda.
4. Se múltiplos registros de mesmo nome normalizado + escola na fase, agregamos por esse par.
5. Relatórios incluem também visão por Nome isolado (potencialmente inflada por homônimos).

Saídas:
  Data/Longitudinal/
	matching_tde_f2_f3.csv
	matching_tde_f3_f4.csv
	matching_vocab_f2_f3.csv
	matching_vocab_f3_f4.csv
	longitudinal_resumo.json

Cada CSV contém:
  Nome, Escola, Turma_FaseOrigem, Turma_FaseDestino, Fase_Origem, Fase_Destino,
  Score_Pre_Origem, Score_Pos_Origem, Score_Pre_Destino, Score_Pos_Destino

Resumo JSON traz contagens agregadas.
"""

import pandas as pd
import unicodedata
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parents[2]  # volta até raiz do projeto
DATA_DIR = BASE_DIR / 'Data'
OUT_DIR = DATA_DIR / 'Longitudinal'
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_TDE = DATA_DIR / 'TDE_consolidado_fases_2_3_4.csv'
ARQ_VOC = DATA_DIR / 'vocabulario_consolidado_fases_2_3_4.csv'

FASE_PARES = [(2,3),(3,4)]

def normalizar_nome(nome: str) -> str:
	if pd.isna(nome):
		return ''
	s = str(nome).strip().upper()
	s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
	s = re.sub(r'\s+', ' ', s)
	return s

def extrair_ano_turma(turma: str) -> int | None:
	if pd.isna(turma):
		return None
	t = str(turma).upper()
	m = re.search(r'(6|7|8|9)\s*(?:º|°)?\s*ANO', t)
	if m:
		return int(m.group(1))
	# Alguns formatos podem ser "6" sozinho
	m2 = re.search(r'\b(6|7|8|9)\b', t)
	if m2:
		return int(m2.group(1))
	return None

def carregar_dataframe(path: Path, prova: str) -> pd.DataFrame:
	if not path.exists():
		raise FileNotFoundError(f"Arquivo não encontrado: {path}")
	df = pd.read_csv(path)
	col_esperadas = {'Nome','Escola','Turma','Fase','Score_Pre','Score_Pos'}
	faltantes = col_esperadas - set(df.columns)
	if faltantes:
		raise ValueError(f"Colunas faltantes em {prova}: {faltantes}")
	df['NomeNorm'] = df['Nome'].apply(normalizar_nome)
	df['Ano'] = df['Turma'].apply(extrair_ano_turma)
	return df

def agrupar_por_chave(df: pd.DataFrame) -> pd.DataFrame:
	"""Agrega múltiplos registros de mesmo NomeNorm+Escola+Fase (caso existam).
	Mantém média de scores (esperado já estar único, mas é um safeguard)."""
	agrupado = (df
		.groupby(['Fase','NomeNorm','Escola'], as_index=False)
		.agg({
			'Score_Pre':'mean',
			'Score_Pos':'mean',
			'Ano':'first',
			'Turma':'first',  # primeira turma encontrada para referência
			'Nome':'first'
		})
	)
	return agrupado

def casar_fases(df: pd.DataFrame, fase_a: int, fase_b: int, prova: str) -> pd.DataFrame:
	a = df[df['Fase']==fase_a].copy()
	b = df[df['Fase']==fase_b].copy()

	# Agregar salvaguarda
	a = agrupar_por_chave(a)
	b = agrupar_por_chave(b)

	# Merge por NomeNorm + Escola
	merged = a.merge(b, on=['NomeNorm','Escola'], how='inner', suffixes=('_A','_B'))

	# Filtrar progressões absurdas (ex: ano reduzindo >1 ou saltando >1). Permitido: mesma série ou +1
	def progressao_valida(row):
		ano_a = row.get('Ano_A')
		ano_b = row.get('Ano_B')
		if pd.isna(ano_a) or pd.isna(ano_b):
			return True  # não conseguimos avaliar, mantemos
		try:
			diff = int(ano_b) - int(ano_a)
			return diff in (0,1)  # admite retenção ou progressão de 1 ano
		except:
			return True

	merged['ProgressaoValida'] = merged.apply(progressao_valida, axis=1)
	validos = merged[merged['ProgressaoValida']].copy()

	# Montar DataFrame final
	final = pd.DataFrame({
		'Prova': prova,
		'Fase_Origem': fase_a,
		'Fase_Destino': fase_b,
		'Nome': validos['Nome_A'],
		'NomeNorm': validos['NomeNorm'],
		'Escola': validos['Escola'],
		'Turma_Origem': validos['Turma_A'],
		'Turma_Destino': validos['Turma_B'],
		'Ano_Origem': validos['Ano_A'],
		'Ano_Destino': validos['Ano_B'],
		'Score_Pre_Origem': validos['Score_Pre_A'],
		'Score_Pos_Origem': validos['Score_Pos_A'],
		'Score_Pre_Destino': validos['Score_Pre_B'],
		'Score_Pos_Destino': validos['Score_Pos_B'],
	})
	final['Delta_Score_Pre_Pos_Origem'] = final['Score_Pos_Origem'] - final['Score_Pre_Origem']
	final['Delta_Score_Pre_Pos_Destino'] = final['Score_Pos_Destino'] - final['Score_Pre_Destino']
	return final

def gerar_matchings(df: pd.DataFrame, prova: str) -> dict:
	resultados = {}
	for (fa, fb) in FASE_PARES:
		match_df = casar_fases(df, fa, fb, prova)
		nome_out = OUT_DIR / f"matching_{prova.lower()}_f{fa}_f{fb}.csv"
		match_df.to_csv(nome_out, index=False, encoding='utf-8-sig')
		resultados[f"{prova}_F{fa}_F{fb}"] = {
			'pares': int(len(match_df)),
			'fase_origem': fa,
			'fase_destino': fb,
			'prova': prova,
		}
	return resultados

def main():
	print('='*90)
	print('MATCHING LONGITUDINAL - TDE & VOCABULÁRIO')
	print(f'Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
	print('='*90)

	# Carregar
	print('Carregando dataframes...')
	tde_df = carregar_dataframe(ARQ_TDE, 'TDE')
	vocab_df = carregar_dataframe(ARQ_VOC, 'VOCAB')
	print(f'TDE registros: {len(tde_df)} | Vocab registros: {len(vocab_df)}')

	# Gerar matchings
	print('Gerando pares TDE...')
	resumo_tde = gerar_matchings(tde_df, 'TDE')
	print('Gerando pares VOCAB...')
	resumo_vocab = gerar_matchings(vocab_df, 'VOCAB')

	# Resumo adicional: contagem de nomes que aparecem em 2 fases qualquer (por prova)
	def contar_multifase(df, prova):
		pivot = df.groupby('NomeNorm')['Fase'].nunique()
		return {
			'nomes_total': int(pivot.shape[0]),
			'nomes_2_fases': int((pivot==2).sum()),
			'nomes_3_fases': int((pivot==3).sum()),
		}
	add_tde = contar_multifase(tde_df, 'TDE')
	add_vocab = contar_multifase(vocab_df, 'VOCAB')

	resumo = {
		'pares': {**resumo_tde, **resumo_vocab},
		'multifase': {'TDE': add_tde, 'VOCAB': add_vocab},
		'metodologia': {
			'chave_primary': 'Nome normalizado + Escola',
			'progressao_aceita_ano': '0 (mesmo ano) ou +1 (progressão)',
			'nota': 'Possível sobre-identificação se houver homônimos na mesma escola.'
		}
	}

	resumo_path = OUT_DIR / 'longitudinal_resumo.json'
	with open(resumo_path, 'w', encoding='utf-8') as f:
		json.dump(resumo, f, ensure_ascii=False, indent=2)

	print('\nResumo salvo em:', resumo_path)
	for k,v in resumo['pares'].items():
		print(f"  {k}: {v['pares']} pares")
	print('\nMultifase:')
	print('  TDE:', add_tde)
	print('  VOCAB:', add_vocab)
	print('\nConcluído.')

if __name__ == '__main__':
	main()

