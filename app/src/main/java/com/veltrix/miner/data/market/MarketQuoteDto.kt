package com.veltrix.miner.data.market

import java.math.BigDecimal

/**
 * Wire representation of backend MarketQuote. Decimal values remain decimal-safe;
 * retrievedAt is an ISO-8601 UTC timestamp supplied by the API.
 */
data class MarketQuoteDto(
    val asset_id: String,
    val currency: String,
    val price: BigDecimal,
    val market_cap: BigDecimal?,
    val volume_24h: BigDecimal?,
    val change_24h_pct: BigDecimal?,
    val source: String,
    val retrieved_at: String
)
