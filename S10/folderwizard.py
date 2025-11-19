import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path

# Categorías de organización
CATEGORIES = {
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'Música': ['.mp3', '.wav', '.flac', '.aac'],
    'Archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Otros': []
}

def organize_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe.")

    # Crear carpetas de categorías
    for category in CATEGORIES:
        (folder / category).mkdir(exist_ok=True)

    # Recorrer archivos
    for file in folder.iterdir():

        # Ignorar carpetas, archivos ocultos y desktop.ini
        if not file.is_file():
            continue
        if file.name.startswith(".") or file.name.lower() == "desktop.ini":
            continue

        moved = False

        for category, extensions in CATEGORIES.items():
            if file.suffix.lower() in extensions:
                dest = folder / category / file.name
                
                # Evitar sobrescrituras
                if dest.exists():
                    dest = dest.with_stem(dest.stem + "_copy")

                shutil.move(str(file), str(dest))
                moved = True
                break

        if not moved:
            dest = folder / 'Otros' / file.name
            if dest.exists():
                dest = dest.with_stem(dest.stem + "_copy")
            shutil.move(str(file), str(dest))

    return "¡Organización completada!"


class FolderWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FolderWizard - Organizador de Archivos")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="Selecciona una carpeta para organizar:", font=("Arial", 12))
        self.label.pack(pady=20)

        self.select_button = tk.Button(root, text="Seleccionar Carpeta", command=self.select_folder)
        self.select_button.pack(pady=10)

        self.organize_button = tk.Button(root, text="Organizar Archivos", command=self.organize_files)
        self.organize_button.pack(pady=10)

        self.folder_path = None

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


if __name__ == "__main__":
    root = tk.Tk()
    app = FolderWizardApp(root)
    root.mainloop()
