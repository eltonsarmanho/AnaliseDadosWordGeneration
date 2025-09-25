#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DE DATASETS CONSOLIDADOS PARA RELATÓRIOS POR FASE
Separa os datasets consolidados em arquivos específicos por fase para
gerar relatórios visuais individuais para cada fase (2, 3 e 4).

Autor: Sistema de Análise WordGen
Data: 2024
"""

import pandas as pd
import pathlib
import os
from typing import Dict, List, Tuple
import json

# Configurações de paths
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DASHBOARD_DIR = BASE_DIR / "Dashboard"
DATA_DIR = BASE_DIR / "Data"
MODULES_DIR = BASE_DIR / "Modules"

# Arquivos consolidados
VOCAB_CONSOLIDADO = DASHBOARD_DIR / "vocabulario_consolidado_fases_2_3_4.csv"
TDE_CONSOLIDADO = DASHBOARD_DIR / "TDE_consolidado_fases_2_3_4.csv"

# Diretórios de saída para cada fase
FASE_DIRS = {
    2: DATA_DIR / "Fase 2",
    3: DATA_DIR / "Fase 3", 
    4: DATA_DIR / "Fase 4"
}

def criar_estrutura_diretorios():
    """Cria a estrutura de diretórios necessária para cada fase."""
    print("📁 Criando estrutura de diretórios...")
    
    for fase, fase_dir in FASE_DIRS.items():
        # Criar diretórios principais
        fase_dir.mkdir(exist_ok=True)
        (fase_dir / "Pre").mkdir(exist_ok=True)
        (fase_dir / "Pos").mkdir(exist_ok=True)
        
        print(f"  ✅ Fase {fase}: {fase_dir}")

def separar_dados_por_fase():
    """Separa os datasets consolidados em arquivos específicos por fase."""
    print("\n📊 Separando dados por fase...")
    
    # Carregar datasets consolidados
    print("  📂 Carregando datasets consolidados...")
    vocab_df = pd.read_csv(VOCAB_CONSOLIDADO)
    tde_df = pd.read_csv(TDE_CONSOLIDADO)
    
    print(f"    Vocabulário: {len(vocab_df)} registros")
    print(f"    TDE: {len(tde_df)} registros")
    
    # Separar por fase
    for fase in [2, 3, 4]:
        print(f"\n  🔄 Processando Fase {fase}...")
        
        # Filtrar dados da fase
        vocab_fase = vocab_df[vocab_df['Fase'] == fase].copy()
        tde_fase = tde_df[tde_df['Fase'] == fase].copy()
        
        print(f"    Vocabulário Fase {fase}: {len(vocab_fase)} registros")
        print(f"    TDE Fase {fase}: {len(tde_fase)} registros")
        
        if len(vocab_fase) == 0 and len(tde_fase) == 0:
            print(f"    ⚠️  Nenhum dado encontrado para Fase {fase}")
            continue
            
        # Criar dados simulados Pré/Pós para compatibilidade com scripts existentes
        if len(vocab_fase) > 0:
            criar_dados_pre_pos_vocabulario(vocab_fase, fase)
            
        if len(tde_fase) > 0:
            criar_dados_pre_pos_tde(tde_fase, fase)

def criar_dados_pre_pos_vocabulario(df: pd.DataFrame, fase: int):
    """Cria arquivos Pré e Pós para Vocabulário compatíveis com scripts existentes."""
    fase_dir = FASE_DIRS[fase]
    
    # Separar colunas Pré e Pós
    colunas_base = ['ID_Unico', 'Nome', 'Escola', 'Turma', 'Fase']
    colunas_pre = [col for col in df.columns if col.endswith('_Pre')]
    colunas_pos = [col for col in df.columns if col.endswith('_Pos')]
    
    # Dataset Pré
    df_pre = df[colunas_base + colunas_pre + ['Score_Pre']].copy()
    # Renomear colunas removendo sufixo _Pre
    rename_dict_pre = {col: col.replace('_Pre', '') for col in colunas_pre}
    rename_dict_pre['Score_Pre'] = 'Score'
    df_pre.rename(columns=rename_dict_pre, inplace=True)
    
    # Dataset Pós
    df_pos = df[colunas_base + colunas_pos + ['Score_Pos']].copy()
    # Renomear colunas removendo sufixo _Pos
    rename_dict_pos = {col: col.replace('_Pos', '') for col in colunas_pos}
    rename_dict_pos['Score_Pos'] = 'Score'
    df_pos.rename(columns=rename_dict_pos, inplace=True)
    
    # Salvar arquivos
    arquivo_pre = fase_dir / "Pre" / "DadosVocabulario.csv"
    arquivo_pos = fase_dir / "Pos" / "DadosVocabulario.csv"
    
    df_pre.to_csv(arquivo_pre, index=False)
    df_pos.to_csv(arquivo_pos, index=False)
    
    print(f"    ✅ Vocabulário Pré: {arquivo_pre} ({len(df_pre)} registros)")
    print(f"    ✅ Vocabulário Pós: {arquivo_pos} ({len(df_pos)} registros)")

def criar_dados_pre_pos_tde(df: pd.DataFrame, fase: int):
    """Cria arquivos Pré e Pós para TDE compatíveis com scripts existentes."""
    fase_dir = FASE_DIRS[fase]
    
    # Separar colunas Pré e Pós
    colunas_base = ['ID_Unico', 'Nome', 'Escola', 'Turma', 'Fase']
    colunas_pre = [col for col in df.columns if col.endswith('_Pre')]
    colunas_pos = [col for col in df.columns if col.endswith('_Pos')]
    
    # Dataset Pré
    df_pre = df[colunas_base + colunas_pre + ['Score_Pre']].copy()
    # Renomear colunas removendo sufixo _Pre
    rename_dict_pre = {col: col.replace('_Pre', '') for col in colunas_pre}
    rename_dict_pre['Score_Pre'] = 'Score'
    df_pre.rename(columns=rename_dict_pre, inplace=True)
    
    # Dataset Pós
    df_pos = df[colunas_base + colunas_pos + ['Score_Pos']].copy()
    # Renomear colunas removendo sufixo _Pos
    rename_dict_pos = {col: col.replace('_Pos', '') for col in colunas_pos}
    rename_dict_pos['Score_Pos'] = 'Score'
    df_pos.rename(columns=rename_dict_pos, inplace=True)
    
    # Salvar arquivos
    arquivo_pre = fase_dir / "Pre" / "DadosTDE.csv"
    arquivo_pos = fase_dir / "Pos" / "DadosTDE.csv"
    
    df_pre.to_csv(arquivo_pre, index=False)
    df_pos.to_csv(arquivo_pos, index=False)
    
    print(f"    ✅ TDE Pré: {arquivo_pre} ({len(df_pre)} registros)")
    print(f"    ✅ TDE Pós: {arquivo_pos} ({len(df_pos)} registros)")

def copiar_arquivos_suporte():
    """Copia arquivos de suporte necessários para cada fase."""
    print("\n📋 Copiando arquivos de suporte...")
    
    # Arquivos comuns que devem estar disponíveis para todas as fases
    arquivos_comuns = [
        ("RespostaVocabulario.json", "RespostaVocabulario.json"),
        ("RespostaTED.json", "RespostaTED.json"),
        ("GabaritoVocabulario.json", "GabaritoVocabulario.json"),
        ("dicionario_dados_vocabulario_fase2.txt", "dicionario_dados_vocabulario.txt"),
        ("dicionario_dados_TDE_fase2.txt", "dicionario_dados_TDE.txt")
    ]
    
    for origem, destino in arquivos_comuns:
        arquivo_origem = DATA_DIR / origem
        if arquivo_origem.exists():
            for fase in [2, 3, 4]:
                arquivo_destino = FASE_DIRS[fase] / destino
                # Copiar conteúdo
                with open(arquivo_origem, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                with open(arquivo_destino, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"    ✅ {destino} copiado para Fase {fase}")

def criar_arquivo_palavras_ensinadas():
    """Cria arquivo de palavras ensinadas para cada fase (simulado)."""
    print("\n📝 Criando arquivos de palavras ensinadas...")
    
    # Template básico de palavras ensinadas
    palavras_template = {
        "palavras_ensinadas": [
            "CASA", "GATO", "LIVRO", "MESA", "ÁGUA", "ESCOLA", "MENINO", "MENINA",
            "BOLA", "CARRO", "FLOR", "PÁSSARO", "ÁRVORE", "CACHORRO", "BONECA",
            "BICICLETA", "COMPUTADOR", "TELEVISÃO", "GELADEIRA", "TELEFONE"
        ],
        "total": 20,
        "fase": 2,
        "observacoes": "Lista simulada para compatibilidade com relatórios visuais"
    }
    
    for fase in [2, 3, 4]:
        palavras_fase = palavras_template.copy()
        palavras_fase["fase"] = fase
        
        arquivo_palavras = FASE_DIRS[fase] / "PalavrasEnsinadasVocabulario.json"
        with open(arquivo_palavras, 'w', encoding='utf-8') as f:
            json.dump(palavras_fase, f, ensure_ascii=False, indent=2)
        
        print(f"    ✅ PalavrasEnsinadasVocabulario.json criado para Fase {fase}")

def gerar_relatorio_estatisticas():
    """Gera relatório de estatísticas da separação dos dados."""
    print("\n📈 Gerando relatório de estatísticas...")
    
    # Carregar datasets originais
    vocab_df = pd.read_csv(VOCAB_CONSOLIDADO)
    tde_df = pd.read_csv(TDE_CONSOLIDADO)
    
    relatorio = []
    relatorio.append("=" * 60)
    relatorio.append("RELATÓRIO DE SEPARAÇÃO DOS DADOS POR FASE")
    relatorio.append("=" * 60)
    relatorio.append(f"Data: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    relatorio.append("")
    
    # Estatísticas por fase
    for fase in [2, 3, 4]:
        vocab_fase = vocab_df[vocab_df['Fase'] == fase]
        tde_fase = tde_df[tde_df['Fase'] == fase]
        
        relatorio.append(f"FASE {fase}:")
        relatorio.append(f"  Vocabulário: {len(vocab_fase)} registros")
        relatorio.append(f"  TDE: {len(tde_fase)} registros")
        relatorio.append(f"  Escolas (Vocab): {len(vocab_fase['Escola'].unique())}")
        relatorio.append(f"  Escolas (TDE): {len(tde_fase['Escola'].unique())}")
        relatorio.append("")
    
    # Salvar relatório
    arquivo_relatorio = BASE_DIR / "RELATORIO_SEPARACAO_FASES.txt"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))
    
    print(f"    ✅ Relatório salvo em: {arquivo_relatorio}")
    
    # Mostrar resumo
    print("\n📊 RESUMO DA SEPARAÇÃO:")
    for linha in relatorio[-15:]:  # Últimas 15 linhas
        print(f"    {linha}")

def main():
    """Função principal."""
    print("🚀 ADAPTADOR DE DATASETS CONSOLIDADOS PARA RELATÓRIOS POR FASE")
    print("=" * 70)
    
    try:
        # Verificar se arquivos consolidados existem
        if not VOCAB_CONSOLIDADO.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {VOCAB_CONSOLIDADO}")
        if not TDE_CONSOLIDADO.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {TDE_CONSOLIDADO}")
        
        # Executar processo
        criar_estrutura_diretorios()
        separar_dados_por_fase()
        copiar_arquivos_suporte()
        criar_arquivo_palavras_ensinadas()
        gerar_relatorio_estatisticas()
        
        print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("📂 Estrutura criada:")
        print("  Data/Fase 2/Pre/ e Data/Fase 2/Pos/")
        print("  Data/Fase 3/Pre/ e Data/Fase 3/Pos/")
        print("  Data/Fase 4/Pre/ e Data/Fase 4/Pos/")
        print("")
        print("🎯 Próximos passos:")
        print("  1. Execute os scripts de relatório visual para cada fase")
        print("  2. Os dados estão separados e prontos para análise")
        print("  3. Cada fase tem seus próprios arquivos Pré/Pós")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())