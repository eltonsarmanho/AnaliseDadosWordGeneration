# Implementação de Anonimização - Conformidade LGPD

## 📋 Resumo
Implementação de sistema de anonimização de dados pessoais dos estudantes no Dashboard WordGen para conformidade com a Lei Geral de Proteção de Dados (LGPD) brasileira.

## 🎯 Objetivo
Proteger a privacidade dos estudantes enquanto mantém a capacidade de rastreamento individual necessária para análises longitudinais.

## 🔐 Método de Anonimização

### Formato do Identificador Anonimizado
```
[PRIMEIRAS_6_LETRAS_ID] - [INICIAIS_NOME]
```

### Exemplos Práticos
- **ID Original**: `56E9C824252F`
- **Nome**: `ABIGAIL ALVES DOS SANTOS`
- **ID Anonimizado**: `56E9C8 - AAS`

---

- **ID Original**: `7F3D12AB98CD`
- **Nome**: `JOÃO PEDRO SILVA`
- **ID Anonimizado**: `7F3D12 - JPS`

---

- **ID Original**: `A1B2C3D4E5F6`
- **Nome**: `MARIA FERNANDA OLIVEIRA COSTA`
- **ID Anonimizado**: `A1B2C3 - MFOC`

## 🛠️ Implementação Técnica

### 1. Função de Anonimização (`data_loader.py`)
```python
def anonimizar_estudante(id_unico: str, nome_completo: str) -> str:
    """
    Cria identificador anonimizado para estudante seguindo LGPD.
    
    Args:
        id_unico: ID único do estudante
        nome_completo: Nome completo do estudante
        
    Returns:
        String anonimizada no formato [ID_PARCIAL] - [INICIAIS]
    """
```

**Regras de Processamento**:
- Extrai os 6 primeiros caracteres do `ID_Unico`
- Normaliza o nome (remove acentos, converte para maiúsculas)
- Extrai primeira letra de cada palavra do nome (máximo 4 iniciais)
- Combina no formato especificado

### 2. Integração no Dashboard (`app.py`)
- Substituição da seleção por "Nome Completo" por "ID Anonimizado"
- Filtros e visualizações adaptados para usar o identificador anonimizado
- Manutenção da funcionalidade de rastreamento longitudinal

### 3. Processamento de Dados
A coluna `ID_Anonimizado` é criada automaticamente durante o carregamento dos datasets:
```python
df['ID_Anonimizado'] = df.apply(
    lambda row: anonimizar_estudante(row['ID_Unico'], row['Nome']), 
    axis=1
)
```

## ✅ Vantagens da Abordagem

1. **Conformidade LGPD**
   - Não expõe nomes completos dos estudantes
   - Mantém pseudonimização adequada
   - Permite rastreamento individual sem identificação direta

2. **Usabilidade**
   - Formato compacto e legível
   - Iniciais permitem reconhecimento rápido por professores/coordenadores
   - Ordenação alfabética mantida

3. **Rastreabilidade**
   - ID parcial garante unicidade
   - Análises longitudinais preservadas
   - Possibilidade de reverter anonimização com acesso ao banco original (apenas para equipe autorizada)

4. **Performance**
   - Processamento rápido
   - Não adiciona overhead significativo
   - Cache de dados mantido

## 🔒 Boas Práticas de Segurança

### Dados Armazenados
- CSV original contém: `ID_Unico`, `Nome`, outras colunas
- Dashboard exibe apenas: `ID_Anonimizado`
- Relação ID↔Nome mantida apenas em backend seguro

### Controle de Acesso
- **Nível 1**: Acesso público ao dashboard → vê apenas IDs anonimizados
- **Nível 2**: Equipe de pesquisa → acesso aos CSVs originais com nomes
- **Nível 3**: Administradores → acesso completo ao banco de dados

### Recomendações Adicionais
1. Implementar autenticação para acesso ao dashboard
2. Logs de acesso aos dados anonimizados
3. Política de retenção de dados definida
4. Termo de consentimento dos responsáveis pelos estudantes
5. Procedimento de anonimização irreversível para dados públicos/publicações

## 📊 Interface do Dashboard

### Sidebar - Filtro de Aluno
```
🔒 Aluno (ID Anonimizado)
┌────────────────────────────────┐
│ <selecione>                  ▼ │
├────────────────────────────────┤
│ 56E9C8 - AAS                   │
│ 7F3D12 - JPS                   │
│ A1B2C3 - MFOC                  │
└────────────────────────────────┘
```

**Tooltip**: "Formato: [Primeiras letras do ID] - [Iniciais do Nome]"

### Visualizações
Todos os gráficos e tabelas individuais agora usam `ID_Anonimizado` no título e labels:
- "Evolução Pré vs Pós - 56E9C8 - AAS"
- "Evolução Delta - 56E9C8 - AAS"

## 🔄 Processo de Migração

### Passo 1: Backup
```bash
cp vocabulario_longitudinal.csv vocabulario_longitudinal.backup.csv
cp TDE_longitudinal.csv TDE_longitudinal.backup.csv
```

### Passo 2: Atualização de Código
- ✅ `data_loader.py`: Função `anonimizar_estudante()` adicionada
- ✅ `data_loader.py`: Coluna `ID_Anonimizado` criada em `get_datasets()`
- ✅ `app.py`: Selectbox substituído de `Nome` para `ID_Anonimizado`
- ✅ `app.py`: Filtros e títulos atualizados

### Passo 3: Testes
```bash
streamlit run Dashboard/app.py
```

Verificar:
- [ ] IDs anonimizados aparecem no dropdown
- [ ] Filtro funciona corretamente
- [ ] Gráficos individuais exibem ID anonimizado
- [ ] Rastreamento longitudinal mantido
- [ ] Nenhum nome completo exposto na interface

## 📝 Considerações Legais (LGPD)

### Artigos Relevantes
- **Art. 6º**: Princípios - Necessidade, adequação, transparência
- **Art. 12**: Anonimização - Dado anonimizado não é considerado pessoal
- **Art. 13**: Estudos - Pseudonimização permitida para pesquisa

### Classificação dos Dados
- **Nome Completo**: Dado Pessoal Sensível (criança/adolescente)
- **ID_Unico**: Pseudônimo (não identifica diretamente)
- **ID_Anonimizado**: Dado Anonimizado (não permite reidentificação sem informação adicional)

### Fundamentação Legal
Esta implementação se baseia na técnica de **pseudonimização** (Art. 13, §4º), adequada para fins de estudos e pesquisas, mantendo a possibilidade de rastreamento para fins legítimos da pesquisa educacional.

## 🎓 Próximos Passos

1. **Curto Prazo**
   - [ ] Implementar autenticação no dashboard
   - [ ] Adicionar logs de acesso
   - [ ] Criar termo de consentimento/autorização

2. **Médio Prazo**
   - [ ] Sistema de permissões granulares
   - [ ] Export de dados anonimizados para publicações
   - [ ] Documentação de privacidade para usuários

3. **Longo Prazo**
   - [ ] Auditoria de conformidade LGPD
   - [ ] Política de retenção e descarte de dados
   - [ ] Treinamento de equipe sobre LGPD

## 📞 Contato
Para dúvidas sobre privacidade e tratamento de dados, consulte o responsável pela pesquisa ou o encarregado de dados (DPO) da instituição.

---

**Data de Implementação**: Outubro 2025  
**Versão**: 1.0  
**Autor**: Sistema automatizado de anonimização WordGen
