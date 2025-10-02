#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa detecção de nomes específicos problemáticos
"""

import sys
sys.path.insert(0, '/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/DetectorSexo')

from detector_sexo_hibrido import DetectorSexoHibrido

def testar_nomes():
    """Testa nomes específicos reportados como problemáticos"""
    
    print("="*70)
    print("TESTE DE NOMES ESPECÍFICOS")
    print("="*70)
    
    detector = DetectorSexoHibrido()
    
    # Verifica se Ollama está disponível
    usar_ollama = detector.verificar_ollama_disponivel()
    
    if usar_ollama:
        print("\n✅ Ollama DISPONÍVEL - Teste com máxima precisão")
    else:
        print("\n⚠️  Ollama NÃO DISPONÍVEL - Teste com gender-guesser + regras")
    
    # Casos de teste
    casos_teste = [
        ("ADRYEL BISPO DOS SANTOS", "Masculino"),  # Reportado como Feminino incorretamente
        ("ADRYEL VIEIRA MARTINIANO DA SILVA", "Masculino"),  # Detectado corretamente como Masculino
        ("MARIA DA SILVA", "Feminino"),  # Caso óbvio feminino
        ("JOÃO PEDRO", "Masculino"),  # Caso óbvio masculino
        ("ALEX SANTOS", "Masculino"),  # Nome andrógino
    ]
    
    print("\n" + "="*70)
    print("RESULTADOS DOS TESTES")
    print("="*70)
    
    acertos = 0
    total = len(casos_teste)
    
    for nome, sexo_esperado in casos_teste:
        sexo_detectado, confianca, metodo = detector.detectar_sexo(nome, usar_ollama=usar_ollama)
        
        correto = "✅" if sexo_detectado == sexo_esperado else "❌"
        acertos += 1 if sexo_detectado == sexo_esperado else 0
        
        print(f"\n{correto} Nome: {nome}")
        print(f"   Esperado: {sexo_esperado}")
        print(f"   Detectado: {sexo_detectado}")
        print(f"   Confiança: {confianca:.2f}")
        print(f"   Método: {metodo}")
    
    print("\n" + "="*70)
    print(f"RESULTADO FINAL: {acertos}/{total} acertos ({acertos/total*100:.1f}%)")
    print("="*70)
    
    # Recomendação
    if usar_ollama and acertos == total:
        print("\n✅ RECOMENDAÇÃO: Processar dataset completo com Ollama habilitado")
        print("   Comando: python detector_sexo_hibrido.py")
    elif not usar_ollama:
        print("\n⚠️  ATENÇÃO: Ollama não está disponível")
        print("   Para máxima precisão, instale e execute Ollama:")
        print("   1. Instalar: https://ollama.ai")
        print("   2. Executar: ollama serve")
        print("   3. Baixar modelo: ollama pull llama3.2")

if __name__ == "__main__":
    testar_nomes()
