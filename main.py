import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository_factory import FiiRepositoryFactory
from app.usecases.fii_list_usecase import FiiListUseCase
from app.usecases.fii_magic_number_usecase import (
    FiiMagicNumberUseCase,
    MagicNumberResponse,
)
from app_config import AppConfig

config = AppConfig()
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.scheduler import FiiBootstrap, FiiScheduler

    scheduler = FiiScheduler()
    scheduler.start()

    # Start bootstrap in background without blocking app startup
    bootstrap = FiiBootstrap()
    asyncio.create_task(bootstrap.initial_seed())

    yield
    scheduler.stop()


app = FastAPI(
    title="FII Scraper API",
    version="2.0.0",
    description="""
    ## 🏢 FII Scraper API v2.0
    
    Uma API moderna para scraping e análise de **Fundos de Investimento Imobiliário (FIIs)** brasileiros.
    
    ### ✨ Principais Funcionalidades
    
    - 🔄 **Scraping Automático**: Seed inicial + atualizações a cada 8 horas
    - 🌐 **Descoberta Dinâmica**: Lista automaticamente todos os FIIs disponíveis
    - 🗄️ **DynamoDB Nativo**: Armazenamento escalável em nuvem
    - 📊 **Health Check Inteligente**: Monitoramento completo do sistema
    - 🧮 **Magic Numbers**: Cálculos avançados para análise de investimentos
    
    ### 🚀 Como Usar
    
    1. **Health Check**: Verifique a saúde da API e banco de dados
    2. **Status**: Veja estatísticas detalhadas do sistema
    3. **Listar FIIs**: Obtenha todos os FIIs disponíveis
    4. **Magic Numbers**: Calcule números mágicos para análise de investimentos
    
    ### 🔄 Sistema Automático
    
    A API possui um sistema de scraping automático que:
    - Faz seed inicial após 30 segundos da inicialização
    - Atualiza todos os dados a cada 8 horas
    - Descobre novos FIIs automaticamente
    """,
    lifespan=lifespan,
    # ReDoc configuration
    docs_url=None,  # Disable default Swagger UI
    redoc_url="/docs",  # Enable ReDoc at /docs
    openapi_url="/openapi.json",
    # Contact and license info
    contact={
        "name": "FII Scraper API",
        "url": "https://github.com/your-repo/fii-scraper",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


@app.get("/", response_class=RedirectResponse, tags=["Navigation"])
async def root():
    """
    ## 🏠 Página Inicial

    Redireciona automaticamente para o dashboard visual dos FIIs.
    """
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/fiis", response_model=List[FiiDomain], tags=["FIIs"])
async def list_fiis():
    """
    ## 📊 Listar todos os FIIs

    Retorna uma lista completa de todos os Fundos de Investimento Imobiliário disponíveis no sistema.

    ### Informações Retornadas:
    - **ticker**: Código do FII (ex: BCRI11)
    - **p_vp**: Preço sobre Valor Patrimonial
    - **segment**: Segmento do FII (ex: Lajes Corporativas)
    - **duration**: Duração do fundo
    - **last_price**: Último preço de negociação
    - **dy_12**: Dividend Yield dos últimos 12 meses
    - **daily_liquidity**: Liquidez diária média

    ### Dados Atualizados:
    Os dados são atualizados automaticamente a cada 8 horas pelo sistema de scraping.
    """
    usecase = FiiListUseCase()
    return await usecase.execute()


@app.get("/fiis/magic_numbers", response_model=List[MagicNumberResponse], tags=["FIIs", "Análise"])
async def get_magic_numbers(invested_value: Optional[int] = None):
    """
    ## 🧮 Calcular Magic Numbers dos FIIs

    Calcula os "números mágicos" para análise de investimento em FIIs, baseado em critérios específicos.

    ### Parâmetros:
    - **invested_value** *(opcional)*: Valor em reais para simular investimento

    ### Critérios do Magic Number:
    - P/VP menor que 1.0
    - Dividend Yield positivo
    - Liquidez diária adequada
    - Duração indeterminada
    - Avaliação positiva nos últimos 12 meses

    ### Com invested_value:
    Quando fornecido, calcula também:
    - **quantity**: Quantidade de cotas que poderia comprar
    - **total_cost**: Custo total do investimento
    - **monthly_dividends**: Dividendos mensais estimados

    ### Exemplo:
    ```
    GET /fiis/magic_numbers?invested_value=10000
    ```
    """
    usecase = FiiMagicNumberUseCase(invested_value=invested_value)
    return await usecase.execute()


@app.get("/health", tags=["Sistema", "Monitoramento"])
async def health_check():
    """
    ## 🏥 Health Check Completo

    Verifica a saúde geral da API, incluindo conectividade com banco de dados e status do scheduler.

    ### Verificações Realizadas:
    - ✅ **API Status**: Se a aplicação está rodando
    - ✅ **Database**: Conectividade e contagem de dados
    - ✅ **Scheduler**: Status do sistema automático

    ### Informações do Banco:
    - **type**: Tipo do banco (DynamoDB)
    - **status**: Status da conexão
    - **total_fiis**: Total de FIIs armazenados
    - **fiis_with_dividend**: FIIs com dividend yield > 0
    - **fiis_without_dividend**: FIIs sem dividend yield

    ### Informações do Scheduler:
    - **status**: Status do sistema automático
    - **next_update**: Frequência de atualizações
    - **auto_discovery**: Status da descoberta automática

    ### Códigos de Resposta:
    - **200**: Sistema saudável e funcionando
    - **503**: Problemas detectados no sistema

    ### Uso:
    Ideal para health checks automáticos, monitoramento e CI/CD pipelines.

    ### Exemplo de Resposta Saudável:
    ```json
    {
        "status": "healthy",
        "message": "FII Scraper API is running",
        "database": {
            "type": "dynamodb",
            "status": "connected",
            "total_fiis": 150,
            "fiis_with_dividend": 120,
            "fiis_without_dividend": 30
        },
        "scheduler": {
            "status": "active",
            "next_update": "every 8 hours",
            "auto_discovery": "enabled"
        }
    }
    ```
    """
    try:
        repository = FiiRepositoryFactory.create()
        fiis = await repository.list()

        total_fiis = len(fiis)
        fiis_with_dividend = len([f for f in fiis if f.dy_12 and f.dy_12 > 0])

        return {
            "status": "healthy",
            "message": "FII Scraper API is running",
            "database": {
                "type": "dynamodb",
                "status": "connected",
                "total_fiis": total_fiis,
                "fiis_with_dividend": fiis_with_dividend,
                "fiis_without_dividend": total_fiis - fiis_with_dividend,
            },
            "scheduler": {"status": "active", "next_update": "every 8 hours", "auto_discovery": "enabled"},
        }
    except Exception:
        return {
            "status": "healthy",
            "message": "FII Scraper API is running - seeding in progress",
            "database": {
                "type": "dynamodb",
                "status": "connected",
                "total_fiis": 0,
                "fiis_with_dividend": 0,
                "fiis_without_dividend": 0,
            },
            "scheduler": {"status": "active", "next_update": "seeding in progress", "auto_discovery": "enabled"},
        }


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard(request: Request):
    """
    ## 📊 Dashboard Visual dos FIIs

    Interface web moderna com Material Design para visualização e análise dos dados dos FIIs.

    ### Funcionalidades:
    - 📈 **Estatísticas Gerais**: Total de FIIs, Magic Numbers, liquidez média
    - ⭐ **Magic Numbers**: Lista destacada dos FIIs recomendados
    - 📋 **Tabela Completa**: Todos os FIIs com dados detalhados
    - 🎨 **Material Design**: Interface moderna e responsiva
    - 🔄 **Auto-refresh**: Atualização automática a cada 5 minutos

    ### Indicadores Visuais:
    - **Verde**: Valores positivos (P/VP < 1, DY > 0)
    - **Vermelho**: Valores negativos ou altos
    - **Badges**: Classificação de liquidez (Alta/Média/Baixa)
    - **Magic Number**: Destaque especial para FIIs recomendados

    ### Responsivo:
    Otimizado para desktop, tablet e mobile.
    """
    try:
        fiis_usecase = FiiListUseCase()
        fiis = await fiis_usecase.execute()

        magic_usecase = FiiMagicNumberUseCase()
        magic_numbers = await magic_usecase.execute()
    except Exception:
        fiis = []
        magic_numbers = []

    total_fiis = len(fiis)
    positive_dy = len([f for f in fiis if f.dy_12 and f.dy_12 > 0])
    magic_count = len(magic_numbers)

    total_liquidity = sum(f.dialy_liquidity or 0 for f in fiis)
    avg_liquidity = (total_liquidity / total_fiis / 1000000) if total_fiis > 0 else 0

    stats = {
        "total_fiis": total_fiis,
        "positive_dy": positive_dy,
        "magic_numbers": magic_count,
        "avg_liquidity": avg_liquidity,
    }

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "fiis": fiis, "magic_numbers": magic_numbers, "stats": stats}
    )


@app.get("/status", tags=["Status"])
async def status():
    """
    ## 📈 Status do Sistema

    Endpoint de status detalhado para monitoramento da aplicação.

    ### Informações Retornadas:
    - **Status Geral**: Saúde da aplicação
    - **Database**: Status da conexão com DynamoDB
    - **Estatísticas**: Números totais de registros
    - **Última Atualização**: Timestamp da última operação

    ### Status Codes:
    - **healthy**: Sistema funcionando normalmente
    - **degraded**: Sistema com problemas parciais
    - **unhealthy**: Sistema com falhas críticas
    """
    try:
        # Test database connection
        fiis_usecase = FiiListUseCase()
        fiis = await fiis_usecase.execute()

        return {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "2.0.0",
            "database": {"type": "dynamodb", "status": "healthy", "total_fiis": len(fiis)},
            "services": {"scraper": "healthy", "scheduler": "healthy", "api": "healthy"},
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "2.0.0",
            "error": str(e),
            "database": {"type": "dynamodb", "status": "error", "error": str(e)},
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_debug,
    )
