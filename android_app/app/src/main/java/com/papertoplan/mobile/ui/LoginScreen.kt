package com.papertoplan.mobile.ui

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.papertoplan.mobile.network.ApiService
import com.papertoplan.mobile.network.LoginResponse
import com.papertoplan.mobile.network.RetrofitClient
import com.papertoplan.mobile.network.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(onLoginSuccess: () -> Unit) {
    var username by remember { mutableStateOf("") }
    var pin by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val sessionManager = remember { SessionManager(context) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Iniciar Sesión", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Usuario") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = pin,
            onValueChange = { pin = it },
            label = { Text("PIN") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                val baseUrl = sessionManager.getBaseUrl()
                if (baseUrl == null) {
                    Toast.makeText(context, "Error: URL base no configurada", Toast.LENGTH_SHORT).show()
                    return@Button
                }

                isLoading = true
                val apiService = RetrofitClient.getClient(baseUrl).create(ApiService::class.java)
                apiService.login(username, pin).enqueue(object : Callback<LoginResponse> {
                    override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                        isLoading = false
                        if (response.isSuccessful) {
                            sessionManager.saveCredentials(username, pin)
                            onLoginSuccess()
                        } else {
                            Toast.makeText(context, "Login fallido: ${response.message()}", Toast.LENGTH_SHORT).show()
                        }
                    }

                    override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                        isLoading = false
                        Toast.makeText(context, "Error de red: ${t.message}", Toast.LENGTH_SHORT).show()
                    }
                })
            },
            enabled = !isLoading && username.isNotEmpty() && pin.isNotEmpty(),
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp), color = MaterialTheme.colorScheme.onPrimary)
            } else {
                Text("Entrar")
            }
        }
    }
}
