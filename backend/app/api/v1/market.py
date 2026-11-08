from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.market import MarketQuote
from app.services.market_data import MarketDataUnavailable, fetch_market_quotes

router = APIRouter(prefix="/market", tags=["market data"])


@router.get("/quotes", response_model=list[MarketQuote])
async def market_quotes(
    assets: str = Query(default="btc,xmr,ltc,doge", max_length=80),
) -> list[MarketQuote]:
    requested = [item.strip().lower() for item in assets.split(",") if item.strip()]
    if not requested or len(requested) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request between one and four supported assets",
        )
    try:
        return await fetch_market_quotes(requested)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except MarketDataUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data temporarily unavailable",
        ) from exc
