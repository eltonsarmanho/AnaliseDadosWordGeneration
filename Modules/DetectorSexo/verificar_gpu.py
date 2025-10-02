#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica disponibilidade de GPU para Ollama
"""

import subprocess
import os

def verificar_nvidia_gpu():
    """Verifica se há GPU NVIDIA disponível"""
    print("="*70)
    print("VERIFICAÇÃO DE GPU")
    print("="*70)
    
    # Verifica nvidia-smi
    print("\n1️⃣  Verificando NVIDIA GPU...")
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            gpus = result.stdout.strip().split('\n')
            print(f"✅ {len(gpus)} GPU(s) NVIDIA detectada(s):")
            for i, gpu_info in enumerate(gpus):
                print(f"   GPU {i}: {gpu_info}")
            return True
        else:
            print("❌ nvidia-smi falhou")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi não encontrado (drivers NVIDIA não instalados)")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar GPU: {str(e)}")
        return False

def verificar_ollama_gpu():
    """Verifica se Ollama está configurado para usar GPU"""
    print("\n2️⃣  Verificando configuração Ollama...")
    
    try:
        # Verifica se Ollama está rodando
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Ollama está rodando")
            
            # Lista modelos disponíveis
            modelos = result.stdout.strip().split('\n')[1:]  # Pula header
            if modelos:
                print(f"\n📦 Modelos disponíveis:")
                for modelo in modelos:
                    if modelo.strip():
                        print(f"   - {modelo}")
                        
                # Verifica se o modelo brasileiro está disponível
                if any('Gemma-3-Gaia-PT-BR' in m for m in modelos):
                    print("\n✅ Modelo brasileiro Gemma-3-Gaia-PT-BR encontrado!")
                else:
                    print("\n⚠️  Modelo brasileiro não encontrado. Para instalar:")
                    print("   ollama pull brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16")
            
            return True
        else:
            print("❌ Ollama não está respondendo")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama não está instalado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar Ollama: {str(e)}")
        return False

def testar_velocidade_gpu():
    """Testa velocidade de inferência com GPU"""
    print("\n3️⃣  Testando velocidade de inferência...")
    
    import time
    
    prompt = "Qual o sexo do nome JOÃO?"
    
    try:
        print("   Executando teste com modelo...")
        start_time = time.time()
        
        result = subprocess.run(
            ['ollama', 'run', 'brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Resposta recebida em {elapsed:.2f}s")
            print(f"   Resposta: {result.stdout.strip()[:100]}...")
            
            if elapsed < 10:
                print("\n🚀 EXCELENTE! GPU está acelerando significativamente (< 10s)")
            elif elapsed < 30:
                print("\n✅ BOM! GPU está funcionando adequadamente (10-30s)")
            else:
                print("\n⚠️  GPU pode não estar sendo usada efetivamente (> 30s)")
                print("   Verifique se Ollama está configurado para usar GPU")
            
            return True
        else:
            print(f"   ❌ Erro na execução")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout (> 30s) - GPU provavelmente não está sendo usada")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def recomendar_configuracao():
    """Recomenda configuração ideal"""
    print("\n" + "="*70)
    print("RECOMENDAÇÕES")
    print("="*70)
    
    print("\n💡 Para melhor desempenho:")
    print("   1. Certifique-se de ter drivers NVIDIA atualizados")
    print("   2. Configure Ollama para usar GPU:")
    print("      export CUDA_VISIBLE_DEVICES=0")
    print("      ollama serve")
    print("   3. Use processamento paralelo (4-8 workers)")
    print("   4. Execute com GPU habilitada:")
    print("      python detector_sexo_hibrido.py")
    print("\n📊 Estimativas de tempo com 2.588 nomes:")
    print("   - Sem GPU: ~43 horas (60s por nome)")
    print("   - Com GPU: ~4-7 horas (5-10s por nome)")
    print("   - Com GPU + 4 workers: ~1-2 horas")

def main():
    gpu_ok = verificar_nvidia_gpu()
    ollama_ok = verificar_ollama_gpu()
    
    if gpu_ok and ollama_ok:
        testar_velocidade_gpu()
    
    recomendar_configuracao()

if __name__ == "__main__":
    main()
