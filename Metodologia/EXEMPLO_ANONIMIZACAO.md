# Exemplo de Uso - Sistema de Anonimização

## 🧪 Teste da Função de Anonimização

Este arquivo demonstra como a função de anonimização funciona com diferentes casos.

```python
from Dashboard.data_loader import anonimizar_estudante

# Casos de Teste
casos_teste = [
    {
        'id': '56E9C824252F',
        'nome': 'ABIGAIL ALVES DOS SANTOS',
        'esperado': '56E9C8 - AADS'
    },
    {
        'id': '7F3D12AB98CD',
        'nome': 'João Pedro Silva',
        'esperado': '7F3D12 - JPS'
    },
    {
        'id': 'A1B2C3D4E5F6',
        'nome': 'Maria Fernanda Oliveira Costa',
        'esperado': 'A1B2C3 - MFOC'
    },
    {
        'id': 'B9F8E7D6C5A4',
        'nome': 'Ana',
        'esperado': 'B9F8E7 - A'
    },
    {
        'id': 'C8D7E6F5A4B3',
        'nome': 'Carlos Eduardo de Souza Santos Lima',
        'esperado': 'C8D7E6 - CESS'  # Máximo 4 iniciais
    }
]

# Executar testes
print("=" * 60)
print("TESTES DO SISTEMA DE ANONIMIZAÇÃO")
print("=" * 60)

for caso in casos_teste:
    resultado = anonimizar_estudante(caso['id'], caso['nome'])
    status = "✅ PASSOU" if resultado == caso['esperado'] else "❌ FALHOU"
    
    print(f"\n{status}")
    print(f"  ID Original:     {caso['id']}")
    print(f"  Nome:            {caso['nome']}")
    print(f"  Esperado:        {caso['esperado']}")
    print(f"  Resultado:       {resultado}")
    print("-" * 60)
```

## 📊 Exemplo de Saída no Dashboard

### Antes da Anonimização
```
Sidebar:
┌─────────────────────────────────────────┐
│ Aluno (Nome Completo)               ▼   │
├─────────────────────────────────────────┤
│ <selecione>                             │
│ ABIGAIL ALVES DOS SANTOS                │
│ ANA CAROLINA FERREIRA                   │
│ CARLOS EDUARDO DE SOUZA SANTOS LIMA     │
│ JOÃO PEDRO SILVA                        │
│ MARIA FERNANDA OLIVEIRA COSTA           │
└─────────────────────────────────────────┘

Título do Gráfico:
"Evolução Pré vs Pós - ABIGAIL ALVES DOS SANTOS"
```

### Depois da Anonimização ✅
```
Sidebar:
┌─────────────────────────────────────────┐
│ 🔒 Aluno (ID Anonimizado)           ▼   │
├─────────────────────────────────────────┤
│ <selecione>                             │
│ 56E9C8 - AADS                           │
│ 7A3B2C - ACF                            │
│ C8D7E6 - CESS                           │
│ 7F3D12 - JPS                            │
│ A1B2C3 - MFOC                           │
└─────────────────────────────────────────┘

Tooltip: "Formato: [Primeiras letras do ID] - [Iniciais do Nome]"

Título do Gráfico:
"Evolução Pré vs Pós - 56E9C8 - AADS"
```

## 🔍 Vantagens Demonstradas

1. **Compacto**: De "ABIGAIL ALVES DOS SANTOS" para "56E9C8 - AADS"
2. **Reconhecível**: Iniciais permitem identificação rápida por professores
3. **Único**: Combinação ID + Iniciais é praticamente única
4. **LGPD**: Não expõe nome completo diretamente

## 💡 Casos Especiais

### Nome Curto
- **Input**: `Ana`
- **Output**: `B9F8E7 - A`

### Nome Muito Longo (> 4 palavras)
- **Input**: `Carlos Eduardo de Souza Santos Lima`
- **Output**: `C8D7E6 - CESS` (primeiras 4 iniciais)

### Nome com Acentos
- **Input**: `José María Ñoño`
- **Output**: `D5E4F3 - JMN` (acentos removidos automaticamente)

### Nome com Preposições
- **Input**: `Maria da Silva`
- **Output**: `E6F5G4 - MDS` (preposições incluídas)

## 🎯 Recomendações de Uso

### Para Professores/Coordenadores
1. Use as **iniciais** para identificar rapidamente o aluno
2. Se necessário, consulte lista de correspondência (acesso restrito)
3. Ao compartilhar capturas de tela, os IDs anonimizados já estão protegidos

### Para Pesquisadores
1. Use o **ID_Unico** original apenas em análises internas
2. Em publicações/relatórios, use sempre o **ID_Anonimizado**
3. Mantenha tabela de correspondência em ambiente seguro

### Para Administradores do Sistema
1. Garanta que CSVs originais estejam protegidos
2. Configure controle de acesso adequado
3. Implemente logs de auditoria

## 📈 Verificação de Unicidade

Para garantir que não haja colisões (dois alunos com mesmo ID anonimizado):

```python
# Verificar unicidade
df['ID_Anonimizado'].nunique() == df['ID_Unico'].nunique()
# Deve retornar True

# Verificar colisões
duplicados = df.groupby('ID_Anonimizado')['ID_Unico'].nunique()
colisoes = duplicados[duplicados > 1]
if len(colisoes) == 0:
    print("✅ Nenhuma colisão detectada!")
else:
    print(f"⚠️ {len(colisoes)} colisões detectadas")
```

## 🔐 Checklist de Conformidade LGPD

- [x] Nomes completos não expostos no dashboard
- [x] Identificador permite rastreamento longitudinal
- [x] Possibilidade de reidentificação controlada (apenas para autorizados)
- [x] Documentação do processo de anonimização
- [ ] Termo de consentimento dos responsáveis (próximo passo)
- [ ] Política de privacidade publicada (próximo passo)
- [ ] Logs de acesso implementados (próximo passo)
- [ ] Auditoria de conformidade (próximo passo)

---

**Última Atualização**: Outubro 2025
