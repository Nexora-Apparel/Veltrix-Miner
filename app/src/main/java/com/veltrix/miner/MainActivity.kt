package com.veltrix.miner

import android.app.Activity
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.MoreHoriz
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ShowChart
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private val Ink = Color(0xFF0B1017)
private val Panel = Color(0xFF151E29)
private val Muted = Color(0xFF9AA8B8)
private val Accent = Color(0xFF35D49A)
private val Amber = Color(0xFFFFC66D)

private enum class AppTab(val label: String, val icon: ImageVector) {
    Dashboard("Home", Icons.Default.Dashboard),
    Profitability("Profit", Icons.Default.ShowChart),
    Coins("Coins", Icons.Default.Bolt),
    Wallet("Wallet", Icons.Default.AccountBalanceWallet),
    More("More", Icons.Default.MoreHoriz)
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { VeltrixMinerApp() }
    }
}

@Composable
private fun VeltrixMinerApp() {
    var selectedTab = remember { androidx.compose.runtime.mutableStateOf(AppTab.Dashboard) }

    MaterialTheme(colorScheme = darkColorScheme(
        background = Ink,
        surface = Panel,
        primary = Accent,
        secondary = Amber,
        onBackground = Color.White,
        onSurface = Color.White
    )) {
        Scaffold(
            containerColor = Ink,
            bottomBar = {
                NavigationBar(containerColor = Panel) {
                    AppTab.entries.forEach { tab ->
                        NavigationBarItem(
                            selected = selectedTab.value == tab,
                            onClick = { selectedTab.value = tab },
                            icon = { Icon(tab.icon, contentDescription = tab.label) },
                            label = { Text(tab.label, fontSize = 10.sp) }
                        )
                    }
                }
            }
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                AppHeader()
                when (selectedTab.value) {
                    AppTab.Dashboard -> DashboardScreen(
                        onOpenProfit = { selectedTab.value = AppTab.Profitability },
                        onOpenWorkers = { selectedTab.value = AppTab.More }
                    )
                    AppTab.Profitability -> ProfitabilityScreen()
                    AppTab.Coins -> CoinComparisonScreen()
                    AppTab.Wallet -> WalletScreen()
                    AppTab.More -> MoreScreen()
                }
            }
        }
    }
}

@Composable
private fun AppHeader() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text("VELTRIX", color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Black)
            Text("MINER  /  CONTROL CENTRE", color = Muted, fontSize = 9.sp, letterSpacing = 1.5.sp)
        }
        Surface(color = Color(0xFF17352D), shape = MaterialTheme.shapes.large) {
            Text(
                "●  MONITORING MODE",
                color = Accent,
                fontSize = 9.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 7.dp)
            )
        }
    }
}

@Composable
private fun DashboardScreen(onOpenProfit: () -> Unit, onOpenWorkers: () -> Unit) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("Mining overview", color = Color.White, fontSize = 23.sp, fontWeight = FontWeight.Bold)
                Text("Your mining operation at a glance", color = Muted, fontSize = 12.sp)
            }
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("VERIFIED NET EARNINGS", color = Muted, fontSize = 10.sp, letterSpacing = 1.2.sp)
                    Text("— USDT", color = Color.White, fontSize = 30.sp, fontWeight = FontWeight.Bold)
                    Text("No mining account connected · no payouts recorded", color = Amber, fontSize = 11.sp)
                    Divider(color = Color(0xFF2A3542))
                    Text("Estimated, pool-confirmed and blockchain-confirmed balances will be kept separate.", color = Muted, fontSize = 11.sp)
                }
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MetricCard("ACTIVE WORKERS", "0", "Not connected", Modifier.weight(1f))
                MetricCard("LIVE HASHRATE", "—", "No worker data", Modifier.weight(1f))
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                MetricCard("TODAY'S REWARDS", "—", "Awaiting pool data", Modifier.weight(1f))
                MetricCard("NET PROFIT", "—", "Costs not configured", Modifier.weight(1f))
            }
        }
        item {
            SectionCard(
                title = "Profitability scanner",
                subtitle = "Coin ranking is unavailable until live market and hardware data are connected.",
                action = "View scanner",
                onClick = onOpenProfit
            )
        }
        item {
            SectionCard(
                title = "Mining workers",
                subtitle = "No workers registered. This phone is currently configured as the control device.",
                action = "Worker monitoring",
                onClick = onOpenWorkers
            )
        }
        item { Text("Data integrity: demo interface only. No mining or earnings are being reported.", color = Muted, fontSize = 10.sp) }
    }
}

@Composable
private fun MetricCard(title: String, value: String, detail: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier, colors = CardDefaults.cardColors(containerColor = Panel)) {
        Column(Modifier.padding(13.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Text(title, color = Muted, fontSize = 9.sp, letterSpacing = 0.7.sp)
            Text(value, color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Bold)
            Text(detail, color = Muted, fontSize = 10.sp)
        }
    }
}

