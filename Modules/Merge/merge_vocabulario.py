#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERGE VOCABULÁRIO - FASES 2, 3 e 4
Script para consolidar dados de vocabulário das três fases em um único CSV

Autor: Sistema de Análise WordGen
Data: 2024
"""

import os
import pandas as pd
import pathlib

# ======================
# Configurações
# ======================
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR = BASE_DIR / "Data"

# Arquivos de entrada
ARQUIVOS_VOCABULARIO = {
    2: DATA_DIR / "tabela_bruta_fase2_vocabulario_wordgen.csv",
    3: DATA_DIR / "tabela_bruta_fase3_vocabulario_wordgen.csv", 
    4: DATA_DIR / "tabela_bruta_fase4_vocabulario_wordgen.csv"
}

# Arquivo de saída
ARQUIVO_SAIDA = DATA_DIR / "vocabulario_consolidado_fases_2_3_4.csv"

def carregar_e_processar_fase(fase: int, arquivo_path: str) -> pd.DataFrame:
    """Carrega e processa dados de uma fase específica"""
    print(f"📊 Processando Fase {fase}: {arquivo_path}")
    
    try:
        df = pd.read_csv(arquivo_path)
        print(f"   Registros carregados: {len(df)}")
        
        # Adicionar coluna Fase
        df['Fase'] = fase
        
        # Selecionar apenas as colunas necessárias
        colunas_base = ['ID_Unico', 'Nome', 'Escola', 'Turma', 'Fase', 'Score_Pre', 'Score_Pos']
        
        # Colunas das questões (Q01 a Q50) - extrair apenas Pre e Pos, sem Delta
        colunas_questoes = []
        for i in range(1, 51):  # Q1 a Q50
            q_num = f"Q{i:02d}"  # Formato Q01, Q02, etc.
            
            # Procurar pelas colunas Pre e Pos
            col_pre = None
            col_pos = None
            
            for col in df.columns:
                if col.startswith(f"{q_num}_Pre_"):
                    col_pre = col
                elif col.startswith(f"{q_num}_Pos_"):
                    col_pos = col
            
            if col_pre and col_pos:
                # Renomear para formato Q1_Pre, Q1_Pos
                df[f"Q{i}_Pre"] = df[col_pre]
                df[f"Q{i}_Pos"] = df[col_pos]
                colunas_questoes.extend([f"Q{i}_Pre", f"Q{i}_Pos"])
        
        # Selecionar todas as colunas necessárias
        colunas_finais = colunas_base + colunas_questoes
        
        # Verificar se todas as colunas existem
        colunas_existentes = [col for col in colunas_finais if col in df.columns]
        colunas_faltantes = [col for col in colunas_finais if col not in df.columns]
        
        if colunas_faltantes:
            print(f"   ⚠️ Colunas faltantes: {colunas_faltantes}")
        
        df_final = df[colunas_existentes].copy()
        print(f"   Colunas selecionadas: {len(colunas_existentes)}")
        print(f"   Registros finais: {len(df_final)}")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Erro ao processar Fase {fase}: {e}")
        return pd.DataFrame()

def main():
    """Função principal para consolidar dados de vocabulário"""
    print("=" * 70)
    print("🎯 CONSOLIDAÇÃO VOCABULÁRIO - FASES 2, 3 e 4")
    print("=" * 70)
    
    # Lista para armazenar DataFrames de todas as fases
    dataframes = []
    
    # Processar cada fase
    for fase, arquivo in ARQUIVOS_VOCABULARIO.items():
        if arquivo.exists():
            df_fase = carregar_e_processar_fase(fase, str(arquivo))
            if not df_fase.empty:
                dataframes.append(df_fase)
        else:
            print(f"⚠️ Arquivo não encontrado para Fase {fase}: {arquivo}")
    
    if not dataframes:
        print("❌ Nenhum dado foi carregado. Verifique os arquivos de entrada.")
        return
    
    # Consolidar todos os dados
    print("\n🔄 Consolidando dados...")
    df_consolidado = pd.concat(dataframes, ignore_index=True)
    
    print(f"   Total de registros consolidados: {len(df_consolidado)}")
    print(f"   Distribuição por fase:")
    for fase in sorted(df_consolidado['Fase'].unique()):
        count = len(df_consolidado[df_consolidado['Fase'] == fase])
        print(f"     Fase {fase}: {count} registros")
    
    # Reorganizar colunas na ordem desejada
    colunas_ordenadas = ['ID_Unico', 'Nome', 'Escola', 'Turma', 'Fase', 'Score_Pre', 'Score_Pos']
    
    # Adicionar colunas das questões na ordem
    for i in range(1, 51):
        q_pre = f"Q{i}_Pre"
        q_pos = f"Q{i}_Pos"
        if q_pre in df_consolidado.columns:
            colunas_ordenadas.append(q_pre)
        if q_pos in df_consolidado.columns:
            colunas_ordenadas.append(q_pos)
    
    # Selecionar apenas colunas que existem
    colunas_existentes = [col for col in colunas_ordenadas if col in df_consolidado.columns]
    df_final = df_consolidado[colunas_existentes]
    
    # Salvar arquivo consolidado
    print(f"\n💾 Salvando arquivo consolidado: {ARQUIVO_SAIDA}")
    df_final.to_csv(ARQUIVO_SAIDA, index=False)
    
    print("=" * 70)
    print("✅ CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"📁 Arquivo gerado: {ARQUIVO_SAIDA}")
    print(f"📊 Total de registros: {len(df_final)}")
    print(f"📋 Total de colunas: {len(df_final.columns)}")
    print("=" * 70)
    
    # Mostrar resumo das colunas
    print("\n📋 Estrutura do arquivo consolidado:")
    print("Colunas base:", [col for col in colunas_existentes if not col.startswith('Q')])
    print(f"Colunas de questões: Q1_Pre/Pos até Q50_Pre/Pos")
    print(f"Total questões encontradas: {len([col for col in colunas_existentes if col.startswith('Q')])//2}")

if __name__ == "__main__":
    main()
