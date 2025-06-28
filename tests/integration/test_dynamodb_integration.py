#!/usr/bin/env python3
"""
Teste local para verificar a integração com DynamoDB
"""
import asyncio
import os
import sys

# Adiciona o path do app
sys.path.append("/home/khwesten/projects/personal/scrapper.fii.py")

from app.config.database import DatabaseConfig
from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository_factory import FiiRepositoryFactory


async def test_dynamodb_integration():
    """
    Testa a integração com DynamoDB
    """
    print("🧪 Testando integração com DynamoDB...")

    # Configura variáveis de ambiente para DynamoDB local
    os.environ["DYNAMODB_ENDPOINT"] = "http://localhost:8002"
    os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["DYNAMODB_TABLE_NAME"] = "fiis"

    # Força a recarregar a configuração
    import importlib

    from app.config import database

    importlib.reload(database)

    # Exibe configuração
    DatabaseConfig.print_config()

    try:
        # Testa repositório
        print("\n📊 Testando repositório...")
        repository = FiiRepositoryFactory.create()

        # Tenta listar FIIs (isso criará a tabela se não existir)
        print("📋 Listando FIIs...")
        fiis = await repository.list()
        print(f"✅ Encontrados {len(fiis)} FIIs no banco")

        # Se não há FIIs, adiciona alguns de teste
        if len(fiis) == 0:
            print("🔧 Adicionando FIIs de teste...")

            test_fiis = [
                FiiDomain(
                    ticker="TEST11",
                    p_vp=0.95,
                    segment="Teste",
                    duration="Indeterminada",
                    last_12_month_evaluation=15.2,
                    current_month_evaluation=1.8,
                    last_price=98.50,
                    last_dividend=0.68,
                    dy_12=8.5,
                ),
                FiiDomain(
                    ticker="DEMO11",
                    p_vp=0.89,
                    segment="Demonstração",
                    duration="Indeterminada",
                    last_12_month_evaluation=18.5,
                    current_month_evaluation=2.1,
                    last_price=128.30,
                    last_dividend=0.98,
                    dy_12=9.2,
                ),
            ]

            for fii in test_fiis:
                await repository.save(fii)
                print(f"   ✅ Adicionado: {fii.ticker}")

            # Lista novamente
            fiis = await repository.list()
            print(f"✅ Total de FIIs após inserção: {len(fiis)}")

        print("🎉 Teste de integração concluído com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro na integração: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_dynamodb_integration())
    sys.exit(0 if success else 1)
