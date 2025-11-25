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
import com.papertoplan.mobile.ui.DashboardScreen
import com.papertoplan.mobile.ui.LoginScreen
import com.papertoplan.mobile.ui.NoteDetailScreen
import com.papertoplan.mobile.ui.StatisticsScreen
import com.papertoplan.mobile.ui.NoteListScreen
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
                    var selectedNoteId by remember { mutableStateOf<Int?>(null) }

                    when (currentScreen) {
                        Screen.Scan -> ScanScreen(onScanSuccess = { currentScreen = Screen.Login })
                        Screen.Login -> LoginScreen(onLoginSuccess = { currentScreen = Screen.Dashboard })
                        Screen.Dashboard -> {
                            val baseUrl = sessionManager.getBaseUrl()
                            if (baseUrl != null) {
                                DashboardScreen(
                                    onCameraClick = { currentScreen = Screen.Camera },
                                    onAudioClick = { currentScreen = Screen.Audio },
                                    onNotesClick = { currentScreen = Screen.NoteList },
                                    onStatsClick = { currentScreen = Screen.Statistics },
                                    onLogoutClick = {
                                        sessionManager.logout()
                                        currentScreen = Screen.Login
                                    }
                                )
                            } else {
                                currentScreen = Screen.Scan
                            }
                        }
                        Screen.Statistics -> {
                            val baseUrl = sessionManager.getBaseUrl()
                            if (baseUrl != null) {
                                StatisticsScreen(
                                    baseUrl = baseUrl,
                                    onBackClick = { currentScreen = Screen.Dashboard }
                                )
                            }
                        }
                        Screen.NoteList -> {
                            val baseUrl = sessionManager.getBaseUrl()
                            if (baseUrl != null) {
                                NoteListScreen(
                                    baseUrl = baseUrl,
                                    onBackClick = { currentScreen = Screen.Dashboard },
                                    onNoteClick = { noteId ->
                                        selectedNoteId = noteId
                                        currentScreen = Screen.NoteDetail
                                    }
                                )
                            }
                        }
                        Screen.NoteDetail -> {
                            val baseUrl = sessionManager.getBaseUrl()
                            if (baseUrl != null && selectedNoteId != null) {
                                NoteDetailScreen(
                                    baseUrl = baseUrl,
                                    noteId = selectedNoteId!!,
                                    onBackClick = { currentScreen = Screen.NoteList }
                                )
                            }
                        }
                        Screen.Camera -> CameraScreen(onCaptureSuccess = { currentScreen = Screen.Dashboard })
                        Screen.Audio -> AudioScreen(onRecordingSuccess = { currentScreen = Screen.Dashboard })
                        else -> {} // Handle other cases if any
                    }
                }
            }
        }
    }

    private fun getInitialScreen(sessionManager: SessionManager): Screen {
        if (sessionManager.getBaseUrl() == null) return Screen.Scan
        if (!sessionManager.isLoggedIn()) return Screen.Login
        return Screen.Dashboard
    }
}

enum class Screen {
    Scan, Login, Dashboard, NoteList, NoteDetail, Camera, Audio, Home, Statistics
}
