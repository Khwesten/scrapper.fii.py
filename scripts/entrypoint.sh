#!/bin/bash

set -e

echo "🚀 Iniciando script de entrada..."

if [ ! -z "$DYNAMODB_ENDPOINT" ]; then
    echo "🔄 DynamoDB local detectado: $DYNAMODB_ENDPOINT"
    echo "⏳ Aguardando DynamoDB estar pronto..."
    
    wait_for_dynamodb() {
        for i in $(seq 1 15); do
            if curl -f -s "$DYNAMODB_ENDPOINT" > /dev/null 2>&1; then
                echo "✅ DynamoDB está pronto!"
                return 0
            fi
            echo "   Tentativa $i/15 - Aguardando DynamoDB..."
            sleep 1
        done
        echo "⚠️  Continuando sem aguardar DynamoDB"
        return 1
    }
    
    if ! wait_for_dynamodb; then
        echo "⚠️  Continuando sem aguardar DynamoDB (pode estar funcionando mesmo assim)"
    fi
    
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

exec "$@"
