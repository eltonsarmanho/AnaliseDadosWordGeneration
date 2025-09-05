import pandas as pd
import os
import pathlib
from datetime import datetime

# Configurar caminhos
current_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
data_dir = str(current_dir) + '/Data'

def gerar_resumo_tabela_bruta():
    """Gera resumo executivo da tabela bruta gerada"""
    
    arquivo_csv = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.csv')
    
    if not os.path.exists(arquivo_csv):
        print("❌ Arquivo de tabela bruta não encontrado!")
        print("Execute primeiro o PipelineTabelaBruta.py")
        return
    
    print("="*80)
    print("RESUMO EXECUTIVO - TABELA BRUTA FASE 2")
    print("="*80)
    print(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Carregar dados
    df = pd.read_csv(arquivo_csv, encoding='utf-8-sig')
    
    print(f"📊 INFORMAÇÕES GERAIS")
    print(f"   Total de registros: {len(df)}")
    print(f"   Total de colunas: {len(df.columns)}")
    print(f"   Tamanho do arquivo: {os.path.getsize(arquivo_csv) / 1024:.1f} KB")
    
    print(f"\n📋 ESTRUTURA DOS DADOS")
    print(f"   Colunas de identificação: 11")
    print(f"   Colunas de questões (Pre/Pos/Delta): {(len(df.columns) - 11)}")
    print(f"   Total de questões analisadas: 50")
    
    print(f"\n👥 DISTRIBUIÇÃO POR GRUPO ETÁRIO")
    grupos = df['GrupoEtario'].value_counts()
    for grupo, count in grupos.items():
        percent = (count / len(df)) * 100
        print(f"   {grupo}: {count} estudantes ({percent:.1f}%)")
    
    print(f"\n🏫 DISTRIBUIÇÃO POR ESCOLA")
    escolas = df['Escola'].value_counts()
    for escola, count in escolas.items():
        percent = (count / len(df)) * 100
        print(f"   {escola}: {count} estudantes ({percent:.1f}%)")
    
    print(f"\n📈 ESTATÍSTICAS DE SCORES")
    print(f"   Score Pré - Média: {df['Score_Pre'].mean():.2f} (DP: {df['Score_Pre'].std():.2f})")
    print(f"   Score Pós - Média: {df['Score_Pos'].mean():.2f} (DP: {df['Score_Pos'].std():.2f})")
    print(f"   Delta Score - Média: {df['Delta_Score'].mean():.2f} (DP: {df['Delta_Score'].std():.2f})")
    
    print(f"\n📊 DISTRIBUIÇÃO DE MUDANÇAS")
    melhoraram = len(df[df['Delta_Score'] > 0])
    pioraram = len(df[df['Delta_Score'] < 0])
    mantiveram = len(df[df['Delta_Score'] == 0])
    
    print(f"   Melhoraram: {melhoraram} ({(melhoraram/len(df)*100):.1f}%)")
    print(f"   Pioraram: {pioraram} ({(pioraram/len(df)*100):.1f}%)")
    print(f"   Mantiveram: {mantiveram} ({(mantiveram/len(df)*100):.1f}%)")
    
    print(f"\n🎯 QUALIDADE DOS DADOS")
    print(f"   Questões válidas por estudante: {df['Questoes_Validas'].mean():.1f}")
    print(f"   Percentual médio no pré-teste: {df['Percentual_Pre'].mean():.1f}%")
    print(f"   Percentual médio no pós-teste: {df['Percentual_Pos'].mean():.1f}%")
    
    print(f"\n📝 COLUNAS DISPONÍVEIS")
    print(f"   Identificação: ID_Unico, Nome, Escola, Turma, GrupoEtario")
    print(f"   Scores: Score_Pre, Score_Pos, Delta_Score, Questoes_Validas")
    print(f"   Percentuais: Percentual_Pre, Percentual_Pos")
    print(f"   Questões individuais: Q01 a Q50 (Pre/Pos/Delta) com nomes das palavras")
    
    # Mostrar algumas palavras como exemplo
    colunas_questoes = [col for col in df.columns if col.startswith('Q') and '_Pre_' in col]
    print(f"\n📚 EXEMPLOS DE PALAVRAS ANALISADAS")
    for i, col in enumerate(colunas_questoes[:10], 1):
        palavra = col.split('_Pre_')[1]
        print(f"   Q{i:02d}: {palavra}")
    
    print(f"\n💾 ARQUIVOS GERADOS")
    arquivo_xlsx = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.xlsx')
    print(f"   📁 CSV: tabela_bruta_fase2_vocabulario_wordgen.csv")
    print(f"   📁 Excel: tabela_bruta_fase2_vocabulario_wordgen.xlsx")
    
    print(f"\n🔍 COMO USAR OS DADOS")
    print(f"   • Análises por estudante individual: usar ID_Unico")
    print(f"   • Comparações por escola: filtrar coluna 'Escola'")
    print(f"   • Análise por faixa etária: filtrar coluna 'GrupoEtario'")
    print(f"   • Análise de palavras específicas: usar colunas Q##_Pre/Pos/Delta")
    print(f"   • Cálculos personalizados: usar Score_Pre, Score_Pos, Delta_Score")
    
    print("="*80)
    print("✅ RESUMO CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    gerar_resumo_tabela_bruta()
