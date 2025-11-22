import customtkinter as ctk
from typing import Dict, Any

class NoteDetail(ctk.CTkFrame):
    def __init__(self, master, on_delete_callback=None, on_regenerate_callback=None):
        super().__init__(master, corner_radius=0, fg_color="gray15")
        self.on_delete_callback = on_delete_callback
        self.on_regenerate_callback = on_regenerate_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Content scrollable (adjusted index)

        # Status Banner
        self.status_banner = ctk.CTkLabel(self, text="", height=30, corner_radius=0, font=ctk.CTkFont(size=12, weight="bold"))
        self.status_banner.grid(row=0, column=0, sticky="ew")
        self.status_banner.grid_remove() # Hide initially

        # Title
        self.title_label = ctk.CTkLabel(self, text="Selecciona una nota", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")

        # Content Area
        self.content_area = ctk.CTkTextbox(self, wrap="word")
        self.content_area.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.content_area.configure(state="disabled")

    def show_note(self, note: Dict[str, Any]):
        # Update Banner
        status = note.get('status', 'pending')
        if status == 'pending':
            self.status_banner.configure(text="⏳ Procesando...", fg_color="orange")
            self.status_banner.grid()
        elif status == 'error':
            self.status_banner.configure(text="❌ Error en el Procesamiento", fg_color="red")
            self.status_banner.grid()
        elif status == 'processed':
            self.status_banner.configure(text="✅ Análisis Completado", fg_color="green")
            self.status_banner.grid()
        else:
            self.status_banner.grid_remove()

        analysis_json = note.get('ai_analysis')
        
        # If analysis is a string (JSON), parse it
        analysis = {}
        if isinstance(analysis_json, str):
            try:
                analysis = json.loads(analysis_json)
            except:
                analysis = {"error": "Invalid JSON"}
        elif isinstance(analysis_json, dict):
            analysis = analysis_json

        # Title
        title = analysis.get('title', f"Nota {note['id']}")
        self.title_label.configure(text=title)

        # Content construction
        text = ""
        
        if "error" in analysis:
             text += f"⚠️ ERROR: {analysis['error']}\n\n"

        if "feasibility_score" in analysis:
            text += f"📊 Viabilidad: {analysis['feasibility_score']}/100\n\n"
        
        if "summary" in analysis:
            text += f"📝 Resumen:\n{analysis['summary']}\n\n"
            
        if "technical_considerations" in analysis:
            text += "🔧 Consideraciones Técnicas:\n"
            for item in analysis['technical_considerations']:
                text += f"• {item}\n"
            text += "\n"

        if "recommended_stack" in analysis:
            text += "💻 Stack Recomendado:\n"
            if isinstance(analysis['recommended_stack'], list):
                for item in analysis['recommended_stack']:
                    text += f"• {item}\n"
            else:
                text += f"{analysis['recommended_stack']}\n"
            text += "\n"

        if "implementation_time" in analysis:
            text += f"⏱️ Tiempo Estimado: {analysis['implementation_time']}\n"

        self.content_area.configure(state="normal")
        self.content_area.delete("0.0", "end")
        self.content_area.insert("0.0", text)
        self.content_area.configure(state="disabled")

        # Editable Raw Text
        self.raw_text_label = ctk.CTkLabel(self, text="Texto Extraído (Editable):", font=ctk.CTkFont(size=14, weight="bold"))
        self.raw_text_label.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")

        self.raw_text_area = ctk.CTkTextbox(self, height=100)
        self.raw_text_area.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.raw_text_area.insert("0.0", note.get('raw_text', ''))

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=5, column=0, padx=20, pady=20)

        self.regenerate_btn = ctk.CTkButton(self.btn_frame, text="Regenerar Plan", fg_color="blue", command=lambda: self.regenerate_note(note))
        self.regenerate_btn.pack(side="left", padx=10)

        self.delete_btn = ctk.CTkButton(self.btn_frame, text="Eliminar Nota", fg_color="red", hover_color="darkred", command=lambda: self.delete_note(note))
        self.delete_btn.pack(side="left", padx=10)

    def regenerate_note(self, note):
        new_text = self.raw_text_area.get("0.0", "end").strip()
        if self.on_regenerate_callback:
            self.on_regenerate_callback(note['id'], new_text)
            self.content_area.configure(state="normal")
            self.content_area.delete("0.0", "end")
            self.content_area.insert("0.0", "Regenerando plan...")
            self.content_area.configure(state="disabled")

    def delete_note(self, note):
        if self.on_delete_callback:
            self.on_delete_callback(note['id'])
            self.content_area.configure(state="normal")
            self.content_area.delete("0.0", "end")
            self.content_area.insert("0.0", "Nota eliminada.")
            self.content_area.configure(state="disabled")
            self.btn_frame.destroy()
            self.raw_text_area.destroy()
            self.raw_text_label.destroy()
