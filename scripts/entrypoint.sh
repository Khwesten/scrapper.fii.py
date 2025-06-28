#!/bin/bash
"""
Script de entrada para aguardar o DynamoDB antes de iniciar a aplicação
"""

set -e

echo "🚀 Iniciando script de entrada..."

# Se estivermos usando DynamoDB local, aguarda ele estar pronto
if [ ! -z "$DYNAMODB_ENDPOINT" ]; then
    echo "🔄 DynamoDB local detectado: $DYNAMODB_ENDPOINT"
    echo "⏳ Aguardando DynamoDB estar pronto..."
    
    # Função para testar se DynamoDB está pronto
    wait_for_dynamodb() {
        for i in {1..30}; do
            if curl -f -s "$DYNAMODB_ENDPOINT" > /dev/null 2>&1; then
                echo "✅ DynamoDB está pronto!"
                return 0
            fi
            echo "   Tentativa $i/30 - Aguardando DynamoDB..."
            sleep 2
        done
        echo "❌ DynamoDB não ficou pronto após 60 segundos"
        return 1
    }
    
    # Aguarda DynamoDB estar pronto
    if ! wait_for_dynamodb; then
        echo "❌ Falha ao conectar com DynamoDB"
        exit 1
    fi
    
    # Aguarda um pouco mais para garantir que está completamente pronto
    echo "⏳ Aguardando estabilização do DynamoDB..."
    sleep 5
    
    echo "🗄️  Preparando ambiente do banco de dados..."
    poetry run python -c "
import asyncio
import sys
import os
sys.path.append('/app')
from scripts.wait_for_dynamodb import main
asyncio.run(main())
" || echo "⚠️  Aviso: Erro na preparação do banco, mas continuando..."

fi

echo "🎉 Iniciando aplicação FastAPI..."

# Executa o comando passado como argumentos
exec "$@"
