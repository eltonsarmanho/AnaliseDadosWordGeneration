#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE RELATÓRIOS VISUAIS POR FASE
Gera relatórios visuais interativos para TDE e Vocabulário
para cada fase (2, 3 e 4) usando dados longitudinais consolidados.

ATUALIZADO: Agora usa vocabulario_longitudinal.csv e TDE_longitudinal.csv
com filtros por Fase.

Autor: Sistema de Análise WordGen
Data: 2024
"""

import os
import sys
import pathlib
import subprocess
from typing import List, Dict, Tuple
import time

# Configurações de paths
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
MODULES_DIR = BASE_DIR / "Modules"
DATA_DIR = BASE_DIR / "Data"

# Scripts de relatório por fase
RELATORIO_SCRIPTS = {
    "vocabulario": {
        2: MODULES_DIR / "Fase2" / "Vocabulario" / "RelatorioVisualCompleto.py",
        3: MODULES_DIR / "Fase3" / "Vocabulario" / "RelatorioVisualCompleto.py",
        4: MODULES_DIR / "Fase4" / "Vocabulario" / "RelatorioVisualCompleto.py"
    },
    "tde": {
        2: MODULES_DIR / "Fase2" / "TDE" / "RelatorioVisualCompleto.py",
        3: MODULES_DIR / "Fase3" / "TDE" / "RelatorioVisualCompleto.py", 
        4: MODULES_DIR / "Fase4" / "TDE" / "RelatorioVisualCompleto.py"
    }
}

def verificar_scripts_existem():
    """Verifica se os scripts de relatório existem para cada fase."""
    print("🔍 Verificando scripts de relatório existentes...")
    
    scripts_existentes = {"vocabulario": {}, "tde": {}}
    scripts_faltantes = []
    
    for tipo in ["vocabulario", "tde"]:
        for fase in [2, 3, 4]:
            script_path = RELATORIO_SCRIPTS[tipo][fase]
            if script_path.exists():
                scripts_existentes[tipo][fase] = script_path
                print(f"  ✅ {tipo.upper()} Fase {fase}: {script_path.name}")
            else:
                scripts_faltantes.append((tipo, fase, script_path))
                print(f"  ⚠️  {tipo.upper()} Fase {fase}: {script_path} (NÃO EXISTE)")
    
    if scripts_faltantes:
        print(f"\n⚠️  ATENÇÃO: {len(scripts_faltantes)} scripts faltantes.")
        print("   Os scripts devem ser criados manualmente com base nos scripts da Fase 2.")
        print("   Todos os scripts agora usam arquivos longitudinais consolidados.")
    
    return scripts_existentes, scripts_faltantes

def criar_script_relatorio_fase(tipo: str, fase: int, script_path: pathlib.Path):
    """
    FUNÇÃO DESCONTINUADA: Scripts agora devem ser criados manualmente.
    
    Os scripts de relatório foram refatorados para usar arquivos longitudinais
    (vocabulario_longitudinal.csv e TDE_longitudinal.csv) com filtros por Fase.
    
    Não é mais possível gerar scripts automaticamente por substituição de texto,
    pois a estrutura de carregamento de dados foi completamente alterada.
    """
    print(f"  ⚠️  Criação automática de scripts descontinuada.")
    print(f"     Por favor, crie manualmente o script para {tipo.upper()} Fase {fase}")
    print(f"     baseando-se no script da Fase 2 como referência.")
    print(f"     Mudanças necessárias:")
    print(f"       - Usar {tipo}_longitudinal.csv")
    print(f"       - Filtrar por Fase={fase}")
    print(f"       - Adaptar colunas Q{{i}}_Pre e Q{{i}}_Pos")
    raise NotImplementedError(
        f"Script {tipo} Fase {fase} deve ser criado manualmente. "
        f"Veja os scripts das Fases 2, 3 e 4 como referência."
    )

def adaptar_script_vocabulario(content: str, fase: int) -> str:
    """
    FUNÇÃO DESCONTINUADA: Não é mais possível adaptar scripts automaticamente.
    
    Os scripts foram refatorados para usar formato longitudinal, o que requer
    mudanças estruturais que não podem ser feitas por substituição de texto.
    """
    raise NotImplementedError(
        "Adaptação automática de scripts descontinuada. "
        "Scripts devem ser criados manualmente usando formato longitudinal."
    )

def adaptar_script_tde(content: str, fase: int) -> str:
    """
    FUNÇÃO DESCONTINUADA: Não é mais possível adaptar scripts automaticamente.
    
    Os scripts foram refatorados para usar formato longitudinal, o que requer
    mudanças estruturais que não podem ser feitas por substituição de texto.
    """
    raise NotImplementedError(
        "Adaptação automática de scripts descontinuada. "
        "Scripts devem ser criados manualmente usando formato longitudinal."
    )

def executar_relatorio(tipo: str, fase: int, script_path: pathlib.Path, interativo: bool = True) -> bool:
    """Executa um script de relatório e retorna True se bem-sucedido."""
    modo = "INTERATIVO" if interativo else "PADRÃO"
    print(f"\n🚀 Executando relatório {tipo.upper()} Fase {fase} (modo {modo})...")
    
    try:
        # Mudar para o diretório do script
        old_cwd = os.getcwd()
        os.chdir(script_path.parent)
        
        # Comando base
        comando = [sys.executable, script_path.name]
        
        # Adicionar flag --interativo se solicitado
        if interativo:
            comando.append("--interativo")
        
        # Executar script
        result = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        # Restaurar diretório
        os.chdir(old_cwd)
        
        if result.returncode == 0:
            print(f"  ✅ Relatório {tipo.upper()} Fase {fase} gerado com sucesso!")
            if result.stdout:
                print(f"  📄 Output: {result.stdout[-200:]}...")  # Últimos 200 chars
            return True
        else:
            print(f"  ❌ Erro ao gerar relatório {tipo.upper()} Fase {fase}")
            print(f"  📄 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Timeout ao executar relatório {tipo.upper()} Fase {fase}")
        return False
    except Exception as e:
        print(f"  ❌ Exceção ao executar relatório {tipo.upper()} Fase {fase}: {e}")
        return False

def gerar_todos_relatorios(interativo: bool = True):
    """Gera todos os relatórios visuais para todas as fases."""
    modo = "INTERATIVO" if interativo else "PADRÃO"
    print(f"🎯 GERANDO TODOS OS RELATÓRIOS VISUAIS (MODO {modo})")
    print("=" * 60)
    
    # Verificar scripts existentes
    scripts_existentes, scripts_faltantes = verificar_scripts_existem()
    
    # Avisar sobre scripts faltantes (não tenta mais criar automaticamente)
    if scripts_faltantes:
        print(f"\n⚠️  AVISO: {len(scripts_faltantes)} scripts faltantes detectados:")
        for tipo, fase, script_path in scripts_faltantes:
            print(f"     - {tipo.upper()} Fase {fase}: {script_path}")
        print("\n   Esses scripts devem ser criados manualmente.")
        print("   Continuando com os scripts disponíveis...\n")
    
    # Executar relatórios
    resultados = {}
    total_scripts = sum(len(fases) for fases in scripts_existentes.values())
    executados = 0
    sucesso = 0
    
    if total_scripts == 0:
        print("\n❌ ERRO: Nenhum script de relatório disponível!")
        print("   Por favor, verifique se os scripts existem em:")
        print(f"   - {MODULES_DIR / 'Fase2'}")
        print(f"   - {MODULES_DIR / 'Fase3'}")
        print(f"   - {MODULES_DIR / 'Fase4'}")
        return {}
    
    print(f"\n🚀 Executando {total_scripts} relatórios...")
    
    for tipo in ["vocabulario", "tde"]:
        resultados[tipo] = {}
        for fase in [2, 3, 4]:
            if fase in scripts_existentes[tipo]:
                script_path = scripts_existentes[tipo][fase]
                executados += 1
                
                print(f"\n[{executados}/{total_scripts}] Executando {tipo.upper()} Fase {fase}...")
                
                if executar_relatorio(tipo, fase, script_path, interativo):
                    resultados[tipo][fase] = "✅ Sucesso"
                    sucesso += 1
                else:
                    resultados[tipo][fase] = "❌ Erro"
                
                # Pequena pausa entre execuções
                time.sleep(1)
            else:
                resultados[tipo][fase] = "⚠️  Script não disponível"
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DA EXECUÇÃO")
    print("=" * 60)
    
    for tipo in ["vocabulario", "tde"]:
        print(f"\n{tipo.upper()}:")
        for fase in [2, 3, 4]:
            status = resultados[tipo].get(fase, "❌ Não processado")
            print(f"  Fase {fase}: {status}")
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"  Total de scripts disponíveis: {total_scripts}")
    print(f"  Executados: {executados}")
    print(f"  Sucessos: {sucesso}")
    print(f"  Erros: {executados - sucesso}")
    print(f"  Taxa de sucesso: {(sucesso/executados*100):.1f}%" if executados > 0 else "N/A")
    
    return resultados

def listar_relatorios_gerados():
    """Lista todos os relatórios HTML gerados."""
    print("\n📂 RELATÓRIOS HTML GERADOS:")
    print("-" * 40)
    
    # Padrões de arquivo (priorizando interativos)
    padroes = [
        "*_interativo.html",  # Interativos primeiro
        "relatorio_visual_wordgen_fase*.html",
        "relatorio_visual_TDE_fase*.html"
    ]
    
    relatorios = []
    for padrao in padroes:
        relatorios.extend(DATA_DIR.glob(padrao))
    
    if relatorios:
        for arquivo in sorted(relatorios):
            tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
            print(f"  📄 {arquivo.name} ({tamanho_mb:.1f} MB)")
    else:
        print("  ⚠️  Nenhum relatório HTML encontrado")
    
    return relatorios

def main():
    """Função principal."""
    import argparse
    
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description='Gera relatórios visuais para todas as fases (2, 3, 4) do WordGen.\n'
                    'NOTA: Scripts usam arquivos longitudinais consolidados.'
    )
    parser.add_argument('--padrao', action='store_true',
                       help='Gera relatórios no formato padrão (por padrão usa formato interativo)')
    parser.add_argument('--interativo', action='store_true', default=True,
                       help='Gera relatórios no formato interativo (padrão)')
    
    args = parser.parse_args()
    
    # Determinar modo (interativo é padrão, exceto se --padrao for especificado)
    interativo = not args.padrao
    
    print("🎯 GERADOR DE RELATÓRIOS VISUAIS POR FASE")
    print("=" * 70)
    print(f"📁 Diretório base: {BASE_DIR}")
    print(f"📊 Diretório de dados: {DATA_DIR}")
    print(f"🔧 Diretório de módulos: {MODULES_DIR}")
    print(f"🎨 Modo: {'INTERATIVO' if interativo else 'PADRÃO'}")
    print(f"📦 Fonte de dados: vocabulario_longitudinal.csv e TDE_longitudinal.csv")
    
    try:
        # Verificar se arquivos longitudinais existem
        dashboard_dir = BASE_DIR / "Dashboard"
        vocab_longitudinal = dashboard_dir / "vocabulario_longitudinal.csv"
        tde_longitudinal = dashboard_dir / "TDE_longitudinal.csv"
        
        if not vocab_longitudinal.exists():
            print(f"\n⚠️  AVISO: Arquivo não encontrado: {vocab_longitudinal}")
        else:
            print(f"✅ Vocabulário longitudinal encontrado")
            
        if not tde_longitudinal.exists():
            print(f"\n⚠️  AVISO: Arquivo não encontrado: {tde_longitudinal}")
        else:
            print(f"✅ TDE longitudinal encontrado")
        
        # Gerar relatórios
        resultados = gerar_todos_relatorios(interativo)
        
        # Listar arquivos gerados
        relatorios = listar_relatorios_gerados()
        
        print("\n✅ PROCESSO CONCLUÍDO!")
        print("=" * 70)
        print("🎯 Próximos passos:")
        print("  1. Abrir os relatórios HTML no navegador")
        print("  2. Verificar a qualidade dos gráficos e análises")
        print("  3. Ajustar configurações se necessário")
        print("\n📌 NOTA IMPORTANTE:")
        print("  Todos os relatórios agora usam dados longitudinais consolidados")
        print("  com filtros por Fase (2, 3 ou 4).")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())