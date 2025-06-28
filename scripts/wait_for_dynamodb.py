#!/usr/bin/env python3
"""
Script para aguardar o DynamoDB estar pronto e criar a tabela inicial
"""
import asyncio

import aioboto3

from app.config.database import DatabaseConfig


async def wait_for_dynamodb(max_retries: int = 15, retry_delay: int = 1) -> bool:
    endpoint_url = DatabaseConfig.get_dynamodb_endpoint()
    region = DatabaseConfig.get_aws_region()

    print(f"🔄 Aguardando DynamoDB estar pronto...")
    print(f"   Endpoint: {endpoint_url}")
    print(f"   Region: {region}")

    session = aioboto3.Session()

    for attempt in range(max_retries):
        try:
            async with session.client(
                "dynamodb",
                region_name=region,
                endpoint_url=endpoint_url,
                aws_access_key_id="dummy",
                aws_secret_access_key="dummy",
            ) as client:
                response = await client.list_tables()
                print(f"✅ DynamoDB está pronto! Tabelas existentes: {response.get('TableNames', [])}")
                return True

        except Exception as e:
            print(f"⏳ Tentativa {attempt + 1}/{max_retries} - DynamoDB não está pronto: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)

    print(f"❌ DynamoDB não ficou pronto após {max_retries} tentativas")
    return False


async def create_table_if_not_exists():
    endpoint_url = DatabaseConfig.get_dynamodb_endpoint()
    region = DatabaseConfig.get_aws_region()
    table_name = DatabaseConfig.get_dynamodb_table_name()

    print(f"🗄️  Verificando se a tabela '{table_name}' existe...")

    session = aioboto3.Session()

    try:
        async with session.client(
            "dynamodb",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        ) as client:
            try:
                await client.describe_table(TableName=table_name)
                print(f"✅ Tabela '{table_name}' já existe")
                return True

            except client.exceptions.ResourceNotFoundException:
                print(f"🔨 Criando tabela '{table_name}'...")

                await client.create_table(
                    TableName=table_name,
                    KeySchema=[{"AttributeName": "ticker", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "ticker", "AttributeType": "S"}],
                    BillingMode="PAY_PER_REQUEST",
                )

                print(f"⏳ Aguardando tabela '{table_name}' estar ativa...")
                waiter = client.get_waiter("table_exists")
                await waiter.wait(TableName=table_name)

                print(f"✅ Tabela '{table_name}' criada com sucesso!")
                return True

    except Exception as e:
        print(f"❌ Erro ao criar/verificar tabela: {str(e)}")
        return False


async def main():
    print("🚀 Inicializando preparação do DynamoDB...")

    if not await wait_for_dynamodb():
        print("❌ Falha ao conectar com DynamoDB")
        exit(1)

    if not await create_table_if_not_exists():
        print("❌ Falha ao criar/verificar tabela")
        exit(1)

    print("🎉 DynamoDB está pronto para uso!")


if __name__ == "__main__":
    asyncio.run(main())
