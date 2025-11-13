"""
Pipeline Gerencial - Fase 5 WordGen
Sistema consolidado para análise gerencial de escolas, turmas e disciplinas
Baseado nos dados de Língua Portuguesa e Matemática
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import warnings
import base64
from io import BytesIO
import re
from datetime import datetime
warnings.filterwarnings('ignore')

# Configurações de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PipelineGerencial:
    def __init__(self, caminho_dados='Modules/Fase5/Data/'):
        self.caminho_dados = Path(caminho_dados)
        self.caminho_output = Path('Data/gerencial_fase5/')
        self.caminho_output.mkdir(exist_ok=True)
        
        # Carregar dados
        self.carregar_dados()
        
    def carregar_dados(self):
        """Carrega os dados de matemática e português"""
        print("📊 Carregando dados para análise gerencial...")
        
        try:
            self.df_matematica = pd.read_csv(self.caminho_dados / 'df_matemática_analitico.csv')
            self.df_portugues = pd.read_csv(self.caminho_dados / 'df_língua_portuguesa_analitico.csv')
            
            print(f"✅ Matemática: {len(self.df_matematica)} registros")
            print(f"✅ Português: {len(self.df_portugues)} registros")
            
            # Preparar dados
            self.preparar_dados()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise
    
    def preparar_dados(self):
        """Prepara e limpa os dados para análise gerencial"""
        print("🔧 Preparando dados para análise gerencial...")
        
        # Converter colunas numéricas
        for df in [self.df_matematica, self.df_portugues]:
            # Encontrar colunas numéricas
            colunas_numericas = [col for col in df.columns if 
                               any(x in col for x in ['Total_Acertos', 'Delta', 'P_Q'])]
            
            for col in colunas_numericas:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Padronizar nomes de colunas de identificação
        for df in [self.df_matematica, self.df_portugues]:
            if 'Turma' not in df.columns and 'Sala' in df.columns:
                df['Turma'] = df['Sala']
            elif 'Turma' not in df.columns and 'Classe' in df.columns:
                df['Turma'] = df['Classe']
            
        print("✅ Dados preparados para análise gerencial")
    
    def _normalizar_serie_label(self, serie):
        """Normaliza rótulos de série para comparação consistente"""
        if not isinstance(serie, str):
            return None
        serie = serie.strip().upper().replace('°', 'º')
        if not serie:
            return None
        if 'ANO' not in serie:
            digitos = re.search(r"\d+", serie)
            if digitos:
                serie = f"{digitos.group()}º ANO"
            else:
                serie = f"{serie}º ANO"
        return serie

    def _calcular_estatisticas_basicas(self, dados):
        """Calcula estatísticas básicas para um DataFrame"""
        if dados.empty:
            return {
                'n': 0,
                'media_pre': 0.0,
                'media_pos': 0.0,
                'media_delta': 0.0,
                'cohen_d': 0.0,
                'perc_melhoraram': 0.0,
                'perc_pioraram': 0.0,
                'desvio_padrao_pre': 0.0,
                'desvio_padrao_pos': 0.0
            }
        
        media_pre = dados['Total_Acertos_Pré'].mean()
        media_pos = dados['Total_Acertos_Pós'].mean()
        media_delta = dados['Delta_Total_Acertos'].mean()
        
        # Cohen's d
        std_delta = dados['Delta_Total_Acertos'].std()
        cohen_d = media_delta / std_delta if std_delta > 0 else 0
        
        # Percentuais
        melhoraram = (dados['Delta_Total_Acertos'] > 0).sum()
        pioraram = (dados['Delta_Total_Acertos'] < 0).sum()
        total = len(dados)
        
        return {
            'n': total,
            'media_pre': round(media_pre, 2),
            'media_pos': round(media_pos, 2),
            'media_delta': round(media_delta, 2),
            'cohen_d': round(cohen_d, 3),
            'perc_melhoraram': round((melhoraram / total) * 100, 1) if total > 0 else 0.0,
            'perc_pioraram': round((pioraram / total) * 100, 1) if total > 0 else 0.0,
            'desvio_padrao_pre': round(dados['Total_Acertos_Pré'].std(), 2),
            'desvio_padrao_pos': round(dados['Total_Acertos_Pós'].std(), 2)
        }
    
    def gerar_relatorio_por_escola(self):
        """Gera relatório consolidado por escola"""
        print("🏫 Gerando relatório por escola...")
        
        relatorio_escolas = []
        
        # Analisar matemática por escola
        for escola in self.df_matematica['Escola'].dropna().unique():
            dados_escola = self.df_matematica[self.df_matematica['Escola'] == escola]
            
            if len(dados_escola) < 5:  # Mínimo para análise
                continue
                
            stats = self._calcular_estadisticas_basicas(dados_escola)
            
            # Adicionar informações específicas da escola
            turmas = dados_escola['Turma'].nunique() if 'Turma' in dados_escola.columns else 0
            series = dados_escola['Serie'].nunique() if 'Serie' in dados_escola.columns else 0
            
            relatorio_escolas.append({
                'escola': escola,
                'disciplina': 'Matemática',
                'n_alunos': stats['n'],
                'n_turmas': turmas,
                'n_series': series,
                **stats
            })
        
        # Analisar português por escola
        for escola in self.df_portugues['Escola'].dropna().unique():
            dados_escola = self.df_portugues[self.df_portugues['Escola'] == escola]
            
            if len(dados_escola) < 5:
                continue
                
            stats = self._calcular_estadisticas_basicas(dados_escola)
            
            turmas = dados_escola['Turma'].nunique() if 'Turma' in dados_escola.columns else 0
            series = dados_escola['Serie'].nunique() if 'Serie' in dados_escola.columns else 0
            
            relatorio_escolas.append({
                'escola': escola,
                'disciplina': 'Língua Portuguesa',
                'n_alunos': stats['n'],
                'n_turmas': turmas,
                'n_series': series,
                **stats
            })
        
        # Salvar relatório
        df_escolas = pd.DataFrame(relatorio_escolas)
        caminho_arquivo = self.caminho_output / 'relatorio_escolas.csv'
        df_escolas.to_csv(caminho_arquivo, index=False)
        
        print(f"✅ Relatório de escolas salvo em: {caminho_arquivo}")
        return df_escolas
    
    def gerar_relatorio_por_turma(self):
        """Gera relatório consolidado por turma"""
        print("🎓 Gerando relatório por turma...")
        
        relatorio_turmas = []
        
        # Verificar se existe coluna Turma
        col_turma_mat = 'Turma' if 'Turma' in self.df_matematica.columns else None
        col_turma_port = 'Turma' if 'Turma' in self.df_portugues.columns else None
        
        if not col_turma_mat and not col_turma_port:
            print("⚠️ Coluna 'Turma' não encontrada nos dados. Pulando análise por turma.")
            return pd.DataFrame()
        
        # Matemática por turma
        if col_turma_mat:
            for escola in self.df_matematica['Escola'].dropna().unique():
                dados_escola = self.df_matematica[self.df_matematica['Escola'] == escola]
                
                for turma in dados_escola[col_turma_mat].dropna().unique():
                    dados_turma = dados_escola[dados_escola[col_turma_mat] == turma]
                    
                    if len(dados_turma) < 3:  # Mínimo para turma
                        continue
                    
                    stats = self._calcular_estadisticas_basicas(dados_turma)
                    serie = dados_turma['Serie'].iloc[0] if 'Serie' in dados_turma.columns else 'N/A'
                    
                    relatorio_turmas.append({
                        'escola': escola,
                        'turma': turma,
                        'serie': serie,
                        'disciplina': 'Matemática',
                        **stats
                    })
        
        # Português por turma
        if col_turma_port:
            for escola in self.df_portugues['Escola'].dropna().unique():
                dados_escola = self.df_portugues[self.df_portugues['Escola'] == escola]
                
                for turma in dados_escola[col_turma_port].dropna().unique():
                    dados_turma = dados_escola[dados_escola[col_turma_port] == turma]
                    
                    if len(dados_turma) < 3:
                        continue
                    
                    stats = self._calcular_estadisticas_basicas(dados_turma)
                    serie = dados_turma['Serie'].iloc[0] if 'Serie' in dados_turma.columns else 'N/A'
                    
                    relatorio_turmas.append({
                        'escola': escola,
                        'turma': turma,
                        'serie': serie,
                        'disciplina': 'Língua Portuguesa',
                        **stats
                    })
        
        # Salvar relatório
        df_turmas = pd.DataFrame(relatorio_turmas)
        if not df_turmas.empty:
            caminho_arquivo = self.caminho_output / 'relatorio_turmas.csv'
            df_turmas.to_csv(caminho_arquivo, index=False)
            print(f"✅ Relatório de turmas salvo em: {caminho_arquivo}")
        
        return df_turmas
    
    def gerar_relatorio_por_disciplina(self):
        """Gera relatório consolidado por disciplina"""
        print("📚 Gerando relatório por disciplina...")
        
        relatorio_disciplinas = []
        
        # Matemática
        stats_mat = self._calcular_estadisticas_basicas(self.df_matematica)
        escolas_mat = self.df_matematica['Escola'].nunique()
        turmas_mat = self.df_matematica['Turma'].nunique() if 'Turma' in self.df_matematica.columns else 0
        
        relatorio_disciplinas.append({
            'disciplina': 'Matemática',
            'n_escolas': escolas_mat,
            'n_turmas': turmas_mat,
            **stats_mat
        })
        
        # Português
        stats_port = self._calcular_estadisticas_basicas(self.df_portugues)
        escolas_port = self.df_portugues['Escola'].nunique()
        turmas_port = self.df_portugues['Turma'].nunique() if 'Turma' in self.df_portugues.columns else 0
        
        relatorio_disciplinas.append({
            'disciplina': 'Língua Portuguesa',
            'n_escolas': escolas_port,
            'n_turmas': turmas_port,
            **stats_port
        })
        
        # Salvar relatório
        df_disciplinas = pd.DataFrame(relatorio_disciplinas)
        caminho_arquivo = self.caminho_output / 'relatorio_disciplinas.csv'
        df_disciplinas.to_csv(caminho_arquivo, index=False)
        
        print(f"✅ Relatório de disciplinas salvo em: {caminho_arquivo}")
        return df_disciplinas
    
    def gerar_ranking_performance(self):
        """Gera rankings de performance por diferentes critérios"""
        print("🏆 Gerando rankings de performance...")
        
        rankings = {}
        
        # Ranking de escolas por Cohen's d
        dados_escolas = []
        
        for escola in set(list(self.df_matematica['Escola'].dropna()) + list(self.df_portugues['Escola'].dropna())):
            # Matemática
            dados_mat = self.df_matematica[self.df_matematica['Escola'] == escola]
            if len(dados_mat) >= 5:
                stats_mat = self._calcular_estadisticas_basicas(dados_mat)
                dados_escolas.append({
                    'escola': escola,
                    'disciplina': 'Matemática',
                    'cohen_d': stats_mat['cohen_d'],
                    'n_alunos': stats_mat['n'],
                    'perc_melhoraram': stats_mat['perc_melhoraram']
                })
            
            # Português
            dados_port = self.df_portugues[self.df_portugues['Escola'] == escola]
            if len(dados_port) >= 5:
                stats_port = self._calcular_estadisticas_basicas(dados_port)
                dados_escolas.append({
                    'escola': escola,
                    'disciplina': 'Língua Portuguesa',
                    'cohen_d': stats_port['cohen_d'],
                    'n_alunos': stats_port['n'],
                    'perc_melhoraram': stats_port['perc_melhoraram']
                })
        
        df_ranking_escolas = pd.DataFrame(dados_escolas).sort_values('cohen_d', ascending=False)
        rankings['escolas'] = df_ranking_escolas
        
        # Salvar rankings
        caminho_ranking = self.caminho_output / 'ranking_escolas.csv'
        df_ranking_escolas.to_csv(caminho_ranking, index=False)
        
        print(f"✅ Rankings salvos em: {self.caminho_output}")
        return rankings
    
    def gerar_dashboard_dados(self):
        """Gera dados consolidados para dashboard"""
        print("📊 Gerando dados para dashboard...")
        
        dashboard_data = {
            'resumo_geral': {
                'total_alunos_matematica': len(self.df_matematica),
                'total_alunos_portugues': len(self.df_portugues),
                'total_escolas': len(set(list(self.df_matematica['Escola'].dropna()) + list(self.df_portugues['Escola'].dropna()))),
                'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'estatisticas_gerais': {
                'matematica': self._calcular_estadisticas_basicas(self.df_matematica),
                'portugues': self._calcular_estadisticas_basicas(self.df_portugues)
            }
        }
        
        # Salvar dados do dashboard
        caminho_dashboard = self.caminho_output / 'dashboard_data.json'
        with open(caminho_dashboard, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados do dashboard salvos em: {caminho_dashboard}")
        return dashboard_data
    
    def executar_pipeline_completo(self):
        """Executa pipeline completo de análise gerencial"""
        print("🚀 Iniciando Pipeline Gerencial - Fase 5...")
        
        try:
            # 1. Relatórios por dimensão
            relatorio_escolas = self.gerar_relatorio_por_escola()
            relatorio_turmas = self.gerar_relatorio_por_turma()
            relatorio_disciplinas = self.gerar_relatorio_por_disciplina()
            
            # 2. Rankings
            rankings = self.gerar_ranking_performance()
            
            # 3. Dados para dashboard
            dashboard_data = self.gerar_dashboard_dados()
            
            # 4. Resumo final
            print("\n" + "="*60)
            print("📋 RESUMO DA ANÁLISE GERENCIAL")
            print("="*60)
            print(f"📊 Total de escolas analisadas: {relatorio_disciplinas['n_escolas'].max()}")
            print(f"👥 Total de alunos (Matemática): {relatorio_disciplinas[relatorio_disciplinas['disciplina'] == 'Matemática']['n'].iloc[0]}")
            print(f"👥 Total de alunos (Português): {relatorio_disciplinas[relatorio_disciplinas['disciplina'] == 'Língua Portuguesa']['n'].iloc[0]}")
            
            if not relatorio_turmas.empty:
                print(f"🎓 Total de turmas analisadas: {relatorio_turmas['turma'].nunique()}")
            
            # Melhores performances
            if not rankings['escolas'].empty:
                melhor_mat = rankings['escolas'][rankings['escolas']['disciplina'] == 'Matemática'].iloc[0]
                melhor_port = rankings['escolas'][rankings['escolas']['disciplina'] == 'Língua Portuguesa'].iloc[0]
                
                print(f"\n🏆 DESTAQUES:")
                print(f"   Matemática: {melhor_mat['escola']} (Cohen's d: {melhor_mat['cohen_d']})")
                print(f"   Português: {melhor_port['escola']} (Cohen's d: {melhor_port['cohen_d']})")
            
            print(f"\n📁 Arquivos gerados em: {self.caminho_output}")
            print("   - relatorio_escolas.csv")
            print("   - relatorio_turmas.csv")
            print("   - relatorio_disciplinas.csv")
            print("   - ranking_escolas.csv")
            print("   - dashboard_data.json")
            print("\n🎉 Pipeline Gerencial concluído com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no pipeline gerencial: {e}")
            raise

    def _calcular_estadisticas_basicas(self, dados):
        """Wrapper para _calcular_estatisticas_basicas (corrige typo)"""
        return self._calcular_estatisticas_basicas(dados)

if __name__ == "__main__":
    pipeline = PipelineGerencial()
    pipeline.executar_pipeline_completo()