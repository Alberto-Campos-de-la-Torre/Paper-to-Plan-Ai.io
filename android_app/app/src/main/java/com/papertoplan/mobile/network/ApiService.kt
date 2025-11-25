package com.papertoplan.mobile.network

import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ApiService {
    @GET("/api/notes")
    fun getNotes(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String
    ): Call<List<Note>>

    @Multipart
    @POST("/api/upload")
    fun uploadImage(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String,
        @Part image: MultipartBody.Part
    ): Call<ResponseBody>

    @Multipart
    @POST("/api/upload_audio")
    fun uploadAudio(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String,
        @Part audio: MultipartBody.Part
    ): Call<ResponseBody>

    @POST("/api/login")
    fun login(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String
    ): Call<LoginResponse>

    @GET("/api/notes/{id}")
    fun getNoteDetail(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String,
        @retrofit2.http.Path("id") id: Int
    ): Call<NoteDetail>

    @GET("/api/stats")
    fun getStats(
        @retrofit2.http.Header("x-auth-user") user: String,
        @retrofit2.http.Header("x-auth-pin") pin: String
    ): Call<StatsResponse>
}

data class LoginResponse(
    val status: String,
    val message: String
)

data class UploadResponse(val status: String, val filename: String, val message: String)

data class Note(
    val id: Int,
    val title: String?,
    val status: String,
    val implementation_time: String?,
    val feasibility_score: Int?
)

data class NoteDetail(
    val id: Int,
    val title: String?,
    val status: String,
    val implementation_time: String?,
    val feasibility_score: Int?,
    val summary: String?,
    val raw_text: String?,
    val technical_considerations: List<String>?,
    val recommended_stack: List<String>?
)

data class StatsResponse(
    val progress: ProgressStats,
    val implementation_time: TimeStats,
    val feasibility_scores: List<Int>
)

data class ProgressStats(
    val completed: Int,
    val in_progress: Int
)

data class TimeStats(
    @com.google.gson.annotations.SerializedName("Corto Plazo") val short_term: Int,
    @com.google.gson.annotations.SerializedName("Mediano Plazo") val medium_term: Int,
    @com.google.gson.annotations.SerializedName("Largo Plazo") val long_term: Int
)
