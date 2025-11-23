import customtkinter as ctk
from typing import Dict, Any

class NoteDetail(ctk.CTkFrame):
    def __init__(self, master, on_delete_callback=None, on_regenerate_callback=None, on_mark_completed_callback=None):
        super().__init__(master, corner_radius=0, fg_color="gray15")
        self.on_delete_callback = on_delete_callback
        self.on_regenerate_callback = on_regenerate_callback
        self.on_mark_completed_callback = on_mark_completed_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Content scrollable (adjusted index)

        # Status Banner
        self.status_banner = ctk.CTkLabel(self, text="", height=30, corner_radius=0, font=ctk.CTkFont(size=12, weight="bold"))
        self.status_banner.grid(row=0, column=0, sticky="ew")
        self.status_banner.grid_remove() # Hide initially

        # Title
        self.title_label = ctk.CTkLabel(self, text="Selecciona una nota", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")

        # Scrollable Content Area (Rich Layout)
        self.scrollable_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_content.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_content.grid_columnconfigure(0, weight=1)

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

        # Clear previous content
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        if "error" in analysis:
             error_lbl = ctk.CTkLabel(self.scrollable_content, text=f"⚠️ ERROR: {analysis['error']}", text_color="red", wraplength=400)
             error_lbl.pack(pady=20)
        else:
            self._render_rich_content(analysis)

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

        # Mark as Completed button (only show if not already completed)
        if note.get('completed') != 1:
            self.complete_btn = ctk.CTkButton(self.btn_frame, text="✓ Marcar Completado", fg_color="green", hover_color="darkgreen", command=lambda: self.mark_completed(note))
            self.complete_btn.pack(side="left", padx=10)

        self.delete_btn = ctk.CTkButton(self.btn_frame, text="Eliminar Nota", fg_color="red", hover_color="darkred", command=lambda: self.delete_note(note))
        self.delete_btn.pack(side="left", padx=10)

    def _render_rich_content(self, analysis):
        # 1. Header Stats (Score & Time)
        stats_frame = ctk.CTkFrame(self.scrollable_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Feasibility Score
        score = analysis.get('feasibility_score', 0)
        score_color = "green" if score >= 80 else "orange" if score >= 50 else "red"
        
        score_frame = ctk.CTkFrame(stats_frame, fg_color=score_color, corner_radius=10)
        score_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(score_frame, text=f"Viabilidad: {score}/100", text_color="white", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=5)

        # Time Estimate
        time_est = analysis.get('implementation_time', 'N/A')
        time_frame = ctk.CTkFrame(stats_frame, fg_color="gray30", corner_radius=10)
        time_frame.pack(side="left")
        ctk.CTkLabel(time_frame, text=f"⏱️ {time_est}", text_color="white").pack(padx=10, pady=5)

        # 2. Executive Summary
        if "summary" in analysis:
            ctk.CTkLabel(self.scrollable_content, text="📝 Resumen Ejecutivo", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 5))
            summary_frame = ctk.CTkFrame(self.scrollable_content, fg_color="gray20", corner_radius=10)
            summary_frame.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(summary_frame, text=analysis['summary'], wraplength=500, justify="left").pack(padx=15, pady=15, fill="x")

        # 3. Tech Stack
        if "recommended_stack" in analysis:
            ctk.CTkLabel(self.scrollable_content, text="💻 Stack Recomendado", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 5))
            stack_frame = ctk.CTkFrame(self.scrollable_content, fg_color="transparent")
            stack_frame.pack(fill="x", pady=(0, 20))
            
            stack_items = analysis['recommended_stack']
            if isinstance(stack_items, list):
                for item in stack_items:
                    chip = ctk.CTkFrame(stack_frame, fg_color="royalblue", corner_radius=15)
                    chip.pack(side="left", padx=(0, 5), pady=5)
                    ctk.CTkLabel(chip, text=item, text_color="white", font=ctk.CTkFont(size=11)).pack(padx=10, pady=2)
            else:
                 ctk.CTkLabel(stack_frame, text=str(stack_items)).pack(anchor="w")

        # 4. Technical Considerations
        if "technical_considerations" in analysis:
            ctk.CTkLabel(self.scrollable_content, text="🔧 Consideraciones Técnicas", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 5))
            tech_frame = ctk.CTkFrame(self.scrollable_content, fg_color="transparent")
            tech_frame.pack(fill="x")
            
            considerations = analysis['technical_considerations']
            if isinstance(considerations, list):
                for item in considerations:
                    row = ctk.CTkFrame(tech_frame, fg_color="transparent")
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text="•", font=ctk.CTkFont(size=16, weight="bold"), width=20).pack(side="left", anchor="n")
                    ctk.CTkLabel(row, text=item, wraplength=480, justify="left").pack(side="left", fill="x")

    def regenerate_note(self, note):
        new_text = self.raw_text_area.get("0.0", "end").strip()
        if self.on_regenerate_callback:
            self.on_regenerate_callback(note['id'], new_text)
            
            # Clear content and show loading
            for widget in self.scrollable_content.winfo_children():
                widget.destroy()
            
            ctk.CTkLabel(self.scrollable_content, text="🔄 Regenerando plan...", font=ctk.CTkFont(size=16)).pack(pady=20)

    def delete_note(self, note):
        if self.on_delete_callback:
            self.on_delete_callback(note['id'])
            
            # Clear content and show deleted message
            for widget in self.scrollable_content.winfo_children():
                widget.destroy()
                
            ctk.CTkLabel(self.scrollable_content, text="✅ Nota eliminada", font=ctk.CTkFont(size=16)).pack(pady=20)
            
            self.btn_frame.destroy()
            self.raw_text_area.destroy()
            self.raw_text_label.destroy()

    def mark_completed(self, note):
        if self.on_mark_completed_callback:
            self.on_mark_completed_callback(note['id'])
            
            # Clear content and show completed message
            for widget in self.scrollable_content.winfo_children():
                widget.destroy()
            
            ctk.CTkLabel(self.scrollable_content, text="✅ Nota marcada como completada", font=ctk.CTkFont(size=16), text_color="green").pack(pady=20)
            
            self.btn_frame.destroy()
            self.raw_text_area.destroy()
            self.raw_text_label.destroy()
