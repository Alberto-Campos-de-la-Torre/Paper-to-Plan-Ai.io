import customtkinter as ctk
from typing import Callable
from config import config

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_new_note_file: Callable, on_new_note_webcam: Callable, on_filter_change: Callable, on_flush_db: Callable, on_toggle_server: Callable = None):
        super().__init__(master, width=200, corner_radius=0)
        self.on_new_note_file = on_new_note_file
        self.on_new_note_webcam = on_new_note_webcam
        self.on_filter_change = on_filter_change
        self.on_flush_db = on_flush_db
        self.on_toggle_server = on_toggle_server

        self.grid_rowconfigure(9, weight=1)

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

        # User Management Frame
        self.user_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.user_frame.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.user_frame.grid_remove()

        self.add_user_btn = ctk.CTkButton(self.user_frame, text="+ Add User", command=self.add_user, width=100, height=24, font=ctk.CTkFont(size=12))
        self.add_user_btn.pack(pady=(0, 5))

        self.users_label = ctk.CTkLabel(self.user_frame, text="", font=ctk.CTkFont(size=12), justify="left")
        self.users_label.pack()

        # Mobile Server
        self.server_btn = ctk.CTkButton(self, text="📱 Mobile Server", command=self.toggle_server, fg_color="#2ecc71", hover_color="#27ae60")
        self.server_btn.grid(row=11, column=0, padx=20, pady=(0, 10), sticky="s")
        
        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.grid(row=12, column=0, padx=20, pady=(0, 5))
        self.qr_label.grid_remove()
        
        self.is_server_running = False

    def toggle_server(self):
        if self.on_toggle_server:
            self.on_toggle_server()

    def set_server_status(self, is_running):
        self.is_server_running = is_running
        if is_running:
            self.server_btn.configure(text="Stop Server", fg_color="#e74c3c", hover_color="#c0392b")
            self.user_frame.grid()
            self.update_user_list()
        else:
            self.server_btn.configure(text="📱 Mobile Server", fg_color="#2ecc71", hover_color="#27ae60")
            self.qr_label.configure(image=None, text="")
            self.qr_label.grid_remove()
            self.user_frame.grid_remove()

    def set_qr_code(self, qr_image):
        self.qr_label.configure(image=qr_image)
        self.qr_label.grid()

    def add_user(self):
        from backend.session_manager import session_manager
        dialog = ctk.CTkInputDialog(text="Enter Username:", title="New User")
        username = dialog.get_input()
        if username:
            pin = session_manager.create_user(username)
            if pin:
                self.update_user_list()
            else:
                # Ideally show an error message, but for now just log/ignore
                print(f"Failed to create user {username}")

    def update_user_list(self):
        from backend.session_manager import session_manager
        users = session_manager.get_all_users()
        text = "Active Users:\n"
        for user_id, pin in users.items():
            text += f"{user_id}: {pin}\n"
        self.users_label.configure(text=text)

    def trigger_filter(self):
        self.on_filter_change(self.filter_var.get())
