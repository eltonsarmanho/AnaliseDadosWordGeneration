#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza CSVs do Dashboard com coluna Sexo (SEM DUPLICAR LINHAS)
Integra casos indeterminados resolvidos manualmente
"""

import pandas as pd
from pathlib import Path
import json

def carregar_casos_resolvidos(arquivo_json: Path) -> dict:
    """
    Carrega casos indeterminados que foram resolvidos manualmente.
    
    Args:
        arquivo_json: Caminho do JSON com casos resolvidos
        
    Returns:
        Dicionário {nome: sexo}
    """
    if not arquivo_json.exists():
        print(f"⚠️  Arquivo de casos resolvidos não encontrado: {arquivo_json.name}")
        return {}
    
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        casos = json.load(f)
    
    # Cria dicionário nome -> sexo
    mapeamento = {caso['nome']: caso['Sexo'] for caso in casos if 'Sexo' in caso}
    
    print(f"📋 Carregados {len(mapeamento)} casos resolvidos manualmente")
    return mapeamento

def atualizar_csv_com_sexo(arquivo_original: Path, arquivo_com_sexo: Path, casos_resolvidos: dict):
    """
    Atualiza CSV original adicionando coluna Sexo SEM DUPLICAR LINHAS.
    
    Args:
        arquivo_original: CSV original a ser atualizado
        arquivo_com_sexo: CSV com as colunas Sexo, Sexo_Confianca, Sexo_Metodo
        casos_resolvidos: Dicionário com casos indeterminados resolvidos manualmente
    """
    print(f"\n{'='*60}")
    print(f"Atualizando: {arquivo_original.name}")
    print(f"{'='*60}")
    
    # Carrega CSV original
    df_original = pd.read_csv(arquivo_original)
    print(f"Registros originais: {len(df_original)}")
    
    # Carrega CSV com sexo detectado
    df_com_sexo = pd.read_csv(arquivo_com_sexo)
    print(f"Registros com sexo: {len(df_com_sexo)}")
    
    # Verifica se colunas já existem e remove
    colunas_sexo = ['Sexo', 'Sexo_Confianca', 'Sexo_Metodo']
    for col in colunas_sexo:
        if col in df_original.columns:
            print(f"⚠️  Coluna '{col}' já existe. Será substituída.")
            df_original = df_original.drop(columns=[col])
    
    # Cria mapeamento Nome -> (Sexo, Confianca, Metodo)
    # Usa Nome como chave, não ID_Unico, para evitar duplicações
    mapeamento_sexo = {}
    
    for _, row in df_com_sexo.iterrows():
        nome = row['Nome']
        if nome not in mapeamento_sexo:
            mapeamento_sexo[nome] = {
                'Sexo': row['Sexo'],
                'Sexo_Confianca': row['Sexo_Confianca'],
                'Sexo_Metodo': row['Sexo_Metodo']
            }
    
    print(f"📊 Mapeamento criado: {len(mapeamento_sexo)} nomes únicos")
    
    # Aplica correções de casos resolvidos manualmente
    casos_corrigidos = 0
    for nome, sexo_manual in casos_resolvidos.items():
        if nome in mapeamento_sexo:
            if mapeamento_sexo[nome]['Sexo'] == 'Indeterminado':
                mapeamento_sexo[nome] = {
                    'Sexo': sexo_manual,
                    'Sexo_Confianca': 1.0,
                    'Sexo_Metodo': 'manual_corrigido'
                }
                casos_corrigidos += 1
    
    if casos_corrigidos > 0:
        print(f"✅ {casos_corrigidos} casos indeterminados corrigidos manualmente")
    
    # Adiciona colunas de sexo DIRETAMENTE (sem merge para evitar duplicação)
    df_original['Sexo'] = df_original['Nome'].map(lambda nome: mapeamento_sexo.get(nome, {}).get('Sexo', 'Indeterminado'))
    df_original['Sexo_Confianca'] = df_original['Nome'].map(lambda nome: mapeamento_sexo.get(nome, {}).get('Sexo_Confianca', 0.0))
    df_original['Sexo_Metodo'] = df_original['Nome'].map(lambda nome: mapeamento_sexo.get(nome, {}).get('Sexo_Metodo', 'indeterminado'))
    
    # Verifica se manteve o mesmo número de linhas
    if len(df_original) != len(pd.read_csv(arquivo_original)):
        print(f"❌ ERRO: Número de linhas mudou!")
        return
    
    print(f"✅ Número de linhas mantido: {len(df_original)}")
    
    # Verifica se todos foram mapeados
    nao_mapeados = (df_original['Sexo'] == 'Indeterminado').sum()
    if nao_mapeados > 0:
        print(f"⚠️  {nao_mapeados} registros permanecem indeterminados")
    else:
        print(f"✅ Todos os registros foram mapeados com sucesso!")
    
    # Salva backup do original (apenas se não existir)
    backup = arquivo_original.parent / f"{arquivo_original.stem}_backup{arquivo_original.suffix}"
    if not backup.exists():
        pd.read_csv(arquivo_original).to_csv(backup, index=False)
        print(f"💾 Backup criado: {backup.name}")
    
    # Salva atualizado
    df_original.to_csv(arquivo_original, index=False)
    print(f"✅ Arquivo atualizado: {arquivo_original.name}")
    
    # Estatísticas
    print(f"\n📊 Estatísticas de Sexo:")
    print(f"  - Masculino: {(df_original['Sexo'] == 'Masculino').sum()} ({(df_original['Sexo'] == 'Masculino').sum()/len(df_original)*100:.1f}%)")
    print(f"  - Feminino: {(df_original['Sexo'] == 'Feminino').sum()} ({(df_original['Sexo'] == 'Feminino').sum()/len(df_original)*100:.1f}%)")
    print(f"  - Indeterminado: {(df_original['Sexo'] == 'Indeterminado').sum()} ({(df_original['Sexo'] == 'Indeterminado').sum()/len(df_original)*100:.1f}%)")

def main():
    """Função principal"""
    print("="*70)
    print("ATUALIZAR CSVs DO DASHBOARD COM COLUNA SEXO")
    print("(SEM DUPLICAR LINHAS)")
    print("="*70)
    
    # Caminhos
    pasta_dashboard = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    pasta_detector = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/DetectorSexo")
    
    # Carrega casos resolvidos manualmente
    arquivo_casos_resolvidos = pasta_detector / "casos_indeterminados_resolvidas.json"
    casos_resolvidos = carregar_casos_resolvidos(arquivo_casos_resolvidos)
    
    # Atualiza TDE
    arquivo_tde_original = pasta_dashboard / "TDE_longitudinal.csv"
    arquivo_tde_com_sexo = pasta_detector / "TDE_longitudinal_com_sexo.csv"
    
    if arquivo_tde_original.exists() and arquivo_tde_com_sexo.exists():
        atualizar_csv_com_sexo(arquivo_tde_original, arquivo_tde_com_sexo, casos_resolvidos)
    else:
        print(f"❌ Arquivos TDE não encontrados")
    
    # Atualiza Vocabulário
    arquivo_vocab_original = pasta_dashboard / "vocabulario_longitudinal.csv"
    arquivo_vocab_com_sexo = pasta_detector / "vocabulario_longitudinal_com_sexo.csv"
    
    if arquivo_vocab_original.exists() and arquivo_vocab_com_sexo.exists():
        atualizar_csv_com_sexo(arquivo_vocab_original, arquivo_vocab_com_sexo, casos_resolvidos)
    else:
        print(f"❌ Arquivos Vocabulário não encontrados")
    
    print(f"\n{'='*70}")
    print("✅ ATUALIZAÇÃO CONCLUÍDA!")
    print("="*70)
    print("\n💡 Dicas:")
    print("   - Arquivos originais foram salvos com sufixo '_backup'")
    print("   - Número de linhas mantido (sem duplicação)")
    print("   - Casos indeterminados corrigidos manualmente foram aplicados")

if __name__ == "__main__":
    main()
