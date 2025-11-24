import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import time
import os

# Directory for captures
CAPTURES_DIR = "captures"

# Ensure captures directory exists
os.makedirs(CAPTURES_DIR, exist_ok=True)

class WebcamWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_capture_callback):
        super().__init__(parent)
        self.on_capture_callback = on_capture_callback
        self.title("Capturar Nota")
        self.geometry("800x600")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.video_label = ctk.CTkLabel(self, text="Iniciando cámara...")
        self.video_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.capture_btn = ctk.CTkButton(self, text="Capturar Foto", command=self.capture_image, fg_color="green")
        self.capture_btn.grid(row=1, column=0, padx=20, pady=20)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        
        if not self.cap.isOpened():
            self.video_label.configure(text="No se encontró cámara web.")
            self.capture_btn.configure(state="disabled")
            self.running = False
        else:
            self.update_feed()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_feed(self):
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert color from BGR to RGB
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                # Create CTkImage
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
                self.video_label.configure(image=ctk_img, text="")
                self.current_frame = frame
            
            self.after(10, self.update_feed)

    def capture_image(self):
        if hasattr(self, 'current_frame'):
            timestamp = int(time.time())
            filename = f"capture_{timestamp}.jpg"
            file_path = os.path.join(CAPTURES_DIR, filename)
            cv2.imwrite(file_path, self.current_frame)
            self.on_capture_callback(os.path.abspath(file_path))
            self.on_close()

    def on_close(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()
