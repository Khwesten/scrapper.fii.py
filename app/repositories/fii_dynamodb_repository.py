from datetime import date
from decimal import Decimal
from typing import List, Optional
import boto3
from aioboto3 import Session
from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository import FiiRepository
from app.libs.logger import logger
from app.config.database import DatabaseConfig


class FiiDynamoDBRepository(FiiRepository):
    def __init__(self, table_name: str = None):
        self.table_name = table_name or DatabaseConfig.get_dynamodb_table_name()
        self.region_name = DatabaseConfig.get_aws_region()
        self.endpoint_url = DatabaseConfig.get_dynamodb_endpoint()
        self._session = Session()
    
    async def _get_table(self):
        async with self._session.resource(
            'dynamodb',
            region_name=self.region_name,
            endpoint_url=self.endpoint_url
        ) as dynamodb:
            return await dynamodb.Table(self.table_name)
    
    async def _ensure_table_exists(self):
        try:
            async with self._session.client(
                'dynamodb',
                region_name=self.region_name,
                endpoint_url=self.endpoint_url
            ) as client:
                try:
                    await client.describe_table(TableName=self.table_name)
                    logger.info(f"Table {self.table_name} already exists")
                except client.exceptions.ResourceNotFoundException:
                    logger.info(f"Creating table {self.table_name}")
                    await client.create_table(
                        TableName=self.table_name,
                        KeySchema=[
                            {
                                'AttributeName': 'ticker',
                                'KeyType': 'HASH'
                            }
                        ],
                        AttributeDefinitions=[
                            {
                                'AttributeName': 'ticker',
                                'AttributeType': 'S'
                            }
                        ],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    waiter = client.get_waiter('table_exists')
                    await waiter.wait(TableName=self.table_name)
                    logger.info(f"Table {self.table_name} created successfully")
        except Exception as e:
            logger.error(f"Error ensuring table exists: {e}")
            raise

    def _fii_to_dynamodb_item(self, fii: FiiDomain) -> dict:
        item = {
            'ticker': fii.ticker,
            'p_vp': str(fii.p_vp),
            'segment': fii.segment,
            'duration': fii.duration,
            'last_12_month_evaluation': str(fii.last_12_month_evaluation),
            'current_month_evaluation': str(fii.current_month_evaluation),
            'last_price': str(fii.last_price),
            'last_dividend': str(fii.last_dividend),
            'dy_12': str(fii.dy_12),
            'dialy_liquidity': str(fii.dialy_liquidity) if fii.dialy_liquidity else "0"
        }
        
        if fii.start_date:
            item['start_date'] = fii.start_date.isoformat()
        
        return item

    def _dynamodb_item_to_fii(self, item: dict) -> FiiDomain:
        return FiiDomain(
            ticker=item['ticker'],
            p_vp=Decimal(item['p_vp']),
            segment=item['segment'],
            duration=item['duration'],
            last_12_month_evaluation=Decimal(item['last_12_month_evaluation']),
            current_month_evaluation=Decimal(item['current_month_evaluation']),
            last_price=Decimal(item['last_price']),
            last_dividend=Decimal(item['last_dividend']),
            dy_12=Decimal(item['dy_12']),
            start_date=date.fromisoformat(item['start_date']) if item.get('start_date') else None,
            dialy_liquidity=Decimal(item.get('dialy_liquidity', '0'))
        )

    async def add(self, fii: FiiDomain) -> int:
        await self._ensure_table_exists()
        
        try:
            table = await self._get_table()
            item = self._fii_to_dynamodb_item(fii)
            
            await table.put_item(Item=item)
            logger.info(f"FII {fii.ticker} added successfully to DynamoDB")
            return 1
        except Exception as e:
            logger.error(f"Error adding FII {fii.ticker} to DynamoDB: {e}")
            raise

    async def get(self, ticker: str) -> Optional[FiiDomain]:
        await self._ensure_table_exists()
        
        try:
            table = await self._get_table()
            response = await table.get_item(Key={'ticker': ticker})
            
            if 'Item' in response:
                fii = self._dynamodb_item_to_fii(response['Item'])
                logger.info(f"FII {ticker} retrieved from DynamoDB")
                return fii
            else:
                logger.info(f"FII {ticker} not found in DynamoDB")
                return None
        except Exception as e:
            logger.error(f"Error getting FII {ticker} from DynamoDB: {e}")
            raise

    async def list(self) -> List[FiiDomain]:
        await self._ensure_table_exists()
        
        try:
            table = await self._get_table()
            response = await table.scan()
            
            fiis = []
            for item in response.get('Items', []):
                fii = self._dynamodb_item_to_fii(item)
                fiis.append(fii)
            
            logger.info(f"Retrieved {len(fiis)} FIIs from DynamoDB")
            return fiis
        except Exception as e:
            logger.error(f"Error listing FIIs from DynamoDB: {e}")
            raise
