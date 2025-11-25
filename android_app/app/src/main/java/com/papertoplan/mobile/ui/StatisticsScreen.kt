package com.papertoplan.mobile.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import com.papertoplan.mobile.network.StatsResponse
import com.papertoplan.mobile.ui.theme.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatisticsScreen(baseUrl: String, onBackClick: () -> Unit) {
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }
    val username = sessionManager.getUsername() ?: ""
    val pin = sessionManager.getPin() ?: ""
    var stats by remember { mutableStateOf<StatsResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
        apiService.getStats(username, pin).enqueue(object : Callback<StatsResponse> {
            override fun onResponse(call: Call<StatsResponse>, response: Response<StatsResponse>) {
                if (response.isSuccessful) {
                    stats = response.body()
                }
                isLoading = false
            }

            override fun onFailure(call: Call<StatsResponse>, t: Throwable) {
                isLoading = false
            }
        })
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Estadísticas", color = TextWhite) },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Volver", tint = TextWhite)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = AppBackground)
            )
        },
        containerColor = AppBackground
    ) { paddingValues ->
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = PrimaryGreen)
            }
        } else {
            stats?.let { data ->
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    // 1. Progress Pie Chart
                    Text("Progreso de Proyectos", color = TextWhite, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(16.dp))
                    PieChart(
                        data = mapOf(
                            "Completados" to data.progress.completed.toFloat(),
                            "En Progreso" to data.progress.in_progress.toFloat()
                        ),
                        colors = listOf(PrimaryGreen, SecondaryBlue)
                    )
                    Spacer(modifier = Modifier.height(24.dp))

                    // 2. Implementation Time Bar Chart
                    Text("Tiempo de Implementación", color = TextWhite, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(16.dp))
                    BarChart(
                        data = mapOf(
                            "Corto" to data.implementation_time.short_term.toFloat(),
                            "Medio" to data.implementation_time.medium_term.toFloat(),
                            "Largo" to data.implementation_time.long_term.toFloat()
                        ),
                        colors = listOf(PrimaryGreen, SecondaryBlue, Color(0xFF9C27B0))
                    )
                    Spacer(modifier = Modifier.height(24.dp))

                    // 3. Feasibility Score Histogram (Simplified as Average/Max/Min for now or simple bars)
                    Text("Distribución de Viabilidad", color = TextWhite, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(16.dp))
                    if (data.feasibility_scores.isNotEmpty()) {
                        val avg = data.feasibility_scores.average()
                        Text("Promedio: ${String.format("%.1f", avg)}/100", color = TextGrey, fontSize = 16.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        ScoreDistribution(scores = data.feasibility_scores)
                    } else {
                        Text("No hay datos suficientes", color = TextGrey)
                    }
                }
            } ?: Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Error al cargar estadísticas", color = StatusError)
            }
        }
    }
}

@Composable
fun PieChart(data: Map<String, Float>, colors: List<Color>) {
    val total = data.values.sum()
    if (total == 0f) {
        Text("No hay datos", color = TextGrey)
        return
    }

    Row(verticalAlignment = Alignment.CenterVertically) {
        Canvas(modifier = Modifier.size(150.dp)) {
            var startAngle = -90f
            data.values.forEachIndexed { index, value ->
                val sweepAngle = (value / total) * 360f
                drawArc(
                    color = colors[index % colors.size],
                    startAngle = startAngle,
                    sweepAngle = sweepAngle,
                    useCenter = true
                )
                startAngle += sweepAngle
            }
        }
        Spacer(modifier = Modifier.width(20.dp))
        Column {
            data.keys.forEachIndexed { index, label ->
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 4.dp)) {
                    Box(modifier = Modifier.size(12.dp).background(colors[index % colors.size], RoundedCornerShape(2.dp)))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("$label (${data[label]?.toInt()})", color = TextWhite, fontSize = 14.sp)
                }
            }
        }
    }
}

@Composable
fun BarChart(data: Map<String, Float>, colors: List<Color>) {
    val max = data.values.maxOrNull() ?: 0f
    if (max == 0f) {
        Text("No hay datos", color = TextGrey)
        return
    }

    Column {
        data.keys.forEachIndexed { index, label ->
            val value = data[label] ?: 0f
            val percentage = value / max
            
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 8.dp)) {
                Text(label, color = TextWhite, modifier = Modifier.width(60.dp), fontSize = 12.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Box(
                    modifier = Modifier
                        .height(20.dp)
                        .fillMaxWidth(percentage * 0.8f) // Scale to 80% of width
                        .background(colors[index % colors.size], RoundedCornerShape(4.dp))
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("${value.toInt()}", color = TextWhite, fontSize = 12.sp)
            }
        }
    }
}

@Composable
fun ScoreDistribution(scores: List<Int>) {
    // Simple visualization: High (>80), Medium (50-80), Low (<50)
    val high = scores.count { it >= 80 }
    val medium = scores.count { it in 50..79 }
    val low = scores.count { it < 50 }
    
    val data = mapOf("Alto (>80)" to high.toFloat(), "Medio (50-79)" to medium.toFloat(), "Bajo (<50)" to low.toFloat())
    BarChart(data, listOf(PrimaryGreen, Color(0xFFFF9800), StatusError))
}
