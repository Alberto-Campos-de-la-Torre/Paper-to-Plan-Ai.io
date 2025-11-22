import customtkinter as ctk
from typing import Callable

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_new_note_file: Callable, on_new_note_webcam: Callable, on_filter_change: Callable, on_flush_db: Callable):
        super().__init__(master, width=200, corner_radius=0)
        self.on_new_note_file = on_new_note_file
        self.on_new_note_webcam = on_new_note_webcam
        self.on_filter_change = on_filter_change
        self.on_flush_db = on_flush_db

        self.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self, text="PaperToPlan AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.new_note_btn = ctk.CTkButton(self, text="Nueva Nota (Archivo)", command=self.on_new_note_file)
        self.new_note_btn.grid(row=1, column=0, padx=20, pady=10)

        self.webcam_btn = ctk.CTkButton(self, text="Nueva Nota (Cámara)", command=self.on_new_note_webcam, fg_color="purple")
        self.webcam_btn.grid(row=2, column=0, padx=20, pady=10)

        self.filter_label = ctk.CTkLabel(self, text="Filtros:", anchor="w")
        self.filter_label.grid(row=3, column=0, padx=20, pady=(20, 0))

        self.filter_var = ctk.StringVar(value="All")

        self.filter_all = ctk.CTkRadioButton(self, text="Todos", variable=self.filter_var, value="All", command=self.trigger_filter)
        self.filter_all.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.filter_short = ctk.CTkRadioButton(self, text="Corto Plazo", variable=self.filter_var, value="Short Term", command=self.trigger_filter)
        self.filter_short.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        self.filter_medium = ctk.CTkRadioButton(self, text="Medio Plazo", variable=self.filter_var, value="Medium Term", command=self.trigger_filter)
        self.filter_medium.grid(row=6, column=0, padx=20, pady=10, sticky="nsw")

        self.filter_long = ctk.CTkRadioButton(self, text="Largo Plazo", variable=self.filter_var, value="Long Term", command=self.trigger_filter)
        self.filter_long.grid(row=7, column=0, padx=20, pady=10, sticky="w")

        self.flush_btn = ctk.CTkButton(self, text="Flush DB (Debug)", command=self.on_flush_db, fg_color="darkred", hover_color="red")
        self.flush_btn.grid(row=8, column=0, padx=20, pady=(20, 20), sticky="s")

    def trigger_filter(self):
        self.on_filter_change(self.filter_var.get())
