import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path
import gzip

# ------------------ CATEGORÍAS ------------------
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
                while dest.exists():
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

def comprimir_archivo(ruta_archivo):
    archivo = Path(ruta_archivo)
    archivo_gz = Path(ruta_archivo + ".gz")
    if not archivo.exists():
        raise FileNotFoundError(f"La carpeta '{ruta_archivo}' no existe.")
    with open(archivo, 'rb') as f_in:
        with gzip.open(archivo_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

# ------------------ CLASE PRINCIPAL ------------------
class FolderWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FolderWizard - Organizador de Archivos")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#ECE9D8")
        self.folder_path = None

        # Frames por paso
        self.frame_welcome = tk.Frame(root, bg="#ECE9D8")
        self.frame_select = tk.Frame(root, bg="#ECE9D8")
        self.frame_actions = tk.Frame(root, bg="#ECE9D8")

        for frame in (self.frame_welcome, self.frame_select, self.frame_actions):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_welcome_frame()
        self.create_select_frame()
        self.create_actions_frame()

        self.show_frame(self.frame_welcome)

    def show_frame(self, frame):
        frame.tkraise()

    # ------------------ Paso 1: Bienvenida ------------------
    def create_welcome_frame(self):
        frame = self.frame_welcome

        # Barra superior
        top_bar = tk.Frame(frame, bg="#245EDC", height=35)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="FolderWizard Setup", fg="white", bg="#245EDC",
                 font=("Tahoma", 11, "bold")).place(x=10, y=7)

        # Panel central
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel logo
        image_frame = tk.Frame(content_frame, width=140, height=220, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)
        try:
            img = tk.PhotoImage(file="logo.png")
            lbl_img = tk.Label(image_frame, image=img, bg="#D4D0C8")
            lbl_img.image = img
            lbl_img.pack(expand=True)
        except Exception:
            tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold")).pack(expand=True)

        # Texto
        text_frame = tk.Frame(content_frame, bg="#ECE9D8")
        text_frame.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(text_frame, text="Bienvenido a FolderWizard",
                 font=("Tahoma", 14, "bold"), bg="#ECE9D8").pack(anchor="nw")
        tk.Label(text_frame, text="Este asistente organiza archivos en carpetas según su tipo.\n"
                                  "Selecciona una carpeta y presiona 'Organizar Archivos'.",
                 justify="left", font=("Tahoma", 10), bg="#ECE9D8", wraplength=380).pack(anchor="nw", pady=10)

        # Botones
        btn_frame = tk.Frame(frame, bg="#D4D0C8", relief="raised", borderwidth=2)
        btn_frame.pack(side="bottom", fill="x")
        tk.Button(btn_frame, text="Salir", width=12, command=self.root.quit, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Siguiente", width=12, command=lambda: self.show_frame(self.frame_select), bg="#ECE9D8").pack(side="right", padx=10, pady=10)

    # ------------------ Paso 2: Selección de carpeta ------------------
    def create_select_frame(self):
        frame = self.frame_select

        top_bar = tk.Frame(frame, bg="#245EDC", height=35)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="FolderWizard Setup", fg="white", bg="#245EDC",
                 font=("Tahoma", 11, "bold")).place(x=10, y=7)

        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        image_frame = tk.Frame(content_frame, width=140, height=220, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)
        try:
            img = tk.PhotoImage(file="logo.png")
            lbl_img = tk.Label(image_frame, image=img, bg="#D4D0C8")
            lbl_img.image = img
            lbl_img.pack(expand=True)
        except Exception:
            tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold")).pack(expand=True)

        text_frame = tk.Frame(content_frame, bg="#ECE9D8")
        text_frame.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(text_frame, text="Selecciona la carpeta que deseas organizar",
                 font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(anchor="nw", pady=10)
        self.folder_label = tk.Label(text_frame, text="No hay carpeta seleccionada", bg="#ECE9D8")
        self.folder_label.pack(anchor="nw", pady=10)
        # Botones
        btn_frame = tk.Frame(frame, bg="#D4D0C8", relief="raised", borderwidth=2)
        btn_frame.pack(side="bottom", fill="x")
        tk.Button(btn_frame, text="Volver", width=12, command=lambda: self.show_frame(self.frame_welcome), bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Salir", width=12, command=self.root.quit, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Seleccionar Carpeta", width=18, command=self.select_folder, bg="#ECE9D8").pack(side="right", padx=10, pady=10)
        tk.Button(btn_frame, text="Siguiente", width=12, command=lambda: self.show_frame(self.frame_actions), bg="#ECE9D8").pack(side="right", padx=10, pady=10)

    # ------------------ Paso 3: Funciones ------------------
    def create_actions_frame(self):
        frame = self.frame_actions

        top_bar = tk.Frame(frame, bg="#245EDC", height=35)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="FolderWizard Setup", fg="white", bg="#245EDC",
                 font=("Tahoma", 11, "bold")).place(x=10, y=7)

        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        image_frame = tk.Frame(content_frame, width=140, height=220, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)
        try:
            img = tk.PhotoImage(file="logo.png")
            lbl_img = tk.Label(image_frame, image=img, bg="#D4D0C8")
            lbl_img.image = img
            lbl_img.pack(expand=True)
        except Exception:
            tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold")).pack(expand=True)

        text_frame = tk.Frame(content_frame, bg="#ECE9D8")
        text_frame.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(text_frame, text="Selecciona una acción a realizar",
                 font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(anchor="nw", pady=10)

        # Botones de acción
        tk.Button(text_frame, text="Organizar Archivos", width=20, command=self.organize_files, bg="#ECE9D8").pack(pady=5)
        tk.Button(text_frame, text="Comprimir Archivo", width=20, command=self.comprimir_carpeta, bg="#ECE9D8").pack(pady=5)
        tk.Button(text_frame, text="Contar Archivos", width=20, command=self.count_files, bg="#ECE9D8").pack(pady=5)
        tk.Button(text_frame, text="Contar Carpetas", width=20, command=self.contar_carpetas, bg="#ECE9D8").pack(pady=5)

        btn_frame = tk.Frame(frame, bg="#D4D0C8", relief="raised", borderwidth=2)
        btn_frame.pack(side="bottom", fill="x")
        tk.Button(btn_frame, text="Volver", width=12, command=lambda: self.show_frame(self.frame_select), bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Salir", width=12, command=self.root.quit, bg="#ECE9D8").pack(side="left", padx=10, pady=10)

    # ------------------ MÉTODOS ------------------
    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=self.folder_path)
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

    def comprimir_carpeta(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo.")
            return
        try:
            comprimir_archivo(self.folder_path)
            messagebox.showinfo("Éxito", "Archivo comprimido correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def count_files(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        num = len([f for f in Path(self.folder_path).iterdir() if f.is_file()])
        messagebox.showinfo("Archivos Encontrados", f"Hay {num} archivos en esta carpeta.")

    def contar_carpetas(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        num = len([f for f in Path(self.folder_path).iterdir() if f.is_dir()])
        messagebox.showinfo("Carpetas Encontradas", f"Hay {num} carpetas en esta carpeta.")

# ------------------ EJECUCIÓN ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderWizardApp(root)
    root.mainloop()
