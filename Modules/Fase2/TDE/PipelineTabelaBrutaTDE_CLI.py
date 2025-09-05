#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERFACE CLI - TDE WORDGEN FASE 2
Interface de linha de comando para todas as operações TDE

Uso:
    python PipelineTabelaBrutaTDE_CLI.py --gerar          # Gerar tabela bruta TDE
    python PipelineTabelaBrutaTDE_CLI.py --dicionario     # Gerar dicionário de dados
    python PipelineTabelaBrutaTDE_CLI.py --resumo         # Mostrar estatísticas
    python PipelineTabelaBrutaTDE_CLI.py --preview        # Preview da tabela
    python PipelineTabelaBrutaTDE_CLI.py --help           # Mostrar ajuda

Autor: Sistema de Análise WordGen
Data: 2024
"""

import argparse
import pandas as pd
import os
from datetime import datetime

# Importar módulos TDE
from .PipelineDataTDE import main as gerar_tabela_tde
from .GeradorDicionarioDadosTDE import main as gerar_dicionario_tde

# Configurações
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', '..', '..', 'Data')
arquivo_csv = os.path.join(data_dir, 'tabela_bruta_fase2_TDE_wordgen.csv')
arquivo_excel = os.path.join(data_dir, 'tabela_bruta_fase2_TDE_wordgen.xlsx')

def mostrar_banner():
    """Mostra banner do sistema"""
    print("="*80)
    print("🎯 INTERFACE CLI - TDE WORDGEN FASE 2")
    print("📊 TESTE DE ESCRITA - ANÁLISE PRÉ/PÓS-TESTE")
    print("="*80)
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def verificar_tabela_existe():
    """Verifica se a tabela TDE já foi gerada"""
    return os.path.exists(arquivo_csv)

def mostrar_resumo():
    """Mostra estatísticas resumo da tabela TDE"""
    if not verificar_tabela_existe():
        print("❌ Tabela TDE não encontrada. Execute primeiro: --gerar")
        return
    
    print("📊 CARREGANDO ESTATÍSTICAS TDE...")
    df = pd.read_csv(arquivo_csv)
    
    print("\n" + "="*60)
    print("📈 ESTATÍSTICAS RESUMO - TDE WORDGEN FASE 2")
    print("="*60)
    
    # Informações gerais
    print(f"📋 Total de registros: {len(df):,}")
    print(f"📋 Total de colunas: {len(df.columns):,}")
    print(f"📋 Período de dados: Fase 2 (2023-2024)")
    
    # Distribuição por grupo TDE
    print("\n🎯 DISTRIBUIÇÃO POR GRUPO TDE:")
    for grupo, count in df['GrupoTDE'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"   {grupo}: {count:,} estudantes ({pct:.1f}%)")
    
    # Distribuição por escola
    print("\n🏫 DISTRIBUIÇÃO POR ESCOLA:")
    for escola, count in df['Escola'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"   {escola}: {count:,} ({pct:.1f}%)")
    
    # Estatísticas dos scores
    print("\n📊 ESTATÍSTICAS DOS SCORES TDE:")
    stats = df[['Score_Pre', 'Score_Pos', 'Delta_Score']].describe()
    
    for col in ['Score_Pre', 'Score_Pos', 'Delta_Score']:
        print(f"\n   {col}:")
        print(f"     Média: {stats.loc['mean', col]:.2f}")
        print(f"     Desvio: {stats.loc['std', col]:.2f}")
        print(f"     Mínimo: {stats.loc['min', col]:.0f}")
        print(f"     Máximo: {stats.loc['max', col]:.0f}")
    
    # Análise por grupo
    print("\n🎯 ANÁLISE COMPARATIVA POR GRUPO:")
    for grupo in df['GrupoTDE'].unique():
        if grupo != 'Indefinido':
            dados_grupo = df[df['GrupoTDE'] == grupo]
            print(f"\n   {grupo}:")
            print(f"     N: {len(dados_grupo)}")
            print(f"     Score Pré: {dados_grupo['Score_Pre'].mean():.2f} ± {dados_grupo['Score_Pre'].std():.2f}")
            print(f"     Score Pós: {dados_grupo['Score_Pos'].mean():.2f} ± {dados_grupo['Score_Pos'].std():.2f}")
            print(f"     Delta médio: {dados_grupo['Delta_Score'].mean():.2f}")
            
            # Percentual de melhora/piora
            melhorou = (dados_grupo['Delta_Score'] > 0).sum()
            piorou = (dados_grupo['Delta_Score'] < 0).sum()
            manteve = (dados_grupo['Delta_Score'] == 0).sum()
            
            print(f"     Melhorou: {melhorou} ({melhorou/len(dados_grupo)*100:.1f}%)")
            print(f"     Piorou: {piorou} ({piorou/len(dados_grupo)*100:.1f}%)")
            print(f"     Manteve: {manteve} ({manteve/len(dados_grupo)*100:.1f}%)")
    
    # Ranking de escolas por performance
    print("\n🏆 RANKING DE ESCOLAS (por Delta Score médio):")
    ranking = df.groupby('Escola')['Delta_Score'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    
    for i, (escola, dados) in enumerate(ranking.iterrows(), 1):
        print(f"   {i}. {escola}")
        print(f"      Delta médio: {dados['mean']:.2f}")
        print(f"      N: {dados['count']} estudantes")
    
    print("\n" + "="*60)
    print("✅ RESUMO ESTATÍSTICO CONCLUÍDO")
    print("="*60)

def mostrar_preview():
    """Mostra preview da tabela TDE"""
    if not verificar_tabela_existe():
        print("❌ Tabela TDE não encontrada. Execute primeiro: --gerar")
        return
    
    print("👁️ CARREGANDO PREVIEW DA TABELA TDE...")
    df = pd.read_csv(arquivo_csv)
    
    print("\n" + "="*60)
    print("👁️ PREVIEW - TABELA BRUTA TDE WORDGEN FASE 2")
    print("="*60)
    
    # Informações básicas
    print(f"📊 Dimensões: {len(df):,} registros × {len(df.columns):,} colunas")
    print(f"📁 Arquivo: {os.path.basename(arquivo_csv)}")
    print(f"💾 Tamanho: {os.path.getsize(arquivo_csv)/1024/1024:.2f} MB")
    
    # Colunas principais
    colunas_principais = ['Nome', 'Escola', 'Turma', 'GrupoTDE', 'Score_Pre', 'Score_Pos', 'Delta_Score', 'Questoes_Validas']
    
    print(f"\n📋 PRIMEIRAS 10 LINHAS (colunas principais):")
    print("-" * 60)
    print(df[colunas_principais].head(10).to_string(index=True))
    
    # Estatísticas rápidas
    print(f"\n📈 ESTATÍSTICAS RÁPIDAS:")
    print("-" * 30)
    print(f"Score Pré médio: {df['Score_Pre'].mean():.2f}")
    print(f"Score Pós médio: {df['Score_Pos'].mean():.2f}")
    print(f"Delta médio: {df['Delta_Score'].mean():.2f}")
    print(f"Questões válidas médio: {df['Questoes_Validas'].mean():.1f}")
    
    # Distribuição de grupos
    print(f"\n🎯 DISTRIBUIÇÃO POR GRUPO:")
    print("-" * 30)
    for grupo, count in df['GrupoTDE'].value_counts().items():
        print(f"{grupo}: {count}")
    
    # Estrutura das colunas
    print(f"\n📋 ESTRUTURA DAS COLUNAS:")
    print("-" * 30)
    print(f"Identificação: {len([c for c in df.columns if c in ['ID_Unico', 'Nome', 'Escola', 'Turma', 'GrupoTDE']])} colunas")
    print(f"Scores/Estatísticas: {len([c for c in df.columns if any(x in c for x in ['Score', 'Delta', 'Percentual', 'Questoes'])])} colunas")
    print(f"Questões TDE (P01-P40): {len([c for c in df.columns if c.startswith('P') and ('_Pre_' in c or '_Pos_' in c or '_Delta_' in c)])} colunas")
    
    print("\n" + "="*60)
    print("✅ PREVIEW CONCLUÍDO")
    print("="*60)

def mostrar_ajuda():
    """Mostra ajuda detalhada do sistema"""
    print("\n" + "="*60)
    print("❓ AJUDA - INTERFACE CLI TDE WORDGEN FASE 2")
    print("="*60)
    
    print("\n🎯 COMANDOS DISPONÍVEIS:")
    print("-" * 30)
    print("--gerar          Gera tabela bruta TDE completa")
    print("--dicionario     Gera dicionário de dados TDE")
    print("--resumo         Mostra estatísticas resumo")
    print("--preview        Mostra preview da tabela")
    print("--help           Mostra esta ajuda")
    
    print("\n📊 SOBRE O TDE (TESTE DE ESCRITA):")
    print("-" * 40)
    print("• Avalia escrita de 40 palavras específicas")
    print("• Grupos baseados na série escolar:")
    print("  - Grupo A (6º/7º): palavras 1º-4º ano")
    print("  - Grupo B (8º/9º): palavras 5º-9º ano")
    print("• Pontuação: 0 (erro) ou 1 (acerto)")
    print("• Análise pré/pós-teste com delta de mudança")
    
    print("\n📁 ARQUIVOS GERADOS:")
    print("-" * 20)
    print("• tabela_bruta_fase2_TDE_wordgen.csv")
    print("• tabela_bruta_fase2_TDE_wordgen.xlsx")
    print("• dicionario_dados_TDE_fase2.txt")
    
    print("\n🔄 FLUXO RECOMENDADO:")
    print("-" * 25)
    print("1. python PipelineTabelaBrutaTDE_CLI.py --gerar")
    print("2. python PipelineTabelaBrutaTDE_CLI.py --dicionario")
    print("3. python PipelineTabelaBrutaTDE_CLI.py --resumo")
    print("4. python PipelineTabelaBrutaTDE_CLI.py --preview")
    
    print("\n📧 SUPORTE:")
    print("-" * 15)
    print("Sistema de Análise WordGen - Fase 2")
    print("Teste de Escrita (TDE)")
    
    print("\n" + "="*60)

def main():
    """Função principal CLI"""
    parser = argparse.ArgumentParser(
        description='Interface CLI para pipeline TDE WordGen Fase 2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python PipelineTabelaBrutaTDE_CLI.py --gerar          # Gerar tabela TDE
  python PipelineTabelaBrutaTDE_CLI.py --dicionario     # Gerar documentação
  python PipelineTabelaBrutaTDE_CLI.py --resumo         # Ver estatísticas
  python PipelineTabelaBrutaTDE_CLI.py --preview        # Preview dos dados
        """
    )
    
    parser.add_argument('--gerar', action='store_true',
                       help='Gera tabela bruta TDE completa')
    parser.add_argument('--dicionario', action='store_true',
                       help='Gera dicionário de dados TDE')
    parser.add_argument('--resumo', action='store_true',
                       help='Mostra estatísticas resumo da tabela TDE')
    parser.add_argument('--preview', action='store_true',
                       help='Mostra preview da tabela TDE')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostrar ajuda
    if not any(vars(args).values()):
        mostrar_banner()
        mostrar_ajuda()
        return
    
    # Mostrar banner
    mostrar_banner()
    
    # Executar comandos
    if args.gerar:
        print("🔄 EXECUTANDO: Geração da tabela bruta TDE...")
        resultado = gerar_tabela_tde()
        if resultado is not None:
            print("✅ Tabela TDE gerada com sucesso!")
        else:
            print("❌ Erro na geração da tabela TDE")
    
    if args.dicionario:
        print("🔄 EXECUTANDO: Geração do dicionário de dados TDE...")
        resultado = gerar_dicionario_tde()
        if resultado is not None:
            print("✅ Dicionário TDE gerado com sucesso!")
        else:
            print("❌ Erro na geração do dicionário TDE")
    
    if args.resumo:
        print("🔄 EXECUTANDO: Geração de estatísticas resumo TDE...")
        mostrar_resumo()
    
    if args.preview:
        print("🔄 EXECUTANDO: Preview da tabela TDE...")
        mostrar_preview()
    
    print("\n" + "="*80)
    print("✅ OPERAÇÕES CONCLUÍDAS - CLI TDE WORDGEN FASE 2")
    print("="*80)

if __name__ == "__main__":
    main()
