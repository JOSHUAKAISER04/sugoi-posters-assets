import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageRenamer:
    def __init__(self, root, image_paths):
        self.root = root
        self.image_paths = image_paths
        self.index = 0

        self.root.title("Renombrador de Imágenes")
        self.root.geometry("600x600")

        # Label para mostrar la imagen
        self.label = tk.Label(self.root)
        self.label.pack()

        # Campo de texto para escribir el nuevo nombre
        self.entry = tk.Entry(self.root, width=40, font=("Arial", 14))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.rename_image)
        self.entry.bind("<Tab>", self.skip_image)  # Tab para saltar imagen

        # Texto de estado
        self.status = tk.Label(self.root, text="", font=("Arial", 10))
        self.status.pack()

        self.show_image()

    def show_image(self):
        if self.index >= len(self.image_paths):
            self.label.config(image="", text="¡Todas las imágenes fueron procesadas!")
            self.entry.pack_forget()
            self.status.config(text="")
            return

        path = self.image_paths[self.index]
        img = Image.open(path)
        img.thumbnail((500, 500))
        photo = ImageTk.PhotoImage(img)

        self.label.config(image=photo)
        self.label.image = photo

        base = os.path.basename(path)
        self.status.config(
            text=f"{self.index + 1}/{len(self.image_paths)}: {base}  |  [Enter = Renombrar, Tab = Saltar]"
        )

        self.entry.delete(0, tk.END)
        self.entry.focus_force()

    def rename_image(self, event):
        new_name = self.entry.get().strip()
        if not new_name:
            return "break"  # evita que tkinter agregue tabulaciones o cambie foco

        old_path = self.image_paths[self.index]
        folder = os.path.dirname(old_path)
        ext = os.path.splitext(old_path)[1]
        new_path = os.path.join(folder, new_name + ext)

        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(folder, f"{new_name}_{counter}{ext}")
            counter += 1

        try:
            os.rename(old_path, new_path)
        except Exception as e:
            print(f"Error al renombrar {old_path}: {e}")

        self.image_paths[self.index] = new_path
        self.index += 1
        self.show_image()
        return "break"

    def skip_image(self, event):
        """Salta la imagen actual sin renombrar."""
        self.index += 1
        self.show_image()
        return "break"  # evita que Tab cambie el foco

def get_image_files(base_path):
    exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    image_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(exts):
                image_files.append(os.path.join(root, file))
    return image_files

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    folder_selected = filedialog.askdirectory(title="Selecciona la carpeta base con imágenes")

    if folder_selected:
        images = get_image_files(folder_selected)
        if images:
            root.deiconify()
            app = ImageRenamer(root, images)
            root.mainloop()
        else:
            print("No se encontraron imágenes en la carpeta seleccionada.")
    else:
        print("No se seleccionó carpeta.")
