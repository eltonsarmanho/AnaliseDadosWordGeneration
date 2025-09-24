#!/bin/bash

echo "🚀 Testando configuração Docker..."
echo ""

echo "1. Verificando se Dockerfile existe:"
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile encontrado"
else
    echo "❌ Dockerfile não encontrado"
    exit 1
fi

echo ""
echo "2. Verificando se requirements.txt existe:"
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt encontrado"
else
    echo "❌ requirements.txt não encontrado"
    exit 1
fi

echo ""
echo "3. Verificando se Dashboard/app.py existe:"
if [ -f "Dashboard/app.py" ]; then
    echo "✅ Dashboard/app.py encontrado"
else
    echo "❌ Dashboard/app.py não encontrado"
    exit 1
fi

echo ""
echo "4. Verificando estrutura da aplicação:"
echo "📁 Estrutura do Dashboard:"
ls -la Dashboard/

echo ""
echo "5. Testando build do Docker (apenas sintaxe):"
docker build --dry-run . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Sintaxe do Dockerfile OK"
else
    echo "⚠️  Verificar sintaxe do Dockerfile"
fi

echo ""
echo "🎯 Resumo das correções aplicadas:"
echo "   - Corrigido: requirements.txt (nome do arquivo correto)"
echo "   - Corrigido: CMD aponta para Dashboard/app.py (era main.py)"
echo "   - Estrutura: Aplicação em Dashboard/ com dados consolidados"
echo ""
echo "🚀 Para fazer o deploy completo:"
echo "   docker build -t wordgen-dashboard ."
echo "   docker run -p 8501:8501 wordgen-dashboard"