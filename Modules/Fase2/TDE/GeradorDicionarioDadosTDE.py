#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE DICIONÁRIO DE DADOS - TDE WORDGEN FASE 2
Cria documentação detalhada da tabela bruta gerada pelo pipeline TDE

Autor: Sistema de Análise WordGen
Data: 2024
"""

import json
import os
from datetime import datetime

# Configurações dos arquivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', '..', '..', 'Data')
mapping_file = os.path.join(data_dir, 'RespostaTED.json')
output_file = os.path.join(data_dir, 'dicionario_dados_TDE_fase2.txt')

print("="*80)
print("GERADOR DE DICIONÁRIO DE DADOS - TDE WORDGEN FASE 2")
print("DOCUMENTAÇÃO DA TABELA BRUTA - TESTE DE ESCRITA")
print("="*80)
print(f"Data/Hora de execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

def carregar_mapeamento_tde():
    """Carrega o mapeamento das questões TDE"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mapeamento_completo = {}
        
        for item in data:
            for pergunta_key, pergunta_data in item.items():
                if 'Pergunta' in pergunta_key:
                    numero = pergunta_key.split(' ')[1]
                    palavra = pergunta_data.get('Palavra Trabalhada', f'Palavra_{numero}')
                    grupo = pergunta_data.get('Grupo', 'A')
                    
                    mapeamento_completo[f'P{numero}'] = {
                        'palavra': palavra,
                        'grupo': grupo
                    }
        
        return mapeamento_completo
    except Exception as e:
        print(f"Erro ao carregar mapeamento TDE: {e}")
        return {}

