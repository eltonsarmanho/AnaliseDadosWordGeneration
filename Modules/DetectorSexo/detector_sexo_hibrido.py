#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Sexo Híbrido - Gender Guesser + Ollama
Processa nomes de alunos e adiciona coluna de sexo aos CSVs longitudinais
"""

import pandas as pd
import gender_guesser.detector as gender
import unicodedata
import re
from pathlib import Path
import json
import subprocess
from typing import Dict, Tuple, Optional
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class DetectorSexoHibrido:
    """
    Detector de sexo híbrido que combina:
    1. Gender Guesser (biblioteca especializada)
    2. Regras heurísticas para nomes brasileiros
    3. Ollama (LLM local) para casos ambíguos
    """
    
    def __init__(self, usar_gpu: bool = True, num_workers: int = 4):
        """Inicializa detector
        
        Args:
            usar_gpu: Se deve usar GPU no Ollama (se disponível)
            num_workers: Número de workers paralelos para processamento
        """
        self.detector_gender = gender.Detector(case_sensitive=False)
        
        # Cache para evitar reprocessamento
        self.cache_nomes = {}
        
        # Configuração de GPU e paralelização
        self.usar_gpu = usar_gpu
        self.num_workers = num_workers
        
        # Dicionário de correções manuais (nomes conhecidos problemáticos)
        self.correcoes_manuais = {
            'ADRYEL': 'Masculino',
            'ADRIEL': 'Masculino',
            'ADERLAN': 'Masculino',
            # Adicione mais conforme necessário
        }
        
        # Estatísticas
        self.stats = {
            'total': 0,
            'correcao_manual': 0,
            'gender_guesser': 0,
            'regras_heuristicas': 0,
            'ollama': 0,
            'indeterminado': 0
        }
    
    def normalizar_nome(self, nome: str) -> str:
        """
        Normaliza nome removendo acentos e caracteres especiais.
        
        Args:
            nome: Nome a ser normalizado
            
        Returns:
            Nome normalizado em maiúsculas
        """
        if not isinstance(nome, str):
            return ""
        
        # Remove acentos
        nome_nfd = unicodedata.normalize('NFD', nome)
        nome_sem_acento = ''.join(ch for ch in nome_nfd if unicodedata.category(ch) != 'Mn')
        
        # Maiúsculas e remove espaços extras
        return nome_sem_acento.upper().strip()
    
    def extrair_primeiro_nome(self, nome_completo: str) -> str:
        """
        Extrai primeiro nome do nome completo.
        
        Args:
            nome_completo: Nome completo do aluno
            
        Returns:
            Primeiro nome extraído
        """
        if not nome_completo:
            return ""
        
        # Remove conectores comuns
        conectores = ['DA', 'DE', 'DO', 'DAS', 'DOS', 'E']
        
        partes = nome_completo.split()
        if not partes:
            return ""
        
        # Retorna primeiro nome que não seja conector
        for parte in partes:
            if parte not in conectores and len(parte) > 1:
                return parte
        
        return partes[0] if partes else ""
    
    def aplicar_regras_sufixo(self, primeiro_nome: str) -> Optional[str]:
        """
        Aplica regras heurísticas baseadas em sufixos comuns de nomes brasileiros.
        
        Args:
            primeiro_nome: Primeiro nome a analisar
            
        Returns:
            'Masculino', 'Feminino' ou None se indeterminado
        """
        nome_lower = primeiro_nome.lower()
        
        # Regras para nomes femininos
        sufixos_femininos = [
            'a', 'ana', 'ina', 'ene', 'elly', 'elle', 'lia', 'ice', 'ane', 'aine',
            'elle', 'ete', 'ette', 'ita', 'ilda', 'isa', 'essa'
        ]
        
        # Regras para nomes masculinos
        sufixos_masculinos = [
            'o', 'os', 'aldo', 'ando', 'ardo', 'ario', 'berto', 'son', 'ton',
            'lio', 'rio', 'nio', 'ito', 'elo', 'ilo'
        ]
        
        # Verifica sufixos femininos
        for sufixo in sufixos_femininos:
            if nome_lower.endswith(sufixo):
                # Exceções: nomes masculinos que terminam em 'a'
                excecoes_masc = ['luca', 'jonas', 'isaias', 'matias', 'elias', 'josias']
                if nome_lower not in excecoes_masc:
                    return 'Feminino'
        
        # Verifica sufixos masculinos
        for sufixo in sufixos_masculinos:
            if nome_lower.endswith(sufixo):
                return 'Masculino'
        
        return None
    
    def detectar_com_gender_guesser(self, primeiro_nome: str) -> Tuple[Optional[str], float]:
        """
        Detecta sexo usando biblioteca gender-guesser.
        
        Args:
            primeiro_nome: Primeiro nome a analisar
            
        Returns:
            Tupla (sexo, confianca) onde:
            - sexo: 'Masculino', 'Feminino' ou None
            - confianca: float entre 0 e 1
        """
        resultado = self.detector_gender.get_gender(primeiro_nome)
        
        # Mapeia resultados do gender-guesser
        mapeamento = {
            'male': ('Masculino', 1.0),
            'female': ('Feminino', 1.0),
            'mostly_male': ('Masculino', 0.75),
            'mostly_female': ('Feminino', 0.75),
            'andy': (None, 0.0),  # andrógino
            'unknown': (None, 0.0)
        }
        
        return mapeamento.get(resultado, (None, 0.0))
    
    def verificar_ollama_disponivel(self) -> bool:
        """
        Verifica se Ollama está instalado e rodando.
        
        Returns:
            True se Ollama está disponível
        """
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Verifica se GPU está disponível
                if self.usar_gpu:
                    self._configurar_gpu()
                return True
            return False
        except:
            return False
    
    def _configurar_gpu(self):
        """
        Configura variáveis de ambiente para usar GPU no Ollama.
        """
        # Força uso de GPU se disponível (CUDA para NVIDIA)
        if 'CUDA_VISIBLE_DEVICES' not in os.environ:
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Usa primeira GPU
        
        # Configuração adicional para otimização
        os.environ['OLLAMA_NUM_PARALLEL'] = str(self.num_workers)  # Paralelização no Ollama
        
        print(f"    🎮 GPU habilitada (CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')})")
        print(f"    ⚡ Paralelização: {self.num_workers} workers")
    
    def detectar_com_ollama(self, nome_completo: str, primeiro_nome: str) -> str:
        """
        Detecta sexo usando Ollama LLM local.
        
        Args:
            nome_completo: Nome completo do aluno
            primeiro_nome: Primeiro nome extraído
            
        Returns:
            'Masculino', 'Feminino' ou 'Indeterminado'
        """
        prompt = f'''Analise o nome brasileiro completo: "{nome_completo}"

Primeiro nome: {primeiro_nome}

IMPORTANTE: No contexto brasileiro, considere que:
- Nomes terminados em -EL podem ser masculinos (ADRYEL, ADRIEL, MIGUEL, DANIEL, RAFAEL)
- Nomes terminados em -ELLE são geralmente femininos (GABRIELLE, MICHELLE)
- Analise o contexto cultural brasileiro específico

Baseado no contexto cultural brasileiro e padrões de nomes, identifique o sexo mais provável.

Responda APENAS com uma palavra:
- Masculino
- Feminino
- Indeterminado (apenas se realmente impossível determinar)

Resposta:'''
        
        try:
            # Usa ollama via subprocess para ter controle de timeout
            result = subprocess.run(
                ['ollama', 'run', 'brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16', prompt],
                capture_output=True,
                text=True,
                timeout=60  # 60 segundos de timeout
            )
            
            resposta = result.stdout.strip().lower()
            
            # Normaliza resposta
            if 'masculino' in resposta:
                return 'Masculino'
            elif 'feminino' in resposta:
                return 'Feminino'
            else:
                return 'Indeterminado'
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout Ollama (60s) para: {primeiro_nome}")
            return 'Indeterminado'
        except PermissionError:
            print(f"⚠️  Erro de permissão ao usar Ollama para: {primeiro_nome}")
            return 'Indeterminado'
        except Exception as e:
            print(f"⚠️  Erro Ollama para {primeiro_nome}: {str(e)}")
            return 'Indeterminado'
    
    def detectar_sexo(self, nome_completo: str, usar_ollama: bool = True) -> Tuple[str, float, str]:
        """
        Detecta sexo usando abordagem híbrida.
        
        Pipeline ATUALIZADO (prioriza precisão):
        0. Verifica dicionário de correções manuais (nomes conhecidos problemáticos)
        1. Tenta Ollama PRIMEIRO (mais preciso, contexto completo)
        2. Se Ollama falhar/timeout, tenta Gender Guesser (rápido, 85-90% de acerto)
        3. Se inconclusivo, aplica regras heurísticas
        
        Args:
            nome_completo: Nome completo do aluno
            usar_ollama: Se deve usar Ollama (recomendado para máxima precisão)
            
        Returns:
            Tupla (sexo, confianca, metodo) onde:
            - sexo: 'Masculino', 'Feminino' ou 'Indeterminado'
            - confianca: float entre 0 e 1
            - metodo: 'manual', 'ollama', 'gender-guesser', 'regras' ou 'indeterminado'
        """
        self.stats['total'] += 1
        
        # Verifica cache
        if nome_completo in self.cache_nomes:
            return self.cache_nomes[nome_completo]
        
        # Normaliza e extrai primeiro nome
        nome_normalizado = self.normalizar_nome(nome_completo)
        primeiro_nome = self.extrair_primeiro_nome(nome_normalizado)
        
        if not primeiro_nome:
            resultado = ('Indeterminado', 0.0, 'indeterminado')
            self.cache_nomes[nome_completo] = resultado
            self.stats['indeterminado'] += 1
            return resultado
        
        # 0. MÁXIMA PRIORIDADE: Verifica dicionário de correções manuais
        if primeiro_nome in self.correcoes_manuais:
            sexo_manual = self.correcoes_manuais[primeiro_nome]
            resultado = (sexo_manual, 1.0, 'manual')
            self.cache_nomes[nome_completo] = resultado
            self.stats['correcao_manual'] += 1
            return resultado
        
        # 1. PRIORIDADE: Tenta Ollama (mais preciso, analisa contexto completo)
        if usar_ollama:
            sexo_ollama = self.detectar_com_ollama(nome_completo, primeiro_nome)
            if sexo_ollama != 'Indeterminado':
                resultado = (sexo_ollama, 0.95, 'ollama')
                self.cache_nomes[nome_completo] = resultado
                self.stats['ollama'] += 1
                return resultado
        
        # 2. FALLBACK: Tenta Gender Guesser
        sexo_gg, confianca_gg = self.detectar_com_gender_guesser(primeiro_nome)
        
        if sexo_gg and confianca_gg >= 0.75:
            resultado = (sexo_gg, confianca_gg, 'gender-guesser')
            self.cache_nomes[nome_completo] = resultado
            self.stats['gender_guesser'] += 1
            return resultado
        
        # 3. ÚLTIMO RECURSO: Tenta regras heurísticas
        sexo_regras = self.aplicar_regras_sufixo(primeiro_nome)
        
        if sexo_regras:
            resultado = (sexo_regras, 0.65, 'regras')
            self.cache_nomes[nome_completo] = resultado
            self.stats['regras_heuristicas'] += 1
            return resultado
        
        # 4. Não conseguiu determinar
        resultado = ('Indeterminado', 0.0, 'indeterminado')
        self.cache_nomes[nome_completo] = resultado
        self.stats['indeterminado'] += 1
        return resultado
    
    def processar_csv(self, arquivo_entrada: Path, arquivo_saida: Path, usar_ollama: bool = True) -> pd.DataFrame:
        """
        Processa CSV adicionando coluna de sexo.
        
        Args:
            arquivo_entrada: Caminho do CSV de entrada
            arquivo_saida: Caminho do CSV de saída
            usar_ollama: Se deve usar Ollama para casos ambíguos
            
        Returns:
            DataFrame processado
        """
        print(f"\n{'='*60}")
        print(f"Processando: {arquivo_entrada.name}")
        print(f"{'='*60}")
        
        # Carrega CSV
        df = pd.read_csv(arquivo_entrada)
        print(f"Total de registros: {len(df)}")
        
        # Conta nomes únicos
        nomes_unicos_lista = df['Nome'].unique()
        nomes_unicos = len(nomes_unicos_lista)
        print(f"Nomes únicos: {nomes_unicos}")
        
        # Detecta sexo para cada nome único
        print(f"\nDetectando sexo dos alunos...")
        
        # Cria mapeamento nome -> (sexo, confianca, metodo)
        mapeamento_sexo = {}
        
        # Processamento paralelo se usar Ollama
        if usar_ollama and self.num_workers > 1:
            print(f"⚡ Processamento paralelo com {self.num_workers} workers")
            
            start_time = time.time()
            processados = 0
            
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                # Submete todas as tarefas
                future_to_nome = {
                    executor.submit(self.detectar_sexo, nome, usar_ollama): nome 
                    for nome in nomes_unicos_lista
                }
                
                # Processa resultados conforme completam
                for future in as_completed(future_to_nome):
                    nome = future_to_nome[future]
                    try:
                        sexo, confianca, metodo = future.result()
                        mapeamento_sexo[nome] = (sexo, confianca, metodo)
                        processados += 1
                        
                        # Progresso
                        if processados % 100 == 0:
                            elapsed = time.time() - start_time
                            taxa = processados / elapsed
                            restante = (nomes_unicos - processados) / taxa if taxa > 0 else 0
                            print(f"  Processados: {processados}/{nomes_unicos} ({processados/nomes_unicos*100:.1f}%) - "
                                  f"Taxa: {taxa:.1f} nomes/s - Restante: {restante/60:.1f}min")
                    except Exception as e:
                        print(f"⚠️  Erro ao processar {nome}: {str(e)}")
                        mapeamento_sexo[nome] = ('Indeterminado', 0.0, 'erro')
            
            print(f"  Processados: {nomes_unicos}/{nomes_unicos} (100.0%)")
            print(f"  ⏱️  Tempo total: {(time.time() - start_time)/60:.1f} minutos")
        
        else:
            # Processamento sequencial (modo original)
            nomes_processados = set()
            
            for idx, nome in enumerate(nomes_unicos_lista, 1):
                if nome not in nomes_processados:
                    sexo, confianca, metodo = self.detectar_sexo(nome, usar_ollama=usar_ollama)
                    mapeamento_sexo[nome] = (sexo, confianca, metodo)
                    nomes_processados.add(nome)
                    
                    # Progresso
                    if idx % 100 == 0:
                        print(f"  Processados: {idx}/{nomes_unicos} ({idx/nomes_unicos*100:.1f}%)")
            
            print(f"  Processados: {nomes_unicos}/{nomes_unicos} (100.0%)")
        
        # Aplica mapeamento ao DataFrame
        df['Sexo'] = df['Nome'].map(lambda nome: mapeamento_sexo[nome][0])
        df['Sexo_Confianca'] = df['Nome'].map(lambda nome: mapeamento_sexo[nome][1])
        df['Sexo_Metodo'] = df['Nome'].map(lambda nome: mapeamento_sexo[nome][2])
        
        # Salva resultado
        df.to_csv(arquivo_saida, index=False)
        print(f"\n✅ Arquivo salvo: {arquivo_saida.name}")
        
        # Estatísticas
        print(f"\n📊 Estatísticas de Detecção:")
        print(f"  - Masculino: {(df['Sexo'] == 'Masculino').sum()} ({(df['Sexo'] == 'Masculino').sum()/len(df)*100:.1f}%)")
        print(f"  - Feminino: {(df['Sexo'] == 'Feminino').sum()} ({(df['Sexo'] == 'Feminino').sum()/len(df)*100:.1f}%)")
        print(f"  - Indeterminado: {(df['Sexo'] == 'Indeterminado').sum()} ({(df['Sexo'] == 'Indeterminado').sum()/len(df)*100:.1f}%)")
        
        print(f"\n📈 Métodos Utilizados:")
        print(f"  - Correção Manual: {self.stats['correcao_manual']} ({self.stats['correcao_manual']/nomes_unicos*100:.1f}%)")
        print(f"  - Ollama: {self.stats['ollama']} ({self.stats['ollama']/nomes_unicos*100:.1f}%)")
        print(f"  - Gender Guesser: {self.stats['gender_guesser']} ({self.stats['gender_guesser']/nomes_unicos*100:.1f}%)")
        print(f"  - Regras Heurísticas: {self.stats['regras_heuristicas']} ({self.stats['regras_heuristicas']/nomes_unicos*100:.1f}%)")
        print(f"  - Indeterminado: {self.stats['indeterminado']} ({self.stats['indeterminado']/nomes_unicos*100:.1f}%)")
        
        return df
    
    def gerar_relatorio(self, df_tde: pd.DataFrame, df_vocab: pd.DataFrame, pasta_saida: Path):
        """
        Gera relatório consolidado da detecção de sexo.
        
        Args:
            df_tde: DataFrame do TDE com sexo detectado
            df_vocab: DataFrame do Vocabulário com sexo detectado
            pasta_saida: Pasta para salvar relatório
        """
        relatorio = {
            'TDE': {
                'total_registros': len(df_tde),
                'nomes_unicos': df_tde['Nome'].nunique(),
                'masculino': int((df_tde['Sexo'] == 'Masculino').sum()),
                'feminino': int((df_tde['Sexo'] == 'Feminino').sum()),
                'indeterminado': int((df_tde['Sexo'] == 'Indeterminado').sum()),
                'metodos': {
                    'gender_guesser': int((df_tde['Sexo_Metodo'] == 'gender-guesser').sum()),
                    'regras': int((df_tde['Sexo_Metodo'] == 'regras').sum()),
                    'ollama': int((df_tde['Sexo_Metodo'] == 'ollama').sum()),
                    'indeterminado': int((df_tde['Sexo_Metodo'] == 'indeterminado').sum())
                }
            },
            'Vocabulario': {
                'total_registros': len(df_vocab),
                'nomes_unicos': df_vocab['Nome'].nunique(),
                'masculino': int((df_vocab['Sexo'] == 'Masculino').sum()),
                'feminino': int((df_vocab['Sexo'] == 'Feminino').sum()),
                'indeterminado': int((df_vocab['Sexo'] == 'Indeterminado').sum()),
                'metodos': {
                    'gender_guesser': int((df_vocab['Sexo_Metodo'] == 'gender-guesser').sum()),
                    'regras': int((df_vocab['Sexo_Metodo'] == 'regras').sum()),
                    'ollama': int((df_vocab['Sexo_Metodo'] == 'ollama').sum()),
                    'indeterminado': int((df_vocab['Sexo_Metodo'] == 'indeterminado').sum())
                }
            }
        }
        
        # Salva JSON
        arquivo_json = pasta_saida / "relatorio_deteccao_sexo.json"
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Relatório salvo: {arquivo_json.name}")
        
        # Lista casos indeterminados
        casos_indeterminados = []
        
        for nome in df_tde[df_tde['Sexo'] == 'Indeterminado']['Nome'].unique():
            casos_indeterminados.append({
                'nome': nome,
                'origem': 'TDE'
            })
        
        for nome in df_vocab[df_vocab['Sexo'] == 'Indeterminado']['Nome'].unique():
            if nome not in [c['nome'] for c in casos_indeterminados]:
                casos_indeterminados.append({
                    'nome': nome,
                    'origem': 'Vocabulario'
                })
        
        # Salva casos indeterminados
        if casos_indeterminados:
            arquivo_indeterminados = pasta_saida / "casos_indeterminados.json"
            with open(arquivo_indeterminados, 'w', encoding='utf-8') as f:
                json.dump(casos_indeterminados, f, indent=2, ensure_ascii=False)
            
            print(f"⚠️  Casos indeterminados salvos: {arquivo_indeterminados.name}")
            print(f"   Total: {len(casos_indeterminados)} nomes")

def main():
    """Função principal"""
    print("="*70)
    print("DETECTOR DE SEXO HÍBRIDO - Gender Guesser + Ollama")
    print("="*70)
    
    # Configuração de caminhos
    pasta_dashboard = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Dashboard")
    pasta_saida = Path("/home/nees/Documents/VSCodigo/AnaliseDadosWordGeneration/Modules/DetectorSexo")
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    arquivo_tde = pasta_dashboard / "TDE_longitudinal.csv"
    arquivo_vocab = pasta_dashboard / "vocabulario_longitudinal.csv"
    
    # Verificar se arquivos existem
    if not arquivo_tde.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_tde}")
        return
    
    if not arquivo_vocab.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_vocab}")
        return
    
    # Criar detector
    detector = DetectorSexoHibrido(usar_gpu=True, num_workers=4)
    
    # Opção de desabilitar Ollama (muito lento para grandes datasets)
    import sys
    desabilitar_ollama = '--no-ollama' in sys.argv
    desabilitar_gpu = '--no-gpu' in sys.argv
    
    # Ajusta configuração de GPU
    if desabilitar_gpu:
        detector.usar_gpu = False
        print("\n⚠️  GPU DESABILITADA via --no-gpu")
    
    # Verificar se Ollama está disponível
    usar_ollama = False if desabilitar_ollama else detector.verificar_ollama_disponivel()
    
    if desabilitar_ollama:
        print("\n⚠️  Ollama DESABILITADO via --no-ollama")
        print("    Pipeline: Gender-guesser → Regras Heurísticas")
        print("    ⚡ Modo rápido, mas menos preciso\n")
    elif usar_ollama:
        print("\n✅ Ollama HABILITADO!")
        print("    Pipeline: Ollama (1º) → Gender-guesser (fallback) → Regras")
        print("    🎯 Modo preciso, priorizando contexto completo do nome")
        print(f"    ⏱️  Estimativa: ~5-10s por nome com GPU (vs 60s sem GPU)\n")
    else:
        print("\n⚠️  Ollama não encontrado ou não está rodando.")
        print("    Pipeline: Gender-guesser → Regras Heurísticas")
        print("    💡 Dica: Execute 'ollama serve' para melhor precisão\n")
    
    # Processa TDE
    arquivo_tde_saida = pasta_saida / "TDE_longitudinal_com_sexo.csv"
    df_tde = detector.processar_csv(arquivo_tde, arquivo_tde_saida, usar_ollama=usar_ollama)
    
    # Reseta estatísticas para Vocabulário
    detector.stats = {
        'total': 0,
        'correcao_manual': 0,
        'gender_guesser': 0,
        'regras_heuristicas': 0,
        'ollama': 0,
        'indeterminado': 0
    }
    
    # Processa Vocabulário
    arquivo_vocab_saida = pasta_saida / "vocabulario_longitudinal_com_sexo.csv"
    df_vocab = detector.processar_csv(arquivo_vocab, arquivo_vocab_saida, usar_ollama=usar_ollama)
    
    # Gera relatório consolidado
    print(f"\n{'='*60}")
    print("GERANDO RELATÓRIO CONSOLIDADO")
    print(f"{'='*60}")
    detector.gerar_relatorio(df_tde, df_vocab, pasta_saida)
    
    print(f"\n{'='*70}")
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
