
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌈 Hilal Image Processor")
        self.root.configure(bg="#f0f8ff")  # Latar belakang cheerful

        self.original_image = None
        self.processed_image = None
        self.camera_active = False
        self.cap = None
        self.show_grayscale = False
        self.apply_equalization = False
        self.max_display_size = (400, 400)

        # Frame untuk tombol
        self.button_frame = tk.Frame(root, bg="#caf0f8")
        self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        btn_opts = {
            "bg": "#00b4d8", "fg": "white", "font": ("Segoe UI", 10, "bold"),
            "padx": 10, "pady": 6, "activebackground": "#0077b6", "activeforeground": "white"
        }

        self.load_button = tk.Button(self.button_frame, text="📂 Load Image", command=self.load_image, **btn_opts)
        self.load_button.grid(row=0, column=0, padx=5)

        self.camera_button = tk.Button(self.button_frame, text="📷 Start Camera", command=self.toggle_camera, **btn_opts)
        self.camera_button.grid(row=0, column=1, padx=5)

        self.filter_button = tk.Button(self.button_frame, text="🌑 Greyscale: OFF", command=self.toggle_greyscale, **btn_opts)
        self.filter_button.grid(row=0, column=2, padx=5)

        self.equalize_button = tk.Button(self.button_frame, text="📊 Equalize: OFF", command=self.toggle_equalization, **btn_opts)
        self.equalize_button.grid(row=0, column=3, padx=5)

        self.save_button = tk.Button(self.button_frame, text="💾 Save Image", command=self.save_image, **btn_opts)
        self.save_button.grid(row=0, column=4, padx=5)

        # Frame utama landscape
        self.content_frame = tk.Frame(root, bg="#f0f8ff")
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.original_frame = tk.Frame(self.content_frame, bg="#ade8f4")
        self.original_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.processed_frame = tk.Frame(self.content_frame, bg="#ade8f4")
        self.processed_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.histogram_frame = tk.Frame(self.content_frame, bg="#ade8f4")
        self.histogram_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.original_label = tk.Label(self.original_frame, text="Original Image", bg="#ade8f4", font=("Segoe UI", 10, "bold"))
        self.original_label.pack()
        self.original_canvas = tk.Label(self.original_frame, bg="#f0f8ff")
        self.original_canvas.pack()

        self.processed_label = tk.Label(self.processed_frame, text="Processed Image", bg="#ade8f4", font=("Segoe UI", 10, "bold"))
        self.processed_label.pack()
        self.processed_canvas = tk.Label(self.processed_frame, bg="#f0f8ff")
        self.processed_canvas.pack()

        self.histogram_label = tk.Label(self.histogram_frame, text="Histogram", bg="#ade8f4", font=("Segoe UI", 10, "bold"))
        self.histogram_label.pack()
        self.histogram_canvas = None

    def resize_image(self, image):
        h, w = image.shape[:2]
        ratio = min(self.max_display_size[0]/w, self.max_display_size[1]/h)
        new_size = (int(w*ratio), int(h*ratio))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.show_grayscale = False
                self.apply_equalization = False
                self.filter_button.config(text="🌑 Greyscale: OFF")
                self.equalize_button.config(text="📊 Equalize: OFF")
                self.update_processed_image()
            else:
                messagebox.showerror("Error", "Failed to load image")

    def display_images(self):
        if self.original_image is not None:
            orig_img = self.resize_image(self.original_image)
            orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
            orig_img = Image.fromarray(orig_img)
            orig_img = ImageTk.PhotoImage(orig_img)
            self.original_canvas.configure(image=orig_img)
            self.original_canvas.image = orig_img

        if self.processed_image is not None:
            proc_img = self.resize_image(self.processed_image)
            if len(proc_img.shape) == 2:
                proc_img = Image.fromarray(proc_img)
            else:
                proc_img = cv2.cvtColor(proc_img, cv2.COLOR_BGR2RGB)
                proc_img = Image.fromarray(proc_img)
            proc_img = ImageTk.PhotoImage(proc_img)
            self.processed_canvas.configure(image=proc_img)
            self.processed_canvas.image = proc_img

    def display_histogram(self):
        if self.processed_image is not None:
            if self.histogram_canvas:
                self.histogram_canvas.get_tk_widget().destroy()

            fig, ax = plt.subplots(figsize=(4, 3))

            if len(self.processed_image.shape) == 2:
                ax.hist(self.processed_image.ravel(), bins=256, color='gray')
            else:
                color = ('b', 'g', 'r')
                for i, col in enumerate(color):
                    hist = cv2.calcHist([self.processed_image], [i], None, [256], [0, 256])
                    ax.plot(hist, color=col)
            ax.set_xlim([0, 256])
            ax.set_title('Histogram')

            self.histogram_canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
            self.histogram_canvas.draw()
            self.histogram_canvas.get_tk_widget().pack()

    def toggle_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera")
                return
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_active = True
            self.camera_button.config(text="🛑 Stop Camera")
            self.update_camera()
        else:
            self.camera_active = False
            if self.cap:
                self.cap.release()
            self.camera_button.config(text="📷 Start Camera")

    def update_camera(self):
        if self.camera_active and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.original_image = frame
                self.update_processed_image()
                self.root.after(30, self.update_camera)
            else:
                self.toggle_camera()
                messagebox.showerror("Error", "Failed to capture frame")

    def toggle_greyscale(self):
        self.show_grayscale = not self.show_grayscale
        status = "ON" if self.show_grayscale else "OFF"
        self.filter_button.config(text=f"🌑 Greyscale: {status}")
        self.update_processed_image()

    def toggle_equalization(self):
        self.apply_equalization = not self.apply_equalization
        status = "ON" if self.apply_equalization else "OFF"
        self.equalize_button.config(text=f"📊 Equalize: {status}")
        self.update_processed_image()

    def update_processed_image(self):
        if self.original_image is not None:
            processed = self.original_image.copy()
            if self.show_grayscale:
                processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            if self.apply_equalization:
                if len(processed.shape) == 2:
                    processed = cv2.equalizeHist(processed)
                else:
                    ycrcb = cv2.cvtColor(processed, cv2.COLOR_BGR2YCrCb)
                    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
                    processed = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
            self.processed_image = processed
            self.display_images()
            self.display_histogram()

    def save_image(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG files", "*.png"),
                                                               ("JPEG files", "*.jpg"),
                                                               ("All files", "*.*")])
            if file_path:
                if len(self.processed_image.shape) == 2:
                    cv2.imwrite(file_path, self.processed_image)
                else:
                    cv2.imwrite(file_path, cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Success", "Image saved successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
