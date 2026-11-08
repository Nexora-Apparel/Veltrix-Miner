package com.veltrix.miner.data.market

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface MarketApi {
    @GET("api/v1/market/quotes")
    suspend fun getQuotes(
        @Query("assets") assets: String = "btc,xmr,ltc,doge"
    ): Response<List<MarketQuoteDto>>
}
