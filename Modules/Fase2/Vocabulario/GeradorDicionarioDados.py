#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE DICIONÁRIO DE DADOS - VOCABULÁRIO WORDGEN FASE 2
Documenta a estrutura das colunas da tabela de vocabulário

Autor: Sistema de Análise WordGen
Data: 2024
"""

import json
import os
from datetime import datetime

# Configurações dos arquivos
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', '..', '..', 'Data')
mapping_file = os.path.join(data_dir, 'RespostaVocabulario.json')
output_file = os.path.join(data_dir, 'dicionario_dados_vocabulario_fase2.txt')

def carregar_mapeamento_vocabulario():
    """Carrega o mapeamento das questões de vocabulário"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            dados_respostas = json.load(f)
        
        mapeamento = {}
        for item in dados_respostas:
            for questao, info in item.items():
                mapeamento[questao] = info['Palavra Trabalhada']
        
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar mapeamento: {e}")
        return {}

def gerar_dicionario_vocabulario():
    """Gera o dicionário de dados de vocabulário simplificado"""
    
    mapeamento = carregar_mapeamento_vocabulario()
    
    conteudo = []
    
    # Cabeçalho simples
    conteudo.append("DICIONÁRIO DE DADOS - VOCABULÁRIO WORDGEN FASE 2")
    conteudo.append("="*55)
    conteudo.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    conteudo.append("")
    
    # Colunas de identificação
    conteudo.append("COLUNAS DE IDENTIFICAÇÃO:")
    conteudo.append("-"*30)
    
    colunas_id = [
        ("ID_Unico", "Texto", "Identificador único (Nome + Turma)"),
        ("Nome", "Texto", "Nome completo do estudante"),
        ("Escola", "Texto", "Nome da escola"),
        ("Turma", "Texto", "Série e turma do estudante"),
        ("GrupoEtario", "Texto", "6º/7º anos ou 8º/9º anos")
    ]
    
    for nome, tipo, descricao in colunas_id:
        conteudo.append(f"{nome}")
        conteudo.append(f"  Tipo: {tipo}")
        conteudo.append(f"  Descrição: {descricao}")
        conteudo.append("")
    
    # Colunas de scores
    conteudo.append("COLUNAS DE SCORES:")
    conteudo.append("-"*20)
    
    colunas_scores = [
        ("Score_Pre", "Numérico", "Pontuação total no pré-teste (0-100)"),
        ("Score_Pos", "Numérico", "Pontuação total no pós-teste (0-100)"),
        ("Delta_Score", "Numérico", "Mudança na pontuação (Pós - Pré)"),
        ("Questoes_Validas", "Numérico", "Número de questões válidas"),
        ("Percentual_Pre", "Numérico", "Percentual de acertos no pré-teste"),
        ("Percentual_Pos", "Numérico", "Percentual de acertos no pós-teste")
    ]
    
    for nome, tipo, descricao in colunas_scores:
        conteudo.append(f"{nome}")
        conteudo.append(f"  Tipo: {tipo}")
        conteudo.append(f"  Descrição: {descricao}")
        conteudo.append("")
    
    # Questões individuais
    conteudo.append("QUESTÕES DE VOCABULÁRIO (Q1-Q50):")
    conteudo.append("-"*35)
    conteudo.append("Para cada questão existem 3 colunas:")
    conteudo.append("")
    
    for i in range(1, 51):
        q_key = f'Q{i}'
        if q_key in mapeamento:
            palavra = mapeamento[q_key]
        else:
            palavra = f'Palavra_{i}'
        
        conteudo.append(f"Q{i:02d}_{palavra}:")
        conteudo.append(f"  Q{i:02d}_Pre_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Resposta no pré-teste (0=erro, 1=parcial, 2=acerto)")
        conteudo.append(f"  Q{i:02d}_Pos_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Resposta no pós-teste (0=erro, 1=parcial, 2=acerto)")
        conteudo.append(f"  Q{i:02d}_Delta_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Mudança na resposta (Pós - Pré)")
        conteudo.append("")
    
    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(conteudo))
    
    print("✅ Dicionário Vocabulário gerado!")
    print(f"📁 Arquivo: {output_file}")
    
    return output_file

def main():
    """Função principal"""
    try:
        return gerar_dicionario_vocabulario()
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    main()