def gerar_dicionario_tde():
    """Gera o dicionário de dados TDE"""
    
    print("1. CARREGANDO MAPEAMENTO TDE...")
    mapeamento = carregar_mapeamento_tde()
    print(f"   Mapeamento carregado: {len(mapeamento)} questões")
    
    print("2. GERANDO DICIONÁRIO DE DADOS TDE...")
    
    conteudo = []
    
    # Cabeçalho
    conteudo.append("="*80)
    conteudo.append("DICIONÁRIO DE DADOS - TDE WORDGEN FASE 2")
    conteudo.append("TESTE DE ESCRITA - ANÁLISE PRÉ/PÓS-TESTE")
    conteudo.append("="*80)
    conteudo.append(f"Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    conteudo.append("="*80)
    conteudo.append("")
    
    # Visão geral
    conteudo.append("1. VISÃO GERAL")
    conteudo.append("-" * 40)
    conteudo.append("Esta tabela contém os dados brutos processados do Teste de Escrita (TDE)")
    conteudo.append("do projeto WordGen - Fase 2, incluindo dados de pré-teste e pós-teste.")
    conteudo.append("")
    conteudo.append("ESTRUTURA: 530 registros × 251 colunas")
    conteudo.append("PERÍODO: Fase 2 do projeto WordGen (2023-2024)")
    conteudo.append("POPULAÇÃO: Estudantes do 6º ao 9º ano do ensino fundamental")
    conteudo.append("GRUPOS TDE:")
    conteudo.append("  - Grupo A: 6º e 7º anos (palavras de 1º-4º ano)")
    conteudo.append("  - Grupo B: 8º e 9º anos (palavras de 5º-9º ano)")
    conteudo.append("")
    
    # Metodologia TDE
    conteudo.append("2. METODOLOGIA TDE")
    conteudo.append("-" * 40)
    conteudo.append("O Teste de Escrita (TDE) avalia a capacidade de escrita de palavras")
    conteudo.append("por meio de 40 questões específicas. A classificação por grupos é:")
    conteudo.append("")
    conteudo.append("GRUPO A (6º/7º anos):")
    conteudo.append("  - Palavras de dificuldade 1º-4º ano")
    conteudo.append("  - Focado em vocabulário básico")
    conteudo.append("  - N = 383 estudantes")
    conteudo.append("")
    conteudo.append("GRUPO B (8º/9º anos):")
    conteudo.append("  - Palavras de dificuldade 5º-9º ano")
    conteudo.append("  - Focado em vocabulário avançado")
    conteudo.append("  - N = 147 estudantes")
    conteudo.append("")
    conteudo.append("CRITÉRIOS DE INCLUSÃO:")
    conteudo.append("  - Participação em pré-teste E pós-teste")
    conteudo.append("  - Pelo menos 80% das questões respondidas (32/40)")
    conteudo.append("  - Dados válidos de identificação")
    conteudo.append("")
    
    # Colunas de identificação
    conteudo.append("3. COLUNAS DE IDENTIFICAÇÃO")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("ID_Unico")
    conteudo.append("  Tipo: Texto")
    conteudo.append("  Descrição: Identificador único formado por Nome + Turma")
    conteudo.append("  Formato: 'NOME_COMPLETO_TURMA'")
    conteudo.append("  Uso: Chave primária para relacionar dados pré/pós-teste")
    conteudo.append("")
    conteudo.append("Nome")
    conteudo.append("  Tipo: Texto")
    conteudo.append("  Descrição: Nome completo do estudante")
    conteudo.append("  Uso: Identificação individual do participante")
    conteudo.append("")
    conteudo.append("Escola")
    conteudo.append("  Tipo: Texto categórico")
    conteudo.append("  Descrição: Nome da instituição de ensino")
    conteudo.append("  Valores possíveis:")
    conteudo.append("    - EMEB PADRE ANCHIETA")
    conteudo.append("    - EMEB NATANAEL DA SILVA")
    conteudo.append("    - EMEF PADRE JOSÉ DOS SANTOS MOUSINHO")
    conteudo.append("    - EMEB PROFESSOR RICARDO VIEIRA DE LIMA")
    conteudo.append("    - EMEB PROFESSORA MARIA QUEIROZ FERRO")
    conteudo.append("")
    conteudo.append("Turma")
    conteudo.append("  Tipo: Texto categórico")
    conteudo.append("  Descrição: Série/ano e turma do estudante")
    conteudo.append("  Formato: 'Nº ANO [TURMA]' (ex: '6º ANO - A')")
    conteudo.append("")
    conteudo.append("GrupoTDE")
    conteudo.append("  Tipo: Texto categórico")
    conteudo.append("  Descrição: Classificação automática baseada na série")
    conteudo.append("  Valores:")
    conteudo.append("    - 'Grupo A (6º/7º anos)': Palavras básicas")
    conteudo.append("    - 'Grupo B (8º/9º anos)': Palavras avançadas")
    conteudo.append("    - 'Indefinido': Turmas não classificadas")
    conteudo.append("")
    
    # Colunas de scores
    conteudo.append("4. COLUNAS DE SCORES TDE")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("Score_Pre")
    conteudo.append("  Tipo: Numérico (0-40)")
    conteudo.append("  Descrição: Pontuação total no pré-teste TDE")
    conteudo.append("  Cálculo: Soma de acertos nas 40 questões")
    conteudo.append("  Interpretação: Maior valor = melhor desempenho inicial")
    conteudo.append("")
    conteudo.append("Score_Pos")
    conteudo.append("  Tipo: Numérico (0-40)")
    conteudo.append("  Descrição: Pontuação total no pós-teste TDE")
    conteudo.append("  Cálculo: Soma de acertos nas 40 questões")
    conteudo.append("  Interpretação: Maior valor = melhor desempenho final")
    conteudo.append("")
    conteudo.append("Delta_Score")
    conteudo.append("  Tipo: Numérico (-40 a +40)")
    conteudo.append("  Descrição: Mudança na pontuação (Pós - Pré)")
    conteudo.append("  Interpretação:")
    conteudo.append("    - Positivo: Melhora no desempenho")
    conteudo.append("    - Negativo: Piora no desempenho")
    conteudo.append("    - Zero: Desempenho mantido")
    conteudo.append("")
    conteudo.append("Questoes_Validas")
    conteudo.append("  Tipo: Numérico (32-40)")
    conteudo.append("  Descrição: Número de questões com dados válidos")
    conteudo.append("  Critério: Mínimo de 32 questões (80%) para inclusão")
    conteudo.append("")
    conteudo.append("Percentual_Pre")
    conteudo.append("  Tipo: Numérico (0-100)")
    conteudo.append("  Descrição: Percentual de acertos no pré-teste")
    conteudo.append("  Cálculo: (Score_Pre / Questoes_Validas) × 100")
    conteudo.append("")
    conteudo.append("Percentual_Pos")
    conteudo.append("  Tipo: Numérico (0-100)")
    conteudo.append("  Descrição: Percentual de acertos no pós-teste")
    conteudo.append("  Cálculo: (Score_Pos / Questoes_Validas) × 100")
    conteudo.append("")
    
    # Questões individuais
    conteudo.append("5. QUESTÕES INDIVIDUAIS TDE (P01-P40)")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("Para cada questão TDE (P01 a P40), existem 3 colunas:")
    conteudo.append("")
    conteudo.append("Formato das colunas:")
    conteudo.append("  - PXX_Pre_[PALAVRA]: Resposta no pré-teste")
    conteudo.append("  - PXX_Pos_[PALAVRA]: Resposta no pós-teste")
    conteudo.append("  - PXX_Delta_[PALAVRA]: Mudança (Pós - Pré)")
    conteudo.append("")
    conteudo.append("Valores possíveis:")
    conteudo.append("  - 0: Erro (escrita incorreta)")
    conteudo.append("  - 1: Acerto (escrita correta)")
    conteudo.append("  - vazio: Questão não respondida ou inválida")
    conteudo.append("")
    conteudo.append("MAPEAMENTO COMPLETO DAS QUESTÕES TDE:")
    conteudo.append("-" * 60)
    
    # Listar todas as questões por grupo
    for i in range(1, 41):
        p_key = f'P{i}'
        if p_key in mapeamento:
            palavra = mapeamento[p_key]['palavra']
            grupo = mapeamento[p_key]['grupo']
            conteudo.append(f"P{i:02d} - {palavra} (Grupo {grupo})")
        else:
            conteudo.append(f"P{i:02d} - Palavra_{i} (Grupo não definido)")
    
    conteudo.append("")
    
    # Estatísticas resumo
    conteudo.append("6. ESTATÍSTICAS RESUMO")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("DISTRIBUIÇÃO POR GRUPO:")
    conteudo.append("  Grupo A (6º/7º anos): 383 estudantes (72.3%)")
    conteudo.append("  Grupo B (8º/9º anos): 147 estudantes (27.7%)")
    conteudo.append("")
    conteudo.append("ESTATÍSTICAS DOS SCORES:")
    conteudo.append("  Score Pré-teste: Média=15.02, DP=7.13, Min=0, Max=32")
    conteudo.append("  Score Pós-teste: Média=10.66, DP=8.41, Min=0, Max=34")
    conteudo.append("  Delta Score: Média=-4.36, DP=8.42, Min=-27, Max=21")
    conteudo.append("")
    conteudo.append("OBSERVAÇÃO: A média negativa do delta indica tendência")
    conteudo.append("de diminuição no desempenho TDE entre pré e pós-teste.")
    conteudo.append("")
    
    # Considerações técnicas
    conteudo.append("7. CONSIDERAÇÕES TÉCNICAS")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("LIMPEZA DE DADOS:")
    conteudo.append("  - Remoção de registros com menos de 80% das questões")
    conteudo.append("  - Exclusão de estudantes sem pré-teste OU pós-teste")
    conteudo.append("  - Padronização dos valores (0/1 para erro/acerto)")
    conteudo.append("")
    conteudo.append("LIMITAÇÕES:")
    conteudo.append("  - Dados baseados apenas em presença/ausência nos testes")
    conteudo.append("  - Não inclui análise qualitativa dos erros")
    conteudo.append("  - Grupos definidos automaticamente por série")
    conteudo.append("")
    conteudo.append("USO RECOMENDADO:")
    conteudo.append("  - Análises estatísticas de mudança pré/pós-teste")
    conteudo.append("  - Comparações entre grupos e escolas")
    conteudo.append("  - Identificação de padrões de desempenho")
    conteudo.append("  - Base para análises de effect size")
    conteudo.append("")
    
    # Rodapé
    conteudo.append("8. INFORMAÇÕES DO ARQUIVO")
    conteudo.append("-" * 40)
    conteudo.append("")
    conteudo.append("Arquivo fonte: tabela_bruta_fase2_TDE_wordgen.csv")
    conteudo.append("Formato: CSV com separador vírgula, encoding UTF-8")
    conteudo.append("Total de registros: 530")
    conteudo.append("Total de colunas: 251")
    conteudo.append("")
    conteudo.append("Arquivos relacionados:")
    conteudo.append("  - tabela_bruta_fase2_TDE_wordgen.xlsx (Excel)")
    conteudo.append("  - RespostaTED.json (mapeamento questões)")
    conteudo.append("  - Dados originais em Data/Fase2/")
    conteudo.append("")
    conteudo.append("="*80)
    conteudo.append("FIM DO DICIONÁRIO DE DADOS TDE")
    conteudo.append("="*80)
    
    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(conteudo))
    
    print("3. SALVANDO DICIONÁRIO TDE...")
    print("="*80)
    print("✅ DICIONÁRIO DE DADOS TDE GERADO COM SUCESSO!")
    print("="*80)
    print(f"📁 Arquivo: {output_file}")
    print(f"📄 Total de linhas: {len(conteudo)}")
    print("="*80)
    
    return output_file

def main():
    """Função principal"""
    try:
        arquivo = gerar_dicionario_tde()
        print(f"\n✅ Dicionário TDE gerado com sucesso!")
        print(f"📋 Documentação completa da tabela TDE disponível")
        return arquivo
    except Exception as e:
        print(f"\n❌ Erro ao gerar dicionário TDE: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
