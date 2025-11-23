import customtkinter as ctk
from typing import Callable

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_new_note_file: Callable, on_new_note_webcam: Callable, on_filter_change: Callable, on_flush_db: Callable):
        super().__init__(master, width=200, corner_radius=0)
        self.on_new_note_file = on_new_note_file
        self.on_new_note_webcam = on_new_note_webcam
        self.on_filter_change = on_filter_change
        self.on_flush_db = on_flush_db

        self.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self, text="PaperToPlan AI", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Action Buttons
        self.new_note_btn = ctk.CTkButton(self, text="📄 Nueva Nota (Archivo)", command=self.on_new_note_file, fg_color="#1f6aa5", hover_color="#144870")
        self.new_note_btn.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.webcam_btn = ctk.CTkButton(self, text="📸 Nueva Nota (Cámara)", command=self.on_new_note_webcam, fg_color="#8e44ad", hover_color="#6c3483")
        self.webcam_btn.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Filters Section
        self.filter_label = ctk.CTkLabel(self, text="FILTROS", anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70")
        self.filter_label.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="w")

        self.filter_var = ctk.StringVar(value="All")

        self.filter_all = ctk.CTkRadioButton(self, text="Todos", variable=self.filter_var, value="All", command=self.trigger_filter)
        self.filter_all.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        self.filter_short = ctk.CTkRadioButton(self, text="Corto Plazo", variable=self.filter_var, value="Short Term", command=self.trigger_filter)
        self.filter_short.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        self.filter_medium = ctk.CTkRadioButton(self, text="Medio Plazo", variable=self.filter_var, value="Medium Term", command=self.trigger_filter)
        self.filter_medium.grid(row=6, column=0, padx=20, pady=5, sticky="w")

        self.filter_long = ctk.CTkRadioButton(self, text="Largo Plazo", variable=self.filter_var, value="Long Term", command=self.trigger_filter)
        self.filter_long.grid(row=7, column=0, padx=20, pady=5, sticky="w")

        # Debug / System
        self.flush_btn = ctk.CTkButton(self, text="⚠️ Flush DB (Debug)", command=self.on_flush_db, fg_color="transparent", border_width=1, border_color="darkred", text_color="red", hover_color="gray20")
        self.flush_btn.grid(row=8, column=0, padx=20, pady=(10, 10), sticky="s")

        # Mobile Server
        self.server_btn = ctk.CTkButton(self, text="📱 Mobile Server", command=self.toggle_server, fg_color="#2ecc71", hover_color="#27ae60")
        self.server_btn.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="s")
        
        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.grid(row=10, column=0, padx=20, pady=(0, 20))
        self.qr_label.grid_remove()
        
        self.is_server_running = False

    def toggle_server(self):
        # This will be handled by main.py via a callback or event, 
        # but for now let's just trigger a callback if we had one.
        # Ideally, Sidebar should take an on_server_toggle callback.
        # Since we didn't add it to __init__, let's add a method to set it or just assume main sets it.
        if hasattr(self, 'on_server_toggle'):
            self.on_server_toggle()

    def set_qr_code(self, qr_image):
        self.qr_label.configure(image=qr_image)
        self.qr_label.grid()
        self.server_btn.configure(text="Stop Server", fg_color="#e74c3c", hover_color="#c0392b")
        self.is_server_running = True

    def trigger_filter(self):
        self.on_filter_change(self.filter_var.get())
