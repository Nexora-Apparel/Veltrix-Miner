package com.veltrix.miner.data.market

import java.io.IOException
import kotlinx.coroutines.CancellationException

sealed interface MarketQuotesResult {
    data class Success(val quotes: List<MarketQuoteDto>) : MarketQuotesResult
    data object NotConfigured : MarketQuotesResult
    data class HttpFailure(val statusCode: Int) : MarketQuotesResult
    data object NetworkFailure : MarketQuotesResult
    data object InvalidResponse : MarketQuotesResult
}

class MarketQuoteRepository(
    private val api: MarketApi?
) {
    suspend fun fetchQuotes(assets: List<String> = listOf("btc", "xmr", "ltc", "doge")): MarketQuotesResult {
        val normalized = assets.map { it.trim().lowercase() }.distinct()
        if (api == null) return MarketQuotesResult.NotConfigured
        if (normalized.isEmpty() || normalized.size > 4 ||
            normalized.any { it !in SUPPORTED_ASSETS }
        ) {
            return MarketQuotesResult.InvalidResponse
        }

        return try {
            val response = api.getQuotes(normalized.joinToString(","))
            if (!response.isSuccessful) {
                MarketQuotesResult.HttpFailure(response.code())
            } else {
                val quotes = response.body()
                if (quotes.isNullOrEmpty() ||
                    quotes.any { it.price.signum() < 0 || it.source.isBlank() || it.retrieved_at.isBlank() }
                ) {
                    MarketQuotesResult.InvalidResponse
                } else {
                    MarketQuotesResult.Success(quotes)
                }
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: IOException) {
            MarketQuotesResult.NetworkFailure
        } catch (_: Exception) {
            MarketQuotesResult.InvalidResponse
        }
    }

    private companion object {
        val SUPPORTED_ASSETS = setOf("btc", "xmr", "ltc", "doge")
    }
}
