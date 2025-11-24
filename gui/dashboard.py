import customtkinter as ctk
from typing import List, Dict, Any
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use("TkAgg")

class Dashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Charts containers
        self.chart1_frame = ctk.CTkFrame(self)
        self.chart1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.chart2_frame = ctk.CTkFrame(self)
        self.chart2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.chart3_frame = ctk.CTkFrame(self)
        self.chart3_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def update_stats(self, notes: List[Dict[str, Any]]):
        # Clear previous charts
        for widget in self.chart1_frame.winfo_children(): widget.destroy()
        for widget in self.chart2_frame.winfo_children(): widget.destroy()
        for widget in self.chart3_frame.winfo_children(): widget.destroy()

        if not notes:
            ctk.CTkLabel(self.chart1_frame, text="No Data").pack(expand=True)
            return

        # 1. Status Pie Chart
        status_counts = {"pending": 0, "processed": 0, "error": 0}
        for note in notes:
            s = note.get('status', 'pending')
            status_counts[s] = status_counts.get(s, 0) + 1
        
        # Filter out zero values to avoid label overlap
        labels = []
        sizes = []
        colors = []
        color_map = {'pending': '#FFA500', 'processed': '#008000', 'error': '#FF0000'}
        
        for status, count in status_counts.items():
            if count > 0:
                labels.append(status)
                sizes.append(count)
                colors.append(color_map.get(status, '#808080'))
        
        fig1 = Figure(figsize=(5, 4), facecolor='#2b2b2b')
        ax1 = fig1.add_subplot(111)
        
        if sizes:
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
                    colors=colors, textprops={'color':"w"})
        else:
            ax1.text(0.5, 0.5, "No Data", ha='center', va='center', color='white')
            
        ax1.set_title("Project Status", color='white')
        
        canvas1 = FigureCanvasTkAgg(fig1, master=self.chart1_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # 2. Implementation Time Bar Chart
        time_counts = {"Corto Plazo": 0, "Medio Plazo": 0, "Largo Plazo": 0}
        for note in notes:
            t = note.get('implementation_time', 'Unknown')
            if not t: t = 'Unknown'
            
            if "Corto" in t or "Short" in t: time_counts["Corto Plazo"] += 1
            elif "Medio" in t or "Medium" in t: time_counts["Medio Plazo"] += 1
            elif "Largo" in t or "Long" in t: time_counts["Largo Plazo"] += 1
            
        fig2 = Figure(figsize=(5, 4), facecolor='#2b2b2b')
        ax2 = fig2.add_subplot(111)
        ax2.bar(time_counts.keys(), time_counts.values(), color=['#4CAF50', '#2196F3', '#9C27B0'])
        ax2.set_title("Implementation Time", color='white')
        ax2.tick_params(colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['top'].set_color('#2b2b2b')
        ax2.spines['right'].set_color('#2b2b2b')
        
        canvas2 = FigureCanvasTkAgg(fig2, master=self.chart2_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        # 3. Feasibility Score Histogram
        scores = []
        for note in notes:
            analysis = note.get('ai_analysis', {})
            if analysis:
                try:
                    s = int(analysis.get('feasibility_score', 0))
                    scores.append(s)
                except: pass
        
        fig3 = Figure(figsize=(10, 3), facecolor='#2b2b2b')
        ax3 = fig3.add_subplot(111)
        if scores:
            ax3.hist(scores, bins=10, range=(0, 100), color='#FFC107', edgecolor='black')
        ax3.set_title("Feasibility Score Distribution", color='white')
        ax3.tick_params(colors='white')
        ax3.spines['bottom'].set_color('white')
        ax3.spines['left'].set_color('white')
        ax3.spines['top'].set_color('#2b2b2b')
        ax3.spines['right'].set_color('#2b2b2b')

        canvas3 = FigureCanvasTkAgg(fig3, master=self.chart3_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True)
