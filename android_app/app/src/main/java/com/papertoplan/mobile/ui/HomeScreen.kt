package com.papertoplan.mobile.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Create
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.Note
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(baseUrl: String, onCameraClick: () -> Unit, onAudioClick: () -> Unit) {
    val notes = remember { mutableStateListOf<Note>() }
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }
    val username = sessionManager.getUsername() ?: ""
    val pin = sessionManager.getPin() ?: ""

    LaunchedEffect(Unit) {
        val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
        apiService.getNotes(username, pin).enqueue(object : Callback<List<Note>> {
            override fun onResponse(call: Call<List<Note>>, response: Response<List<Note>>) {
                if (response.isSuccessful) {
                    notes.clear()
                    response.body()?.let { notes.addAll(it) }
                }
            }

            override fun onFailure(call: Call<List<Note>>, t: Throwable) {
                // Handle error
            }
        })
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text("PaperToPlan AI") }) },
        floatingActionButton = {
            Column(horizontalAlignment = Alignment.End) {
                FloatingActionButton(
                    onClick = onAudioClick,
                    containerColor = MaterialTheme.colorScheme.secondaryContainer,
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    Icon(Icons.Default.Call, contentDescription = "Grabar Audio")
                }
                FloatingActionButton(onClick = onCameraClick) {
                    Icon(Icons.Default.Add, contentDescription = "Tomar Foto")
                }
            }
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            items(notes) { note ->
                NoteCard(note)
            }
        }
    }
}

@Composable
fun NoteCard(note: Note) {
    Card(
        modifier = Modifier
            .padding(8.dp)
            .fillMaxSize()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = note.title ?: "Sin Título")
            Text(text = "Status: ${note.status}")
            Text(text = "Time: ${note.implementation_time ?: "N/A"}")
        }
    }
}
