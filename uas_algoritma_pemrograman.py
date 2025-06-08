import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class HilalObservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengamatan Hilal")
        self.root.geometry("1366x768")
        
        # Variabel untuk menyimpan gambar
        self.original_image = None
        self.processed_image = None
        self.stacked_images = []
        self.stacked_result = None
        
        # Frame untuk gambar
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)
        
        # Label untuk gambar asli
        self.original_label = tk.Label(self.image_frame)
        self.original_label.grid(row=0, column=0, padx=10)
        tk.Label(self.image_frame, text="Gambar Asli").grid(row=1, column=0)
        
        # Label untuk gambar hasil proses
        self.processed_label = tk.Label(self.image_frame)
        self.processed_label.grid(row=0, column=1, padx=10)
        tk.Label(self.image_frame, text="Hasil Proses").grid(row=1, column=1)
        
        # Frame untuk tombol menu
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=10)
        
        # Tombol untuk membuka gambar
        tk.Button(self.menu_frame, text="Buka Gambar", command=self.open_image).grid(row=0, column=0, padx=5)

        # Tombol untuk membuka kamera
        tk.Button(self.menu_frame, text="Buka Kamera", command=self.open_camera).grid(row=0, column=1, padx=5)
        
        # Tombol untuk greyscale
        tk.Button(self.menu_frame, text="Greyscale", command=self.apply_greyscale).grid(row=0, column=2, padx=5)
        
        # Tombol untuk histogram equalization
        tk.Button(self.menu_frame, text="Histogram Equalize", command=self.apply_histogram_equalization).grid(row=0, column=3, padx=5)
        
        # Tombol untuk menambahkan gambar ke stacking
        tk.Button(self.menu_frame, text="Tambahkan ke Stacking", command=self.add_to_stack).grid(row=0, column=4, padx=5)
        
        # Tombol untuk melakukan stacking
        tk.Button(self.menu_frame, text="Lakukan Stacking", command=self.perform_stacking).grid(row=0, column=5, padx=5)
        
        # Tombol untuk menyimpan hasil
        tk.Button(self.menu_frame, text="Simpan Hasil", command=self.save_result).grid(row=0, column=6, padx=5)

        # content frame
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, expand=True)

        self.original_frame = tk.Frame(self.content_frame)
        self.original_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.processed_frame = tk.Frame(self.content_frame)
        self.processed_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.histogram_frame = tk.Frame(self.content_frame)
        self.histogram_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.original_label = tk.Label(self.original_frame, text="Original Image")
        self.original_label.pack()
        self.original_canvas = tk.Label(self.original_frame)
        self.original_canvas.pack()

        self.processed_label = tk.Label(self.processed_frame, text="Processed Image")
        self.processed_label.pack()
        self.processed_canvas = tk.Label(self.processed_frame)
        self.processed_canvas.pack()

        self.histogram_label = tk.Label(self.histogram_frame, text="Histogram")
        self.histogram_label.pack()
        self.histogram_canvas = None

        self.slider_frame = tk.Frame(self.root)
        self.slider_frame.pack(pady=10)

        r_row = tk.Frame(self.slider_frame)
        r_row.pack(side="left", padx=10)
        tk.Label(r_row, text="R: ").pack(side="left")
        self.r_min = tk.Scale(r_row, from_=0, to=255, orient="horizontal", label="Min", length=150, command=lambda val: self.update_rgb_preview())
        self.r_min.set(0)
        self.r_min.pack(side="left")
        self.r_max = tk.Scale(r_row, from_=0, to=255, orient="horizontal", label="Max", length=150, command=lambda val: self.update_rgb_preview())
        self.r_max.set(255)
        self.r_max.pack(side="left")

        # Baris untuk Green
        g_row = tk.Frame(self.slider_frame)
        g_row.pack(side="left", padx=10)
        tk.Label(g_row, text="G: ").pack(side="left")
        self.g_min = tk.Scale(g_row, from_=0, to=255, orient="horizontal", label="Min", length=150, command=lambda val: self.update_rgb_preview())
        self.g_min.set(0)
        self.g_min.pack(side="left")
        self.g_max = tk.Scale(g_row, from_=0, to=255, orient="horizontal", label="Max", length=150, command=lambda val: self.update_rgb_preview())
        self.g_max.set(255)
        self.g_max.pack(side="left")

        # Baris untuk Blue
        b_row = tk.Frame(self.slider_frame)
        b_row.pack(side="left", padx=10)
        tk.Label(b_row, text="B: ").pack(side="left")
        self.b_min = tk.Scale(b_row, from_=0, to=255, orient="horizontal", label="Min", length=150, command=lambda val: self.update_rgb_preview())
        self.b_min.set(0)
        self.b_min.pack(side="left")
        self.b_max = tk.Scale(b_row, from_=0, to=255, orient="horizontal", label="Max", length=150, command=lambda val: self.update_rgb_preview())
        self.b_max.set(255)
        self.b_max.pack(side="left")
        # Frame untuk informasi
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        # Label informasi
        self.info_label = tk.Label(self.info_frame, text="Tidak ada gambar yang dimuat", fg="red")
        self.info_label.pack()
        
        # Frame untuk daftar gambar stacking
        self.stack_frame = tk.Frame(self.root)
        self.stack_frame.pack(pady=10)
        
        tk.Label(self.stack_frame, text="Daftar Gambar untuk Stacking:").pack()
        self.stack_listbox = tk.Listbox(self.stack_frame, width=80, height=3)
        self.stack_listbox.pack()
        
        # Tombol untuk menghapus dari stacking
        tk.Button(self.stack_frame, text="Hapus Terpilih", command=self.remove_from_stack).pack(pady=5)

    def open_camera(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("Tidak dapat membuka kamera.")

            self.info_label.config(text="Tekan 'q' untuk ambil gambar dari kamera...", fg="blue")
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Gagal mengambil gambar dari kamera.")

                cv2.imshow("Tekan 'q' untuk ambil gambar", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            self.original_image = frame
            self.processed_image = frame.copy()
            self.display_histogram()

            # Tambahkan ke stack langsung
            # self.stacked_images.append(frame.copy())
            # self.stack_listbox.insert(tk.END, f"Gambar {len(self.stacked_images)} - {frame.shape}")
            # self.info_label.config(text="Gambar dari kamera ditambahkan ke stacking", fg="green")

            self.display_images()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka kamera: {str(e)}")
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Pilih Gambar Hilal",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.bmp *.tif"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                # Baca gambar dengan OpenCV
                image = cv2.imread(file_path)
                
                if image is None:
                    raise ValueError("Gagal memuat gambar")
                
                # Simpan gambar asli
                self.original_image = image
                self.processed_image = image.copy()
                
                # Tampilkan gambar
                self.display_images()
                self.display_histogram()
                
                self.info_label.config(text=f"Gambar dimuat: {os.path.basename(file_path)}", fg="green")
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")
    
    def display_images(self):
        if self.original_image is not None:
            # Konversi BGR ke RGB untuk ditampilkan di Tkinter
            original_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB) if len(self.processed_image.shape) == 3 else cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2RGB)
            
            # Resize gambar agar sesuai dengan tampilan
            display_height = 300
            aspect_ratio = original_rgb.shape[1] / original_rgb.shape[0]
            display_width = int(display_height * aspect_ratio)
            
            original_resized = cv2.resize(original_rgb, (display_width, display_height))
            processed_resized = cv2.resize(processed_rgb, (display_width, display_height))
            
            # Konversi ke format ImageTk
            original_img = ImageTk.PhotoImage(image=Image.fromarray(original_resized))
            processed_img = ImageTk.PhotoImage(image=Image.fromarray(processed_resized))
            
            # Update label
            self.original_label.config(image=original_img)
            self.original_label.image = original_img
            
            self.processed_label.config(image=processed_img)
            self.processed_label.image = processed_img
    
    def apply_greyscale(self):
        if self.original_image is not None:
            self.processed_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            self.display_images()
            self.display_histogram()
            self.info_label.config(text="Greyscale diterapkan", fg="blue")
    
    def apply_histogram_equalization(self):
        if self.original_image is not None:
            if len(self.original_image.shape) == 2:  # Jika sudah greyscale
                self.processed_image = cv2.equalizeHist(self.original_image)
            else:  # Jika gambar berwarna
                # Konversi ke YCrCb dan equalize channel Y saja
                ycrcb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2YCrCb)
                channels = list(cv2.split(ycrcb))
                channels[0] = cv2.equalizeHist(channels[0])
                ycrcb = cv2.merge(channels)
                self.processed_image = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
            
            self.display_images()
            self.display_histogram()
        # Postprocessing RGB Range
        b, g, r = cv2.split(self.processed_image)

        r = np.clip(r, self.r_min.get(), self.r_max.get())
        g = np.clip(g, self.g_min.get(), self.g_max.get())
        b = np.clip(b, self.b_min.get(), self.b_max.get())

        r = cv2.normalize(r, None, 0, 255, cv2.NORM_MINMAX)
        g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)
        b = cv2.normalize(b, None, 0, 255, cv2.NORM_MINMAX)

        self.processed_image = cv2.merge([b, g, r])
        
        self.info_label.config(text="Histogram equalization diterapkan", fg="blue")

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
    
    def add_to_stack(self):
        if self.processed_image is not None:
            img = self.processed_image
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            img_resized = cv2.resize(img, (640, 480))
            self.stacked_images.append(img_resized)
            self.stack_listbox.insert(tk.END, f"Gambar {len(self.stacked_images)} - {img_resized.shape}")
            self.info_label.config(text=f"Gambar ditambahkan ke stacking (Total: {len(self.stacked_images)})", fg="blue")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada gambar yang diproses untuk ditambahkan ke stacking")

    
    def remove_from_stack(self):
        selected = self.stack_listbox.curselection()
        if selected:
            index = selected[0]
            self.stack_listbox.delete(index)
            del self.stacked_images[index]
            self.info_label.config(text=f"Gambar dihapus dari stacking (Total: {len(self.stacked_images)})", fg="blue")
    
    def perform_stacking(self):
        if len(self.stacked_images) < 2:
            messagebox.showwarning("Peringatan", "Diperlukan minimal 2 gambar untuk stacking")
            return
        
        try:
            # Konversi semua gambar ke float32 untuk akurasi
            images_float = [img.astype(np.float32) for img in self.stacked_images]
            
            # Rata-rata stacking
            stacked = np.mean(images_float, axis=0)
            
            # Konversi kembali ke uint8
            self.stacked_result = np.uint8(stacked)
            
            # Tampilkan hasil stacking
            self.processed_image = self.stacked_result
            self.display_images()
            self.display_histogram()
            
            self.info_label.config(text=f"Stacking selesai ({len(self.stacked_images)} gambar)", fg="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal melakukan stacking: {str(e)}")
    
    def save_result(self):
        if self.stacked_result is not None:
            file_path = filedialog.asksaveasfilename(
                title="Simpan Hasil Stacking",
                defaultextension=".png",
                filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")))
            
            if file_path:
                try:
                    cv2.imwrite(file_path, self.stacked_result)
                    messagebox.showinfo("Sukses", f"Gambar berhasil disimpan di:\n{file_path}")
                    self.info_label.config(text=f"Hasil disimpan: {os.path.basename(file_path)}", fg="green")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menyimpan gambar: {str(e)}")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada hasil stacking yang tersedia untuk disimpan")


    def update_rgb_preview(self):
        if self.original_image is None:
            return

        img = self.original_image.copy()
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        b, g, r = cv2.split(img)

        r = np.clip(r, self.r_min.get(), self.r_max.get())
        g = np.clip(g, self.g_min.get(), self.g_max.get())
        b = np.clip(b, self.b_min.get(), self.b_max.get())

        r = cv2.normalize(r, None, 0, 255, cv2.NORM_MINMAX)
        g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)
        b = cv2.normalize(b, None, 0, 255, cv2.NORM_MINMAX)

        preview = cv2.merge([b, g, r])
        self.processed_image = preview
        self.display_images()
        self.display_histogram()

if __name__ == "__main__":
    root = tk.Tk()
    app = HilalObservationApp(root)
    root.mainloop()