@Composable
private fun SectionCard(title: String, subtitle: String, action: String, onClick: () -> Unit) {
    Card(onClick = onClick, colors = CardDefaults.cardColors(containerColor = Panel)) {
        Column(Modifier.padding(15.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp)
            Text(subtitle, color = Muted, fontSize = 11.sp)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(action, color = Accent, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Icon(Icons.Default.ChevronRight, contentDescription = null, tint = Accent)
            }
        }
    }
}

@Composable
private fun ProfitabilityScreen() {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { ScreenHeading("Profitability", "Net-return analysis after operating costs") }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("SCANNER STATUS", color = Muted, fontSize = 10.sp)
                    Text("Waiting for verified inputs", color = Amber, fontWeight = FontWeight.Bold)
                    Text("Live coin prices, network difficulty, hardware hashrate, power draw and electricity tariff are not connected yet.", color = Muted, fontSize = 12.sp)
                }
            }
        }
        item { MetricCard("BEST NET OPPORTUNITY", "Not calculated", "No unsupported profit estimates", Modifier.fillMaxWidth()) }
        item { Text("Required inputs", color = Color.White, fontWeight = FontWeight.Bold) }
        items(listOf("Coin price and network difficulty", "Verified worker hashrate", "Measured power consumption", "Electricity tariff and pool fee", "Withdrawal and conversion costs")) { row ->
            InfoRow(Icons.Default.CheckCircle, row, "Required")
        }
    }
}

@Composable
private fun CoinComparisonScreen() {
    val candidates = listOf(
        Triple("Bitcoin", "BTC · SHA-256", "ASIC-focused"),
        Triple("Monero", "XMR · RandomX", "CPU-compatible algorithm"),
        Triple("Litecoin", "LTC · Scrypt", "Scrypt hardware"),
        Triple("Dogecoin", "DOGE · Scrypt", "Merged-mining ecosystem")
    )
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item { ScreenHeading("Coin comparison", "Research candidates · not a live profitability ranking") }
        items(candidates) { coin ->
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                    Text(coin.first, color = Color.White, fontWeight = FontWeight.Bold)
                    Text(coin.second, color = Accent, fontSize = 11.sp)
                    Text(coin.third, color = Muted, fontSize = 11.sp)
                    Text("Profitability: not yet verified", color = Amber, fontSize = 10.sp)
                }
            }
        }
        item { Text("USDT is the target settlement currency; it is not a mineable proof-of-work coin.", color = Muted, fontSize = 11.sp) }
    }
}

@Composable
private fun WalletScreen() {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { ScreenHeading("Wallet", "Track public addresses and confirmed payouts") }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("TOTAL VERIFIED BALANCE", color = Muted, fontSize = 10.sp)
                    Text("— USDT", color = Color.White, fontSize = 29.sp, fontWeight = FontWeight.Bold)
                    Text("No wallet connected", color = Amber, fontSize = 11.sp)
                }
            }
        }
        item { InfoRow(Icons.Default.Security, "Private keys", "Never requested or stored") }
        item { InfoRow(Icons.Default.CheckCircle, "Transaction verification", "Not connected") }
        item { Text("Only blockchain-confirmed receipts will count as settled earnings.", color = Muted, fontSize = 11.sp) }
    }
}

@Composable
private fun MoreScreen() {
    val context = LocalContext.current
    val batteryManager = context.getSystemService(BatteryManager::class.java)
    val battery = remember { batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY).coerceIn(0, 100) }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item { ScreenHeading("System & settings", "Device telemetry and application controls") }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(15.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("DEVICE HEALTH", color = Muted, fontSize = 10.sp, letterSpacing = 1.sp)
                    InfoRow(Icons.Default.Bolt, "Battery level", if (battery in 1..100) "$battery%" else "Unavailable")
                    InfoRow(Icons.Default.Memory, "Device", Build.MODEL ?: "Android device")
                    InfoRow(Icons.Default.Settings, "Android version", "Android ${Build.VERSION.RELEASE} · API ${Build.VERSION.SDK_INT}")
                    InfoRow(Icons.Default.Wifi, "Mining connection", "Not configured")
                }
            }
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                Column(Modifier.padding(15.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("SECURITY", color = Muted, fontSize = 10.sp, letterSpacing = 1.sp)
                    InfoRow(Icons.Default.Security, "Wallet custody", "Non-custodial design")
                    InfoRow(Icons.Default.CheckCircle, "Backend authentication", "Not connected")
                    InfoRow(Icons.Default.Tune, "Conversion automation", "Disabled")
                }
            }
        }
        item { Text("Temperature and detailed CPU telemetry require device-specific validation and are not inferred when unavailable.", color = Muted, fontSize = 10.sp) }
    }
}

@Composable
private fun ScreenHeading(title: String, subtitle: String) {
    Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {
        Text(title, color = Color.White, fontSize = 23.sp, fontWeight = FontWeight.Bold)
        Text(subtitle, color = Muted, fontSize = 11.sp)
    }
}

@Composable
private fun InfoRow(icon: ImageVector, title: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Icon(icon, contentDescription = null, tint = Accent)
        Column(Modifier.weight(1f)) {
            Text(title, color = Color.White, fontSize = 12.sp)
            Text(value, color = Muted, fontSize = 10.sp)
        }
    }
}
