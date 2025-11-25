package com.papertoplan.mobile.ui

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.util.Log
import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun AudioScreen(onRecordingSuccess: () -> Unit) {
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }
    var isRecording by remember { mutableStateOf(false) }
    var recorder: MediaRecorder? by remember { mutableStateOf(null) }
    var audioFile: File? by remember { mutableStateOf(null) }

    DisposableEffect(Unit) {
        onDispose {
            recorder?.release()
        }
    }

    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = if (isRecording) "Grabando..." else "Presiona para grabar",
                style = MaterialTheme.typography.headlineMedium,
                color = if (isRecording) Color.Red else MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.height(32.dp))

            FloatingActionButton(
                onClick = {
                    if (isRecording) {
                        stopRecording(recorder)
                        isRecording = false
                        recorder = null
                        audioFile?.let { file ->
                            uploadAudio(context, file, sessionManager, onRecordingSuccess)
                        }
                    } else {
                        val file = createAudioFile(context)
                        audioFile = file
                        recorder = startRecording(context, file)
                        if (recorder != null) {
                            isRecording = true
                        }
                    }
                },
                containerColor = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary
            ) {
                Icon(
                    if (isRecording) Icons.Default.Done else Icons.Default.Call,
                    contentDescription = if (isRecording) "Detener" else "Grabar"
                )
            }
        }
    }
}

private fun createAudioFile(context: Context): File {
    val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
    return File(context.externalCacheDir, "voice_note_$timeStamp.m4a")
}

private fun startRecording(context: Context, file: File): MediaRecorder? {
    return try {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context).apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setOutputFile(file.absolutePath)
                prepare()
                start()
            }
        } else {
            @Suppress("DEPRECATION")
            MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setOutputFile(file.absolutePath)
                prepare()
                start()
            }
        }
    } catch (e: IOException) {
        Log.e("AudioScreen", "prepare() failed", e)
        Toast.makeText(context, "Error al iniciar grabación", Toast.LENGTH_SHORT).show()
        null
    }
}

private fun stopRecording(recorder: MediaRecorder?) {
    try {
        recorder?.stop()
        recorder?.release()
    } catch (e: Exception) {
        Log.e("AudioScreen", "stop() failed", e)
    }
}

private fun uploadAudio(
    context: Context,
    file: File,
    sessionManager: SessionManager,
    onSuccess: () -> Unit
) {
    val baseUrl = sessionManager.getBaseUrl() ?: return
    val username = sessionManager.getUsername() ?: return
    val pin = sessionManager.getPin() ?: return

    val requestFile = file.asRequestBody("audio/mp4".toMediaTypeOrNull())
    val body = MultipartBody.Part.createFormData("file", file.name, requestFile)

    val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
    apiService.uploadAudio(username, pin, body).enqueue(object : Callback<ResponseBody> {
        override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
            if (response.isSuccessful) {
                Toast.makeText(context, "Audio subido exitosamente", Toast.LENGTH_SHORT).show()
                onSuccess()
            } else {
                Toast.makeText(context, "Error al subir: ${response.message()}", Toast.LENGTH_SHORT).show()
            }
        }

        override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
            Toast.makeText(context, "Fallo de red: ${t.message}", Toast.LENGTH_SHORT).show()
        }
    })
}
