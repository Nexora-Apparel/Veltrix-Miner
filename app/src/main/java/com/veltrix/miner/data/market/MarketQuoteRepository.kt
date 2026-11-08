package com.veltrix.miner.data.market

import java.io.IOException
import java.time.Clock
import java.time.Duration
import java.time.Instant
import kotlinx.coroutines.CancellationException

sealed interface MarketQuotesResult {
    data class Fresh(val quotes: List<MarketQuoteDto>) : MarketQuotesResult
    data class Stale(val quotes: List<MarketQuoteDto>, val oldestAge: Duration) : MarketQuotesResult
    data object NotConfigured : MarketQuotesResult
    data class HttpFailure(val statusCode: Int) : MarketQuotesResult
    data object NetworkFailure : MarketQuotesResult
    data object InvalidResponse : MarketQuotesResult
}

class MarketQuoteRepository(
    private val api: MarketApi?,
    private val clock: Clock = Clock.systemUTC(),
    private val maxQuoteAge: Duration = Duration.ofMinutes(5),
    private val allowedFutureClockSkew: Duration = Duration.ofSeconds(60)
) {
    suspend fun fetchQuotes(
        assets: List<String> = listOf("btc", "xmr", "ltc", "doge")
    ): MarketQuotesResult {
        val normalized = assets.map { it.trim().lowercase() }.distinct()
        if (api == null) return MarketQuotesResult.NotConfigured
        if (normalized.isEmpty() || normalized.size > SUPPORTED_ASSETS.size ||
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
                validateAndClassify(quotes, normalized)
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: IOException) {
            MarketQuotesResult.NetworkFailure
        } catch (_: Exception) {
            MarketQuotesResult.InvalidResponse
        }
    }

    private fun validateAndClassify(
        quotes: List<MarketQuoteDto>?,
        requestedAssets: List<String>
    ): MarketQuotesResult {
        if (quotes.isNullOrEmpty()) return MarketQuotesResult.InvalidResponse

        val now = clock.instant()
        val seenAssets = mutableSetOf<String>()
        val timestamps = mutableListOf<Instant>()

        for (quote in quotes) {
            val asset = quote.asset_id.lowercase()
            if (asset !in requestedAssets ||
                !seenAssets.add(asset) ||
                quote.currency.lowercase() != "usd" ||
                quote.price.signum() <= 0 ||
                quote.market_cap?.signum() == -1 ||
                quote.volume_24h?.signum() == -1 ||
                quote.source.isBlank()
            ) {
                return MarketQuotesResult.InvalidResponse
            }

            val timestamp = try {
                Instant.parse(quote.retrieved_at)
            } catch (_: Exception) {
                return MarketQuotesResult.InvalidResponse
            }

            if (timestamp.isAfter(now.plus(allowedFutureClockSkew))) {
                return MarketQuotesResult.InvalidResponse
            }
            timestamps += timestamp
        }

        if (seenAssets != requestedAssets.toSet()) {
            return MarketQuotesResult.InvalidResponse
        }

        val oldestTimestamp = timestamps.minOrNull()
            ?: return MarketQuotesResult.InvalidResponse
        val age = Duration.between(oldestTimestamp, now)
        return if (age > maxQuoteAge) {
            MarketQuotesResult.Stale(quotes, age)
        } else {
            MarketQuotesResult.Fresh(quotes)
        }
    }

    private companion object {
        val SUPPORTED_ASSETS = setOf("btc", "xmr", "ltc", "doge")
    }
}
