package com.papertoplan.mobile.ui

import android.content.Context
import android.net.Uri
import android.util.Log
import android.widget.Toast
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
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
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.concurrent.Executor

@Composable
fun CameraScreen(onCaptureSuccess: () -> Unit) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val imageCapture = remember { ImageCapture.Builder().build() }
    val sessionManager = remember { SessionManager(context) }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                val executor = ContextCompat.getMainExecutor(ctx)
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            cameraSelector,
                            preview,
                            imageCapture
                        )
                    } catch (exc: Exception) {
                        Log.e("CameraScreen", "Use case binding failed", exc)
                    }
                }, executor)
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )

        FloatingActionButton(
            onClick = {
                takePhoto(
                    context = context,
                    imageCapture = imageCapture,
                    executor = ContextCompat.getMainExecutor(context),
                    sessionManager = sessionManager,
                    onSuccess = onCaptureSuccess
                )
            },
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
        ) {
            Icon(Icons.Default.Add, contentDescription = "Capturar")
        }
    }
}

private fun takePhoto(
    context: Context,
    imageCapture: ImageCapture,
    executor: Executor,
    sessionManager: SessionManager,
    onSuccess: () -> Unit
) {
    val photoFile = File(
        context.externalCacheDir,
        SimpleDateFormat("yyyy-MM-dd-HH-mm-ss-SSS", Locale.US)
            .format(System.currentTimeMillis()) + ".jpg"
    )

    val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

    imageCapture.takePicture(
        outputOptions,
        executor,
        object : ImageCapture.OnImageSavedCallback {
            override fun onError(exc: ImageCaptureException) {
                Log.e("CameraScreen", "Photo capture failed: ${exc.message}", exc)
                Toast.makeText(context, "Error al capturar", Toast.LENGTH_SHORT).show()
            }

            override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                val savedUri = Uri.fromFile(photoFile)
                val msg = "Foto capturada: $savedUri"
                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                uploadImage(context, photoFile, sessionManager, onSuccess)
            }
        }
    )
}

private fun uploadImage(
    context: Context,
    file: File,
    sessionManager: SessionManager,
    onSuccess: () -> Unit
) {
    val baseUrl = sessionManager.getBaseUrl() ?: return
    val username = sessionManager.getUsername() ?: return
    val pin = sessionManager.getPin() ?: return

    val requestFile = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
    val body = MultipartBody.Part.createFormData("file", file.name, requestFile)

    val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
    apiService.uploadImage(username, pin, body).enqueue(object : Callback<ResponseBody> {
        override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
            if (response.isSuccessful) {
                Toast.makeText(context, "Imagen subida exitosamente", Toast.LENGTH_SHORT).show()
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
