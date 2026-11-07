from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MarketQuote(BaseModel):
    model_config = ConfigDict(frozen=True)

    asset_id: str
    currency: str = "usd"
    price: Decimal
    market_cap: Decimal | None = None
    volume_24h: Decimal | None = None
    change_24h_pct: Decimal | None = None
    source: str
    retrieved_at: datetime
