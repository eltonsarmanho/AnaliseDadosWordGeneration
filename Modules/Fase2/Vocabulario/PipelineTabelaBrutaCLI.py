#!/usr/bin/env python3
"""
Pipeline de Tabela Bruta - WordGen Fase 2

Script para gerar tabela consolidada com dados brutos após pré-processamento.
Pode ser executado com argumentos de linha de comando para diferentes opções.

Uso:
    python PipelineTabelaBrutaCLI.py --gerar
    python PipelineTabelaBrutaCLI.py --resumo
    python PipelineTabelaBrutaCLI.py --preview
    python PipelineTabelaBrutaCLI.py --help
"""

import argparse
import sys
import os
import pathlib

# Adicionar o diretório do módulo ao path
current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(current_dir))

from Modules.Fase2.PipelineTabelaBruta import main as gerar_tabela
from Modules.Fase2.ResumoTabelaBruta import gerar_resumo_tabela_bruta
from Modules.Fase2.GeradorDicionarioDados import main as gerar_dicionario
import pandas as pd

def preview_tabela():
    """Mostra preview da tabela bruta gerada"""
    data_dir = str(current_dir) + '/Data'
    arquivo_csv = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.csv')
    
    if not os.path.exists(arquivo_csv):
        print("❌ Tabela bruta não encontrada!")
        print("Execute primeiro: python PipelineTabelaBrutaCLI.py --gerar")
        return
    
    print("="*80)
    print("PREVIEW DA TABELA BRUTA - PRIMEIRAS 10 LINHAS")
    print("="*80)
    
    # Carregar apenas as colunas principais para preview
    colunas_principais = ['Nome', 'Escola', 'Turma', 'GrupoEtario', 'Score_Pre', 'Score_Pos', 'Delta_Score']
    
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8-sig', usecols=colunas_principais, nrows=10)
        print(df.to_string(index=False))
        print("\n" + "="*80)
        print(f"Tabela completa contém {len(pd.read_csv(arquivo_csv, encoding='utf-8-sig', usecols=['Nome']))} registros")
        print("Para ver resumo completo: python PipelineTabelaBrutaCLI.py --resumo")
        print("="*80)
    except Exception as e:
        print(f"❌ Erro ao carregar preview: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Tabela Bruta - WordGen Fase 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python PipelineTabelaBrutaCLI.py --gerar       # Gera a tabela bruta
  python PipelineTabelaBrutaCLI.py --resumo      # Mostra resumo da tabela
  python PipelineTabelaBrutaCLI.py --preview     # Mostra preview dos dados
  python PipelineTabelaBrutaCLI.py --dicionario  # Gera dicionário de dados
  python PipelineTabelaBrutaCLI.py --all         # Executa todos os comandos

A tabela bruta contém:
  • 1.362 registros de estudantes
  • 161 colunas com dados detalhados
  • Respostas individuais para 50 questões de vocabulário
  • Dados pré e pós-teste com nomes das palavras
  • Scores calculados e estatísticas por estudante
        """
    )
    
    parser.add_argument('--gerar', action='store_true',
                       help='Gera a tabela bruta com dados pré-processados')
    parser.add_argument('--resumo', action='store_true',
                       help='Mostra resumo executivo da tabela gerada')
    parser.add_argument('--preview', action='store_true',
                       help='Mostra preview das primeiras linhas da tabela')
    parser.add_argument('--dicionario', action='store_true',
                       help='Gera dicionário de dados completo em TXT')
    parser.add_argument('--all', action='store_true',
                       help='Executa todas as operações (gerar + resumo + preview + dicionário)')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostrar help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        if args.all:
            print("🚀 Executando pipeline completo...")
            print("\n1️⃣ Gerando tabela bruta...")
            gerar_tabela()
            print("\n2️⃣ Gerando resumo...")
            gerar_resumo_tabela_bruta()
            print("\n3️⃣ Mostrando preview...")
            preview_tabela()
            print("\n4️⃣ Gerando dicionário de dados...")
            gerar_dicionario()
            
        else:
            if args.gerar:
                print("🚀 Gerando tabela bruta...")
                gerar_tabela()
            
            if args.resumo:
                print("📊 Gerando resumo...")
                gerar_resumo_tabela_bruta()
            
            if args.preview:
                print("👀 Mostrando preview...")
                preview_tabela()
                
            if args.dicionario:
                print("📖 Gerando dicionário de dados...")
                gerar_dicionario()
                
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
