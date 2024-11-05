import decimal
from typing import List, Optional

import aiohttp
from aiohttp import ClientSession
from lxml import etree

from app.domain.fii_domain import FiiDomain
from app.libs.data_crawler_converter import DataCrawlerConverter
from app.libs.logger import logger


class FiiGateway:
    session: ClientSession

    async def list(self) -> List[str]: ...

    async def get(self, ticker: str) -> Optional[FiiDomain]: ...


class StatusInvestGateway(FiiGateway):
    STATUS_INVEST_URL = "https://statusinvest.com.br/fundos-imobiliarios/"

    XPATH_P_VP = "/html/body/main/div[2]/div[5]/div/div[2]/div/div[1]/strong/text()"
    XPATH_SEGMENT = "/html/body/main/div[3]/div/div/div[2]/div/div[6]/div/div/strong/text()"
    XPATH_START_DATE = "/html/body/main/div[3]/div/div/div[2]/div/div[3]/div/div/strong/text()"
    XPATH_LAST_12_MONTH_EVALUATION = "/html/body/main/div[2]/div[1]/div[5]/div/div[1]/strong/text()"
    XPATH_CURRENT_MONTH_EVALUATION = "/html/body/main/div[2]/div[1]/div[5]/div/div[2]/div/span[2]/b/text()"
    XPATH_QUOTA_VALUE = "/html/body/main/div[2]/div[1]/div[1]/div/div[1]/strong/text()"
    XPATH_LAST_DIVIDEND = "/html/body/main/div[2]/div[7]/div[2]/div/div[1]/strong/text()"
    XPATH_DURATION = "/html/body/main/div[3]/div/div/div[2]/div/div[4]/div/div/div/strong/text()"
    XPATH_LAST_12_MONTH_DY = "/html/body/main/div[2]/div[1]/div[4]/div/div[1]/strong/text()"
    XPATH_DIALY_LIQUIDITY = "/html/body/main/div[2]/div[6]/div/div/div[3]/div/div/div/strong/text()"
    XPATH_QUOTA_HOLDER = "/html/body/main/div[2]/div[5]/div/div[6]/div/div[1]/strong/text()"
    XPATH_QUOTA_QUANTITY = "/html/body/main/div[2]/div[5]/div/div[6]/div/div[2]/span[2]/text()"
    XPATH_PATRIMONY = "/html/body/main/div[2]/div[5]/div/div[1]/div/div[2]/span[2]/text()"  # TODO

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()

    async def list(self) -> List[str]:
        fii_list = []
        url = "https://statusinvest.com.br/fii/fundsnavigation?size=99999"

        async with self.session.get(url) as response:
            response.raise_for_status()

            logger.info("GOT response [%s] for URL: %s", response.status, url)

            json = await response.json()

            for fii in json:
                fii_list.append(fii["url"].split("/")[-1])

            return fii_list

    async def get(self, ticker: str) -> Optional[FiiDomain]:
        found = None
        url = str.strip(f"{self.STATUS_INVEST_URL}{ticker}").lower()

        try:
            html = await self._fetch_html(url=url)
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ) as e:
            logger.error(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )
            return found
        except Exception as e:
            logger.exception("Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {}))
            return found
        else:
            parser = etree.HTMLParser()
            tree = etree.HTML(html, parser)

            try:
                start_date_element = tree.xpath(self.XPATH_START_DATE)[0]
                p_vp_element = tree.xpath(self.XPATH_P_VP)[0]
                last_12_month_evaluation_element = tree.xpath(self.XPATH_LAST_12_MONTH_EVALUATION)[0]
                current_month_evaluation_element = tree.xpath(self.XPATH_CURRENT_MONTH_EVALUATION)[0]
                quota_value_element = tree.xpath(self.XPATH_QUOTA_VALUE)[0]
                last_dividend_element = tree.xpath(self.XPATH_LAST_DIVIDEND)[0]
                dy_12_element = tree.xpath(self.XPATH_LAST_12_MONTH_DY)[0]
                dialy_liquidity_element = tree.xpath(self.XPATH_DIALY_LIQUIDITY)[0].lower()

                segment = tree.xpath(self.XPATH_SEGMENT)[0].lower()
                duration = tree.xpath(self.XPATH_DURATION)[0].lower()
                tree.xpath(self.XPATH_QUOTA_HOLDER)[0].lower()
                tree.xpath(self.XPATH_QUOTA_QUANTITY)[0].lower()

                start_date = DataCrawlerConverter.to_date_or_none(start_date_element)
                p_vp = DataCrawlerConverter.to_decimal(p_vp_element)
                current_month_evaluation = DataCrawlerConverter.to_decimal(current_month_evaluation_element)
                last_12_month_evaluation = DataCrawlerConverter.to_decimal(last_12_month_evaluation_element)
                quota_value = DataCrawlerConverter.to_decimal(quota_value_element)
                last_dividend = DataCrawlerConverter.to_decimal(last_dividend_element)
                dy_12 = DataCrawlerConverter.to_decimal(dy_12_element)
                dialy_liquidity = DataCrawlerConverter.to_decimal_or_none(dialy_liquidity_element)

                logger.info(f"{ticker.upper()} CONVERTED")

                return FiiDomain(
                    ticker=ticker,
                    p_vp=p_vp,
                    last_dividend=last_dividend,
                    segment=segment,
                    last_12_month_evaluation=last_12_month_evaluation,
                    current_month_evaluation=current_month_evaluation,
                    last_price=quota_value,
                    start_date=start_date,
                    dy_12=dy_12,
                    duration=duration,
                    dialy_liquidity=dialy_liquidity,
                )
            except decimal.InvalidOperation as _:
                logger.info(f"DIDNT CONVERTED - {ticker.upper()}: Decimal values couldn't convert")
                return None
            except Exception as e:
                logger.error(f"DIDNT CONVERTED - {ticker.upper()}: {str(e)}")
                return None

    async def close(self):
        await self.session.close()

    async def _fetch_html(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()

            return await response.text()
