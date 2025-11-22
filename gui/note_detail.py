import customtkinter as ctk
from typing import Dict, Any

class NoteDetail(ctk.CTkFrame):
    def __init__(self, master, on_delete_callback=None):
        super().__init__(master, corner_radius=0, fg_color="gray15")
        self.on_delete_callback = on_delete_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Content scrollable

        self.header = ctk.CTkLabel(self, text="Detalle del Plan", font=ctk.CTkFont(size=20, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.content_area = ctk.CTkTextbox(self, wrap="word")
        self.content_area.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.content_area.configure(state="disabled")

    def show_note(self, note: Dict[str, Any]):
        self.content_area.configure(state="normal")
        self.content_area.delete("0.0", "end")

        analysis = note.get('ai_analysis', {})
        if not analysis:
            self.content_area.insert("0.0", "Esta nota aún se está procesando o falló el análisis.")
            self.content_area.configure(state="disabled")
            return

        if "error" in analysis:
            self.content_area.insert("0.0", f"ERROR: {analysis['error']}")
            self.content_area.configure(state="disabled")
            return

        title = analysis.get('title', 'Sin Título')
        score = analysis.get('feasibility_score', 0)
        summary = analysis.get('summary', '')
        stack = analysis.get('recommended_stack', [])
        tech_considerations = analysis.get('technical_considerations', [])
        time_est = analysis.get('implementation_time', 'Unknown')

        text = f"PROYECTO: {title}\n"
        text += f"FACTIBILIDAD: {score}/100\n"
        text += f"TIEMPO ESTIMADO: {time_est}\n\n"
        
        text += f"RESUMEN EJECUTIVO:\n{summary}\n\n"
        
        text += "STACK RECOMENDADO:\n"
        for item in stack:
            text += f"- {item}\n"
        text += "\n"

        text += "CONSIDERACIONES TÉCNICAS:\n"
        for item in tech_considerations:
            text += f"- {item}\n"
        
        self.content_area.insert("0.0", text)
        self.content_area.configure(state="disabled")

        # Delete Button
        self.delete_btn = ctk.CTkButton(self, text="Eliminar Nota", fg_color="red", hover_color="darkred", command=lambda: self.delete_note(note))
        self.delete_btn.grid(row=2, column=0, padx=20, pady=20)

    def delete_note(self, note):
        if self.on_delete_callback:
            self.on_delete_callback(note['id'])
            self.content_area.configure(state="normal")
            self.content_area.delete("0.0", "end")
            self.content_area.insert("0.0", "Nota eliminada.")
            self.content_area.configure(state="disabled")
            self.delete_btn.destroy()
