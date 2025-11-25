package com.papertoplan.mobile.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
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
import com.papertoplan.mobile.network.Note
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import com.papertoplan.mobile.ui.theme.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NoteListScreen(baseUrl: String, onBackClick: () -> Unit, onNoteClick: (Int) -> Unit) {
    val notes = remember { mutableStateListOf<Note>() }
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }
    val username = sessionManager.getUsername() ?: ""
    val pin = sessionManager.getPin() ?: ""
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        while (true) {
            val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
            apiService.getNotes(username, pin).enqueue(object : Callback<List<Note>> {
                override fun onResponse(call: Call<List<Note>>, response: Response<List<Note>>) {
                    isLoading = false
                    if (response.isSuccessful) {
                        val newNotes = response.body() ?: emptyList()
                        if (notes != newNotes) {
                            notes.clear()
                            notes.addAll(newNotes)
                        }
                    }
                }

                override fun onFailure(call: Call<List<Note>>, t: Throwable) {
                    isLoading = false
                }
            })
            kotlinx.coroutines.delay(5000) // Poll every 5 seconds
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mis Notas", color = TextWhite) },
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
        if (isLoading && notes.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = PrimaryGreen)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
            ) {
                items(notes) { note ->
                    NoteCard(note, onClick = { onNoteClick(note.id) })
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NoteCard(note: Note, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 10.dp),
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(8.dp),
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(15.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = note.title ?: "Sin Título",
                    color = TextWhite,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                // StatusPill removed as requested
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "${note.implementation_time ?: "Sin tiempo estimado"}",
                color = TextGrey,
                fontSize = 14.sp
            )
        }
    }
}

