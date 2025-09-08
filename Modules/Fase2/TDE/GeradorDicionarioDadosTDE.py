#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE DICIONÁRIO DE DADOS - TDE WORDGEN FASE 2
Documenta a estrutura das colunas da tabela TDE

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
    """Gera o dicionário de dados TDE simplificado"""
    
    mapeamento = carregar_mapeamento_tde()
    
    conteudo = []
    
    # Cabeçalho simples
    conteudo.append("DICIONÁRIO DE DADOS - TDE WORDGEN FASE 2")
    conteudo.append("="*50)
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
        ("GrupoTDE", "Texto", "Grupo A (6º/7º) ou B (8º/9º)")
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
        ("Score_Pre", "Numérico", "Pontuação total no pré-teste (0-40)"),
        ("Score_Pos", "Numérico", "Pontuação total no pós-teste (0-40)"),
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
    conteudo.append("QUESTÕES TDE (P01-P40):")
    conteudo.append("-"*25)
    conteudo.append("Para cada questão existem 3 colunas:")
    conteudo.append("")
    
    for i in range(1, 41):
        p_key = f'P{i}'
        if p_key in mapeamento:
            palavra = mapeamento[p_key]['palavra']
        else:
            palavra = f'Palavra_{i}'
        
        conteudo.append(f"P{i:02d}_{palavra}:")
        conteudo.append(f"  P{i:02d}_Pre_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Resposta no pré-teste (0=erro, 1=acerto)")
        conteudo.append(f"  P{i:02d}_Pos_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Resposta no pós-teste (0=erro, 1=acerto)")
        conteudo.append(f"  P{i:02d}_Delta_{palavra}")
        conteudo.append(f"    Tipo: Numérico")
        conteudo.append(f"    Descrição: Mudança na resposta (Pós - Pré)")
        conteudo.append("")
    
    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(conteudo))
    
    print("✅ Dicionário TDE gerado!")
    print(f"📁 Arquivo: {output_file}")
    
    return output_file

def main():
    """Função principal"""
    try:
        return gerar_dicionario_tde()
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    main()
