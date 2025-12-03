import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path
import gzip
from datetime import datetime, timedelta
import os
import subprocess
import sys

# ------------------ CATEGORÍAS DE ARCHIVOS ------------------
# Diccionario que define las carpetas por tipo de archivo.
CATEGORIES = {
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'Música': ['.mp3', '.wav', '.flac', '.aac'],
    'Archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Otros': []  # Archivos que no encajan en ninguna categoría
}

# ------------------ HISTORIAL DE ACCIONES ------------------
# Guarda las últimas acciones realizadas para permitir "deshacer"
ultima_accion = []  # Lista de tuplas (archivo_destino, archivo_original)

# ------------------ FUNCIONES AUXILIARES ------------------
def mover_archivo(origen, destino):
    """
    Mueve un archivo asegurando que no se sobrescriba.
    Si el archivo ya existe, se crea una copia con sufijo _copyX.
    Retorna la ruta final del archivo movido.
    """
    counter = 1
    dest_path = Path(destino)
    while dest_path.exists():
        dest_path = Path(f"{destino.stem}_copy{counter}{destino.suffix}")
        counter += 1
    shutil.move(str(origen), str(dest_path))
    return dest_path

def obtener_archivos_recientes(folder_path, dias=7):
    """
    Devuelve una lista de archivos modificados en los últimos 'dias' días.
    """
    folder = Path(folder_path)
    limite_fecha = datetime.now() - timedelta(days=dias)
    return [f.name for f in folder.iterdir() if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) > limite_fecha]

# ------------------ FUNCIONES PRINCIPALES ------------------
def organize_folder(folder_path):
    """
    Organiza los archivos dentro de la carpeta en subcarpetas según su tipo.
    Guarda las acciones en 'ultima_accion' para poder deshacer.
    """
    global ultima_accion
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe.")
    
    movimientos = []  # Para registrar todos los archivos movidos
    # Crear carpetas si no existen
    for category in CATEGORIES:
        (folder / category).mkdir(exist_ok=True)

    # Iterar archivos y moverlos
    for file in folder.iterdir():
        if not file.is_file() or file.name.startswith('.') or file.name.lower() == "desktop.ini":
            continue
        moved = False
        for category, extensions in CATEGORIES.items():
            if file.suffix.lower() in extensions:
                destino = mover_archivo(file, folder / category / file.name)
                movimientos.append((str(destino), str(file)))  # Guardamos destino y origen
                moved = True
                break
        if not moved:
            destino = mover_archivo(file, folder / 'Otros' / file.name)
            movimientos.append((str(destino), str(file)))
    ultima_accion = movimientos  # Guardar movimientos para deshacer
    return "¡Organización completada!"

