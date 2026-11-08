package com.veltrix.miner.data.market

import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.time.ZoneOffset
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import retrofit2.Response

class MarketQuoteRepositoryTest {
    private val now = Instant.parse("2026-11-08T08:00:00Z")
    private val clock = Clock.fixed(now, ZoneOffset.UTC)

    @Test
    fun returnsFreshOnlyWhenAllRequestedQuotesAreFresh() = runBlocking {
        val result = repository(quotes(retrievedAt = now.minusSeconds(30).toString()))
            .fetchQuotes(listOf("btc", "xmr", "ltc", "doge"))
        assertTrue(result is MarketQuotesResult.Fresh)
        assertEquals(4, (result as MarketQuotesResult.Fresh).quotes.size)
    }

    @Test
    fun marksOldQuotesStaleRatherThanFresh() = runBlocking {
        val result = repository(quotes(retrievedAt = now.minus(Duration.ofMinutes(6)).toString()))
            .fetchQuotes(listOf("btc", "xmr", "ltc", "doge"))
        assertTrue(result is MarketQuotesResult.Stale)
        assertTrue((result as MarketQuotesResult.Stale).oldestAge > Duration.ofMinutes(5))
    }

    @Test
    fun rejectsFutureTimestampBeyondAllowedClockSkew() = runBlocking {
        val result = repository(quotes(retrievedAt = now.plusSeconds(61).toString()))
            .fetchQuotes(listOf("btc", "xmr", "ltc", "doge"))
        assertTrue(result is MarketQuotesResult.InvalidResponse)
    }

    @Test
    fun rejectsMissingOrDuplicateAssetQuotes() = runBlocking {
        val missing = repository(quotes().dropLast(1)).fetchQuotes()
        val duplicate = repository(quotes() + quotes().first()).fetchQuotes()
        assertTrue(missing is MarketQuotesResult.InvalidResponse)
        assertTrue(duplicate is MarketQuotesResult.InvalidResponse)
    }

    @Test
    fun rejectsNonUsdAndNonPositivePrices() = runBlocking {
        val badCurrency = quotes().mapIndexed { index, quote ->
            if (index == 0) quote.copy(currency = "ngn") else quote
        }
        val badPrice = quotes().mapIndexed { index, quote ->
            if (index == 0) quote.copy(price = java.math.BigDecimal.ZERO) else quote
        }
        assertTrue(repository(badCurrency).fetchQuotes() is MarketQuotesResult.InvalidResponse)
        assertTrue(repository(badPrice).fetchQuotes() is MarketQuotesResult.InvalidResponse)
    }

    private fun repository(data: List<MarketQuoteDto>): MarketQuoteRepository {
        val fakeApi = object : MarketApi {
            override suspend fun getQuotes(assets: String): Response<List<MarketQuoteDto>> =
                Response.success(data)
        }
        return MarketQuoteRepository(fakeApi, clock)
    }

    private fun quotes(
        retrievedAt: String = now.minusSeconds(30).toString()
    ): List<MarketQuoteDto> = listOf("btc", "xmr", "ltc", "doge").map { asset ->
        MarketQuoteDto(
            asset_id = asset,
            currency = "usd",
            price = java.math.BigDecimal("123.45"),
            market_cap = null,
            volume_24h = null,
            change_24h_pct = null,
            source = "coingecko",
            retrieved_at = retrievedAt
        )
    }
}
