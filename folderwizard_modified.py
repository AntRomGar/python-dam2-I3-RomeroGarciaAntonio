import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path

# ------------------ CATEGORÍAS DE ORGANIZACIÓN ------------------
CATEGORIES = {
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'Música': ['.mp3', '.wav', '.flac', '.aac'],
    'Archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Otros': []
}

# ------------------ FUNCIONES ------------------
def organize_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe.")

    for category in CATEGORIES:
        (folder / category).mkdir(exist_ok=True)

    for file in folder.iterdir():
        if not file.is_file():
            continue
        if file.name.startswith(".") or file.name.lower() == "desktop.ini":
            continue

        moved = False
        for category, extensions in CATEGORIES.items():
            if file.suffix.lower() in extensions:
                dest = folder / category / file.name
                counter = 1
                while dest.exists():  # Evitar sobreescribir archivos
                    dest = folder / f"{file.stem}_copy{counter}{file.suffix}"
                    counter += 1
                shutil.move(str(file), str(dest))
                moved = True
                break

        if not moved:
            dest = folder / 'Otros' / file.name
            counter = 1
            while dest.exists():
                dest = folder / f"{file.stem}_copy{counter}{file.suffix}"
                counter += 1
            shutil.move(str(file), str(dest))

    return "¡Organización completada!"

# ------------------ CLASE PRINCIPAL ------------------
class FolderWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FolderWizard - Organizador de Archivos")
        self.root.geometry("600x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#ECE9D8")

        # ---------- BARRA AZUL SUPERIOR ----------
        top_bar = tk.Frame(root, bg="#245EDC", height=35)
        top_bar.pack(fill="x")
        title_top = tk.Label(top_bar, text="FolderWizard Setup", fg="white", bg="#245EDC",
                             font=("Tahoma", 11, "bold"))
        title_top.place(x=10, y=7)

        # ---------- FRAME CENTRAL ----------
        content_frame = tk.Frame(root, bg="#ECE9D8")
        content_frame.pack(fill="both", padx=10, pady=10, expand=True)

        # Panel de imagen estilo XP (vertical)
        image_frame = tk.Frame(content_frame, width=140, height=220, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)

        # Cargar imagen (solo PNG/GIF)
        try:
            img = tk.PhotoImage(file="logo.png")  # Cambia 'logo.png' por tu archivo
            img_label = tk.Label(image_frame, image=img, bg="#D4D0C8")
            img_label.image = img  # Mantener referencia
            img_label.pack(expand=True)
        except Exception as e:
            img_label = tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold"))
            img_label.pack(expand=True)

        # Panel de texto
        text_frame = tk.Frame(content_frame, bg="#ECE9D8")
        text_frame.pack(side="left", fill="both", expand=True, padx=10)

        title_label = tk.Label(text_frame, text="Bienvenido a FolderWizard",
                               font=("Tahoma", 14, "bold"), bg="#ECE9D8", fg="black")
        title_label.pack(anchor="nw")

        descr_label = tk.Label(
            text_frame,
            text="Este asistente organiza archivos en carpetas según su tipo.\n"
                 "Selecciona una carpeta y presiona 'Organizar Archivos'.\n"
                 "Ideal para mantener tus documentos ordenados automáticamente.",
            justify="left",
            font=("Tahoma", 10),
            bg="#ECE9D8",
            fg="black",
            wraplength=380
        )
        descr_label.pack(anchor="nw", pady=10)

        # ---------- BARRA INFERIOR (Botones) ----------
        button_frame = tk.Frame(root, bg="#D4D0C8", relief="raised", borderwidth=2)
        button_frame.pack(side="bottom", fill="x")

        exit_button = tk.Button(button_frame, text="Salir", width=12,
                                command=root.quit, relief="raised", bg="#ECE9D8")
        exit_button.pack(side="left", padx=10, pady=10)

        self.organize_button = tk.Button(button_frame, text="Organizar Archivos", width=18,
                                         command=self.organize_files, relief="raised", bg="#ECE9D8")
        self.organize_button.pack(side="right", padx=10)

        self.select_button = tk.Button(button_frame, text="Seleccionar Carpeta", width=18,
                                       command=self.select_folder, relief="raised", bg="#ECE9D8")
        self.select_button.pack(side="right")

        self.folder_path = None

    # ------------------ MÉTODOS ------------------
    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("Carpeta seleccionada", f"Has seleccionado: {self.folder_path}")

    def organize_files(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        try:
            result = organize_folder(self.folder_path)
            messagebox.showinfo("Éxito", result)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ------------------ EJECUCIÓN ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderWizardApp(root)
    root.mainloop()
