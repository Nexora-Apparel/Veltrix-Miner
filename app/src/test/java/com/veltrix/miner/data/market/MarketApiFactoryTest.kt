package com.veltrix.miner.data.market

import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class MarketApiFactoryTest {
    @Test
    fun rejectsMissingOrCleartextEndpoint() {
        assertNull(MarketApiFactory.create(""))
        assertNull(MarketApiFactory.create("http://api.example.test/"))
    }

    @Test
    fun rejectsCredentialsAndUrlParameters() {
        assertNull(MarketApiFactory.create("https://user:password@api.example.test/"))
        assertNull(MarketApiFactory.create("https://api.example.test/?token=secret"))
        assertNull(MarketApiFactory.create("https://api.example.test/#fragment"))
    }

    @Test
    fun acceptsHttpsOrigin() {
        assertNotNull(MarketApiFactory.create("https://api.example.test"))
    }

    @Test
    fun repositoryDoesNotInventDataWhenUnconfigured() = runBlocking {
        val result = MarketQuoteRepository(null).fetchQuotes()
        assertTrue(result is MarketQuotesResult.NotConfigured)
    }
}
