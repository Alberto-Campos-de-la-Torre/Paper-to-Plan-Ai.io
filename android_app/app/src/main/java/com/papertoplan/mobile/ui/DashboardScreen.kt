package com.papertoplan.mobile.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.papertoplan.mobile.ui.theme.*

@Composable
fun DashboardScreen(
    onCameraClick: () -> Unit,
    onAudioClick: () -> Unit,
    onNotesClick: () -> Unit,
    onStatsClick: () -> Unit,
    onLogoutClick: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = AppBackground
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "PaperToPlan AI",
                color = PrimaryGreen,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Sube una foto o usa tu cámara",
                color = TextGrey,
                fontSize = 16.sp
            )
            Spacer(modifier = Modifier.height(48.dp))

            // Camera Button
            DashboardButton(
                text = "Tomar Foto",
                icon = Icons.Default.Add,
                borderColor = PrimaryGreen,
                textColor = TextWhite,
                onClick = onCameraClick
            )
            Spacer(modifier = Modifier.height(16.dp))

            // Audio Button
            DashboardButton(
                text = "Grabar Voz",
                icon = Icons.Default.Call,
                borderColor = AccentOrange,
                textColor = AccentOrange, // Or white if preferred, web uses orange text/border
                onClick = onAudioClick
            )
            Spacer(modifier = Modifier.height(48.dp))

            // View Notes Button
            Button(
                onClick = onNotesClick,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                border = BorderStroke(2.dp, SecondaryBlue),
                shape = RoundedCornerShape(50),
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.List, contentDescription = null, tint = SecondaryBlue)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Ver Notas", color = SecondaryBlue, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(20.dp))

            // View Stats Button
            Button(
                onClick = onStatsClick,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                border = BorderStroke(2.dp, Color(0xFF9C27B0)),
                shape = RoundedCornerShape(50),
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.Info, contentDescription = null, tint = Color(0xFF9C27B0))
                Spacer(modifier = Modifier.width(8.dp))
                Text("Ver Estadísticas", color = Color(0xFF9C27B0), fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.weight(1f))

            // Logout Button (Bottom Center)
            TextButton(onClick = onLogoutClick) {
                Text("Cerrar Sesión", color = TextGrey)
            }
        }
    }
}

@Composable
fun DashboardButton(
    text: String,
    icon: ImageVector,
    borderColor: Color,
    textColor: Color,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        border = BorderStroke(2.dp, borderColor),
        shape = RoundedCornerShape(50),
        modifier = Modifier
            .fillMaxWidth()
            .height(60.dp),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = textColor)
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(24.dp))
        Spacer(modifier = Modifier.width(12.dp))
        Text(text = text, fontSize = 20.sp, fontWeight = FontWeight.Bold)
    }
}
