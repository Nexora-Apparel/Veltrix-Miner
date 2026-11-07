package com.veltrix.miner.data.market

import com.veltrix.miner.BuildConfig

/**
 * Application-scoped entry point for market data. The repository remains
 * explicitly unconfigured until a real HTTPS API origin is supplied at build time.
 */
object MarketDataModule {
    val quoteRepository: MarketQuoteRepository by lazy {
        MarketQuoteRepository(
            MarketApiFactory.create(BuildConfig.VELTRIX_API_BASE_URL)
        )
    }
}
