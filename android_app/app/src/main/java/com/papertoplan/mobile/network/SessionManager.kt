package com.papertoplan.mobile.network

import android.content.Context
import android.content.SharedPreferences

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("paper_to_plan_prefs", Context.MODE_PRIVATE)

    companion object {
        const val KEY_BASE_URL = "base_url"
        const val KEY_USERNAME = "username"
        const val KEY_PIN = "pin"
    }

    fun saveBaseUrl(url: String) {
        prefs.edit().putString(KEY_BASE_URL, url).apply()
    }

    fun getBaseUrl(): String? {
        return prefs.getString("base_url", null)
    }

    fun logout() {
        val editor = prefs.edit()
        editor.remove("username")
        editor.remove("pin")
        editor.apply()
    }

    fun saveCredentials(username: String, pin: String) {
        prefs.edit()
            .putString(KEY_USERNAME, username)
            .putString(KEY_PIN, pin)
            .apply()
    }

    fun getUsername(): String? {
        return prefs.getString(KEY_USERNAME, null)
    }

    fun getPin(): String? {
        return prefs.getString(KEY_PIN, null)
    }

    fun isLoggedIn(): Boolean {
        return !getUsername().isNullOrEmpty() && !getPin().isNullOrEmpty()
    }

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}
