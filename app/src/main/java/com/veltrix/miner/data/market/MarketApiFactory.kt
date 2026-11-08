package com.veltrix.miner.data.market

import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

object MarketApiFactory {
    /**
     * Returns null when no valid HTTPS endpoint is configured. HTTP, embedded
     * credentials, query strings and fragments are rejected by design.
     */
    fun create(baseUrl: String): MarketApi? {
        val configured = baseUrl.trim()
        if (configured.isEmpty()) return null

        val normalized = if (configured.endsWith("/")) configured else "$configured/"
        val parsed = normalized.toHttpUrlOrNull() ?: return null
        if (parsed.scheme != "https" ||
            parsed.host.isBlank() ||
            parsed.username.isNotEmpty() ||
            parsed.password.isNotEmpty() ||
            parsed.query != null ||
            parsed.fragment != null
        ) {
            return null
        }

        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .retryOnConnectionFailure(false)
            .build()

        val moshi = Moshi.Builder()
            .addLast(KotlinJsonAdapterFactory())
            .build()

        return Retrofit.Builder()
            .baseUrl(parsed)
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(MarketApi::class.java)
    }
}
