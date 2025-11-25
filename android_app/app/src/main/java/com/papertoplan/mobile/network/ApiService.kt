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
    fun getNotes(): Call<List<Note>>

    @Multipart
    @POST("/api/upload")
    fun uploadImage(@Part image: MultipartBody.Part): Call<ResponseBody>

    @Multipart
    @POST("/api/upload_audio")
    fun uploadAudio(@Part audio: MultipartBody.Part): Call<ResponseBody>
}

data class Note(
    val id: Int,
    val title: String?,
    val status: String,
    val implementation_time: String?,
    val feasibility_score: Int?
)
