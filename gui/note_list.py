import customtkinter as ctk
from typing import List, Dict, Any, Callable
import json

class NoteCard(ctk.CTkFrame):
    def __init__(self, master, note: Dict[str, Any], on_click: Callable):
        super().__init__(master, corner_radius=10, fg_color="gray20", border_width=1, border_color="gray30")
        self.note = note
        self.on_click = on_click

        # Bind click events to the frame and its children
        self.bind("<Button-1>", self.clicked)
        
        analysis = note.get('ai_analysis', {})
        title = analysis.get('title', 'Sin Título') if analysis else 'Procesando...'
        time_est = note.get('implementation_time', 'Unknown')
        if not time_est:
            time_est = 'Unknown'
        
        self.title_lbl = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        self.title_lbl.pack(padx=10, pady=(10, 5), anchor="w")
        self.title_lbl.bind("<Button-1>", self.clicked)

        self.time_lbl = ctk.CTkLabel(self, text=time_est, text_color="gray70", font=ctk.CTkFont(size=12))
        self.time_lbl.pack(padx=10, pady=(0, 10), anchor="w")
        self.time_lbl.bind("<Button-1>", self.clicked)

        status = note.get('status', 'pending')
        if status == 'pending':
            self.configure(border_color="orange")
        elif status == 'processed':
            self.configure(border_color="green")
        elif status == 'error':
            self.configure(border_color="red")
            self.title_lbl.configure(text_color="red")

    def clicked(self, event=None):
        self.on_click(self.note)

class NoteList(ctk.CTkScrollableFrame):
    def __init__(self, master, on_note_select: Callable):
        super().__init__(master, label_text="Mis Notas")
        self.on_note_select = on_note_select
        self.cards = []

    def update_notes(self, notes: List[Dict[str, Any]]):
        # Clear existing
        for card in self.cards:
            card.destroy()
        self.cards = []

        for note in notes:
            card = NoteCard(self, note, self.on_note_select)
            card.pack(fill="x", padx=10, pady=5)
            self.cards.append(card)
