package com.papertoplan.mobile.ui

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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.NoteDetail
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import com.papertoplan.mobile.ui.theme.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NoteDetailScreen(baseUrl: String, noteId: Int, onBackClick: () -> Unit) {
    var note by remember { mutableStateOf<NoteDetail?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }
    val username = sessionManager.getUsername() ?: ""
    val pin = sessionManager.getPin() ?: ""

    LaunchedEffect(noteId) {
        val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
        apiService.getNoteDetail(username, pin, noteId).enqueue(object : Callback<NoteDetail> {
            override fun onResponse(call: Call<NoteDetail>, response: Response<NoteDetail>) {
                isLoading = false
                if (response.isSuccessful) {
                    note = response.body()
                }
            }

            override fun onFailure(call: Call<NoteDetail>, t: Throwable) {
                isLoading = false
            }
        })
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Detalle de Nota", color = TextWhite) },
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
            note?.let { n ->
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    // Header Card
                    Card(
                        colors = CardDefaults.cardColors(containerColor = CardBackground),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = n.title ?: "Sin Título",
                                    color = PrimaryGreen,
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.weight(1f)
                                )
                                StatusPill(status = n.status)
                            }
                            Spacer(modifier = Modifier.height(16.dp))
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text("Tiempo Estimado:", color = TextGrey, fontSize = 14.sp)
                                    Text(n.implementation_time ?: "N/A", color = TextWhite, fontSize = 16.sp)
                                }
                                Column(modifier = Modifier.weight(1f)) {
                                    Text("Score Viabilidad:", color = TextGrey, fontSize = 14.sp)
                                    val score = n.feasibility_score ?: 0
                                    val scoreColor = when {
                                        score >= 80 -> PrimaryGreen
                                        score >= 50 -> StatusPending
                                        else -> StatusError
                                    }
                                    Text("$score/100", color = scoreColor, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Summary Section
                    SectionCard(title = "📝 Resumen Ejecutivo", content = n.summary ?: "Sin resumen")

                    Spacer(modifier = Modifier.height(16.dp))

                    // Stack Section
                    SectionCard(title = "💻 Stack Tecnológico") {
                        if (n.recommended_stack.isNullOrEmpty()) {
                            Text("Sin stack recomendado", color = TextWhite)
                        } else {
                            FlowRow {
                                n.recommended_stack.forEach { item ->
                                    Surface(
                                        color = SecondaryBlue,
                                        shape = RoundedCornerShape(15.dp)
                                    ) {
                                        Text(
                                            text = item,
                                            color = TextWhite,
                                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                                            fontSize = 14.sp
                                        )
                                    }
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Considerations Section
                    SectionCard(title = "🔧 Consideraciones Técnicas") {
                        if (n.technical_considerations.isNullOrEmpty()) {
                            Text("Sin consideraciones", color = TextWhite)
                        } else {
                            n.technical_considerations.forEach { item ->
                                Row(modifier = Modifier.padding(vertical = 4.dp)) {
                                    Text("• ", color = TextGrey)
                                    Text(item, color = TextWhite)
                                }
                            }
                        }
                    }
                    
                    if (!n.raw_text.isNullOrEmpty()) {
                        Spacer(modifier = Modifier.height(16.dp))
                        SectionCard(title = "📄 Texto Extraído", content = n.raw_text)
                    }
                }
            } ?: Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Error al cargar la nota", color = StatusError)
            }
        }
    }
}

@Composable
fun SectionCard(title: String, content: String) {
    SectionCard(title) {
        Text(text = content, color = TextWhite, lineHeight = 24.sp)
    }
}

@Composable
fun SectionCard(title: String, content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, color = SecondaryBlue, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            content()
        }
    }
}

@Composable
fun FlowRow(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    // Simple FlowRow implementation since it's experimental in some versions
    // For simplicity in this generated code, we'll just use a Column if FlowRow is complex to add without dependencies
    // But let's try a simple Column for now to avoid compilation errors with experimental APIs
    Column(modifier = modifier) {
        content()
    }
}
