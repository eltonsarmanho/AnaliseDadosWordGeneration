import pandas as pd
import os
import sys
import pathlib
from datetime import datetime
import json

# Configurar caminhos
current_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
data_dir = str(current_dir) + '/Data'

def carregar_mapeamento_palavras():
    """Carrega o mapeamento das questões para palavras"""
    arquivo_respostas = os.path.join(data_dir, 'RespostaVocabulario.json')
    try:
        with open(arquivo_respostas, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # O arquivo é uma lista de objetos, vamos converter para dicionário
        mapeamento = {}
        for i, item in enumerate(data, 1):
            q_key = f'Q{i}'
            if q_key in item:
                palavra_trabalhada = item[q_key].get('Palavra Trabalhada', f'Palavra_{i}')
                palavra_correta = item[q_key].get('Palavra Correta', 'N/A')
                mapeamento[str(i)] = {
                    'palavra_trabalhada': palavra_trabalhada,
                    'palavra_correta': palavra_correta
                }
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento de palavras: {e}")
        return {}

def gerar_dicionario_dados():
    """Gera dicionário de dados completo em formato TXT"""
    
    print("="*80)
    print("GERADOR DE DICIONÁRIO DE DADOS - TABELA BRUTA FASE 2")
    print("="*80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Verificar se a tabela existe
    arquivo_excel = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.xlsx')
    arquivo_csv = os.path.join(data_dir, 'tabela_bruta_fase2_vocabulario_wordgen.csv')
    
    if not os.path.exists(arquivo_excel) and not os.path.exists(arquivo_csv):
        print("❌ Tabela bruta não encontrada!")
        print("Execute primeiro: python PipelineTabelaBrutaCLI.py --gerar")
        return
    
    # Carregar dados para obter informações das colunas
    if os.path.exists(arquivo_excel):
        print("📊 Carregando dados do arquivo Excel...")
        df = pd.read_excel(arquivo_excel, nrows=5)  # Apenas primeiras linhas para estrutura
    else:
        print("📊 Carregando dados do arquivo CSV...")
        df = pd.read_csv(arquivo_csv, nrows=5, encoding='utf-8-sig')
    
    # Carregar mapeamento de palavras
    mapeamento_palavras = carregar_mapeamento_palavras()
    print(f"   Mapeamento de palavras carregado: {len(mapeamento_palavras)} questões")
    
    # Criar dicionário de dados
    print("📝 Gerando dicionário de dados...")
    
    dicionario_texto = []
    
    # Cabeçalho
    dicionario_texto.append("="*100)
    dicionario_texto.append("DICIONÁRIO DE DADOS - TABELA BRUTA WORDGEN FASE 2")
    dicionario_texto.append("VOCABULÁRIO - ANÁLISE PRÉ/PÓS-TESTE")
    dicionario_texto.append("="*100)
    dicionario_texto.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    dicionario_texto.append(f"Fonte: {arquivo_excel if os.path.exists(arquivo_excel) else arquivo_csv}")
    dicionario_texto.append("="*100)
    
    # Informações gerais
    dicionario_texto.append("")
    dicionario_texto.append("📊 INFORMAÇÕES GERAIS")
    dicionario_texto.append("-" * 50)
    
    # Carregar dados completos para estatísticas
    if os.path.exists(arquivo_excel):
        df_completo = pd.read_excel(arquivo_excel)
    else:
        df_completo = pd.read_csv(arquivo_csv, encoding='utf-8-sig')
    
    dicionario_texto.append(f"Total de registros: {len(df_completo)}")
    dicionario_texto.append(f"Total de colunas: {len(df_completo.columns)}")
    dicionario_texto.append(f"Período dos dados: 2023-2024")
    dicionario_texto.append(f"Tipo de análise: Pré/Pós-teste pareado")
    dicionario_texto.append(f"População: Estudantes do 6º ao 9º ano")
    dicionario_texto.append(f"Intervenção: WordGen (programa de vocabulário)")
    
    # Distribuições
    dicionario_texto.append("")
    dicionario_texto.append("👥 DISTRIBUIÇÕES")
    dicionario_texto.append("-" * 50)
    
    # Por grupo etário
    grupos = df_completo['GrupoEtario'].value_counts()
    dicionario_texto.append("Por Grupo Etário:")
    for grupo, count in grupos.items():
        percent = (count / len(df_completo)) * 100
        dicionario_texto.append(f"  • {grupo}: {count} estudantes ({percent:.1f}%)")
    
    # Por escola
    dicionario_texto.append("")
    dicionario_texto.append("Por Escola:")
    escolas = df_completo['Escola'].value_counts()
    for escola, count in escolas.items():
        percent = (count / len(df_completo)) * 100
        dicionario_texto.append(f"  • {escola}: {count} estudantes ({percent:.1f}%)")
    
    # Estrutura dos dados
    dicionario_texto.append("")
    dicionario_texto.append("📋 ESTRUTURA DOS DADOS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("A tabela está organizada em três seções principais:")
    dicionario_texto.append("1. IDENTIFICAÇÃO (11 colunas): Dados do estudante e scores gerais")
    dicionario_texto.append("2. QUESTÕES PRÉ-TESTE (50 colunas): Respostas individuais no pré-teste")
    dicionario_texto.append("3. QUESTÕES PÓS-TESTE (50 colunas): Respostas individuais no pós-teste")
    dicionario_texto.append("4. QUESTÕES DELTA (50 colunas): Diferenças entre pós e pré-teste")
    dicionario_texto.append("")
    dicionario_texto.append("Total: 161 colunas")
    
    # Seção 1: Colunas de Identificação
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("SEÇÃO 1: COLUNAS DE IDENTIFICAÇÃO E SCORES GERAIS (11 colunas)")
    dicionario_texto.append("="*100)
    
    colunas_identificacao = [
        ("ID_Unico", "Texto", "Identificador único do estudante", "Formato: 'Nome_Turma' para evitar duplicatas"),
        ("Nome", "Texto", "Nome completo do estudante", "Conforme registro escolar"),
        ("Escola", "Texto", "Nome da escola", "5 escolas participantes do estudo"),
        ("Turma", "Texto", "Turma do estudante", "Formato: '6º ANO - A', '7° ANO B', etc."),
        ("GrupoEtario", "Categórica", "Classificação por faixa etária", "Valores: '6º/7º anos' ou '8º/9º anos'"),
        ("Score_Pre", "Numérica", "Pontuação total no pré-teste", "Faixa: 0-100 pontos (soma de Q1-Q50)"),
        ("Score_Pos", "Numérica", "Pontuação total no pós-teste", "Faixa: 0-100 pontos (soma de Q1-Q50)"),
        ("Delta_Score", "Numérica", "Diferença entre pós e pré-teste", "Faixa: -100 a +100 (Score_Pos - Score_Pre)"),
        ("Questoes_Validas", "Numérica", "Número de questões válidas respondidas", "Faixa: 40-50 (mínimo 80% para inclusão)"),
        ("Percentual_Pre", "Numérica", "Percentual de acerto no pré-teste", "Faixa: 0-100% (Score_Pre/100)"),
        ("Percentual_Pos", "Numérica", "Percentual de acerto no pós-teste", "Faixa: 0-100% (Score_Pos/100)")
    ]
    
    for i, (coluna, tipo, descricao, detalhes) in enumerate(colunas_identificacao, 1):
        dicionario_texto.append(f"{i:2d}. {coluna}")
        dicionario_texto.append(f"    Tipo: {tipo}")
        dicionario_texto.append(f"    Descrição: {descricao}")
        dicionario_texto.append(f"    Detalhes: {detalhes}")
        if i < len(colunas_identificacao):
            dicionario_texto.append("")
    
    # Seção 2, 3, 4: Questões
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("SEÇÃO 2-4: QUESTÕES DE VOCABULÁRIO (150 colunas)")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append("📚 ESTRUTURA DAS QUESTÕES")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("Para cada uma das 50 questões de vocabulário, há 3 colunas:")
    dicionario_texto.append("")
    dicionario_texto.append("Formato: Q##_[TIPO]_[PALAVRA]")
    dicionario_texto.append("  • Q##_Pre_[palavra]: Resposta no pré-teste")
    dicionario_texto.append("  • Q##_Pos_[palavra]: Resposta no pós-teste")
    dicionario_texto.append("  • Q##_Delta_[palavra]: Diferença (Pós - Pré)")
    dicionario_texto.append("")
    dicionario_texto.append("Onde:")
    dicionario_texto.append("  ## = Número da questão (01 a 50)")
    dicionario_texto.append("  [palavra] = Palavra trabalhada na questão")
    
    dicionario_texto.append("")
    dicionario_texto.append("📊 CODIFICAÇÃO DAS RESPOSTAS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("Valores das colunas Pre e Pos:")
    dicionario_texto.append("  0 = Erro (resposta incorreta)")
    dicionario_texto.append("  1 = Acerto parcial (resposta parcialmente correta)")
    dicionario_texto.append("  2 = Acerto total (resposta completamente correta)")
    dicionario_texto.append("  (vazio) = Não respondido ou valor inválido (D/M no original)")
    dicionario_texto.append("")
    dicionario_texto.append("Valores das colunas Delta:")
    dicionario_texto.append("  -2 = Piorou muito (de 2 para 0)")
    dicionario_texto.append("  -1 = Piorou (de 2 para 1, ou de 1 para 0)")
    dicionario_texto.append("   0 = Manteve (mesmo valor)")
    dicionario_texto.append("  +1 = Melhorou (de 0 para 1, ou de 1 para 2)")
    dicionario_texto.append("  +2 = Melhorou muito (de 0 para 2)")
    dicionario_texto.append("  (vazio) = Não foi possível calcular")
    
    # Lista completa das 50 questões
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("LISTA COMPLETA DAS 50 QUESTÕES DE VOCABULÁRIO")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append("Cada questão avalia o conhecimento de uma palavra específica.")
    dicionario_texto.append("O estudante deve escolher o significado correto entre alternativas.")
    dicionario_texto.append("")
    
    for i in range(1, 51):
        if str(i) in mapeamento_palavras:
            palavra_info = mapeamento_palavras[str(i)]
            palavra_trabalhada = palavra_info['palavra_trabalhada']
            palavra_correta = palavra_info['palavra_correta']
            
            dicionario_texto.append(f"Q{i:02d} - {palavra_trabalhada}")
            dicionario_texto.append(f"     Colunas: Q{i:02d}_Pre_{palavra_trabalhada}, Q{i:02d}_Pos_{palavra_trabalhada}, Q{i:02d}_Delta_{palavra_trabalhada}")
            dicionario_texto.append(f"     Resposta correta: {palavra_correta}")
            dicionario_texto.append("")
        else:
            dicionario_texto.append(f"Q{i:02d} - Palavra_{i}")
            dicionario_texto.append(f"     Colunas: Q{i:02d}_Pre_Palavra_{i}, Q{i:02d}_Pos_Palavra_{i}, Q{i:02d}_Delta_Palavra_{i}")
            dicionario_texto.append(f"     Resposta correta: N/A")
            dicionario_texto.append("")
    
    # Critérios de inclusão
    dicionario_texto.append("="*100)
    dicionario_texto.append("CRITÉRIOS DE INCLUSÃO E PRÉ-PROCESSAMENTO")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append("📋 CRITÉRIOS DE INCLUSÃO")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("Para ser incluído na tabela final, o estudante deve atender:")
    dicionario_texto.append("")
    dicionario_texto.append("1. PARTICIPAÇÃO COMPLETA:")
    dicionario_texto.append("   • Presença nos dados de pré-teste E pós-teste")
    dicionario_texto.append("   • Identificação válida (Nome + Turma)")
    dicionario_texto.append("")
    dicionario_texto.append("2. QUALIDADE DOS DADOS:")
    dicionario_texto.append("   • Pelo menos 40 questões respondidas (80% de 50)")
    dicionario_texto.append("   • Respostas em formato válido (0, 1, 2, D, M)")
    dicionario_texto.append("")
    dicionario_texto.append("3. CONSISTÊNCIA:")
    dicionario_texto.append("   • Mesmo estudante identificado em ambos os testes")
    dicionario_texto.append("   • Dados completos de identificação")
    
    dicionario_texto.append("")
    dicionario_texto.append("🔄 TRANSFORMAÇÕES APLICADAS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("1. VALORES DAS QUESTÕES:")
    dicionario_texto.append("   • Padronização para 0, 1, 2 (numérico)")
    dicionario_texto.append("   • Conversão D/M para valores vazios (missing)")
    dicionario_texto.append("   • Remoção de espaços e caracteres especiais")
    dicionario_texto.append("")
    dicionario_texto.append("2. IDENTIFICAÇÃO:")
    dicionario_texto.append("   • Criação de ID_Unico (Nome_Turma)")
    dicionario_texto.append("   • Classificação em grupos etários")
    dicionario_texto.append("   • Padronização de nomes de escolas")
    dicionario_texto.append("")
    dicionario_texto.append("3. CÁLCULOS:")
    dicionario_texto.append("   • Score_Pre/Pos: Soma de todas as questões válidas")
    dicionario_texto.append("   • Delta_Score: Diferença simples (Pós - Pré)")
    dicionario_texto.append("   • Percentuais: (Score / Máximo possível) × 100")
    dicionario_texto.append("   • Questões_Validas: Contagem de respostas não vazias")
    
    # Estatísticas descritivas
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("ESTATÍSTICAS DESCRITIVAS")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append("📈 SCORES GERAIS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append(f"Score Pré-teste:")
    dicionario_texto.append(f"  • Média: {df_completo['Score_Pre'].mean():.2f}")
    dicionario_texto.append(f"  • Desvio padrão: {df_completo['Score_Pre'].std():.2f}")
    dicionario_texto.append(f"  • Mínimo: {df_completo['Score_Pre'].min():.0f}")
    dicionario_texto.append(f"  • Máximo: {df_completo['Score_Pre'].max():.0f}")
    dicionario_texto.append("")
    dicionario_texto.append(f"Score Pós-teste:")
    dicionario_texto.append(f"  • Média: {df_completo['Score_Pos'].mean():.2f}")
    dicionario_texto.append(f"  • Desvio padrão: {df_completo['Score_Pos'].std():.2f}")
    dicionario_texto.append(f"  • Mínimo: {df_completo['Score_Pos'].min():.0f}")
    dicionario_texto.append(f"  • Máximo: {df_completo['Score_Pos'].max():.0f}")
    dicionario_texto.append("")
    dicionario_texto.append(f"Delta Score (Mudança):")
    dicionario_texto.append(f"  • Média: {df_completo['Delta_Score'].mean():.2f}")
    dicionario_texto.append(f"  • Desvio padrão: {df_completo['Delta_Score'].std():.2f}")
    dicionario_texto.append(f"  • Mínimo: {df_completo['Delta_Score'].min():.0f}")
    dicionario_texto.append(f"  • Máximo: {df_completo['Delta_Score'].max():.0f}")
    
    # Distribuição de mudanças
    melhoraram = len(df_completo[df_completo['Delta_Score'] > 0])
    pioraram = len(df_completo[df_completo['Delta_Score'] < 0])
    mantiveram = len(df_completo[df_completo['Delta_Score'] == 0])
    
    dicionario_texto.append("")
    dicionario_texto.append("📊 DISTRIBUIÇÃO DE MUDANÇAS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append(f"Melhoraram: {melhoraram} estudantes ({(melhoraram/len(df_completo)*100):.1f}%)")
    dicionario_texto.append(f"Pioraram: {pioraram} estudantes ({(pioraram/len(df_completo)*100):.1f}%)")
    dicionario_texto.append(f"Mantiveram: {mantiveram} estudantes ({(mantiveram/len(df_completo)*100):.1f}%)")
    
    # Informações de uso
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("INFORMAÇÕES DE USO")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append("💡 COMO USAR ESTA TABELA")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("1. ANÁLISES POR ESTUDANTE:")
    dicionario_texto.append("   • Use ID_Unico como chave primária")
    dicionario_texto.append("   • Analise Score_Pre, Score_Pos, Delta_Score para performance geral")
    dicionario_texto.append("   • Examine questões específicas para análise detalhada")
    dicionario_texto.append("")
    dicionario_texto.append("2. ANÁLISES POR GRUPO:")
    dicionario_texto.append("   • Filtre por 'Escola' para comparações entre escolas")
    dicionario_texto.append("   • Filtre por 'GrupoEtario' para análises de faixa etária")
    dicionario_texto.append("   • Use 'Turma' para análises por classe")
    dicionario_texto.append("")
    dicionario_texto.append("3. ANÁLISES POR PALAVRA:")
    dicionario_texto.append("   • Use colunas Q##_Pre_[palavra] para dificuldade inicial")
    dicionario_texto.append("   • Use colunas Q##_Pos_[palavra] para performance final")
    dicionario_texto.append("   • Use colunas Q##_Delta_[palavra] para identificar melhoria")
    dicionario_texto.append("")
    dicionario_texto.append("4. CÁLCULOS PERSONALIZADOS:")
    dicionario_texto.append("   • Effect Size: (Média_Pós - Média_Pré) / DP_Pré")
    dicionario_texto.append("   • Taxa de acerto: Score / (Questoes_Validas × 2)")
    dicionario_texto.append("   • Ganho relativo: Delta_Score / Score_Pre")
    
    dicionario_texto.append("")
    dicionario_texto.append("⚠️ LIMITAÇÕES E CUIDADOS")
    dicionario_texto.append("-" * 50)
    dicionario_texto.append("1. DADOS FALTANTES:")
    dicionario_texto.append("   • Valores vazios em questões indicam não-resposta ou D/M")
    dicionario_texto.append("   • Não interprete como zero - use análises que lidem com missing")
    dicionario_texto.append("")
    dicionario_texto.append("2. DESENHO DO ESTUDO:")
    dicionario_texto.append("   • Análise pré-pós sem grupo controle")
    dicionario_texto.append("   • Mudanças podem ter outras causas além da intervenção")
    dicionario_texto.append("   • Considere efeitos de maturação e outras variáveis")
    dicionario_texto.append("")
    dicionario_texto.append("3. INTERPRETAÇÃO:")
    dicionario_texto.append("   • Effect sizes pequenos podem ser educacionalmente relevantes")
    dicionario_texto.append("   • Considere heterogeneidade entre escolas e estudantes")
    dicionario_texto.append("   • Analise distribuição, não apenas médias")
    
    # Rodapé
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("INFORMAÇÕES TÉCNICAS")
    dicionario_texto.append("="*100)
    
    dicionario_texto.append("")
    dicionario_texto.append(f"Arquivo original PRÉ: Fase2/Pre/Avaliação de vocabulário - RelaçãoCompletaAlunos.xlsx")
    dicionario_texto.append(f"Arquivo original PÓS: Fase2/Pos/Avaliação de vocabulário - RelaçãoCompletaAlunos (...).xlsx")
    dicionario_texto.append(f"Mapeamento de palavras: RespostaVocabulario.json")
    dicionario_texto.append(f"")
    dicionario_texto.append(f"Processamento:")
    dicionario_texto.append(f"  • Software: Python 3.x com pandas")
    dicionario_texto.append(f"  • Codificação: UTF-8")
    dicionario_texto.append(f"  • Formato de saída: CSV e Excel")
    dicionario_texto.append(f"")
    dicionario_texto.append(f"Contato: Pipeline gerado automaticamente")
    dicionario_texto.append(f"Versão: 1.0")
    dicionario_texto.append(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    
    dicionario_texto.append("")
    dicionario_texto.append("="*100)
    dicionario_texto.append("FIM DO DICIONÁRIO DE DADOS")
    dicionario_texto.append("="*100)
    
    # Salvar arquivo
    arquivo_dicionario = os.path.join(data_dir, 'dicionario_dados_tabela_bruta_fase2.txt')
    
    with open(arquivo_dicionario, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dicionario_texto))
    
    print("✅ Dicionário de dados gerado com sucesso!")
    print("="*80)
    print(f"📁 Arquivo: {arquivo_dicionario}")
    print(f"📄 Linhas: {len(dicionario_texto)}")
    print(f"📊 Colunas documentadas: {len(df.columns)}")
    print(f"📚 Questões mapeadas: {len(mapeamento_palavras)}")
    print("="*80)
    
    # Mostrar preview
    print("\n📋 PREVIEW DO DICIONÁRIO:")
    print("-" * 50)
    for linha in dicionario_texto[:15]:
        print(linha)
    print("...")
    print(f"[... mais {len(dicionario_texto)-15} linhas ...]")
    
    return arquivo_dicionario

def main():
    """Função principal"""
    try:
        arquivo_gerado = gerar_dicionario_dados()
        print(f"\n🎯 Dicionário completo salvo em:")
        print(f"   {arquivo_gerado}")
        return arquivo_gerado
    except Exception as e:
        print(f"\n❌ Erro durante geração: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
