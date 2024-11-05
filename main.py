from typing import List, Optional, Dict

from fastapi import FastAPI

from app.domain.fii_domain import FiiDomain
from app.usecases.fii_list_usecase import FiiListUseCase
from app.usecases.fii_magic_number_usecase import FiiMagicNumberUseCase, MagicNumberResponse

app = FastAPI()


@app.get("/fiis", response_model=List[FiiDomain])
async def read_root():
    usecase = FiiListUseCase()
    return await usecase.execute()


@app.get("/fiis/magic_numbers", response_model=List[MagicNumberResponse])
async def read_root(invested_value: Optional[int] = None):
    usecase = FiiMagicNumberUseCase(invested_value=invested_value)
    return await usecase.execute()
