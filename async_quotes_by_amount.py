import logging
import sys

from aiohttp import ClientSession
import aiofiles
import aiohttp
import asyncio
import re
import os
from typing import IO
from lxml import etree
from decimal import *
from dataclasses import dataclass
from app_config import CSV_DIR

logger = logging.getLogger("async_fii_req")
logging.getLogger("chardet.charsetprober").disabled = True

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

HREF_RE = re.compile(r'href="(.*?)"')


@dataclass
class FiiResponseDomain:
    fii_code: str
    quota_value: Decimal
    last_dividend: Decimal


@dataclass
class FiiDomain:
    fii_code: str
    quota_value: Decimal
    last_dividend: Decimal
    magic_number: int
    quotas_for_invested_value: int
    dividend_for_invested_value: Decimal
    invested_value: int

    @classmethod
    def from_fii_response(cls, fii_response: FiiResponseDomain, invested_value: int = None):
        invested_value = invested_value or 10000
        quotas_for_invested_value = int(invested_value / fii_response.quota_value)
        magic_number = int(fii_response.quota_value / fii_response.last_dividend)
        dividend_for_invested_value = Decimal(quotas_for_invested_value * fii_response.last_dividend)
        return FiiDomain(
            fii_response.fii_code,
            fii_response.quota_value,
            fii_response.last_dividend,
            magic_number,
            quotas_for_invested_value,
            dividend_for_invested_value,
            invested_value,
        )


