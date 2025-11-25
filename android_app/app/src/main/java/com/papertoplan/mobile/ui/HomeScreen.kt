package com.papertoplan.mobile.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.Note
import com.papertoplan.mobile.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(baseUrl: String) {
    val notes = remember { mutableStateListOf<Note>() }

    LaunchedEffect(Unit) {
        val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
        apiService.getNotes().enqueue(object : Callback<List<Note>> {
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
        topBar = { TopAppBar(title = { Text("PaperToPlan AI") }) }
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
