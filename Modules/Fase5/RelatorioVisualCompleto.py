"""
Gerador de Visualizações para Fase 5 - WordGen
Sistema para criar gráficos interativos para o relatório HTML
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
warnings.filterwarnings('ignore')

# Configurações de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class GeradorVisualizacoesFase5:
    def __init__(self, caminho_dados='Modules/Fase5/Data/'):
        self.caminho_dados = Path(caminho_dados)
        self.caminho_figuras = Path('Data/figures/')
        self.caminho_figuras.mkdir(exist_ok=True)
        
        # Carregar dados
        self.carregar_dados()
        
    def carregar_dados(self):
        """Carrega os dados de matemática e português"""
        print("📊 Carregando dados da Fase 5...")
        
        try:
            self.df_matematica = pd.read_csv(self.caminho_dados / 'df_matemática_analitico.csv')
            self.df_portugues = pd.read_csv(self.caminho_dados / 'df_língua_portuguesa_analitico.csv')
            
            print(f"✅ Matemática: {len(self.df_matematica)} registros")
            print(f"✅ Português: {len(self.df_portugues)} registros")
            
            # Limpar dados
            self.preparar_dados()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise
    
    def preparar_dados(self):
        """Prepara e limpa os dados para análise"""
        print("🔧 Preparando dados...")
        
        # Converter colunas numéricas
        for df in [self.df_matematica, self.df_portugues]:
            # Encontrar colunas numéricas
            colunas_numericas = [col for col in df.columns if 
                               any(x in col for x in ['Total_Acertos', 'Delta', 'P_Q'])]
            
            for col in colunas_numericas:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        print("✅ Dados preparados com sucesso")
    
    def _normalizar_serie_label(self, serie):
        """Normaliza rótulos de série para comparação consistente"""
        if not isinstance(serie, str):
            return None
        serie = serie.strip().upper().replace('°', 'º')
        if not serie:
            return None
        if 'ANO' not in serie:
            # Extrair apenas dígitos se vier como '6'
            digitos = re.search(r"\d+", serie)
            if digitos:
                serie = f"{digitos.group()}º ANO"
            else:
                serie = f"{serie}º ANO"
        return serie

    def _ordenar_series(self, serie):
        """Define ordem numérica para as séries"""
        if not isinstance(serie, str):
            return 999
        serie = serie.upper()
        match = re.search(r"\d+", serie)
        if match:
            try:
                return int(match.group())
            except ValueError:
                return 999
        return 999

    def _filtrar_dataframe(self, df, escola, serie_label):
        """Aplica filtros de escola e série sobre um DataFrame"""
        dados = df
        if escola != 'todas':
            dados = dados[dados['Escola'] == escola]
        if serie_label != 'todas':
            serie_norm = self._normalizar_serie_label(serie_label)
            dados = dados[dados['Serie'].fillna('').str.upper() == serie_norm]
        return dados

    def _plotar_mensagem_sem_dados(self, ax, mensagem):
        """Exibe mensagem centralizada quando não há dados suficientes"""
        ax.text(0.5, 0.5, mensagem, ha='center', va='center', fontsize=12)
        ax.set_axis_off()

    def _plotar_evolucao_por_disciplina(self, ax, dados, titulo, cor_pre, cor_pos):
        """Plota barras de evolução pré/pós por série"""
        if dados.empty:
            self._plotar_mensagem_sem_dados(ax, 'Sem dados após aplicar filtros')
            return
        dados = dados.copy()
        dados['Serie'] = dados['Serie'].fillna('').apply(self._normalizar_serie_label)
        dados = dados[dados['Serie'].notna()]
        if dados.empty:
            self._plotar_mensagem_sem_dados(ax, 'Sem dados após aplicar filtros')
            return
        resumo = dados.groupby('Serie', as_index=False)[['Total_Acertos_Pré', 'Total_Acertos_Pós']].mean()
        if resumo.empty:
            self._plotar_mensagem_sem_dados(ax, 'Sem dados suficientes')
            return
        resumo = resumo.sort_values(by='Serie', key=lambda s: s.apply(self._ordenar_series))
        series = resumo['Serie'].tolist()
        pre = resumo['Total_Acertos_Pré'].tolist()
        pos = resumo['Total_Acertos_Pós'].tolist()
        x = np.arange(len(series))
        width = 0.35
        ax.bar(x - width/2, pre, width, label='Pré-teste', alpha=0.75, color=cor_pre)
        ax.bar(x + width/2, pos, width, label='Pós-teste', alpha=0.75, color=cor_pos)
        ax.set_xlabel('Série')
        ax.set_ylabel('Média de Acertos')
        ax.set_title(titulo)
        ax.set_xticks(x)
        ax.set_xticklabels(series, rotation=15)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plotar_distribuicao_por_disciplina(self, ax, dados, titulo, cor):
        """Plota histograma da distribuição de ganhos"""
        if dados.empty:
            self._plotar_mensagem_sem_dados(ax, 'Sem dados após aplicar filtros')
            return
        deltas = dados['Delta_Total_Acertos'].dropna()
        if len(deltas) < 3:
            mensagem = 'Menos de 3 registros para distribuir'
            if len(deltas) == 0:
                mensagem = 'Nenhum dado disponível'
            self._plotar_mensagem_sem_dados(ax, mensagem)
            return
        ax.hist(deltas, bins=20, alpha=0.75, color=cor, edgecolor='black')
        media_delta = deltas.mean()
        ax.axvline(media_delta, color='red', linestyle='--', label=f'Média: {media_delta:.2f}')
        ax.set_xlabel('Crescimento (pontos)')
        ax.set_ylabel('Frequência')
        ax.set_title(titulo)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _converter_figura_para_base64(self, fig):
        """Converte figura Matplotlib para string base64"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"
    
    def gerar_dados_filtros(self):
        """Gera dados estruturados para os filtros do HTML"""
        print("🎛️ Gerando dados para filtros...")
        
        # Extrair escolas únicas
        escolas_mat = set(self.df_matematica['Escola'].dropna().unique())
        escolas_port = set(self.df_portugues['Escola'].dropna().unique())
        escolas = sorted(list(escolas_mat.union(escolas_port)))
        
        # Extrair séries
        series_mat = set(self.df_matematica['Serie'].dropna().unique())
        series_port = set(self.df_portugues['Serie'].dropna().unique())
        series = sorted(list(series_mat.union(series_port)))
        
        dados_filtros = {
            'escolas': escolas,
            'series': series,
            'disciplinas': ['Matemática', 'Língua Portuguesa']
        }
        
        # Salvar em JSON para uso no HTML
        with open('Data/dados_filtros_fase5.json', 'w', encoding='utf-8') as f:
            json.dump(dados_filtros, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(escolas)} escolas, {len(series)} séries identificadas")
        return dados_filtros
    
    def calcular_estatisticas_por_escola(self):
        """Calcula estatísticas por escola para o ranking"""
        print("📈 Calculando estatísticas por escola...")
        
        resultado = {}
        
        # Matemática
        estatisticas_mat = []
        for escola in self.df_matematica['Escola'].unique():
            if pd.isna(escola):
                continue
                
            dados_escola = self.df_matematica[self.df_matematica['Escola'] == escola]
            
            if len(dados_escola) < 5:  # Mínimo de 5 alunos
                continue
            
            # Calcular estatísticas
            media_pre = dados_escola['Total_Acertos_Pré'].mean()
            media_pos = dados_escola['Total_Acertos_Pós'].mean()
            media_delta = dados_escola['Delta_Total_Acertos'].mean()
            
            # Cohen's d
            std_delta = dados_escola['Delta_Total_Acertos'].std()
            cohen_d = media_delta / std_delta if std_delta > 0 else 0
            
            # Percentuais
            melhoraram = (dados_escola['Delta_Total_Acertos'] > 0).sum()
            total = len(dados_escola)
            perc_melhoraram = (melhoraram / total) * 100
            
            estatisticas_mat.append({
                'escola': escola,
                'disciplina': 'Matemática',
                'n': total,
                'media_pre': round(media_pre, 2),
                'media_pos': round(media_pos, 2),
                'media_delta': round(media_delta, 2),
                'cohen_d': round(cohen_d, 3),
                'perc_melhoraram': round(perc_melhoraram, 1)
            })
        
        # Português
        estatisticas_port = []
        for escola in self.df_portugues['Escola'].unique():
            if pd.isna(escola):
                continue
                
            dados_escola = self.df_portugues[self.df_portugues['Escola'] == escola]
            
            if len(dados_escola) < 5:  # Mínimo de 5 alunos
                continue
            
            # Calcular estatísticas
            media_pre = dados_escola['Total_Acertos_Pré'].mean()
            media_pos = dados_escola['Total_Acertos_Pós'].mean()
            media_delta = dados_escola['Delta_Total_Acertos'].mean()
            
            # Cohen's d
            std_delta = dados_escola['Delta_Total_Acertos'].std()
            cohen_d = media_delta / std_delta if std_delta > 0 else 0
            
            # Percentuais
            melhoraram = (dados_escola['Delta_Total_Acertos'] > 0).sum()
            total = len(dados_escola)
            perc_melhoraram = (melhoraram / total) * 100
            
            estatisticas_port.append({
                'escola': escola,
                'disciplina': 'Língua Portuguesa',
                'n': total,
                'media_pre': round(media_pre, 2),
                'media_pos': round(media_pos, 2),
                'media_delta': round(media_delta, 2),
                'cohen_d': round(cohen_d, 3),
                'perc_melhoraram': round(perc_melhoraram, 1)
            })
        
        resultado['matematica'] = estatisticas_mat
        resultado['portugues'] = estatisticas_port
        
        # Salvar dados
        with open('Data/estatisticas_escolas_fase5.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Estatísticas calculadas para {len(estatisticas_mat)} escolas (Mat) e {len(estatisticas_port)} escolas (Port)")
        return resultado
    
    def gerar_grafico_evolucao_series(self):
        """Gera gráfico de evolução por série"""
        print("📊 Gerando gráfico de evolução por série...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Matemática
        series_mat = []
        for serie in ['6º ANO', '7º ANO', '8º ANO', '9º ANO']:
            dados_serie = self.df_matematica[self.df_matematica['Serie'] == serie]
            if len(dados_serie) > 0:
                media_pre = dados_serie['Total_Acertos_Pré'].mean()
                media_pos = dados_serie['Total_Acertos_Pós'].mean()
                series_mat.append({
                    'serie': serie,
                    'pre': media_pre,
                    'pos': media_pos,
                    'n': len(dados_serie)
                })
        
        if series_mat:
            series_nomes = [s['serie'] for s in series_mat]
            pre_valores = [s['pre'] for s in series_mat]
            pos_valores = [s['pos'] for s in series_mat]
            
            x = np.arange(len(series_nomes))
            width = 0.35
            
            ax1.bar(x - width/2, pre_valores, width, label='Pré-teste', alpha=0.7, color='lightblue')
            ax1.bar(x + width/2, pos_valores, width, label='Pós-teste', alpha=0.7, color='darkblue')
            
            ax1.set_xlabel('Série')
            ax1.set_ylabel('Média de Acertos')
            ax1.set_title('Evolução por Série - Matemática')
            ax1.set_xticks(x)
            ax1.set_xticklabels(series_nomes)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Português
        series_port = []
        for serie in ['6º ANO', '7º ANO', '8º ANO', '9º ANO']:
            dados_serie = self.df_portugues[self.df_portugues['Serie'] == serie]
            if len(dados_serie) > 0:
                media_pre = dados_serie['Total_Acertos_Pré'].mean()
                media_pos = dados_serie['Total_Acertos_Pós'].mean()
                series_port.append({
                    'serie': serie,
                    'pre': media_pre,
                    'pos': media_pos,
                    'n': len(dados_serie)
                })
        
        if series_port:
            series_nomes = [s['serie'] for s in series_port]
            pre_valores = [s['pre'] for s in series_port]
            pos_valores = [s['pos'] for s in series_port]
            
            x = np.arange(len(series_nomes))
            width = 0.35
            
            ax2.bar(x - width/2, pre_valores, width, label='Pré-teste', alpha=0.7, color='lightgreen')
            ax2.bar(x + width/2, pos_valores, width, label='Pós-teste', alpha=0.7, color='darkgreen')
            
            ax2.set_xlabel('Série')
            ax2.set_ylabel('Média de Acertos')
            ax2.set_title('Evolução por Série - Língua Portuguesa')
            ax2.set_xticks(x)
            ax2.set_xticklabels(series_nomes)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.caminho_figuras / 'fase5_evolucao_series.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Gráfico de evolução por série salvo")
    
    def gerar_grafico_distribuicao_crescimento(self):
        """Gera histograma da distribuição de crescimento"""
        print("📊 Gerando gráfico de distribuição de crescimento...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Matemática
        deltas_mat = self.df_matematica['Delta_Total_Acertos'].dropna()
        ax1.hist(deltas_mat, bins=30, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(deltas_mat.mean(), color='red', linestyle='--', 
                   label=f'Média: {deltas_mat.mean():.2f}')
        ax1.set_xlabel('Crescimento (pontos)')
        ax1.set_ylabel('Frequência')
        ax1.set_title('Distribuição de Crescimento - Matemática')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Português
        deltas_port = self.df_portugues['Delta_Total_Acertos'].dropna()
        ax2.hist(deltas_port, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax2.axvline(deltas_port.mean(), color='red', linestyle='--', 
                   label=f'Média: {deltas_port.mean():.2f}')
        ax2.set_xlabel('Crescimento (pontos)')
        ax2.set_ylabel('Frequência')
        ax2.set_title('Distribuição de Crescimento - Língua Portuguesa')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.caminho_figuras / 'fase5_distribuicao_crescimento.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Gráfico de distribuição de crescimento salvo")
    
    def gerar_ranking_escolas(self):
        """Gera gráfico de ranking das escolas"""
        print("📊 Gerando ranking de escolas...")
        
        # Usar dados já calculados
        with open('Data/estatisticas_escolas_fase5.json', 'r', encoding='utf-8') as f:
            estatisticas = json.load(f)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Ranking Matemática
        dados_mat = sorted(estatisticas['matematica'], 
                          key=lambda x: x['cohen_d'], reverse=True)[:10]
        
        if dados_mat:
            escolas = [d['escola'][:20] + '...' if len(d['escola']) > 20 else d['escola'] 
                      for d in dados_mat]
            cohen_values = [d['cohen_d'] for d in dados_mat]
            
            colors = ['green' if v >= 0.4 else 'orange' if v >= 0.2 else 'red' 
                     for v in cohen_values]
            
            bars1 = ax1.barh(escolas, cohen_values, color=colors, alpha=0.7)
            ax1.set_xlabel("Cohen's d")
            ax1.set_title('Top 10 Escolas - Matemática (por Effect Size)')
            ax1.axvline(0.4, color='red', linestyle='--', alpha=0.5, label='Benchmark (0.4)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Ranking Português
        dados_port = sorted(estatisticas['portugues'], 
                           key=lambda x: x['cohen_d'], reverse=True)[:10]
        
        if dados_port:
            escolas = [d['escola'][:20] + '...' if len(d['escola']) > 20 else d['escola'] 
                      for d in dados_port]
            cohen_values = [d['cohen_d'] for d in dados_port]
            
            colors = ['green' if v >= 0.4 else 'orange' if v >= 0.2 else 'red' 
                     for v in cohen_values]
            
            bars2 = ax2.barh(escolas, cohen_values, color=colors, alpha=0.7)
            ax2.set_xlabel("Cohen's d")
            ax2.set_title('Top 10 Escolas - Língua Portuguesa (por Effect Size)')
            ax2.axvline(0.4, color='red', linestyle='--', alpha=0.5, label='Benchmark (0.4)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.caminho_figuras / 'fase5_ranking_escolas.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Ranking de escolas salvo")
    
    def gerar_analise_habilidades(self):
        """Gera análise detalhada das habilidades"""
        print("📊 Gerando análise de habilidades...")
        
        # Identificar colunas de habilidades
        colunas_hab_mat = [col for col in self.df_matematica.columns 
                          if col.startswith('Total_Acertos_H') and col.endswith('_Pré')]
        
        colunas_hab_port = [col for col in self.df_portugues.columns 
                           if col.startswith('Total_Acertos_H') and col.endswith('_Pré')]
        
        # Analisar habilidades matemática
        dados_hab_mat = []
        for col_pre in colunas_hab_mat:
            habilidade = col_pre.replace('Total_Acertos_', '').replace('_Pré', '')
            col_pos = f'Total_Acertos_{habilidade}_Pós'
            col_delta = f'Delta_Total_Acertos_{habilidade}'
            
            if col_pos in self.df_matematica.columns and col_delta in self.df_matematica.columns:
                media_delta = self.df_matematica[col_delta].mean()
                std_delta = self.df_matematica[col_delta].std()
                cohen_d = media_delta / std_delta if std_delta > 0 else 0
                
                dados_hab_mat.append({
                    'habilidade': habilidade,
                    'media_delta': round(media_delta, 3),
                    'cohen_d': round(cohen_d, 3),
                    'disciplina': 'Matemática'
                })
        
        # Analisar habilidades português
        dados_hab_port = []
        for col_pre in colunas_hab_port:
            habilidade = col_pre.replace('Total_Acertos_', '').replace('_Pré', '')
            col_pos = f'Total_Acertos_{habilidade}_Pós'
            col_delta = f'Delta_Total_Acertos_{habilidade}'
            
            if col_pos in self.df_portugues.columns and col_delta in self.df_portugues.columns:
                media_delta = self.df_portugues[col_delta].mean()
                std_delta = self.df_portugues[col_delta].std()
                cohen_d = media_delta / std_delta if std_delta > 0 else 0
                
                dados_hab_port.append({
                    'habilidade': habilidade,
                    'media_delta': round(media_delta, 3),
                    'cohen_d': round(cohen_d, 3),
                    'disciplina': 'Língua Portuguesa'
                })
        
        # Salvar dados das habilidades
        dados_habilidades = {
            'matematica': dados_hab_mat,
            'portugues': dados_hab_port
        }
        
        with open('Data/analise_habilidades_fase5.json', 'w', encoding='utf-8') as f:
            json.dump(dados_habilidades, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Análise de {len(dados_hab_mat)} habilidades (Mat) e {len(dados_hab_port)} habilidades (Port)")
        return dados_habilidades
    
    def executar_pipeline_completo(self):
        """Executa pipeline completo de geração de visualizações"""
        print("🚀 Iniciando pipeline completo de visualizações...")
        
        try:
            # 1. Dados para filtros
            self.gerar_dados_filtros()
            
            # 2. Estatísticas por escola
            self.calcular_estatisticas_por_escola()
            
            # 3. Gráficos principais
            graficos_base64 = self.gerar_graficos_base64()
            
            # 4. Análise de habilidades
            self.gerar_analise_habilidades()
            
            # 5. Gerar HTML integrado
            self.gerar_html_integrado(graficos_base64)
            
            print("🎉 Pipeline de visualizações concluído com sucesso!")
            print(f"📁 Arquivos gerados em: {self.caminho_figuras}")
            print("📊 Dados JSON salvos em: Data/")
            print("🌐 HTML integrado gerado: Data/relatorio_visual_wordgen_fase5_integrado.html")
            
        except Exception as e:
            print(f"❌ Erro no pipeline: {e}")
            raise
    
    def gerar_graficos_base64(self):
        """Gera gráficos e converte para base64"""
        print("🎨 Gerando gráficos em base64...")
        
        graficos = {}
        
        # 1. Gráfico de evolução por série
        graficos['evolucao_series'] = self.criar_grafico_evolucao_series_base64()
        
        # 2. Distribuição de crescimento
        graficos['distribuicao_crescimento'] = self.criar_grafico_distribuicao_base64()
        
        # 3. Ranking de escolas
        graficos['ranking_escolas'] = self.criar_grafico_ranking_base64()
        
        # 4. Conjuntos filtrados para uso dinâmico
        graficos['filtrados'] = self.gerar_graficos_filtrados_base64()
        
        print("✅ Gráficos convertidos para base64")
        return graficos
    
    def criar_grafico_evolucao_series_base64(self):
        """Cria gráfico de evolução por série e retorna base64"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Matemática
        series_mat = []
        for serie in ['6º ANO', '7º ANO', '8º ANO', '9º ANO']:
            dados_serie = self.df_matematica[self.df_matematica['Serie'] == serie]
            if len(dados_serie) > 0:
                media_pre = dados_serie['Total_Acertos_Pré'].mean()
                media_pos = dados_serie['Total_Acertos_Pós'].mean()
                series_mat.append({
                    'serie': serie,
                    'pre': media_pre,
                    'pos': media_pos,
                    'n': len(dados_serie)
                })
        
        if series_mat:
            series_nomes = [s['serie'] for s in series_mat]
            pre_valores = [s['pre'] for s in series_mat]
            pos_valores = [s['pos'] for s in series_mat]
            
            x = np.arange(len(series_nomes))
            width = 0.35
            
            ax1.bar(x - width/2, pre_valores, width, label='Pré-teste', alpha=0.7, color='lightblue')
            ax1.bar(x + width/2, pos_valores, width, label='Pós-teste', alpha=0.7, color='darkblue')
            
            ax1.set_xlabel('Série')
            ax1.set_ylabel('Média de Acertos')
            ax1.set_title('Evolução por Série - Matemática')
            ax1.set_xticks(x)
            ax1.set_xticklabels(series_nomes)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Português
        series_port = []
        for serie in ['6º ANO', '7º ANO', '8º ANO', '9º ANO']:
            dados_serie = self.df_portugues[self.df_portugues['Serie'] == serie]
            if len(dados_serie) > 0:
                media_pre = dados_serie['Total_Acertos_Pré'].mean()
                media_pos = dados_serie['Total_Acertos_Pós'].mean()
                series_port.append({
                    'serie': serie,
                    'pre': media_pre,
                    'pos': media_pos,
                    'n': len(dados_serie)
                })
        
        if series_port:
            series_nomes = [s['serie'] for s in series_port]
            pre_valores = [s['pre'] for s in series_port]
            pos_valores = [s['pos'] for s in series_port]
            
            x = np.arange(len(series_nomes))
            width = 0.35
            
            ax2.bar(x - width/2, pre_valores, width, label='Pré-teste', alpha=0.7, color='lightgreen')
            ax2.bar(x + width/2, pos_valores, width, label='Pós-teste', alpha=0.7, color='darkgreen')
            
            ax2.set_xlabel('Série')
            ax2.set_ylabel('Média de Acertos')
            ax2.set_title('Evolução por Série - Língua Portuguesa')
            ax2.set_xticks(x)
            ax2.set_xticklabels(series_nomes)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def criar_grafico_distribuicao_base64(self):
        """Cria gráfico de distribuição e retorna base64"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Matemática
        deltas_mat = self.df_matematica['Delta_Total_Acertos'].dropna()
        ax1.hist(deltas_mat, bins=30, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(deltas_mat.mean(), color='red', linestyle='--', 
                   label=f'Média: {deltas_mat.mean():.2f}')
        ax1.set_xlabel('Crescimento (pontos)')
        ax1.set_ylabel('Frequência')
        ax1.set_title('Distribuição de Crescimento - Matemática')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Português
        deltas_port = self.df_portugues['Delta_Total_Acertos'].dropna()
        ax2.hist(deltas_port, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax2.axvline(deltas_port.mean(), color='red', linestyle='--', 
                   label=f'Média: {deltas_port.mean():.2f}')
        ax2.set_xlabel('Crescimento (pontos)')
        ax2.set_ylabel('Frequência')
        ax2.set_title('Distribuição de Crescimento - Língua Portuguesa')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def criar_grafico_ranking_base64(self):
        """Cria gráfico de ranking e retorna base64"""
        # Usar dados já calculados
        with open('Data/estatisticas_escolas_fase5.json', 'r', encoding='utf-8') as f:
            estatisticas = json.load(f)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Ranking Matemática
        dados_mat = sorted(estatisticas['matematica'], 
                          key=lambda x: x['cohen_d'], reverse=True)[:10]
        
        if dados_mat:
            escolas = [d['escola'][:20] + '...' if len(d['escola']) > 20 else d['escola'] 
                      for d in dados_mat]
            cohen_values = [d['cohen_d'] for d in dados_mat]
            
            colors = ['green' if v >= 0.4 else 'orange' if v >= 0.2 else 'red' 
                     for v in cohen_values]
            
            bars1 = ax1.barh(escolas, cohen_values, color=colors, alpha=0.7)
            ax1.set_xlabel("Cohen's d")
            ax1.set_title('Top 10 Escolas - Matemática (por Effect Size)')
            ax1.axvline(0.4, color='red', linestyle='--', alpha=0.5, label='Benchmark (0.4)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Ranking Português
        dados_port = sorted(estatisticas['portugues'], 
                           key=lambda x: x['cohen_d'], reverse=True)[:10]
        
        if dados_port:
            escolas = [d['escola'][:20] + '...' if len(d['escola']) > 20 else d['escola'] 
                      for d in dados_port]
            cohen_values = [d['cohen_d'] for d in dados_port]
            
            colors = ['green' if v >= 0.4 else 'orange' if v >= 0.2 else 'red' 
                     for v in cohen_values]
            
            bars2 = ax2.barh(escolas, cohen_values, color=colors, alpha=0.7)
            ax2.set_xlabel("Cohen's d")
            ax2.set_title('Top 10 Escolas - Língua Portuguesa (por Effect Size)')
            ax2.axvline(0.4, color='red', linestyle='--', alpha=0.5, label='Benchmark (0.4)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"

    def gerar_grafico_evolucao_filtrado_base64(self, dados_mat, dados_port, disciplina):
        """Gera gráfico de evolução considerando filtros aplicados"""
        if disciplina == 'ambas':
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            self._plotar_evolucao_por_disciplina(axes[0], dados_mat, 'Evolução - Matemática', 'lightblue', 'darkblue')
            self._plotar_evolucao_por_disciplina(axes[1], dados_port, 'Evolução - Língua Portuguesa', 'lightgreen', 'darkgreen')
        elif disciplina == 'matematica':
            fig, ax = plt.subplots(1, 1, figsize=(7, 6))
            self._plotar_evolucao_por_disciplina(ax, dados_mat, 'Evolução - Matemática', 'lightblue', 'darkblue')
        else:
            fig, ax = plt.subplots(1, 1, figsize=(7, 6))
            self._plotar_evolucao_por_disciplina(ax, dados_port, 'Evolução - Língua Portuguesa', 'lightgreen', 'darkgreen')
        plt.tight_layout()
        return self._converter_figura_para_base64(fig)

    def gerar_grafico_distribuicao_filtrado_base64(self, dados_mat, dados_port, disciplina):
        """Gera gráfico de distribuição considerando filtros aplicados"""
        if disciplina == 'ambas':
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            self._plotar_distribuicao_por_disciplina(axes[0], dados_mat, 'Distribuição - Matemática', 'royalblue')
            self._plotar_distribuicao_por_disciplina(axes[1], dados_port, 'Distribuição - Língua Portuguesa', 'seagreen')
        elif disciplina == 'matematica':
            fig, ax = plt.subplots(1, 1, figsize=(7, 6))
            self._plotar_distribuicao_por_disciplina(ax, dados_mat, 'Distribuição - Matemática', 'royalblue')
        else:
            fig, ax = plt.subplots(1, 1, figsize=(7, 6))
            self._plotar_distribuicao_por_disciplina(ax, dados_port, 'Distribuição - Língua Portuguesa', 'seagreen')
        plt.tight_layout()
        return self._converter_figura_para_base64(fig)

    def gerar_graficos_filtrados_base64(self):
        """Gera coleção de gráficos filtrados para todas as combinações relevantes"""
        print("🧩 Gerando variações filtradas de gráficos...")
        disciplinas = ['ambas', 'matematica', 'portugues']
        escolas = sorted({e for e in self.df_matematica['Escola'].dropna().unique()} |
                         {e for e in self.df_portugues['Escola'].dropna().unique()})
        series = sorted({self._normalizar_serie_label(s) for s in self.df_matematica['Serie'].dropna().unique()} |
                        {self._normalizar_serie_label(s) for s in self.df_portugues['Serie'].dropna().unique()},
                        key=self._ordenar_series)
        combinacoes = {
            'evolucao': {},
            'distribuicao': {}
        }
        for disciplina in disciplinas:
            for escola in ['todas'] + escolas:
                for serie in ['todas'] + [s for s in series if s]:
                    dados_mat = self._filtrar_dataframe(self.df_matematica, escola, serie)
                    dados_port = self._filtrar_dataframe(self.df_portugues, escola, serie)
                    chave = f"{disciplina}|{escola}|{serie if serie else 'todas'}"
                    combinacoes['evolucao'][chave] = self.gerar_grafico_evolucao_filtrado_base64(dados_mat, dados_port, disciplina)
                    combinacoes['distribuicao'][chave] = self.gerar_grafico_distribuicao_filtrado_base64(dados_mat, dados_port, disciplina)
        print(f"✅ {len(combinacoes['evolucao'])} variações de evolução e {len(combinacoes['distribuicao'])} distribuições geradas")
        return combinacoes
    
    def gerar_html_integrado(self, graficos_base64):
        """Gera HTML com dados e gráficos integrados"""
        print("📄 Gerando HTML integrado...")
        
        # Carregar dados auxiliares
        with open('Data/dados_filtros_fase5.json', 'r', encoding='utf-8') as f:
            dados_filtros = json.load(f)
        
        with open('Data/estatisticas_escolas_fase5.json', 'r', encoding='utf-8') as f:
            estatisticas_escolas = json.load(f)
        
        with open('Data/analise_habilidades_fase5.json', 'r', encoding='utf-8') as f:
            analise_habilidades = json.load(f)
        
        # Preparar dados CSV completos (mas otimizados para HTML)
        # Incluir apenas colunas essenciais para reduzir tamanho do arquivo
        colunas_essenciais = ['ID_Aluno', 'Nome', 'Escola', 'Serie', 'Turma', 
                             'Total_Acertos_Pré', 'Total_Acertos_Pós', 'Delta_Total_Acertos']
        
        # Adicionar colunas de habilidades principais
        colunas_habilidades_mat = [col for col in self.df_matematica.columns 
                                  if col.startswith('Total_Acertos_H') and not col.startswith('Delta_')]
        colunas_habilidades_port = [col for col in self.df_portugues.columns 
                                   if col.startswith('Total_Acertos_H') and not col.startswith('Delta_')]
        
        # Dados matemática com colunas essenciais
        dados_mat_otimizado = self.df_matematica[colunas_essenciais + colunas_habilidades_mat[:10]].copy()
        dados_mat_sample = dados_mat_otimizado.to_csv(index=False)
        
        # Dados português com colunas essenciais  
        dados_port_otimizado = self.df_portugues[colunas_essenciais + colunas_habilidades_port[:10]].copy()
        dados_port_sample = dados_port_otimizado.to_csv(index=False)
        
        # Template HTML
        html_template = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Relatório Visual - WordGen Fase 5 - Integrado</title>
<style>
    :root {{
        --bg: #f5f6fa;
        --text: #2c3e50;
        --muted: #6b7280;
        --purple1: #6a11cb;
        --purple2: #8d36ff;
        --blue1: #1e3a8a;
        --blue2: #3b82f6;
        --card-grad: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --green-grad: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        --red-grad: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        --yellow-grad: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        --math-grad: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        --port-grad: linear-gradient(135deg, #059669 0%, #10b981 100%);
    }}
    body {{
        margin: 0; background: var(--bg); color: var(--text); font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }}
    .header {{
        background: linear-gradient(120deg, var(--purple1) 0%, var(--purple2) 100%);
        color: #fff; padding: 28px 18px; box-shadow: 0 2px 14px rgba(0,0,0,.12);
    }}
    .header .title {{
        font-size: 26px; font-weight: 700; margin: 0;
    }}
    .header .subtitle {{
        font-size: 14px; opacity: 0.95; margin-top: 6px;
    }}
    .header .timestamp {{
        font-size: 12px; opacity: 0.85; margin-top: 4px;
    }}
    
    .menu-container {{
        background: #fff; margin: 18px auto; max-width: 1200px; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }}
    .menu-title {{
        font-size: 18px; font-weight: 600; margin-bottom: 12px; color: var(--purple1);
    }}
    .filters-grid {{
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 12px;
    }}
    @media (max-width: 768px) {{ .filters-grid {{ grid-template-columns: 1fr; }} }}
    .filter-group {{
        display: flex; flex-direction: column;
    }}
    .filter-label {{
        font-size: 14px; font-weight: 500; margin-bottom: 6px; color: var(--text);
    }}
    .filter-select {{
        width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px; background: #fff; cursor: pointer;
        transition: border-color 0.3s ease;
    }}
    .filter-select:focus {{
        outline: none; border-color: var(--purple1);
    }}
    
    .container {{
        max-width: 1200px; margin: 18px auto; background: #fff; border-radius: 12px; padding: 22px; box-shadow: 0 10px 24px rgba(0,0,0,.06);
    }}
    .cards {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-top: 16px;
    }}
    .card {{
        background: var(--card-grad); color: #fff; border-radius: 10px; padding: 14px; box-shadow: 0 4px 12px rgba(0,0,0,.12);
    }}
    .card.green {{ background: var(--green-grad); }}
    .card.red {{ background: var(--red-grad); }}
    .card.yellow {{ background: var(--yellow-grad); }}
    .card.math {{ background: var(--math-grad); }}
    .card.port {{ background: var(--port-grad); }}
    .card .card-label {{ font-size: 13px; opacity: 0.95; }}
    .card .valor {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
    .card .desc {{ font-size: 11px; opacity: 0.9; }}

    h2.section {{
        margin-top: 22px; font-size: 18px; border-left: 4px solid var(--purple1); padding-left: 10px; color: #1f2937;
    }}
    .figs {{ display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 10px; }}
    .figs-dual {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 10px; }}
    @media (max-width: 768px) {{ .figs-dual {{ grid-template-columns: 1fr; }} }}
    .fig {{ background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 8px; }}
    .fig img {{ width: 100%; height: auto; border-radius: 6px; }}
    .fig .caption {{ font-size: 12px; color: var(--muted); margin-top: 6px; text-align: center; }}

    .interp {{ background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 14px; margin-top: 10px; }}
    .grupo-item {{ background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px 12px; margin: 10px 0; }}
    .grupo-titulo {{ font-weight: 600; }}
    .grupo-detalhes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 6px; color: #374151; font-size: 13px; margin-top: 6px; }}
    .interpretacao-grupo {{ margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid var(--purple1); }}
    .interpretacao-grupo p {{ margin: 3px 0; font-size: 12px; }}
    .interpretacao-grupo strong {{ color: var(--purple1); }}

    .habilidades-grid {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;
    }}
    .habilidade-card {{
        background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,.1);
    }}
    .habilidade-titulo {{ font-weight: 600; font-size: 14px; margin-bottom: 6px; }}
    .habilidade-stats {{ font-size: 12px; color: var(--muted); }}
    .habilidade-delta {{ font-weight: 600; }}
    .habilidade-delta.positive {{ color: #059669; }}
    .habilidade-delta.negative {{ color: #dc2626; }}

    .recomendacoes {{
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
        border: 1px solid #f59e0b; border-radius: 10px; padding: 16px; margin-top: 16px;
    }}
    .recomendacao-titulo {{ font-weight: 600; color: #92400e; margin-bottom: 8px; }}
    .recomendacao-item {{ margin: 6px 0; color: #92400e; font-size: 14px; }}

    .foot-note {{ font-size: 12px; color: var(--muted); text-align: center; margin-top: 16px; }}
    
    .loading {{ text-align: center; padding: 40px; color: var(--muted); }}
    .error {{ text-align: center; padding: 40px; color: #dc2626; background: #fef2f2; border-radius: 8px; margin: 10px 0; }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">Relatório Visual WordGen - Fase 5</div>
        <div class="subtitle">Análise Matemática e Língua Portuguesa (6º ao 9º ano). Versão integrada para gestores.</div>
        <div class="timestamp" id="timestamp">Gerado em: <span id="dataHora"></span></div>
    </div>

    <div class="menu-container">
        <div class="menu-title">🔍 Filtros de Análise</div>
        <div class="filters-grid">
            <div class="filter-group">
                <div class="filter-label">🏫 Escola</div>
                <select class="filter-select" id="escolaSelect" onchange="atualizarDados()">
                    <option value="todas">Todas as Escolas</option>
                </select>
            </div>
            <div class="filter-group">
                <div class="filter-label">📚 Série</div>
                <select class="filter-select" id="serieSelect" onchange="atualizarDados()">
                    <option value="todas">Todas as Séries</option>
                    <option value="6">6º Ano</option>
                    <option value="7">7º Ano</option>
                    <option value="8">8º Ano</option>
                    <option value="9">9º Ano</option>
                </select>
            </div>
            <div class="filter-group">
                <div class="filter-label">📖 Disciplina</div>
                <select class="filter-select" id="disciplinaSelect" onchange="atualizarDados()">
                    <option value="matematica">Matemática</option>
                    <option value="portugues">Língua Portuguesa</option>
                </select>
            </div>
        </div>
    </div>

    <div class="container">
        <h2 class="section">📊 Indicadores Principais</h2>
        <div class="cards" id="cardsContainer">
            <div class="loading">Carregando indicadores...</div>
        </div>

        <h2 class="section">📈 Evolução de Performance</h2>
        <div class="figs-dual">
            <div class="fig" id="grafico-evolucao-geral">
                <img id="img-evolucao-performance" src="{graficos_base64['evolucao_series']}" alt="Evolução por Série" style="width: 100%; height: auto;">
                <div class="caption">Evolução das médias pré/pós teste por série em ambas as disciplinas</div>
            </div>
            <div class="fig" id="grafico-distribuicao-crescimento">
                <img id="img-distribuicao-crescimento" src="{graficos_base64['distribuicao_crescimento']}" alt="Distribuição de Crescimento" style="width: 100%; height: auto;">
                <div class="caption">Distribuição dos ganhos individuais de aprendizagem</div>
            </div>
        </div>

        <h2 class="section">🎯 Análise por Habilidades</h2>
        <div class="habilidades-grid" id="habilidadesContainer">
            <div class="loading">Carregando análise de habilidades...</div>
        </div>

        <h2 class="section">🏆 Comparações Entre Escolas e Séries</h2>
        <div class="figs-dual">
            <div class="fig" id="comparacao-escolas">
                <div id="comparacao-escolas-conteudo">
                    <div class="loading">Carregando comparação entre escolas...</div>
                </div>
            </div>
            <div class="fig" id="grafico-series-comparacao">
                <div id="comparacao-series-conteudo">
                    <div class="loading">Carregando comparação entre séries...</div>
                </div>
            </div>
        </div>

        <h2 class="section">📋 Qualidade dos Dados</h2>
        <div class="interp" id="qualidadeDados">
            <div class="loading">Carregando indicadores de qualidade...</div>
        </div>

        <h2 class="section">💡 Recomendações</h2>
        <div class="recomendacoes" id="recomendacoesContainer">
            <div class="loading">Gerando recomendações...</div>
        </div>

        <div class="foot-note">
            Relatório baseado na análise de dados da Fase 5 do programa WordGen. 
            Métricas calculadas usando Cohen's d e benchmarks educacionais (Hattie, 2009).
            <br>Dados processados em formato pareado garantindo comparabilidade pré/pós intervenção.
            <br><strong>Versão integrada</strong> - Todos os dados e gráficos embutidos no arquivo HTML.
        </div>
    </div>

<script>
// Dados integrados
const DADOS_INTEGRADOS = {{
    filtros: {json.dumps(dados_filtros, ensure_ascii=False)},
    estatisticas_escolas: {json.dumps(estatisticas_escolas, ensure_ascii=False)},
    analise_habilidades: {json.dumps(analise_habilidades, ensure_ascii=False)},
    sample_data: {{
        matematica: `{dados_mat_sample}`,
        portugues: `{dados_port_sample}`
    }},
    graficos: {{
        padrao: {{
            evolucao: "{graficos_base64['evolucao_series']}",
            distribuicao: "{graficos_base64['distribuicao_crescimento']}"
        }},
        filtrados: {json.dumps(graficos_base64.get('filtrados', {}), ensure_ascii=False)}
    }}
}};

// Variáveis globais
let dadosMatematica = null;
let dadosPortugues = null;
let dadosCarregados = false;

// Função para formatar timestamp
function formatarTimestamp() {{
    const agora = new Date();
    const data = agora.toLocaleDateString('pt-BR');
    const hora = agora.toLocaleTimeString('pt-BR');
    document.getElementById('dataHora').textContent = `${{data}} às ${{hora}}`;
}}

// Função para converter CSV string em array de objetos
function parseCSV(csv) {{
    const linhas = csv.trim().split('\\n');
    const headers = linhas[0].split(',');
    
    return linhas.slice(1).map(linha => {{
        const valores = linha.split(',');
        const obj = {{}};
        headers.forEach((header, index) => {{
            obj[header] = valores[index] || '';
        }});
        return obj;
    }});
}}

// Função para carregar dados integrados
function carregarDados() {{
    try {{
        console.log('Carregando dados integrados...');
        
        // Carregar dados CSV das amostras
        dadosMatematica = parseCSV(DADOS_INTEGRADOS.sample_data.matematica);
        dadosPortugues = parseCSV(DADOS_INTEGRADOS.sample_data.portugues);
        
        // Disponibilizar dados auxiliares globalmente
        window.dadosFiltros = DADOS_INTEGRADOS.filtros;
        window.estatisticasEscolas = DADOS_INTEGRADOS.estatisticas_escolas;
        window.analiseHabilidades = DADOS_INTEGRADOS.analise_habilidades;
        
        dadosCarregados = true;
        console.log('Dados integrados carregados com sucesso:', {{
            matematica: dadosMatematica.length,
            portugues: dadosPortugues.length
        }});
        
        popularFiltros();
        atualizarDados();
        
    }} catch (error) {{
        console.error('Erro ao carregar dados integrados:', error);
        mostrarErro('Erro ao carregar os dados integrados.');
    }}
}}'''
        
        # Adicionar resto do JavaScript (continua...)
        
        # Salvar HTML integrado
        with open('Data/relatorio_visual_wordgen_fase5_integrado.html', 'w', encoding='utf-8') as f:
            f.write(html_template)
            # Adicionar o resto do JavaScript aqui
            f.write(self.obter_javascript_completo())
        
        print("✅ HTML integrado gerado com sucesso")
    
    def obter_javascript_completo(self):
        """Retorna o JavaScript completo para o HTML integrado"""
        return '''
function formatarNomeEscola(escola) {
    if (!escola || escola === 'todas') {
        return 'Todas as Escolas';
    }
    return escola.toLowerCase().replace(/\\b\\w/g, l => l.toUpperCase());
}

function obterSerieChave(serieValor) {
    if (!serieValor || serieValor === 'todas') {
        return 'todas';
    }
    const chave = `${serieValor}º ANO`;
    return chave.toUpperCase().replace('°', 'º');
}

function montarLegendaFiltros(escola, serieValor, disciplina) {
    const partes = [];
    if (disciplina && disciplina !== 'ambas') {
        const nomeDisciplina = disciplina === 'matematica' ? 'Matemática' : 'Língua Portuguesa';
        partes.push(`Disciplina: ${nomeDisciplina}`);
    }
    if (escola && escola !== 'todas') {
        partes.push(`Escola: ${formatarNomeEscola(escola)}`);
    }
    if (serieValor && serieValor !== 'todas') {
        partes.push(`Série: ${serieValor}º ano`);
    }
    return partes.join(' • ');
}

// Função para popular os filtros
function popularFiltros() {
    if (!dadosCarregados) return;
    
    const escolaSelect = document.getElementById('escolaSelect');
    escolaSelect.innerHTML = '<option value="todas">Todas as Escolas</option>';
    
    if (window.dadosFiltros && window.dadosFiltros.escolas) {
        console.log('Usando dados de filtros integrados');
        window.dadosFiltros.escolas.forEach(escola => {
            if (escola && escola.trim()) {
                const escolaFormatada = escola.toLowerCase().replace(/\\b\\w/g, l => l.toUpperCase());
                escolaSelect.innerHTML += `<option value="${escola}">${escolaFormatada}</option>`;
            }
        });
    }
    
    console.log(`Escolas carregadas: ${escolaSelect.options.length - 1}`);
}

// Função principal para atualizar dados
function atualizarDados() {
    if (!dadosCarregados) return;
    
    const escola = document.getElementById('escolaSelect').value;
    const serie = document.getElementById('serieSelect').value;
    const disciplina = document.getElementById('disciplinaSelect').value;
    
    console.log('Atualizando dados com filtros:', { escola, serie, disciplina });
    
    const dadosFiltrados = filtrarDados(escola, serie, disciplina);
    
    atualizarIndicadores(dadosFiltrados);
    atualizarGraficosInterativos(dadosFiltrados);  // Nova função para gráficos
    atualizarComparacaoEscolasESeries(dadosFiltrados);  // Renomeada
    atualizarHabilidades(dadosFiltrados);
    atualizarQualidadeDados(dadosFiltrados);
    atualizarRecomendacoes(dadosFiltrados);
}

// Função para filtrar dados
function filtrarDados(escola, serie, disciplina) {
    let dadosMat = dadosMatematica;
    let dadosPort = dadosPortugues;
    
    if (escola !== 'todas') {
        dadosMat = dadosMat.filter(row => row.Escola === escola);
        dadosPort = dadosPort.filter(row => row.Escola === escola);
    }
    
    if (serie !== 'todas') {
        const serieFiltro = `${serie}º ANO`;
        dadosMat = dadosMat.filter(row => row.Serie === serieFiltro);
        dadosPort = dadosPort.filter(row => row.Serie === serieFiltro);
    }
    
    return { matematica: dadosMat, portugues: dadosPort };
}

// Função para calcular estatísticas
function calcularEstatisticas(dados, prefixo = 'Total_Acertos') {
    const colunaPre = `${prefixo}_Pré`;
    const colunaPos = `${prefixo}_Pós`;
    const colunaDelta = `Delta_${prefixo}`;
    
    const valoresPre = dados.map(row => parseFloat(row[colunaPre]) || 0);
    const valoresPos = dados.map(row => parseFloat(row[colunaPos]) || 0);
    const valoresDelta = dados.map(row => parseFloat(row[colunaDelta]) || 0);
    
    const n = dados.length;
    if (n === 0) {
        return {
            n: 0,
            mediaPre: '0.00',
            mediaPos: '0.00',
            mediaDelta: '0.00',
            cohenD: '0.000',
            percMelhoraram: '0.0',
            percPioraram: '0.0',
            percMantiveram: '0.0',
            totalMelhoraram: 0,
            totalPioraram: 0,
            totalMantiveram: 0
        };
    }

    const somaPre = valoresPre.reduce((a, b) => a + b, 0);
    const somaPos = valoresPos.reduce((a, b) => a + b, 0);
    const somaDelta = valoresDelta.reduce((a, b) => a + b, 0);
    const mediaPre = somaPre / n;
    const mediaPos = somaPos / n;
    const mediaDelta = somaDelta / n;
    
    const varianceDelta = valoresDelta.reduce((acc, val) => acc + Math.pow(val - mediaDelta, 2), 0) / n;
    const desvioPadraoDelta = varianceDelta > 0 ? Math.sqrt(varianceDelta) : 0;
    
    const cohenD = desvioPadraoDelta !== 0 ? mediaDelta / desvioPadraoDelta : 0;
    
    const melhoraram = valoresDelta.filter(d => d > 0).length;
    const pioraram = valoresDelta.filter(d => d < 0).length;
    const mantiveram = valoresDelta.filter(d => d === 0).length;
    
    return {
        n,
        mediaPre: mediaPre.toFixed(2),
        mediaPos: mediaPos.toFixed(2),
        mediaDelta: mediaDelta.toFixed(2),
        cohenD: cohenD.toFixed(3),
        percMelhoraram: ((melhoraram / n) * 100).toFixed(1),
        percPioraram: ((pioraram / n) * 100).toFixed(1),
        percMantiveram: ((mantiveram / n) * 100).toFixed(1),
        totalMelhoraram: melhoraram,
        totalPioraram: pioraram,
        totalMantiveram: mantiveram
    };
}

function combinarDadosAmbas(dadosMat, dadosPort) {
    const mapa = new Map();
    const adicionar = (row = {}) => {
        const id = row.ID_Aluno || `${row.Nome || ''}-${row.Escola || ''}-${row.Serie || ''}`;
        if (!mapa.has(id)) {
            mapa.set(id, {
                pre: [],
                pos: [],
                delta: []
            });
        }
        const registro = mapa.get(id);
        const pre = parseFloat(row['Total_Acertos_Pré']);
        const pos = parseFloat(row['Total_Acertos_Pós']);
        const delta = parseFloat(row['Delta_Total_Acertos']);
        if (!Number.isNaN(pre)) registro.pre.push(pre);
        if (!Number.isNaN(pos)) registro.pos.push(pos);
        if (!Number.isNaN(delta)) registro.delta.push(delta);
    };
    (dadosMat || []).forEach(adicionar);
    (dadosPort || []).forEach(adicionar);
    return Array.from(mapa.values()).map(registro => {
        const media = arr => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
        return {
            'Total_Acertos_Pré': media(registro.pre),
            'Total_Acertos_Pós': media(registro.pos),
            'Delta_Total_Acertos': media(registro.delta)
        };
    });
}

function obterDadosIndicadores(dadosFiltrados, disciplina) {
    if (disciplina === 'matematica') {
        return { dados: dadosFiltrados.matematica || [], rotulo: 'Estudantes de Matemática' };
    }
    if (disciplina === 'portugues') {
        return { dados: dadosFiltrados.portugues || [], rotulo: 'Estudantes de Língua Portuguesa' };
    }
    return {
        dados: combinarDadosAmbas(dadosFiltrados.matematica, dadosFiltrados.portugues),
        rotulo: 'Estudantes (Matemática + Língua Portuguesa)'
    };
}

function classificarEffectSize(valor) {
    const d = parseFloat(valor);
    if (Number.isNaN(d)) {
        return { texto: 'Sem dados suficientes', classe: 'yellow' };
    }
    if (d >= 0.6) {
        return { texto: 'Impacto Excelente 🏆', classe: 'green' };
    }
    if (d >= 0.4) {
        return { texto: 'Bom Resultado ✅', classe: 'green' };
    }
    if (d >= 0.2) {
        return { texto: 'Resultado Moderado ⚠️', classe: 'yellow' };
    }
    if (d > 0) {
        return { texto: 'Ganho Discreto 🔍', classe: 'yellow' };
    }
    return { texto: 'Sem ganho aparente', classe: 'red' };
}

function formatarDelta(valor) {
    const numero = parseFloat(valor);
    if (Number.isNaN(numero)) return '0.0';
    const sinal = numero >= 0 ? '+' : '';
    return `${sinal}${numero.toFixed(1)}`;
}

function formatarPercentual(valor) {
    const numero = parseFloat(valor);
    if (Number.isNaN(numero)) return '0%';
    return `${numero.toFixed(1)}%`;
}

// Função para atualizar indicadores
function atualizarIndicadores(dadosFiltrados) {
    const container = document.getElementById('cardsContainer');
    const disciplina = document.getElementById('disciplinaSelect').value;
    const { dados, rotulo } = obterDadosIndicadores(dadosFiltrados, disciplina);
    const estatisticas = calcularEstatisticas(dados);

    if (!dados || dados.length === 0 || estatisticas.n === 0) {
        container.innerHTML = `
            <div class="card red">
                <div class="card-label">⚠️ Sem dados disponíveis</div>
                <div class="valor">0</div>
                <div class="desc">Ajuste os filtros para visualizar os indicadores</div>
            </div>
        `;
        return;
    }

    const deltaFormatado = formatarDelta(estatisticas.mediaDelta);
    const percentualEvolucao = formatarPercentual(estatisticas.percMelhoraram);
    const efeito = classificarEffectSize(estatisticas.cohenD);
    const classeEfeito = efeito.classe ? ` ${efeito.classe}` : '';

    const cards = `
        <div class="card">
            <div class="card-label">👤 Nº de Participantes</div>
            <div class="valor">${estatisticas.n}</div>
            <div class="desc">${rotulo}</div>
        </div>
        <div class="card math">
            <div class="card-label">🧮 Ganho Médio (Delta)</div>
            <div class="valor">${deltaFormatado} acertos</div>
            <div class="desc">Média da coluna Δ Total_Acertos</div>
        </div>
        <div class="card${classeEfeito}">
            <div class="card-label">🎯 Tamanho do Efeito</div>
            <div class="valor">d = ${parseFloat(estatisticas.cohenD).toFixed(2)}</div>
            <div class="desc">${efeito.texto}</div>
        </div>
        <div class="card port">
            <div class="card-label">📈 % de Alunos que Evoluíram</div>
            <div class="valor">${percentualEvolucao}</div>
            <div class="desc">${estatisticas.totalMelhoraram} de ${estatisticas.n} estudantes</div>
        </div>
    `;

    container.innerHTML = cards;
}

// Função para atualizar gráficos interativos baseados nos filtros
function atualizarGraficosInterativos(dadosFiltrados) {
    const disciplina = document.getElementById('disciplinaSelect').value;
    const escola = document.getElementById('escolaSelect').value;
    const serieSelecionada = document.getElementById('serieSelect').value;
    const serieChave = obterSerieChave(serieSelecionada);
    const chaveGrafico = `${disciplina}|${escola}|${serieChave}`;

    const graficosPadrao = (DADOS_INTEGRADOS.graficos && DADOS_INTEGRADOS.graficos.padrao) ? DADOS_INTEGRADOS.graficos.padrao : {};
    const graficosFiltrados = (DADOS_INTEGRADOS.graficos && DADOS_INTEGRADOS.graficos.filtrados) ? DADOS_INTEGRADOS.graficos.filtrados : {};

    const imgEvolucao = document.getElementById('img-evolucao-performance');
    const imgDistribuicao = document.getElementById('img-distribuicao-crescimento');
    const captionEvolucao = document.querySelector('#grafico-evolucao-geral .caption');
    const captionDistribuicao = document.querySelector('#grafico-distribuicao-crescimento .caption');

    const graficoEvolucaoFiltrado = graficosFiltrados.evolucao ? graficosFiltrados.evolucao[chaveGrafico] : null;
    const graficoDistribuicaoFiltrado = graficosFiltrados.distribuicao ? graficosFiltrados.distribuicao[chaveGrafico] : null;

    const legenda = montarLegendaFiltros(escola, serieSelecionada, disciplina);

    if (graficoEvolucaoFiltrado) {
        imgEvolucao.src = graficoEvolucaoFiltrado;
        if (captionEvolucao) {
            captionEvolucao.innerHTML = legenda ? `Evolução das médias (${legenda})` : 'Evolução das médias pré/pós teste por série em ambas as disciplinas';
        }
    } else if (graficosPadrao.evolucao) {
        imgEvolucao.src = graficosPadrao.evolucao;
        if (captionEvolucao) {
            captionEvolucao.innerHTML = 'Evolução das médias pré/pós teste por série em ambas as disciplinas';
        }
    }

    if (graficoDistribuicaoFiltrado) {
        imgDistribuicao.src = graficoDistribuicaoFiltrado;
        if (captionDistribuicao) {
            captionDistribuicao.innerHTML = legenda ? `Distribuição de crescimento (${legenda})` : 'Distribuição dos ganhos individuais de aprendizagem';
        }
    } else if (graficosPadrao.distribuicao) {
        imgDistribuicao.src = graficosPadrao.distribuicao;
        if (captionDistribuicao) {
            captionDistribuicao.innerHTML = 'Distribuição dos ganhos individuais de aprendizagem';
        }
    }
}

// Função para atualizar comparações entre escolas e séries
function atualizarComparacaoEscolasESeries(dadosFiltrados) {
    atualizarComparacaoEscolas(dadosFiltrados);
    atualizarComparacaoSeries(dadosFiltrados);
}

// Função para atualizar comparação entre escolas
function atualizarComparacaoEscolas(dadosFiltrados) {
    const container = document.getElementById('comparacao-escolas-conteudo');
    const disciplina = document.getElementById('disciplinaSelect').value;
    
    let conteudo = '<div style="padding: 15px;">';
    conteudo += '<h3 style="text-align: center; margin-bottom: 15px; color: #6a11cb;">🏫 Comparação por Escola</h3>';
    
    if (disciplina === 'ambas' || disciplina === 'matematica') {
        const estatsMat = calcularEstatisticasPorEscola(dadosFiltrados.matematica, 'Matemática');
        conteudo += '<h4 style="color: #1e40af; margin-bottom: 10px;">📐 Matemática - Comparação por Escola</h4>';
        conteudo += criarTabelaComparacaoEscolas(estatsMat);
    }
    
    if (disciplina === 'ambas' || disciplina === 'portugues') {
        const estatsPort = calcularEstatisticasPorEscola(dadosFiltrados.portugues, 'Língua Portuguesa');
        conteudo += '<h4 style="color: #059669; margin-bottom: 10px; margin-top: 20px;">📝 Língua Portuguesa - Comparação por Escola</h4>';
        conteudo += criarTabelaComparacaoEscolas(estatsPort);
    }
    
    conteudo += '</div>';
    conteudo += '<div class="caption">Análise comparativa detalhada entre escolas por disciplina</div>';
    
    container.innerHTML = conteudo;
}

// Função para atualizar comparação entre séries
function atualizarComparacaoSeries(dadosFiltrados) {
    const container = document.getElementById('comparacao-series-conteudo');
    const disciplina = document.getElementById('disciplinaSelect').value;
    
    let conteudo = '<div style="padding: 15px;">';
    conteudo += '<h3 style="text-align: center; margin-bottom: 15px; color: #6a11cb;">📚 Comparação por Série</h3>';
    
    if (disciplina === 'ambas' || disciplina === 'matematica') {
        const estatsMat = calcularEstatisticasPorSerie(dadosFiltrados.matematica, 'Matemática');
        conteudo += '<h4 style="color: #1e40af; margin-bottom: 10px;">📐 Matemática - Comparação por Série</h4>';
        conteudo += criarTabelaComparacao(estatsMat);
    }
    
    if (disciplina === 'ambas' || disciplina === 'portugues') {
        const estatsPort = calcularEstatisticasPorSerie(dadosFiltrados.portugues, 'Língua Portuguesa');
        conteudo += '<h4 style="color: #059669; margin-bottom: 10px; margin-top: 20px;">📝 Língua Portuguesa - Comparação por Série</h4>';
        conteudo += criarTabelaComparacao(estatsPort);
    }
    
    conteudo += '</div>';
    conteudo += '<div class="caption">Análise comparativa detalhada entre as séries por disciplina</div>';
    
    container.innerHTML = conteudo;
}

// Função auxiliar para calcular estatísticas por série
function calcularEstatisticasPorSerie(dados, disciplina) {
    const series = ['6º ANO', '7º ANO', '8º ANO', '9º ANO'];
    const resultado = [];
    
    series.forEach(serie => {
        const dadosSerie = dados.filter(row => row.Serie === serie);
        if (dadosSerie.length > 0) {
            const stats = calcularEstatisticas(dadosSerie);
            resultado.push({
                serie: serie,
                disciplina: disciplina,
                ...stats
            });
        }
    });
    
    return resultado;
}

// Função auxiliar para calcular estatísticas por escola
function calcularEstatisticasPorEscola(dados, disciplina) {
    const escolas = [...new Set(dados.map(row => row.Escola))].filter(escola => escola && escola.trim());
    const resultado = [];
    
    escolas.forEach(escola => {
        const dadosEscola = dados.filter(row => row.Escola === escola);
        if (dadosEscola.length >= 5) { // Mínimo de 5 alunos por escola
            const stats = calcularEstatisticas(dadosEscola);
            resultado.push({
                escola: escola,
                disciplina: disciplina,
                ...stats
            });
        }
    });
    
    // Ordenar por Cohen's d (descrescente)
    return resultado.sort((a, b) => parseFloat(b.cohenD) - parseFloat(a.cohenD));
}

// Função para criar tabela de comparação por séries
function criarTabelaComparacao(estatisticas) {
    if (estatisticas.length === 0) return '<p style="text-align: center; color: #6b7280;">Nenhum dado disponível para esta disciplina</p>';
    
    let tabela = `
        <table style="width: 100%; margin: 10px 0; border-collapse: collapse; font-size: 13px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 10px 8px; text-align: left; font-weight: 600;">Série</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">N</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">Média Pré</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">Média Pós</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">Δ Média</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">Cohen's d</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">% Melhoraram</th>
                    <th style="padding: 10px 8px; text-align: center; font-weight: 600;">Status</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    estatisticas.forEach(stats => {
        const cohenD = parseFloat(stats.cohenD);
        const corCohend = cohenD >= 0.4 ? '#059669' : cohenD >= 0.2 ? '#f59e0b' : '#dc2626';
        const statusIcon = cohenD >= 0.4 ? '✅' : cohenD >= 0.2 ? '⚠️' : '🔍';
        const statusTexto = cohenD >= 0.4 ? 'Efetivo' : cohenD >= 0.2 ? 'Moderado' : 'Limitado';
        
        tabela += `
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 8px; font-weight: 500;">${stats.serie}</td>
                <td style="padding: 8px; text-align: center;">${stats.n}</td>
                <td style="padding: 8px; text-align: center;">${stats.mediaPre}</td>
                <td style="padding: 8px; text-align: center;">${stats.mediaPos}</td>
                <td style="padding: 8px; text-align: center; color: ${parseFloat(stats.mediaDelta) >= 0 ? '#059669' : '#dc2626'}; font-weight: 600;">
                    ${parseFloat(stats.mediaDelta) >= 0 ? '+' : ''}${stats.mediaDelta}
                </td>
                <td style="padding: 8px; text-align: center; color: ${corCohend}; font-weight: 600;">${stats.cohenD}</td>
                <td style="padding: 8px; text-align: center;">${stats.percMelhoraram}%</td>
                <td style="padding: 8px; text-align: center;">${statusIcon} ${statusTexto}</td>
            </tr>
        `;
    });
    
    tabela += '</tbody></table>';
    
    // Adicionar interpretação
    const melhorSerie = estatisticas.reduce((max, serie) => 
        parseFloat(serie.cohenD) > parseFloat(max.cohenD) ? serie : max
    );
    
    tabela += `
        <div style="margin-top: 10px; padding: 8px; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #0284c7;">
            <p style="margin: 0; font-size: 12px;"><strong>🏆 Melhor Performance:</strong> 
            ${melhorSerie.serie} com Cohen's d = ${melhorSerie.cohenD} 
            (${melhorSerie.percMelhoraram}% dos estudantes melhoraram)</p>
        </div>
    `;
    
    return tabela;
}

// Função para criar tabela de comparação por escolas
function criarTabelaComparacaoEscolas(estatisticas) {
    if (estatisticas.length === 0) return '<p style="text-align: center; color: #6b7280;">Nenhum dado disponível para esta disciplina</p>';
    
    // Limitar a 15 escolas para evitar tabelas muito longas
    const estatisticasLimitadas = estatisticas.slice(0, 15);
    
    let tabela = `
        <table style="width: 100%; margin: 10px 0; border-collapse: collapse; font-size: 12px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 8px 6px; text-align: left; font-weight: 600;">Escola</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">N</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">Pré</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">Pós</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">Δ</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">Cohen's d</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">% ↗</th>
                    <th style="padding: 8px 6px; text-align: center; font-weight: 600;">Status</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    estatisticasLimitadas.forEach((stats, index) => {
        const cohenD = parseFloat(stats.cohenD);
        const corCohend = cohenD >= 0.4 ? '#059669' : cohenD >= 0.2 ? '#f59e0b' : '#dc2626';
        const statusIcon = cohenD >= 0.4 ? '✅' : cohenD >= 0.2 ? '⚠️' : '🔍';
        const statusTexto = cohenD >= 0.4 ? 'Efetivo' : cohenD >= 0.2 ? 'Moderado' : 'Limitado';
        
        // Truncar nome da escola se muito longo
        const nomeEscola = stats.escola.length > 30 ? 
            stats.escola.substring(0, 27) + '...' : stats.escola;
        
        // Cor de fundo alternada
        const corFundo = index % 2 === 0 ? '#ffffff' : '#f9fafb';
        
        tabela += `
            <tr style="border-bottom: 1px solid #e5e7eb; background-color: ${corFundo};">
                <td style="padding: 6px; font-weight: 500; font-size: 11px;" title="${stats.escola}">${nomeEscola}</td>
                <td style="padding: 6px; text-align: center;">${stats.n}</td>
                <td style="padding: 6px; text-align: center;">${stats.mediaPre}</td>
                <td style="padding: 6px; text-align: center;">${stats.mediaPos}</td>
                <td style="padding: 6px; text-align: center; color: ${parseFloat(stats.mediaDelta) >= 0 ? '#059669' : '#dc2626'}; font-weight: 600;">
                    ${parseFloat(stats.mediaDelta) >= 0 ? '+' : ''}${stats.mediaDelta}
                </td>
                <td style="padding: 6px; text-align: center; color: ${corCohend}; font-weight: 600;">${stats.cohenD}</td>
                <td style="padding: 6px; text-align: center;">${stats.percMelhoraram}%</td>
                <td style="padding: 6px; text-align: center; font-size: 11px;">${statusIcon}</td>
            </tr>
        `;
    });
    
    tabela += '</tbody></table>';
    
    // Adicionar interpretação
    const melhorEscola = estatisticasLimitadas[0]; // Já está ordenada
    const totalEscolas = estatisticas.length;
    
    tabela += `
        <div style="margin-top: 10px; padding: 8px; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #0284c7;">
            <p style="margin: 0; font-size: 11px;">
                <strong>🏆 Melhor Escola:</strong> ${melhorEscola.escola.substring(0, 40)}${melhorEscola.escola.length > 40 ? '...' : ''}<br>
                Cohen's d = ${melhorEscola.cohenD} | ${melhorEscola.percMelhoraram}% melhoraram
            </p>
            ${totalEscolas > 15 ? `<p style="margin: 4px 0 0 0; font-size: 10px; color: #6b7280;">Mostrando top 15 de ${totalEscolas} escolas</p>` : ''}
        </div>
    `;
    
    return tabela;
}

// Função para atualizar habilidades
function atualizarHabilidades(dadosFiltrados) {
    const container = document.getElementById('habilidadesContainer');
    const disciplina = document.getElementById('disciplinaSelect').value;
    
    let habilidadesHTML = '';
    
    if (window.analiseHabilidades) {
        if (disciplina === 'ambas' || disciplina === 'matematica') {
            if (window.analiseHabilidades.matematica && window.analiseHabilidades.matematica.length > 0) {
                habilidadesHTML += '<h3 style="grid-column: 1/-1; margin: 0 0 10px 0; color: #1e40af;">📐 Matemática</h3>';
                
                const habilidadesMat = window.analiseHabilidades.matematica
                    .sort((a, b) => b.cohen_d - a.cohen_d)
                    .slice(0, 15);
                
                habilidadesMat.forEach(hab => {
                    const deltaClass = hab.media_delta >= 0 ? 'positive' : 'negative';
                    
                    habilidadesHTML += `
                        <div class="habilidade-card">
                            <div class="habilidade-titulo">${hab.habilidade}</div>
                            <div class="habilidade-stats">
                                <div>Evolução: <span class="habilidade-delta ${deltaClass}">${hab.media_delta >= 0 ? '+' : ''}${hab.media_delta}</span></div>
                                <div>Cohen's d: <span style="color: ${hab.cohen_d >= 0.4 ? '#059669' : hab.cohen_d >= 0.2 ? '#f59e0b' : '#dc2626'}; font-weight: 600;">${hab.cohen_d}</span></div>
                                <div>Status: ${hab.cohen_d >= 0.4 ? '✅ Efetivo' : hab.cohen_d >= 0.2 ? '⚠️ Moderado' : '🔍 Limitado'}</div>
                            </div>
                        </div>
                    `;
                });
            }
        }
        
        if (disciplina === 'ambas' || disciplina === 'portugues') {
            if (window.analiseHabilidades.portugues && window.analiseHabilidades.portugues.length > 0) {
                habilidadesHTML += '<h3 style="grid-column: 1/-1; margin: 20px 0 10px 0; color: #059669;">📝 Língua Portuguesa</h3>';
                
                const habilidadesPort = window.analiseHabilidades.portugues
                    .sort((a, b) => b.cohen_d - a.cohen_d)
                    .slice(0, 15);
                
                habilidadesPort.forEach(hab => {
                    const deltaClass = hab.media_delta >= 0 ? 'positive' : 'negative';
                    
                    habilidadesHTML += `
                        <div class="habilidade-card">
                            <div class="habilidade-titulo">${hab.habilidade}</div>
                            <div class="habilidade-stats">
                                <div>Evolução: <span class="habilidade-delta ${deltaClass}">${hab.media_delta >= 0 ? '+' : ''}${hab.media_delta}</span></div>
                                <div>Cohen's d: <span style="color: ${hab.cohen_d >= 0.4 ? '#059669' : hab.cohen_d >= 0.2 ? '#f59e0b' : '#dc2626'}; font-weight: 600;">${hab.cohen_d}</span></div>
                                <div>Status: ${hab.cohen_d >= 0.4 ? '✅ Efetivo' : hab.cohen_d >= 0.2 ? '⚠️ Moderado' : '🔍 Limitado'}</div>
                            </div>
                        </div>
                    `;
                });
            }
        }
    } else {
        habilidadesHTML = '<div class="error">Dados de habilidades não disponíveis</div>';
    }
    
    container.innerHTML = habilidadesHTML;
}

// Função para atualizar qualidade dos dados
function atualizarQualidadeDados(dadosFiltrados) {
    const container = document.getElementById('qualidadeDados');
    const totalMat = dadosFiltrados.matematica.length;
    const totalPort = dadosFiltrados.portugues.length;
    
    container.innerHTML = `
        <div class="grupo-item">
            <div class="grupo-titulo">📊 Amostra e Representatividade</div>
            <div class="grupo-detalhes">
                <span><strong>Matemática:</strong> ${totalMat} estudantes</span>
                <span><strong>Língua Portuguesa:</strong> ${totalPort} estudantes</span>
                <span><strong>Total:</strong> ${totalMat + totalPort} avaliações</span>
                <span><strong>Versão:</strong> Dados integrados (amostra)</span>
            </div>
        </div>
        <div class="interpretacao-grupo" style="background: #f0fdf4; border-left-color: #22c55e;">
            <p><strong>🎯 Status:</strong> 🟢 EXCELENTE - Dados integrados com alta qualidade</p>
            <p><strong>💬 Observações:</strong> Relatório autocontido para distribuição</p>
        </div>
    `;
}

// Função para atualizar recomendações
function atualizarRecomendacoes(dadosFiltrados) {
    const container = document.getElementById('recomendacoesContainer');
    const disciplina = document.getElementById('disciplinaSelect').value;
    
    let recomendacao = '';
    
    if (disciplina === 'matematica' || disciplina === 'ambas') {
        const estatsMat = calcularEstatisticas(dadosFiltrados.matematica);
        const effectSize = parseFloat(estatsMat.cohenD);
        
        if (effectSize >= 0.4) {
            recomendacao += '<div class="recomendacao-item">✅ <strong>Matemática:</strong> Programa demonstra efetividade significativa. Manter estratégias atuais.</div>';
        } else if (effectSize >= 0.2) {
            recomendacao += '<div class="recomendacao-item">⚠️ <strong>Matemática:</strong> Efeito moderado. Considerar ajustes metodológicos.</div>';
        } else {
            recomendacao += '<div class="recomendacao-item">🔍 <strong>Matemática:</strong> Efeito limitado. Revisão estratégica necessária.</div>';
        }
    }
    
    if (disciplina === 'portugues' || disciplina === 'ambas') {
        const estatsPort = calcularEstatisticas(dadosFiltrados.portugues);
        const effectSize = parseFloat(estatsPort.cohenD);
        
        if (effectSize >= 0.4) {
            recomendacao += '<div class="recomendacao-item">✅ <strong>Língua Portuguesa:</strong> Programa demonstra efetividade significativa. Manter estratégias atuais.</div>';
        } else if (effectSize >= 0.2) {
            recomendacao += '<div class="recomendacao-item">⚠️ <strong>Língua Portuguesa:</strong> Efeito moderado. Considerar ajustes metodológicos.</div>';
        } else {
            recomendacao += '<div class="recomendacao-item">🔍 <strong>Língua Portuguesa:</strong> Efeito limitado. Revisão estratégica necessária.</div>';
        }
    }
    
    container.innerHTML = `
        <div class="recomendacao-titulo">🎯 Recomendações Baseadas nos Dados</div>
        ${recomendacao}
        <div class="recomendacao-item">📊 <strong>Versão Integrada:</strong> Este relatório é autocontido e pode ser compartilhado diretamente com gestores.</div>
        <div class="recomendacao-item">🔄 <strong>Próximos Passos:</strong> Implementar acompanhamento longitudinal para próxima fase.</div>
    `;
}

function mostrarErro(mensagem) {
    const containers = ['cardsContainer', 'habilidadesContainer'];
    containers.forEach(id => {
        document.getElementById(id).innerHTML = `<div class="error">${mensagem}</div>`;
    });
}

// Inicializar quando a página carregar
window.onload = function() {
    formatarTimestamp();
    carregarDados();
};
</script>
</body>
</html>'''

if __name__ == "__main__":
    gerador = GeradorVisualizacoesFase5()
    gerador.executar_pipeline_completo()