def comprimir_archivo(ruta_archivo):
    """
    Comprime un archivo usando gzip. Se crea un archivo .gz
    """
    archivo = Path(ruta_archivo)
    archivo_gz = Path(ruta_archivo + ".gz")
    if not archivo.exists():
        raise FileNotFoundError(f"El archivo '{ruta_archivo}' no existe.")
    with open(archivo, 'rb') as f_in, gzip.open(archivo_gz, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

def deshacer_accion():
    """
    Deshace la última acción registrada en 'ultima_accion'.
    Mueve los archivos de vuelta a su ubicación original.
    """
    global ultima_accion
    if not ultima_accion:
        return "No hay acciones para deshacer."
    for dest, orig in reversed(ultima_accion):
        if Path(dest).exists():
            shutil.move(dest, orig)
    ultima_accion = []
    return "Se deshicieron los cambios de la última acción."

# ------------------ CLASE PRINCIPAL ------------------
class FolderWizardApp:
    """
    Clase principal de la aplicación GUI.
    Contiene tres "pantallas" dentro de la misma ventana:
    1. Bienvenida
    2. Selección de carpeta
    3. Acciones disponibles
    """
    def __init__(self, root):
        self.root = root
        self.root.title("FolderWizard - Organizador de Archivos")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#ECE9D8")
        self.folder_path = None

        # ------------------ FRAMES ------------------
        self.frame_welcome = tk.Frame(root, bg="#ECE9D8")
        self.frame_select = tk.Frame(root, bg="#ECE9D8")
        self.frame_actions = tk.Frame(root, bg="#ECE9D8")
        for frame in (self.frame_welcome, self.frame_select, self.frame_actions):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Crear contenido de cada frame
        self.create_welcome_frame()
        self.create_select_frame()
        self.create_actions_frame()

        # Mostrar pantalla inicial
        self.show_frame(self.frame_welcome)

    def show_frame(self, frame):
        """Muestra un frame y oculta los demás."""
        frame.tkraise()

    # ------------------ CREACIÓN DE FRAMES ------------------
    def create_welcome_frame(self):
        """Frame de bienvenida con explicación de la aplicación."""
        frame = self.frame_welcome
        self._crear_top_bar(frame, "FolderWizard Setup")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)
        tk.Label(content_frame, text="Bienvenido a FolderWizard",
                 font=("Tahoma", 14, "bold"), bg="#ECE9D8").pack(anchor="nw")
        tk.Label(content_frame, text="Este asistente organiza archivos en carpetas según su tipo.\n"
                                      "Selecciona una carpeta y presiona 'Organizar Archivos'.",
                 justify="left", font=("Tahoma", 10), bg="#ECE9D8", wraplength=380).pack(anchor="nw", pady=10)
        self._crear_botones_navegacion(frame, siguiente=lambda: self.show_frame(self.frame_select))

    def create_select_frame(self):
        """Frame para seleccionar la carpeta a organizar."""
        frame = self.frame_select
        
        self._crear_top_bar(frame, "FolderWizard Setup")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)
        tk.Label(content_frame, text="Selecciona la carpeta que deseas organizar",
                 font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(anchor="nw", pady=10)
        self.folder_label = tk.Entry(content_frame, width=50, state="disabled", justify="left")
        self.folder_label.pack(anchor="nw", pady=10)
        tk.Button(content_frame, text="Seleccionar Carpeta", width=18,
                  command=self.select_folder, bg="#ECE9D8").pack(anchor="nw", pady=5)
        self._crear_botones_navegacion(frame, volver=lambda: self.show_frame(self.frame_welcome),
                                       siguiente=lambda: self.show_frame(self.frame_actions))

    def create_actions_frame(self):
        """Frame con todas las acciones que puede realizar la app."""
        frame = self.frame_actions
        self._crear_top_bar(frame, "FolderWizard Setup")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)
        tk.Label(content_frame, text="Selecciona una acción a realizar",
                 font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(anchor="nw", pady=10)

        # Botones de acciones
        acciones = [
            ("Organizar Archivos", self.organize_files),
            ("Comprimir Archivo", self.comprimir_carpeta),
            ("Contar Archivos", self.count_files),
            ("Contar Carpetas", self.contar_carpetas),
            ("Archivos últimos 7 días", self.archivos_recientes),
            ("Deshacer Última Acción", self.deshacer)
        ]
        for texto, cmd in acciones:
            tk.Button(content_frame, text=texto, width=20, command=cmd, bg="#ECE9D8").pack(pady=5)

        self._crear_botones_navegacion(frame, volver=lambda: self.show_frame(self.frame_select))

    # ------------------ MÉTODOS AUXILIARES DE GUI ------------------
    def _crear_top_bar(self, frame, titulo):
        """Crea la barra superior con título de la app."""
        top_bar = tk.Frame(frame, bg="#245EDC", height=35)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text=titulo, fg="white", bg="#245EDC",
                 font=("Tahoma", 11, "bold")).place(x=10, y=7)

    def _crear_panel_con_logo(self, frame):
        """Crea un panel a la izquierda con el logo de la app."""
        image_frame = tk.Frame(frame, width=140, height=220, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)
        try:
            img = tk.PhotoImage(file="logo.png")
            lbl_img = tk.Label(image_frame, image=img, bg="#D4D0C8")
            lbl_img.image = img
            lbl_img.pack(expand=True)
        except Exception:
            tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold")).pack(expand=True)

    def _crear_botones_navegacion(self, frame, volver=None, siguiente=None):
        """Crea la barra inferior con botones de Volver, Siguiente y Salir."""
        btn_frame = tk.Frame(frame, bg="#D4D0C8", relief="raised", borderwidth=2)
        btn_frame.pack(side="bottom", fill="x")
        if volver:
            tk.Button(btn_frame, text="Volver", width=12, command=volver, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Salir", width=12, command=self.root.quit, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        if siguiente:
            tk.Button(btn_frame, text="Siguiente", width=12, command=siguiente, bg="#ECE9D8").pack(side="right", padx=10, pady=10)

    # ------------------ MÉTODOS DE ACCIÓN ------------------
    def select_folder(self):
        """Abre un diálogo para seleccionar la carpeta a organizar."""
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "No has seleccionado ninguna carpeta.")
            return
        self.folder_label.config(state="normal")
        self.folder_label.delete(0, tk.END)
        self.folder_label.insert(0, self.folder_path)
        self.folder_label.config(state="disabled")

    def organize_files(self):
        """Organiza los archivos de la carpeta seleccionada."""
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        try:
            resultado = organize_folder(self.folder_path)
            messagebox.showinfo("Éxito", resultado)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def comprimir_carpeta(self):
        """Comprime el archivo seleccionado en formato .gz"""
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo.")
            return
        try:
            comprimir_archivo(self.folder_path)
            messagebox.showinfo("Éxito", "Archivo comprimido correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def count_files(self):
        """Cuenta la cantidad de archivos en la carpeta seleccionada."""
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        num = len([f for f in Path(self.folder_path).iterdir() if f.is_file()])
        messagebox.showinfo("Archivos Encontrados", f"Hay {num} archivos en esta carpeta.")

    def contar_carpetas(self):
        """Cuenta la cantidad de carpetas en la carpeta seleccionada."""
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        num = len([f for f in Path(self.folder_path).iterdir() if f.is_dir()])
        messagebox.showinfo("Carpetas Encontradas", f"Hay {num} carpetas en esta carpeta.")

    def archivos_recientes(self):
        """Muestra los archivos modificados en los últimos 7 días."""
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        recientes = obtener_archivos_recientes(self.folder_path)
        if not recientes:
            messagebox.showinfo("Archivos recientes", "No se encontraron archivos modificados en los últimos 7 días.")
        else:
            messagebox.showinfo("Archivos recientes", f"Archivos modificados en los últimos 7 días:\n\n" + "\n".join(recientes))

    def deshacer(self):
        """Deshace la última acción de organización."""
        resultado = deshacer_accion()
        messagebox.showinfo("Deshacer", resultado)

# ------------------ EJECUCIÓN ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderWizardApp(root)
    root.mainloop()

# =====================================================
# ================== BUILD FUNCIONAL ==================
# =====================================================