class StatusInvestAdapter:
    STATUS_INVEST_URL = "https://statusinvest.com.br/fundos-imobiliarios/"
    XPATH_QUOTA_VALUE = "/html/body/main/div[2]/div[1]/div[1]/div/div[1]/strong/text()"
    XPATH_LAST_DIVIDEND = "/html/body/main/div[2]/div[7]/div[2]/div/div[1]/strong/text()"

    def __init__(self, session: ClientSession = None):
        self.session = session or ClientSession()

    async def get(self, fii_code: str) -> FiiResponseDomain:
        found = set()
        url = str.strip(f"{self.STATUS_INVEST_URL}{fii_code}").lower()
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

            dividend_element = tree.xpath(self.XPATH_LAST_DIVIDEND)[0]
            quota_element = tree.xpath(self.XPATH_QUOTA_VALUE)[0]

            try:
                dividend = Decimal(dividend_element.replace(",", "."))
                quota = Decimal(quota_element.replace(",", "."))

                if dividend == 0 or quota == 0:
                    return None

                return FiiResponseDomain(fii_code=fii_code, quota_value=quota, last_dividend=dividend)
            except:
                return None

    async def _fetch_html(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()

            logger.info("GOT response [%s] for URL: %s", response.status, url)

            return await response.text()


class CSVAdapter:
    def __init__(self, file: IO):
        self.file = file

    async def save(self, fii_domain: FiiDomain):
        async with aiofiles.open(self.file, "a") as f:
            await f.write(
                f"{fii_domain.fii_code.upper()},"
                f"{fii_domain.quota_value:0.2f},"
                f"{fii_domain.last_dividend:0.2f},"
                f"{fii_domain.dividend_for_invested_value:0.2f},"
                f"{fii_domain.magic_number},"
                f"{fii_domain.invested_value},"
                f"{fii_domain.quotas_for_invested_value}\n"
            )


class CalculateUseCase:
    session: ClientSession

    def __init__(self, fii_codes: set):
        self.fii_codes = fii_codes

    async def calculate(self):
        self.session = ClientSession()

        outpath = here.joinpath("fii_division.csv")

        with open(outpath, "w") as outfile:
            outfile.write(
                "fii_code,quota_value,dividend,dividend_for_invested_value,magic_number,invested_value,quotas_for_invested_value\n"
            )

        async with self.session as session:
            tasks = []

            for fii_code in self.fii_codes:
                tasks.append(self._get_and_save(outpath, fii_code=fii_code))

            await asyncio.gather(*tasks)

    async def _get_and_save(self, file: IO, fii_code: str) -> None:
        fii_crawler_adapter = StatusInvestAdapter(session=self.session)
        fii_response_domain = await fii_crawler_adapter.get(fii_code=fii_code)

        if not fii_response_domain:
            return None

        fii_domain = FiiDomain.from_fii_response(fii_response_domain)

        if not fii_domain:
            return None

        await CSVAdapter(file).save(fii_domain)


class StatusInvest:
    @staticmethod
    async def fii_list() -> list:
        fii_list = []
        url = "https://statusinvest.com.br/fii/fundsnavigation?size=99999"
        response = await ClientSession().request(method="GET", url=url)
        response.raise_for_status()

        logger.info("GOT response [%s] for URL: %s", response.status, url)

        json = await response.json()

        for fii in json:
            fii_list.append(fii["url"].split("/")[-1])

        return fii_list


# if __name__ == "__main__":
#     assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
#     here = pathlib.Path(__file__).parent

#     loop = asyncio.get_event_loop()
#     fiis_code = loop.run_until_complete(StatusInvest.fii_list())
#     loop.close()

#     # with open(here.joinpath("fiis.txt")) as file_content:
#     fii_codes = set([str.strip(line.lower()) for line in fiis_code])
#     urls = set([str.strip(f"{StatusInvestAdapter.STATUS_INVEST_URL}{line.lower()}") for line in fiis_code])

#     start = time.perf_counter()

#     asyncio.run(CalculateUseCase(fii_codes).calculate())

#     elapsed = time.perf_counter() - start
#     print(f"{__file__} executed in {elapsed:0.2f} seconds")


# core:
# - receber lista de fiis(Adapter)
# - Fazer alguns cálculos
# - Recuperar valores dos fiis (Adapter)
# - Salvar valores dos FIIs (Adapter)


import asyncio
import aiohttp
from asyncio import Queue, Semaphore


class Fetch:
    def __init__(self, semaphore: Semaphore):
        self.semaphore = semaphore

    async def fetch(self, fii_code: str):
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                # async with session.get(url) as response:
                #     return await response.text()
                fii_crawler_adapter = StatusInvestAdapter(session=session)
                fii_response_domain = await fii_crawler_adapter.get(fii_code=fii_code)

                if not fii_response_domain:
                    return None

                fii_domain = FiiDomain.from_fii_response(fii_response_domain)

                if not fii_domain:
                    return None

                outpath = CSV_DIR.joinpath("fii_division.csv")

                await CSVAdapter(outpath).save(fii_domain)


class Worker:
    def __init__(self, queue: Queue, semaphore: Semaphore, fetch_service: Fetch):
        self.queue = queue
        self.semaphore = semaphore
        self.fetch_service = fetch_service

    async def execute(self):
        while True:
            url = await self.queue.get()
            try:
                await self.fetch_service.fetch(url)
                # processar o conteúdo aqui
            except Exception as e:
                print(f"Erro ao fazer request para {url}: {e}")
            finally:
                self.queue.task_done()


class AsyncRequestService:
    def __init__(self, urls: list[str], max_concurrent_requests: int):
        self.urls = urls
        self.max_concurrent_requests = max_concurrent_requests

    async def execute(self):
        queue = Queue()
        semaphore = Semaphore(self.max_concurrent_requests)

        # Adicionando URLs na fila
        for url in self.urls:
            queue.put_nowait(url)

        outpath = CSV_DIR.joinpath("fii_division.csv")

        with open(outpath, "w") as outfile:
            outfile.write(
                "fii_code,quota_value,dividend,dividend_for_invested_value,magic_number,invested_value,quotas_for_invested_value\n"
            )

        # Criando workers
        workers = []
        fetch_service = Fetch(semaphore)
        for i in range(self.max_concurrent_requests):
            worker = Worker(queue, semaphore, fetch_service)
            worker_task = asyncio.create_task(worker.execute())
            workers.append(worker_task)

        # Esperando todas as tarefas terminarem
        await queue.join()
        for worker_task in workers:
            worker_task.cancel()

        await asyncio.gather(*workers, return_exceptions=True)


loop = asyncio.get_event_loop()
fiis_code = loop.run_until_complete(StatusInvest.fii_list())
loop.close()

# with open(here.joinpath("fiis.txt")) as file_content:
fii_codes = set([str.strip(line.lower()) for line in fiis_code])
# urls = set([str.strip(f"{StatusInvestAdapter.STATUS_INVEST_URL}{line.lower()}") for line in fiis_code])

fii_codes = [
    "BCRI11",
    "BPFF11",
    "CPTS11",
    "HFOF11",
    "HGRU11",
    "KISU11",
    "MFII11",
    "MXRF11",
    "RBFF11",
    "RECR11",
    "VISC11",
    "VINO11",
    "VILG11",
]


if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)

max_concurrent_requests = 4
async_request_service = AsyncRequestService(fii_codes, max_concurrent_requests)
asyncio.run(async_request_service.execute())
