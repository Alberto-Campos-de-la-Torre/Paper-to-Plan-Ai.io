import customtkinter as ctk
from typing import Callable
import logging
import traceback
from config import config

# Configure logging for sidebar
logger = logging.getLogger(__name__)

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_new_note_file: Callable, on_new_note_webcam: Callable, on_filter_change: Callable, on_flush_db: Callable, on_toggle_server: Callable = None, on_show_qr: Callable = None, on_show_kanban: Callable = None, on_show_dashboard: Callable = None, on_show_list: Callable = None):
        try:
            logger.info("Sidebar.__init__: Starting initialization...")
            super().__init__(master, width=200, corner_radius=0)
            logger.info("Sidebar.__init__: Super().__init__ completed")
            
            self.on_new_note_file = on_new_note_file
            self.on_new_note_webcam = on_new_note_webcam
            self.on_filter_change = on_filter_change
            self.on_flush_db = on_flush_db
            self.on_toggle_server = on_toggle_server
            self.on_show_qr = on_show_qr
            self.on_show_kanban = on_show_kanban
            self.on_show_dashboard = on_show_dashboard
            self.on_show_list = on_show_list
            logger.info("Sidebar.__init__: Callbacks assigned")

            # Note: Removed grid_rowconfigure(10, weight=1) as it was causing segmentation fault
            # The layout will work fine without it
            logger.info("Sidebar.__init__: Skipping grid_rowconfigure (removed to avoid segfault)")

            try:
                logger.info("Sidebar.__init__: Creating logo label...")
                self.logo_label = ctk.CTkLabel(self, text="PaperToPlan AI", font=ctk.CTkFont(size=22, weight="bold"))
                self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
                logger.info("Sidebar.__init__: Logo label created and gridded")
            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating logo label: {e}")
                logger.error(traceback.format_exc())
                raise

            # Action Buttons
            try:
                logger.info("Sidebar.__init__: Creating action buttons...")
                self.new_note_btn = ctk.CTkButton(self, text="📄 Nueva Nota (Archivo)", command=self.on_new_note_file, fg_color="#1f6aa5", hover_color="#144870")
                self.new_note_btn.grid(row=1, column=0, padx=20, pady=(0, 10))
                logger.info("Sidebar.__init__: New note button created")

                self.webcam_btn = ctk.CTkButton(self, text="📸 Nueva Nota (Cámara)", command=self.on_new_note_webcam, fg_color="#8e44ad", hover_color="#6c3483")
                self.webcam_btn.grid(row=2, column=0, padx=20, pady=(0, 20))
                logger.info("Sidebar.__init__: Webcam button created")

                # Views Section
                # Views Section (Wrapped in Frame)
                logger.info("Sidebar.__init__: Creating Views frame...")
                self.views_frame = ctk.CTkFrame(self, fg_color="transparent")
                self.views_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=(10, 5))
                self.views_frame.grid_columnconfigure(0, weight=1)
                
                self.views_label = ctk.CTkLabel(self.views_frame, text="VISTAS", anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70")
                self.views_label.grid(row=0, column=0, padx=20, pady=(0, 5), sticky="w")
                logger.info("Sidebar.__init__: Views label created")

                self.list_btn = ctk.CTkButton(self.views_frame, text="📋 Lista", command=self.on_show_list, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
                self.list_btn.grid(row=1, column=0, padx=20, pady=(0, 5))
                logger.info("Sidebar.__init__: List button created")

                self.kanban_btn = ctk.CTkButton(self.views_frame, text="📊 Kanban", command=self.on_show_kanban, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
                self.kanban_btn.grid(row=2, column=0, padx=20, pady=(0, 5))
                logger.info("Sidebar.__init__: Kanban button created")

                self.dash_btn = ctk.CTkButton(self.views_frame, text="📈 Dashboard", command=self.on_show_dashboard, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
                self.dash_btn.grid(row=3, column=0, padx=20, pady=(0, 5))
                logger.info("Sidebar.__init__: Dashboard button created")

            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating action buttons: {e}")
                logger.error(traceback.format_exc())
                raise

            # Filters Section
            try:
                logger.info("Sidebar.__init__: Creating filters section...")
                self.filter_label = ctk.CTkLabel(self, text="FILTROS", anchor="w", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70")
                self.filter_label.grid(row=4, column=0, padx=20, pady=(10, 10), sticky="w")
                logger.info("Sidebar.__init__: Filter label created")

                self.filter_var = ctk.StringVar(value="All")
                logger.info("Sidebar.__init__: Filter variable created")

                self.filter_all = ctk.CTkRadioButton(self, text="Todos", variable=self.filter_var, value="All", command=self.trigger_filter)
                self.filter_all.grid(row=5, column=0, padx=20, pady=5, sticky="w")
                logger.info("Sidebar.__init__: Filter 'All' created")

                self.filter_short = ctk.CTkRadioButton(self, text="Corto Plazo", variable=self.filter_var, value="Short Term", command=self.trigger_filter)
                self.filter_short.grid(row=6, column=0, padx=20, pady=5, sticky="w")
                logger.info("Sidebar.__init__: Filter 'Short Term' created")
                
                self.filter_medium = ctk.CTkRadioButton(self, text="Medio Plazo", variable=self.filter_var, value="Medium Term", command=self.trigger_filter)
                self.filter_medium.grid(row=7, column=0, padx=20, pady=5, sticky="w")
                logger.info("Sidebar.__init__: Filter 'Medium Term' created")

                self.filter_long = ctk.CTkRadioButton(self, text="Largo Plazo", variable=self.filter_var, value="Long Term", command=self.trigger_filter)
                self.filter_long.grid(row=8, column=0, padx=20, pady=5, sticky="w")
                logger.info("Sidebar.__init__: Filter 'Long Term' created")

                logger.info("Sidebar.__init__: Creating 'Completed' filter...")
                self.filter_completed = ctk.CTkRadioButton(self, text="✓ Completadas", variable=self.filter_var, value="Completed", command=self.trigger_filter)
                logger.info("Sidebar.__init__: 'Completed' filter radio button created")
                self.filter_completed.grid(row=9, column=0, padx=20, pady=5, sticky="w")
                logger.info("Sidebar.__init__: 'Completed' filter gridded")

                # User filter dropdown
                logger.info("Sidebar.__init__: Creating user filter...")
                self.user_filter_label = ctk.CTkLabel(self, text="Filtrar por Usuario:", anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70")
                self.user_filter_label.grid(row=10, column=0, padx=20, pady=(15, 5), sticky="w")
                
                self.user_filter_var = ctk.StringVar(value="All Users")
                self.user_filter_dropdown = ctk.CTkComboBox(
                    self,
                    values=["All Users"],
                    variable=self.user_filter_var,
                    command=self.trigger_user_filter,
                    width=160
                )
                self.user_filter_dropdown.grid(row=11, column=0, padx=20, pady=(0, 10), sticky="w")
                logger.info("Sidebar.__init__: User filter dropdown created")
                
                # Update user filter dropdown with actual users
                self.update_user_filter_dropdown()
            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating filters: {e}")
                logger.error(traceback.format_exc())
                raise

            # Debug / System
            try:
                logger.info("Sidebar.__init__: Creating flush button...")
                self.flush_btn = ctk.CTkButton(self, text="⚠️ Flush DB (Debug)", command=self.on_flush_db, fg_color="transparent", border_width=1, border_color="darkred", text_color="red", hover_color="gray20")
                self.flush_btn.grid(row=12, column=0, padx=20, pady=(10, 10))
                logger.info("Sidebar.__init__: Flush button created")
            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating flush button: {e}")
                logger.error(traceback.format_exc())
                # No fallback for debug button

            # Mobile Server Section
            try:
                logger.info("Sidebar.__init__: Creating mobile server section...")
                # Server Status Indicator
                self.server_status_indicator = ctk.CTkLabel(self, text="⚫ Server Offline", text_color="gray", font=ctk.CTkFont(size=10))
                self.server_status_indicator.grid(row=13, column=0, padx=20, pady=(10, 0))
                logger.info("Sidebar.__init__: Server status indicator created")

                # Server Toggle Button
                logger.info("Sidebar.__init__: Creating server toggle button...")
                self.server_btn = ctk.CTkButton(
                    self, 
                    text="📱 Start Mobile Server", 
                    command=self.on_toggle_server,
                    fg_color="green", 
                    hover_color="darkgreen"
                )
                
                # Add emoji if possible (sometimes causes issues on minimal linux)
                try:
                    self.server_btn.configure(text="📱 Start Mobile Server")
                except Exception as e:
                    logger.warning(f"Could not add emoji to button: {e}, keeping text without emoji")
                
                logger.info("Sidebar.__init__: Step 5: Calling grid()...")
                self.server_btn.grid(row=14, column=0, padx=20, pady=(0, 10))
                logger.info("Sidebar.__init__: Step 5 complete: grid() called")
                logger.info("Sidebar.__init__: Mobile server button created and gridded successfully")
                
                # Show QR button (only visible when server is running)
                # Place it right after the server button (row 13)
                logger.info("Sidebar.__init__: Creating show QR button...")
                self.show_qr_btn = ctk.CTkButton(
                    self,
                    text="📱 Mostrar QR",
                    command=self.show_qr_window,
                    fg_color="#2196F3",
                    hover_color="#1976D2"
                )
                self.show_qr_btn.grid(row=15, column=0, padx=20, pady=(0, 10))
                self.show_qr_btn.grid_remove()  # Hide initially
                logger.info("Sidebar.__init__: Show QR button created at row 17")
            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating mobile server button: {e}")
                logger.error(traceback.format_exc())
                # Try to create a minimal button as fallback
                try:
                    logger.info("Sidebar.__init__: Attempting fallback minimal button...")
                    self.server_btn = ctk.CTkButton(self, text="Server")
                    self.server_btn.grid(row=14, column=0, padx=20, pady=(0, 10))
                    logger.info("Sidebar.__init__: Fallback button created")
                except Exception as e2:
                    logger.error(f"Sidebar.__init__: Even fallback button failed: {e2}")
                    logger.error(traceback.format_exc())
                    # Don't raise - just skip the button creation
                    logger.warning("Sidebar.__init__: Skipping mobile server button due to errors")
                    self.server_btn = None
                    self.show_qr_btn = None
            
            # User Management Section
            try:
                logger.info("Sidebar.__init__: Creating user management section...")
                self.add_user_btn = ctk.CTkButton(
                    self, 
                    text="+ Add User", 
                    command=self.add_user, 
                    width=100, 
                    height=24, 
                    font=ctk.CTkFont(size=12)
                )
                # Place add user button after the QR button (row 14)
                self.add_user_btn.grid(row=18, column=0, padx=20, pady=(0, 5))
                self.add_user_btn.grid_remove()  # Hide initially
                logger.info("Sidebar.__init__: Add user button created directly on sidebar at row 18")
                
                self.users_label = ctk.CTkLabel(
                    self, 
                    text="Usuarios:\n(Cargando...)", 
                    font=ctk.CTkFont(size=12), 
                    justify="left",
                    anchor="nw"
                )
                # Place users label at row 15, with some bottom padding
                self.users_label.grid(row=19, column=0, padx=20, pady=(0, 15), sticky="nw")
                self.users_label.grid_remove()  # Hide initially
                logger.info("Sidebar.__init__: Users label created directly on sidebar at row 19")
            except Exception as e:
                logger.error(f"Sidebar.__init__: Error creating user widgets directly: {e}")
                logger.error(traceback.format_exc())
                logger.warning("Sidebar.__init__: User management widgets will not be available")
                self.add_user_btn = None
                self.users_label = None
            
            # QR Code is now shown in a separate window, so we don't need the label in sidebar
            self.qr_image = None
            self.qr_url = None
            
            self.is_server_running = False
            logger.info("Sidebar.__init__: Initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Sidebar.__init__: FATAL ERROR during initialization: {e}")
            logger.error(traceback.format_exc())
            raise

    def toggle_server(self):
        if self.on_toggle_server:
            self.on_toggle_server()
    
    def set_server_status(self, is_running):
        if self.server_btn is None:
            logger.warning("set_server_status: server_btn is None, cannot update status")
            return
        self.is_server_running = is_running
        if is_running:
            self.server_btn.configure(text="Stop Server", fg_color="#e74c3c", hover_color="#c0392b")
            if hasattr(self, 'server_status_indicator'):
                self.server_status_indicator.configure(text="🟢 Server Online", text_color="green")
            
            # Show "Show QR" button
            if hasattr(self, 'show_qr_btn'):
                self.show_qr_btn.grid()
            # Show user management widgets if they exist
            if self.add_user_btn:
                self.add_user_btn.grid()
            if self.users_label:
                self.users_label.grid()
                self.update_user_list()
        else:
            self.server_btn.configure(text="📱 Mobile Server", fg_color="#2ecc71", hover_color="#27ae60")
            if hasattr(self, 'server_status_indicator'):
                self.server_status_indicator.configure(text="⚫ Server Offline", text_color="gray")

            # Hide "Show QR" button
            if hasattr(self, 'show_qr_btn'):
                self.show_qr_btn.grid_remove()
            # Hide user management widgets if they exist
            if self.add_user_btn:
                self.add_user_btn.grid_remove()
            if self.users_label:
                self.users_label.grid_remove()

    def set_qr_code(self, qr_image, qr_url):
        """Store QR code image and URL for later display in a window."""
        self.qr_image = qr_image
        self.qr_url = qr_url
        logger.info("set_qr_code: QR code stored for display in window")
    
    def show_qr_window(self):
        """Show QR code in a separate window."""
        if not self.qr_image or not self.qr_url:
            logger.warning("show_qr_window: No QR code available")
            import tkinter.messagebox as messagebox
            messagebox.showwarning("QR no disponible", "El código QR aún no está generado. Por favor, espera un momento.")
            return
        
        if self.on_show_qr:
            self.on_show_qr(self.qr_image, self.qr_url)

    def add_user(self):
        # Import only when needed to avoid initialization conflicts
        from backend.session_manager import session_manager
        
        # Show dialog to get username
        dialog = ctk.CTkInputDialog(text="Ingresa el nombre de usuario:", title="Nuevo Usuario")
        username = dialog.get_input()
        
        if username:
            logger.info(f"add_user: Attempting to create user '{username}'")
            pin = session_manager.create_user(username)
            if pin:
                logger.info(f"add_user: User '{username}' created with PIN: {pin}")
                self.update_user_list()  # Refresh the user list
                self.update_user_filter_dropdown()  # Update the filter dropdown
                # Show success message
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Usuario Creado", f"Usuario '{username}' creado exitosamente.\nPIN: {pin}")
            else:
                # User already exists or error
                logger.warning(f"add_user: Failed to create user '{username}' - may already exist")
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", f"No se pudo crear el usuario '{username}'.\nEl usuario ya existe o hubo un error.")

    def update_user_list(self):
        if self.users_label is None:
            logger.warning("update_user_list: users_label is None, cannot update")
            return
        try:
            # Import only when needed to avoid initialization conflicts
            from backend.session_manager import session_manager
            
            logger.info("update_user_list: Fetching users from session_manager...")
            users = session_manager.get_all_users()
            logger.info(f"update_user_list: Found {len(users)} users")
            
            if not users or len(users) == 0:
                text = "Usuarios Activos:\n(No hay usuarios registrados)"
            else:
                text = "Usuarios Activos:\n\n"
                for user_id, pin in users.items():
                    text += f"👤 {user_id}\n🔑 PIN: {pin}\n\n"
                text = text.rstrip()  # Remove trailing newlines
            
            logger.info(f"update_user_list: Updating label text (length: {len(text)})")
            self.users_label.configure(text=text)
            logger.info("update_user_list: Label updated successfully")
        except Exception as e:
            logger.error(f"update_user_list: Error updating user list: {e}")
            logger.error(traceback.format_exc())
            self.users_label.configure(text="Error al cargar usuarios")

    def trigger_filter(self):
        # Reset user filter when changing time/completion filter
        self.user_filter_var.set("All Users")
        self.on_filter_change(self.filter_var.get(), user_filter="All Users")
    
    def trigger_user_filter(self, selected_user):
        # When user filter changes, apply both filters
        self.on_filter_change(self.filter_var.get(), user_filter=selected_user)
    
    def update_user_filter_dropdown(self):
        """Update the user filter dropdown with current users from database."""
        try:
            from backend.session_manager import session_manager
            users = session_manager.get_all_users()
            user_list = ["All Users"] + list(users.keys())
            self.user_filter_dropdown.configure(values=user_list)
            logger.info(f"User filter dropdown updated with {len(user_list)} options")
        except Exception as e:
            logger.error(f"Error updating user filter dropdown: {e}")
