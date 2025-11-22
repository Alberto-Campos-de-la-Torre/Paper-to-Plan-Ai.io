import customtkinter as ctk
import threading
import os
from tkinter import filedialog
from gui.sidebar import Sidebar
from gui.note_list import NoteList
from gui.note_detail import NoteDetail
from gui.webcam import WebcamWindow
from backend.ai_manager import AIEngine
from database.db_manager import DBManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PaperToPlanApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PaperToPlan AI")
        self.geometry("1200x800")

        # Data & Logic
        self.db = DBManager()
        self.ai = None # Lazy init or init here
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Components
        self.sidebar = Sidebar(self, 
                               on_new_note_file=self.new_note_file, 
                               on_new_note_webcam=self.new_note_webcam,
                               on_filter_change=self.apply_filter,
                               on_flush_db=self.flush_db_action)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.note_list = NoteList(self, on_note_select=self.show_detail)
        self.note_list.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.note_detail = NoteDetail(self, on_delete_callback=self.delete_note, on_regenerate_callback=self.regenerate_note)
        self.note_detail.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Status Bar / Progress
        self.status_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.status_bar.set(0)
        self.status_bar.grid_remove() # Hide initially

        # Init AI in background to not freeze UI startup
        self.init_ai_thread()

        # Load initial notes
        self.refresh_notes()

    def init_ai_thread(self):
        def _init():
            print("Initializing AI Engine...")
            self.ai = AIEngine()
            print("AI Engine Ready.")
        threading.Thread(target=_init, daemon=True).start()

    def refresh_notes(self, filter_type="All"):
        notes = self.db.get_all_notes()
        filtered_notes = []
        if filter_type == "All":
            filtered_notes = notes
        else:
            for note in notes:
                if note.get('implementation_time') == filter_type:
                    filtered_notes.append(note)
        
        self.note_list.update_notes(filtered_notes)

    def apply_filter(self, filter_value):
        self.refresh_notes(filter_value)

    def delete_note(self, note_id):
        if self.db.delete_note(note_id):
            print(f"Deleted note {note_id}")
            self.refresh_notes()

    def flush_db_action(self):
        if self.db.flush_db():
            print("DB Flushed")
            self.refresh_notes()

    def regenerate_note(self, note_id, new_text):
        print(f"Regenerating note {note_id} with new text...")
        
        # Update raw text in DB first
        self.db.update_note_text(note_id, new_text)
        
        # Start AI pipeline again (skipping image extraction)
        self.status_bar.grid()
        self.status_bar.start()
        threading.Thread(target=self.ai_pipeline_text_only, args=(note_id, new_text), daemon=True).start()

    def ai_pipeline_text_only(self, note_id, text):
        try:
            print("Analyzing text (Regeneration)...")
            analysis = self.ai.analyze_text(text)
            self.db.update_note_analysis(note_id, analysis)
        except Exception as e:
            print(f"Regeneration Error: {e}")
            self.db.update_note_error(note_id, str(e))
        finally:
            self.after(0, self.finish_processing)

    def show_detail(self, note):
        self.note_detail.show_note(note)

    def new_note_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.process_new_note(file_path)

    def new_note_webcam(self):
        # Open webcam window
        WebcamWindow(self, self.process_new_note)

    def process_new_note(self, image_path):
        if not self.ai:
            print("AI Engine not ready yet!")
            return

        # 1. Create pending note in DB
        note_id = self.db.add_note(raw_text="Procesando imagen...", status="pending")
        self.refresh_notes()

        # 2. Start processing thread
        self.status_bar.grid()
        self.status_bar.start()
        
        threading.Thread(target=self.ai_pipeline, args=(note_id, image_path), daemon=True).start()

    def ai_pipeline(self, note_id, image_path):
        try:
            # Extract Text
            print(f"Extracting text from {image_path}...")
            extracted_text = self.ai.extract_text_from_image(image_path)
            self.db.update_note_text(note_id, extracted_text)
            
            # Analyze Text
            print("Analyzing text...")
            analysis = self.ai.analyze_text(extracted_text)
            
            # Update DB
            # We need to update raw_text too, but our DBManager.update_note_analysis only updates analysis.
            # I'll assume for now we just update analysis and maybe I should have added a method to update raw_text.
            # Let's do a raw SQL update here or modify DBManager. 
            # Since I can't easily modify DBManager from here without re-writing it, I'll use a private access or just update analysis.
            # Wait, I should fix DBManager to update raw_text too.
            # For now, I will just update the analysis. The raw_text in DB will remain "Procesando imagen..." which is bad.
            # I will quickly patch DBManager in the next step if needed, or just use a direct query if I was lazy, but I should be clean.
            # Actually, I can just call a new method I'll add to DBManager, or modify the existing one.
            # Let's assume I'll fix DBManager.
            
            self.db.update_note_analysis(note_id, analysis)
            
            # Also update raw_text? 
            # I'll add a method to DBManager in a separate tool call if I can, or just overwrite the file now.
            # Actually, I'll just use a direct SQL execution here since I have access to the db file? No, that's bad practice.
            # I will rely on `update_note_analysis` for now and maybe the raw_text stays as placeholder.
            # Wait, the user wants "raw_text (texto extraído)".
            # I MUST update raw_text.
            
            # Let's manually update raw_text using a helper or just re-instantiate a cursor here? 
            # No, I should use the DBManager.
            # I will modify DBManager.py in a subsequent step to add `update_note_text`.
            
            # For now, I will proceed.
            
        except Exception as e:
            print(f"Pipeline Error: {e}")
            self.db.update_note_error(note_id, str(e))
        finally:
            # Update UI on main thread
            self.after(0, self.finish_processing)

    def finish_processing(self):
        self.status_bar.stop()
        self.status_bar.grid_remove()
        self.refresh_notes()

if __name__ == "__main__":
    app = PaperToPlanApp()
    app.mainloop()
