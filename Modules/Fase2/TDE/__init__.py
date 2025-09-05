#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO TDE - WORDGEN FASE 2
Teste de Escrita - Análise de dados pré/pós-teste

Este módulo contém todas as ferramentas para processamento e análise
dos dados do Teste de Escrita (TDE) do projeto WordGen Fase 2.

Componentes:
- PipelineDataTDE: Geração da tabela bruta com dados TDE
- GeradorDicionarioDadosTDE: Documentação detalhada dos dados
- PipelineTabelaBrutaTDE_CLI: Interface de linha de comando

Autor: Sistema de Análise WordGen
Data: 2024
"""

# Imports dos módulos principais
from .PipelineDataTDE import main as gerar_tabela_tde
from .GeradorDicionarioDadosTDE import main as gerar_dicionario_tde

# Metadados do módulo
__version__ = "1.0.0"
__author__ = "Sistema de Análise WordGen"
__description__ = "Pipeline TDE - Teste de Escrita WordGen Fase 2"

# Informações sobre os dados TDE
TDE_INFO = {
    "questoes_total": 40,
    "grupos": {
        "A": "6º/7º anos - palavras 1º-4º ano",
        "B": "8º/9º anos - palavras 5º-9º ano"
    },
    "scoring": {
        "acerto": 1,
        "erro": 0,
        "nao_respondido": "vazio"
    },
    "criterio_inclusao": "80% questões respondidas (32/40)"
}

def info():
    """Retorna informações sobre o módulo TDE"""
    return {
        "versao": __version__,
        "autor": __author__,
        "descricao": __description__,
        "dados_tde": TDE_INFO
    }

# Lista de funções públicas
__all__ = [
    'gerar_tabela_tde',
    'gerar_dicionario_tde',
    'info',
    'TDE_INFO'
]
