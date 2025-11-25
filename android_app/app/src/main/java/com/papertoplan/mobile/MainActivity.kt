package com.papertoplan.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.papertoplan.mobile.network.SessionManager
import com.papertoplan.mobile.ui.AudioScreen
import com.papertoplan.mobile.ui.CameraScreen
import com.papertoplan.mobile.ui.HomeScreen
import com.papertoplan.mobile.ui.LoginScreen
import com.papertoplan.mobile.ui.ScanScreen
import com.papertoplan.mobile.ui.theme.PaperToPlanMobileTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val sessionManager = SessionManager(this)

        setContent {
            PaperToPlanMobileTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    var currentScreen by remember { mutableStateOf(getInitialScreen(sessionManager)) }

                    when (currentScreen) {
                        Screen.Scan -> ScanScreen(onScanSuccess = { currentScreen = Screen.Login })
                        Screen.Login -> LoginScreen(onLoginSuccess = { currentScreen = Screen.Home })
                        Screen.Home -> {
                            val baseUrl = sessionManager.getBaseUrl()
                            if (baseUrl != null) {
                                HomeScreen(
                                    baseUrl = baseUrl,
                                    onCameraClick = { currentScreen = Screen.Camera },
                                    onAudioClick = { currentScreen = Screen.Audio }
                                )
                            } else {
                                currentScreen = Screen.Scan
                            }
                        }
                        Screen.Camera -> CameraScreen(onCaptureSuccess = { currentScreen = Screen.Home })
                        Screen.Audio -> AudioScreen(onRecordingSuccess = { currentScreen = Screen.Home })
                    }
                }
            }
        }
    }

    private fun getInitialScreen(sessionManager: SessionManager): Screen {
        if (sessionManager.getBaseUrl() == null) return Screen.Scan
        if (!sessionManager.isLoggedIn()) return Screen.Login
        return Screen.Home
    }
}

enum class Screen {
    Scan, Login, Home, Camera, Audio
}
