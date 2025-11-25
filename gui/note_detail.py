import customtkinter as ctk
import json
import os
from typing import Dict, Any, Callable
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog, messagebox

class NoteDetail(ctk.CTkFrame):
    def __init__(self, master, on_delete_callback=None, on_regenerate_callback=None, on_mark_completed_callback=None):
        super().__init__(master, corner_radius=0, fg_color="gray15")
        self.on_delete_callback = on_delete_callback
        self.on_regenerate_callback = on_regenerate_callback
        self.on_mark_completed_callback = on_mark_completed_callback
        self.note = None # To store the currently displayed note

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

        # Editable Raw Text
        self.raw_text_label = ctk.CTkLabel(self, text="Texto Extraído (Editable):", font=ctk.CTkFont(size=14, weight="bold"))
        self.raw_text_label.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")
        self.raw_text_label.grid_remove() # Hide initially

        self.raw_text_area = ctk.CTkTextbox(self, height=100)
        self.raw_text_area.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.raw_text_area.grid_remove() # Hide initially

        # Action Buttons Frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=5, column=0, padx=20, pady=20)
        self.actions_frame.grid_remove() # Hide initially

        self.delete_btn = ctk.CTkButton(self.actions_frame, text="Eliminar Nota", fg_color="red", hover_color="darkred", command=self.delete_note)
        self.delete_btn.pack(side="left", padx=5)

        self.regenerate_btn = ctk.CTkButton(self.actions_frame, text="Regenerar Plan", fg_color="blue", command=self.regenerate_note)
        self.regenerate_btn.pack(side="left", padx=5)

        self.complete_btn = ctk.CTkButton(self.actions_frame, text="✓ Marcar Completado", fg_color="green", hover_color="darkgreen", command=self.mark_completed)
        # self.complete_btn.pack(side="left", padx=5) # Packed conditionally in show_note

        # Export Buttons
        self.export_pdf_btn = ctk.CTkButton(self.actions_frame, text="Exportar PDF", fg_color="#3F51B5", hover_color="#303F9F", command=self.export_pdf)
        self.export_pdf_btn.pack(side="right", padx=5)

        self.export_md_btn = ctk.CTkButton(self.actions_frame, text="Exportar MD", fg_color="#607D8B", hover_color="#455A64", command=self.export_md)
        self.export_md_btn.pack(side="right", padx=5)


    def show_note(self, note: Dict[str, Any]):
        self.note = note # Store the current note

        # Check if note is completed first
        is_completed = note.get('completed') == 1
        
        # Update Banner
        status = note.get('status', 'pending')
        if is_completed:
            self.status_banner.configure(text="🎉 PROYECTO COMPLETADO", fg_color="#27ae60", text_color="white")
            self.status_banner.grid()
        elif status == 'pending':
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

        # Title - Highlight if completed
        title = analysis.get('title', f"Nota {note['id']}")
        if is_completed:
            title = f"✓ {title}"
            self.title_label.configure(text=title, text_color="#27ae60")
        else:
            self.title_label.configure(text=title, text_color="white")

        # Clear previous content
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()

        if "error" in analysis:
             error_lbl = ctk.CTkLabel(self.scrollable_content, text=f"⚠️ ERROR: {analysis['error']}", text_color="red", wraplength=400)
             error_lbl.pack(pady=20)
        else:
            self._render_rich_content(analysis)

        # Show/Update Editable Raw Text
        self.raw_text_label.grid()
        self.raw_text_area.grid()
        self.raw_text_area.delete("0.0", "end")
        self.raw_text_area.insert("0.0", note.get('raw_text', ''))

        # Show/Update Buttons Frame
        self.actions_frame.grid()
        if note.get('completed') != 1:
            self.complete_btn.pack(side="left", padx=5)
        else:
            self.complete_btn.pack_forget()


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
                # Use a flow layout for chips
                current_row = ctk.CTkFrame(stack_frame, fg_color="transparent")
                current_row.pack(fill="x", pady=2)
                
                # Simple logic to wrap chips (approximate width check not possible easily in CTk without complex calculations)
                # Instead, we just pack them and let them flow if we use a proper flow layout manager, but CTk doesn't have one built-in.
                # We will use a grid-like approach or just pack them in rows of 3-4 to be safe.
                
                for i, item in enumerate(stack_items):
                    if i > 0 and i % 3 == 0: # New row every 3 items
                        current_row = ctk.CTkFrame(stack_frame, fg_color="transparent")
                        current_row.pack(fill="x", pady=2)
                        
                    chip = ctk.CTkFrame(current_row, fg_color="royalblue", corner_radius=15)
                    chip.pack(side="left", padx=(0, 5), pady=5)
                    # Limit text length in chip
                    display_text = item[:20] + "..." if len(item) > 20 else item
                    ctk.CTkLabel(chip, text=display_text, text_color="white", font=ctk.CTkFont(size=11)).pack(padx=10, pady=2)
            else:
                 ctk.CTkLabel(stack_frame, text=str(stack_items), wraplength=480).pack(anchor="w")

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

    def regenerate_note(self):
        if not self.note: return
        new_text = self.raw_text_area.get("0.0", "end").strip()
        if self.on_regenerate_callback:
            self.on_regenerate_callback(self.note['id'], new_text)
            
            # Clear content and show loading
            for widget in self.scrollable_content.winfo_children():
                widget.destroy()
            
            ctk.CTkLabel(self.scrollable_content, text="🔄 Regenerando plan...", font=ctk.CTkFont(size=16)).pack(pady=20)

    def delete_note(self):
        if not self.note: return
        if self.on_delete_callback:
            self.on_delete_callback(self.note['id'])
            
            # Clear content and show deleted message
            for widget in self.scrollable_content.winfo_children():
                widget.destroy()
                
            ctk.CTkLabel(self.scrollable_content, text="✅ Nota eliminada", font=ctk.CTkFont(size=16)).pack(pady=20)
            
            self.actions_frame.grid_remove()
            self.raw_text_area.grid_remove()
            self.raw_text_label.grid_remove()
            self.title_label.configure(text="Selecciona una nota", text_color="white")
            self.status_banner.grid_remove()
            self.note = None # Clear the stored note

    def mark_completed(self):
        if self.note:
            self.on_mark_completed_callback(self.note['id'])

    def export_pdf(self):
        if not self.note: return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not file_path: return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y = height - 50
            
            analysis = self.note.get('ai_analysis', {})
            title = analysis.get('title', 'Sin Título')
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, f"Project Plan: {title}")
            y -= 30
            
            c.setFont("Helvetica", 12)
            c.drawString(50, y, f"Feasibility: {analysis.get('feasibility_score', 'N/A')}/100")
            y -= 20
            c.drawString(50, y, f"Time: {analysis.get('implementation_time', 'N/A')}") # Changed from self.note.get to analysis.get
            y -= 40
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Summary")
            y -= 20
            c.setFont("Helvetica", 10)
            
            summary = analysis.get('summary', '')
            # Simple text wrapping
            text_obj = c.beginText(50, y)
            for line in summary.split('\n'):
                text_obj.textLine(line)
            c.drawText(text_obj)
            
            # Add Tech Stack
            if "recommended_stack" in analysis:
                y = text_obj.getY() - 30 # Get current y position and add some space
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "Recommended Stack")
                y -= 20
                c.setFont("Helvetica", 10)
                stack_items = analysis['recommended_stack']
                if isinstance(stack_items, list):
                    for item in stack_items:
                        c.drawString(60, y, f"• {item}")
                        y -= 15
                else:
                    c.drawString(60, y, str(stack_items))
                    y -= 15

            # Add Technical Considerations
            if "technical_considerations" in analysis:
                y -= 30
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "Technical Considerations")
                y -= 20
                c.setFont("Helvetica", 10)
                considerations = analysis['technical_considerations']
                if isinstance(considerations, list):
                    for item in considerations:
                        c.drawString(60, y, f"• {item}")
                        y -= 15
            
            c.save()
            messagebox.showinfo("Success", "PDF Exported Successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")

    def export_md(self):
        if not self.note: return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md")])
        if not file_path: return

        try:
            analysis = self.note.get('ai_analysis', {})
            title = analysis.get('title', 'Sin Título')
            
            content = f"# {title}\n\n"
            content += f"**Feasibility Score:** {analysis.get('feasibility_score', 'N/A')}/100\n"
            content += f"**Implementation Time:** {analysis.get('implementation_time', 'N/A')}\n\n" # Changed from self.note.get to analysis.get
            
            if "summary" in analysis:
                content += "## Summary\n"
                content += f"{analysis.get('summary', '')}\n\n"
            
            if "recommended_stack" in analysis:
                content += "## Recommended Stack\n"
                stack_items = analysis['recommended_stack']
                if isinstance(stack_items, list):
                    for item in stack_items:
                        content += f"- {item}\n"
                else:
                    content += f"{stack_items}\n"
                content += "\n"

            if "technical_considerations" in analysis:
                content += "## Technical Considerations\n"
                considerations = analysis['technical_considerations']
                if isinstance(considerations, list):
                    for item in considerations:
                        content += f"- {item}\n"
                else:
                    content += f"{considerations}\n"
                content += "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            messagebox.showinfo("Success", "Markdown Exported Successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Markdown: {e}")
