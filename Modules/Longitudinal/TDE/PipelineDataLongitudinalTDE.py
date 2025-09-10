#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE DE DADOS LONGITUDINAIS - TDE WORDGEN
Análise longitudinal do Teste de Escrita (TDE) ao longo das Fases 2, 3 e 4

Este módulo consolida dados das diferentes fases para análise longitudinal,
incluindo melhorias por escola, turma e geral.

Autor: Sistema de Análise WordGen
Data: 2024
"""

import os
import json
import pathlib
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys

# Adicionar o diretório do módulo Longitudinal ao path
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from DetectorSexo import DetectorSexo

# ======================
# Configurações de Paths
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"
LONGITUDINAL_DIR = BASE_DIR / "Modules" / "Longitudinal" / "Data"

# Criar diretórios se não existirem
LONGITUDINAL_DIR.mkdir(parents=True, exist_ok=True)
(LONGITUDINAL_DIR / "figures").mkdir(parents=True, exist_ok=True)

# Arquivos de saída longitudinal
CSV_LONGITUDINAL_TDE = LONGITUDINAL_DIR / "dados_longitudinais_TDE.csv"
JSON_RESUMO_LONGITUDINAL = LONGITUDINAL_DIR / "resumo_longitudinal_TDE.json"

class PipelineDataLongitudinalTDE:
    """Pipeline para processamento de dados longitudinais do TDE"""
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.data_dir = DATA_DIR
        self.longitudinal_dir = LONGITUDINAL_DIR
        
        # Dados consolidados
        self.dados_consolidados = []
        self.resumo_geral = {}
        
        # Inicializar detector de sexo
        self.detector_sexo = DetectorSexo()
    
    def normalizar_colunas_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nomes das colunas para um padrão consistente"""
        # Criar um mapeamento para normalizar os nomes das colunas
        df_normalized = df.copy()
        
        # Normalizar colunas principais (case insensitive)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['escola', 'school']:
                column_mapping[col] = 'Escola'
            elif col_lower in ['turma', 'class', 'classe']:
                column_mapping[col] = 'Turma'
            elif col_lower in ['nome', 'name']:
                column_mapping[col] = 'Nome'
            elif col_lower in ['sexo', 'sex', 'genero', 'gender']:
                column_mapping[col] = 'Sexo'
            elif col_lower in ['idade', 'age']:
                column_mapping[col] = 'Idade'
        
        # Aplicar mapeamento
        if column_mapping:
            df_normalized = df_normalized.rename(columns=column_mapping)
        
        return df_normalized
    
    def identificar_colunas_questoes(self, df: pd.DataFrame) -> List[str]:
        """Identifica colunas de questões (Q1, Q2, P1, P2, etc.)"""
        colunas_questoes = []
        
        for col in df.columns:
            # Verifica se a coluna começa com Q ou P seguido de números
            if (col.startswith('Q') and col[1:].isdigit()) or \
               (col.startswith('P') and col[1:].isdigit()):
                colunas_questoes.append(col)
        
        return sorted(colunas_questoes)
    
    def obter_valor_coluna_flexible(self, row: pd.Series, possiveis_nomes: List[str], default='') -> str:
        """Obtém valor de uma coluna considerando possíveis nomes (case insensitive)"""
        for nome in possiveis_nomes:
            if nome in row and pd.notna(row[nome]):
                return str(row[nome]).strip()
        return str(default)
        
    def carregar_dados_fase(self, fase: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Carrega dados pré e pós de uma fase específica"""
        fase_dir = self.data_dir / f"Fase {fase}"
        
        # Caminhos para os arquivos
        arquivo_pre = fase_dir / "Pre" / "DadosTDE.csv"
        arquivo_pos = fase_dir / "Pos" / "DadosTDE.csv"
        
        try:
            df_pre = pd.read_csv(arquivo_pre)
            df_pos = pd.read_csv(arquivo_pos)
            
            # Normalizar colunas
            df_pre = self.normalizar_colunas_dataframe(df_pre)
            df_pos = self.normalizar_colunas_dataframe(df_pos)
            
            print(f"✅ Fase {fase} carregada: {len(df_pre)} registros PRE, {len(df_pos)} registros POS")
            
            return df_pre, df_pos
            
        except Exception as e:
            print(f"❌ Erro ao carregar Fase {fase}: {e}")
            return pd.DataFrame(), pd.DataFrame()
    
    def normalizar_dados_fase(self, df_pre: pd.DataFrame, df_pos: pd.DataFrame, fase: int) -> pd.DataFrame:
        """Normaliza e consolida dados de uma fase"""
        dados_fase = []
        
        # Identificar colunas de questões dinamicamente (Q1, Q2, P1, P2, etc.)
        colunas_questoes_pre = self.identificar_colunas_questoes(df_pre)
        colunas_questoes_pos = self.identificar_colunas_questoes(df_pos)
        
        print(f"📋 Fase {fase} - Colunas PRE: {len(colunas_questoes_pre)}, POS: {len(colunas_questoes_pos)}")
        
        # Para cada estudante no PRE
        for _, row_pre in df_pre.iterrows():
            try:
                # Calcular total PRE
                respostas_pre = []
                for col in colunas_questoes_pre:
                    if col in row_pre and pd.notna(row_pre[col]):
                        try:
                            respostas_pre.append(float(row_pre[col]))
                        except (ValueError, TypeError):
                            continue
                
                total_pre = sum(respostas_pre) if respostas_pre else 0
                
                # Obter dados do estudante de forma flexível
                nome = self.obter_valor_coluna_flexible(row_pre, ['Nome', 'NOME', 'nome'])
                escola = self.obter_valor_coluna_flexible(row_pre, ['Escola', 'ESCOLA', 'escola'])
                turma = self.obter_valor_coluna_flexible(row_pre, ['Turma', 'TURMA', 'turma'])
                
                if not nome or not escola:
                    continue  # Pular registros sem nome ou escola
                
                # Buscar correspondente no POS usando busca flexível
                pos_match = pd.DataFrame()
                
                # Tentar diferentes combinações para encontrar o match
                for nome_col in ['Nome', 'NOME', 'nome']:
                    for escola_col in ['Escola', 'ESCOLA', 'escola']:
                        if nome_col in df_pos.columns and escola_col in df_pos.columns:
                            pos_match = df_pos[
                                (df_pos[nome_col].fillna('').str.strip() == nome) & 
                                (df_pos[escola_col].fillna('').str.strip() == escola)
                            ]
                            if not pos_match.empty:
                                break
                    if not pos_match.empty:
                        break
                
                total_pos = 0
                if not pos_match.empty:
                    row_pos = pos_match.iloc[0]
                    respostas_pos = []
                    for col in colunas_questoes_pos:
                        if col in row_pos and pd.notna(row_pos[col]):
                            try:
                                respostas_pos.append(float(row_pos[col]))
                            except (ValueError, TypeError):
                                continue
                    total_pos = sum(respostas_pos) if respostas_pos else 0
                
                # Obter sexo (primeiro tentar colunas existentes, depois detectar pelo nome)
                sexo = self.obter_valor_coluna_flexible(row_pre, ['Sexo', 'SEXO', 'sexo'])
                if not sexo or sexo in ['', 'nan', 'NaN', 'NULL', 'null']:
                    # Se não há coluna de sexo ou está vazia, detectar pelo nome
                    sexo = self.detector_sexo.detectar_sexo(nome)
                
                # Dados do estudante
                dados_estudante = {
                    'Fase': fase,
                    'Escola': escola,
                    'Turma': turma,
                    'Nome': nome,
                    'Sexo': sexo,
                    'Idade': self.obter_valor_coluna_flexible(row_pre, ['Idade', 'IDADE', 'idade'], 0),
                    'Score_Pre': total_pre,
                    'Score_Pos': total_pos,
                    'Delta': total_pos - total_pre,
                    'Melhoria': 1 if total_pos > total_pre else 0,
                    'Manutencao': 1 if total_pos == total_pre else 0,
                    'Piora': 1 if total_pos < total_pre else 0
                }
                
                # Converter idade para número se possível
                try:
                    dados_estudante['Idade'] = float(dados_estudante['Idade']) if dados_estudante['Idade'] else 0
                except (ValueError, TypeError):
                    dados_estudante['Idade'] = 0
                
                dados_fase.append(dados_estudante)
                
            except Exception as e:
                print(f"⚠️ Erro ao processar estudante na Fase {fase}: {e}")
                continue
        
        return pd.DataFrame(dados_fase)
    
    def processar_todas_fases(self):
        """Processa dados de todas as fases (2, 3, 4)"""
        print("🔄 Iniciando processamento longitudinal TDE...")
        
        for fase in [2, 3, 4]:
            print(f"\n📊 Processando Fase {fase}...")
            
            df_pre, df_pos = self.carregar_dados_fase(fase)
            
            if not df_pre.empty and not df_pos.empty:
                dados_fase = self.normalizar_dados_fase(df_pre, df_pos, fase)
                self.dados_consolidados.append(dados_fase)
                print(f"✅ Fase {fase} processada: {len(dados_fase)} estudantes")
            else:
                print(f"⚠️ Fase {fase} pulada por dados insuficientes")
    
    def gerar_resumo_geral(self) -> Dict:
        """Gera resumo estatístico geral dos dados longitudinais"""
        if not self.dados_consolidados:
            return {}
        
        # Consolidar todos os dados
        df_all = pd.concat(self.dados_consolidados, ignore_index=True)
        
        resumo = {
            'data_processamento': datetime.now().isoformat(),
            'total_estudantes': len(df_all),
            'fases_analisadas': sorted(df_all['Fase'].unique().tolist()),
            
            # Estatísticas por fase
            'estatisticas_por_fase': {},
            
            # Perfil demográfico geral
            'perfil_demografico': {
                'distribuicao_sexo': df_all['Sexo'].value_counts().to_dict(),
                'idade_media': float(df_all['Idade'].mean()) if not df_all['Idade'].isna().all() else 0,
                'escolas_unicas': len(df_all['Escola'].unique()),
                'turmas_unicas': len(df_all.groupby(['Escola', 'Turma']).size()),
            },
            
            # Performance geral
            'performance_geral': {
                'score_pre_medio': float(df_all['Score_Pre'].mean()),
                'score_pos_medio': float(df_all['Score_Pos'].mean()),
                'delta_medio': float(df_all['Delta'].mean()),
                'taxa_melhoria': float(df_all['Melhoria'].mean() * 100),
                'taxa_manutencao': float(df_all['Manutencao'].mean() * 100),
                'taxa_piora': float(df_all['Piora'].mean() * 100),
            }
        }
        
        # Estatísticas detalhadas por fase
        for fase in sorted(df_all['Fase'].unique()):
            df_fase = df_all[df_all['Fase'] == fase]
            
            resumo['estatisticas_por_fase'][f'fase_{fase}'] = {
                'num_estudantes': len(df_fase),
                'num_escolas': len(df_fase['Escola'].unique()),
                'num_turmas': len(df_fase.groupby(['Escola', 'Turma']).size()),
                'score_pre_medio': float(df_fase['Score_Pre'].mean()),
                'score_pos_medio': float(df_fase['Score_Pos'].mean()),
                'delta_medio': float(df_fase['Delta'].mean()),
                'taxa_melhoria': float(df_fase['Melhoria'].mean() * 100),
                'distribuicao_sexo': df_fase['Sexo'].value_counts().to_dict(),
                'escolas': sorted(df_fase['Escola'].unique().tolist())
            }
        
        # Análise por escola (consolidada)
        resumo['analise_por_escola'] = {}
        for escola in df_all['Escola'].unique():
            df_escola = df_all[df_all['Escola'] == escola]
            
            resumo['analise_por_escola'][escola] = {
                'total_estudantes': len(df_escola),
                'fases_participantes': sorted(df_escola['Fase'].unique().tolist()),
                'delta_medio': float(df_escola['Delta'].mean()),
                'taxa_melhoria': float(df_escola['Melhoria'].mean() * 100),
                'score_pre_medio': float(df_escola['Score_Pre'].mean()),
                'score_pos_medio': float(df_escola['Score_Pos'].mean()),
            }
        
        self.resumo_geral = resumo
        return resumo
    
    def salvar_dados(self):
        """Salva dados consolidados e resumo"""
        print("\n💾 Salvando dados longitudinais...")
        
        if self.dados_consolidados:
            # Consolidar e salvar CSV
            df_consolidado = pd.concat(self.dados_consolidados, ignore_index=True)
            df_consolidado.to_csv(CSV_LONGITUDINAL_TDE, index=False, encoding='utf-8')
            print(f"✅ CSV salvo: {CSV_LONGITUDINAL_TDE}")
            
            # Salvar resumo JSON
            with open(JSON_RESUMO_LONGITUDINAL, 'w', encoding='utf-8') as f:
                json.dump(self.resumo_geral, f, indent=2, ensure_ascii=False)
            print(f"✅ Resumo salvo: {JSON_RESUMO_LONGITUDINAL}")
            
            print(f"\n📈 Resumo Final:")
            print(f"   • Total de estudantes: {len(df_consolidado)}")
            print(f"   • Fases analisadas: {sorted(df_consolidado['Fase'].unique())}")
            print(f"   • Escolas únicas: {len(df_consolidado['Escola'].unique())}")
            print(f"   • Taxa de melhoria média: {df_consolidado['Melhoria'].mean()*100:.1f}%")
        else:
            print("❌ Nenhum dado para salvar")
    
    def executar_pipeline(self):
        """Executa o pipeline completo"""
        print("🚀 Iniciando Pipeline Longitudinal TDE")
        print("="*50)
        
        # Processar todas as fases
        self.processar_todas_fases()
        
        # Gerar resumo
        print("\n📊 Gerando resumo estatístico...")
        self.gerar_resumo_geral()
        
        # Salvar dados
        self.salvar_dados()
        
        print("\n✅ Pipeline Longitudinal TDE concluído!")
        return True

def main():
    """Função principal"""
    pipeline = PipelineDataLongitudinalTDE()
    pipeline.executar_pipeline()

if __name__ == "__main__":
    main()
