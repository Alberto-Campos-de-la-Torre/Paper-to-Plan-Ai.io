import customtkinter as ctk
from typing import List, Dict, Any, Callable
from gui.note_list import NoteCard

class KanbanColumn(ctk.CTkFrame):
    def __init__(self, master, title: str, status_filter: str, on_note_click: Callable, on_drop: Callable):
        super().__init__(master, corner_radius=10, fg_color="gray15")
        self.title = title
        self.status_filter = status_filter
        self.on_note_click = on_note_click
        self.on_drop = on_drop
        self.cards = []

        # Header
        self.header = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        self.header.pack(pady=10, padx=10, fill="x")

        # Scrollable area for cards
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(expand=True, fill="both", padx=5, pady=5)

    def add_note(self, note: Dict[str, Any]):
        card = NoteCard(self.scroll_frame, note, self.on_note_click)
        card.pack(fill="x", padx=5, pady=5)
        
        # Context menu for moving notes (simulated drag & drop)
        card.bind("<Button-3>", lambda event, n=note: self.show_context_menu(event, n))
        self.cards.append(card)

    def clear(self):
        for card in self.cards:
            card.destroy()
        self.cards = []

    def show_context_menu(self, event, note):
        # This is a hacky way to show a context menu in CTk
        # We'll use a Toplevel window positioned at the cursor
        menu = ctk.CTkToplevel(self)
        menu.geometry(f"200x150+{event.x_root}+{event.y_root}")
        menu.overrideredirect(True)
        
        label = ctk.CTkLabel(menu, text="Mover a:", font=ctk.CTkFont(weight="bold"))
        label.pack(pady=5)

        options = ["Corto Plazo", "Medio Plazo", "Largo Plazo"]
        for opt in options:
            if opt != self.title:
                btn = ctk.CTkButton(menu, text=opt, command=lambda o=opt: self.move_note(menu, note, o))
                btn.pack(pady=2, padx=10, fill="x")
        
        close = ctk.CTkButton(menu, text="Cancelar", fg_color="gray", command=menu.destroy)
        close.pack(pady=5, padx=10, fill="x")
        
        # Auto close when losing focus (imperfect but works)
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_force()

    def move_note(self, menu, note, target_column):
        menu.destroy()
        self.on_drop(note, target_column)


class KanbanBoard(ctk.CTkFrame):
    def __init__(self, master, on_note_click: Callable, on_move_note: Callable):
        super().__init__(master, fg_color="transparent")
        self.on_note_click = on_note_click
        self.on_move_note = on_move_note
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.col_short = KanbanColumn(self, "Corto Plazo", "Short Term", on_note_click, self.handle_drop)
        self.col_short.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.col_medium = KanbanColumn(self, "Medio Plazo", "Medium Term", on_note_click, self.handle_drop)
        self.col_medium.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.col_long = KanbanColumn(self, "Largo Plazo", "Long Term", on_note_click, self.handle_drop)
        self.col_long.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    def update_notes(self, notes: List[Dict[str, Any]]):
        self.col_short.clear()
        self.col_medium.clear()
        self.col_long.clear()

        for note in notes:
            time_est = note.get('implementation_time', 'Unknown')
            if "Corto" in time_est or "Short" in time_est:
                self.col_short.add_note(note)
            elif "Medio" in time_est or "Medium" in time_est:
                self.col_medium.add_note(note)
            elif "Largo" in time_est or "Long" in time_est:
                self.col_long.add_note(note)
            else:
                # Default to short if unknown or put in a separate "Unsorted" list?
                # For now, let's put in Short
                self.col_short.add_note(note)

    def handle_drop(self, note, target_column_title):
        # Map title to value
        new_time = ""
        if target_column_title == "Corto Plazo":
            new_time = "Corto Plazo"
        elif target_column_title == "Medio Plazo":
            new_time = "Medio Plazo"
        elif target_column_title == "Largo Plazo":
            new_time = "Largo Plazo"
        
        self.on_move_note(note['id'], new_time)
