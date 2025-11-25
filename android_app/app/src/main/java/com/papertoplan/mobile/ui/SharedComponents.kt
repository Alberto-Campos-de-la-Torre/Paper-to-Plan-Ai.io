package com.papertoplan.mobile.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.papertoplan.mobile.ui.theme.PrimaryGreen
import com.papertoplan.mobile.ui.theme.StatusError
import com.papertoplan.mobile.ui.theme.StatusPending
import com.papertoplan.mobile.ui.theme.TextWhite

@Composable
fun StatusPill(status: String) {
    val (color, text) = when (status) {
        "processed" -> PrimaryGreen to "Completado"
        "error" -> StatusError to "Error"
        else -> StatusPending to "Pendiente"
    }

    Surface(
        color = color,
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text = text,
            color = TextWhite,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
        )
    }
}
