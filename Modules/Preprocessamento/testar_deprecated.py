#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE AVISOS DEPRECATED DO STREAMLIT/PLOTLY
Verifica se a correção dos parâmetros deprecated foi bem-sucedida
"""

import sys
import re
import warnings
from pathlib import Path

def verificar_parametros_deprecated():
    """Verifica se há parâmetros deprecated no código"""
    print("🔍 VERIFICANDO PARÂMETROS DEPRECATED NO DASHBOARD")
    print("=" * 60)
    
    dashboard_path = Path("Dashboard/app.py")
    
    if not dashboard_path.exists():
        print(f"❌ Arquivo não encontrado: {dashboard_path}")
        return False
    
    # Ler conteúdo do arquivo
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Padrões deprecated para verificar
    padroes_deprecated = [
        (r'st\.plotly_chart\([^)]*width\s*=\s*["\']stretch["\']', 'st.plotly_chart(..., width="stretch")'),
        (r'st\.plotly_chart\([^)]*height\s*=\s*["\']stretch["\']', 'st.plotly_chart(..., height="stretch")'),
        (r'st\.dataframe\([^)]*width\s*=\s*["\']stretch["\']', 'st.dataframe(..., width="stretch")'),
        (r'st\.dataframe\([^)]*height\s*=\s*["\']stretch["\']', 'st.dataframe(..., height="stretch")'),
    ]
    
    problemas_encontrados = []
    
    for padrao, descricao in padroes_deprecated:
        matches = re.finditer(padrao, conteudo, re.MULTILINE | re.DOTALL)
        for match in matches:
            # Encontrar linha do problema
            linha_num = conteudo[:match.start()].count('\n') + 1
            linha_conteudo = conteudo.split('\n')[linha_num - 1].strip()
            problemas_encontrados.append({
                'linha': linha_num,
                'conteudo': linha_conteudo,
                'problema': descricao
            })
    
    if problemas_encontrados:
        print(f"❌ ENCONTRADOS {len(problemas_encontrados)} PROBLEMAS:")
        for problema in problemas_encontrados:
            print(f"  Linha {problema['linha']}: {problema['problema']}")
            print(f"    Código: {problema['conteudo']}")
        return False
    else:
        print("✅ NENHUM PARÂMETRO DEPRECATED ENCONTRADO!")
    
    # Verificar se os parâmetros corretos estão sendo usados
    print(f"\n🔍 VERIFICANDO PARÂMETROS CORRETOS:")
    
    # Contar use_container_width=True
    count_container_width = len(re.findall(r'use_container_width\s*=\s*True', conteudo))
    print(f"  ✅ use_container_width=True: {count_container_width} ocorrências")
    
    # Contar st.plotly_chart
    count_plotly_chart = len(re.findall(r'st\.plotly_chart\(', conteudo))
    print(f"  📊 st.plotly_chart: {count_plotly_chart} ocorrências")
    
    # Contar st.dataframe
    count_dataframe = len(re.findall(r'st\.dataframe\(', conteudo))
    print(f"  📋 st.dataframe: {count_dataframe} ocorrências")
    
    print(f"\n📈 RESUMO DA CORREÇÃO:")
    print(f"  ✅ Todas as chamadas st.plotly_chart corrigidas")
    print(f"  ✅ Todas as chamadas st.dataframe corrigidas")
    print(f"  ✅ Parâmetro width='stretch' → use_container_width=True")
    
    return True

def verificar_imports_streamlit():
    """Verifica se os imports estão corretos"""
    print(f"\n🔍 VERIFICANDO IMPORTS:")
    
    try:
        import streamlit as st
        print(f"  ✅ Streamlit: {st.__version__}")
        
        import plotly
        print(f"  ✅ Plotly: {plotly.__version__}")
        
        # Verificar se use_container_width está disponível
        if hasattr(st, 'plotly_chart'):
            print(f"  ✅ st.plotly_chart disponível")
        
        return True
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE CORREÇÃO - PARÂMETROS DEPRECATED")
    print("=" * 70)
    print("Verificando se a correção dos avisos deprecated foi bem-sucedida")
    print()
    
    try:
        # 1. Verificar parâmetros deprecated
        sucesso_parametros = verificar_parametros_deprecated()
        
        # 2. Verificar imports
        sucesso_imports = verificar_imports_streamlit()
        
        print("\n" + "=" * 70)
        if sucesso_parametros and sucesso_imports:
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("🎯 Todas as correções aplicadas corretamente:")
            print("  • width='stretch' → use_container_width=True")
            print("  • Parâmetros deprecated removidos")
            print("  • Compatibilidade com versões mais recentes")
            return 0
        else:
            print("❌ TESTE FALHOU!")
            print("🔧 Ainda há problemas que precisam ser corrigidos")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())