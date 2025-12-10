import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path
import zipfile
from datetime import datetime, timedelta
import os
import gzip


# ------------------ CATEGORÍAS DE ARCHIVOS ------------------
CATEGORIES = {
    'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'Música': ['.mp3', '.wav', '.flac', '.aac'],
    'Archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Otros': []
}


# ------------------ Configuraciones Tkinter ------------------
resolucion = "700x500"
nombre_ventana = "FolderWizard"
carpeta_por_defecto = None
titulo_ventanas = "Asistente de Organización de Archivos"
imagen_banner = "logo.png"
nombre_dialogo_1 = "Bienvenido a FolderWizard"
descripcion_dialogo_1 = "Este asistente organiza archivos en carpetas según su tipo.\nSelecciona una carpeta y presiona 'Organizar Archivos'."


#------------------ LANGS ------------------
msg_desacer_accion = "¡La última acción ha sido deshecha correctamente!"
organizacion_exitosa = "¡Los archivos han sido organizados correctamente!"
ultima_accion_vacia = "No hay ninguna acción para deshacer."

# ------------------ HISTORIAL DE ACCIONES ------------------
ultima_accion = []



# ------------------ FUNCIONES AUXILIARES ------------------
""" Mueve un archivo de origen a destino, manejando conflictos de nombres. """
def mover_archivo(origen, destino):
    counter = 1
    dest_path = Path(destino)
    while dest_path.exists():
        dest_path = Path(f"{destino.stem}_copy{counter}{destino.suffix}")
        counter += 1
    shutil.move(str(origen), str(dest_path))
    return dest_path

""" Devuelve los archivos del directorio que fueron modificados dentro del intervalo dado. """
def obtener_archivos_recientes(folder_path, dias=7):
    folder = Path(folder_path)
    limite_fecha = datetime.now() - timedelta(days=dias)
    return [f.name for f in folder.iterdir() if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) > limite_fecha]

""" Organiza los archivos de una carpeta en subcarpetas según su tipo y registra los movimientos para deshacerlos """
def organizar_carpeta(folder_path):
    global ultima_accion
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe.")

    movimientos = []
    for category in CATEGORIES:
        (folder / category).mkdir(exist_ok=True)

    for file in folder.iterdir():
        if not file.is_file() or file.name.startswith('.') or file.name.lower() == "desktop.ini":
            continue
        moved = False
        for category, extensions in CATEGORIES.items():
            if file.suffix.lower() in extensions:
                destino = mover_archivo(file, folder / category / file.name)
                movimientos.append((str(destino), str(file)))
                moved = True
                break
        if not moved:
            destino = mover_archivo(file, folder / 'Otros' / file.name)
            movimientos.append((str(destino), str(file)))
    ultima_accion = movimientos
    return f"{organizacion_exitosa}"

""" Revierte la última acción realizada restaurando los archivos a su ubicación original. """
def deshacer_accion():
    global ultima_accion

    if not ultima_accion:
        return f"{ultima_accion_vacia}"

    # Mover cada archivo de regreso a su ubicación original
    for destino, origen in reversed(ultima_accion):
        if Path(destino).exists():
            shutil.move(destino, origen)
            
    # Obtener la carpeta base donde se organizó
    primer_origen = ultima_accion[0][1] 
    carpeta_base = Path(primer_origen).parent
    categorias = list(CATEGORIES.keys())
    categorias.append("Otros")  

    for categoria in categorias:
        ruta = carpeta_base / categoria  
        if not ruta.exists():
            continue
        if not ruta.is_dir():
            continue
        contenido = list(ruta.iterdir())
        if len(contenido) > 0:
            continue
        # Si está vacía, la eliminamos
        ruta.rmdir()
    # Borrar registro de la última acción
    ultima_accion = []
    return f"{msg_desacer_accion}"

# ------------------ CLASE PRINCIPAL ------------------

class FolderWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{nombre_ventana}")
        self.root.geometry(f"{resolucion}")
        self.root.resizable(False, False)
        self.root.configure(bg="#ECE9D8")
        self.folder_path = {carpeta_por_defecto}

        self.frame_welcome = tk.Frame(root, bg="#ECE9D8")
        self.frame_select = tk.Frame(root, bg="#ECE9D8")
        self.frame_actions = tk.Frame(root, bg="#ECE9D8")
        for frame in (self.frame_welcome, self.frame_select, self.frame_actions):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.crear_bienvenida_frame()
        self.create_select_frame()
        self.create_actions_frame()
        self.enseniar_frame(self.frame_welcome)

    def enseniar_frame(self, frame):
        frame.tkraise()

    # ------------------ FRAMES ------------------ 
    """ Genera la pantalla de bienvenida del asistente. """
    def crear_bienvenida_frame(self):
        frame = self.frame_welcome
        self._crear_top_bar(frame, f"{titulo_ventanas}")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)
        tk.Label(content_frame, text=f"{nombre_dialogo_1}",
                 font=("Tahoma", 14, "bold"), bg="#ECE9D8").pack(anchor="nw")
        tk.Label(content_frame,
                 text=f"{descripcion_dialogo_1}",
                 justify="left", font=("Tahoma", 10), bg="#ECE9D8", wraplength=380).pack(anchor="nw", pady=10)
        self._crear_botones_navegacion(frame, siguiente=lambda: self.enseniar_frame(self.frame_select))

    """ Crea la pantalla de selección de carpeta dentro de la interfaz. """
    def create_select_frame(self):
        frame = self.frame_select
        self._crear_top_bar(frame, f"{titulo_ventanas}")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)
        tk.Label(content_frame, text="Selecciona la carpeta que deseas organizar",
                 font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(anchor="nw", pady=10)
        self.folder_label = tk.Entry(content_frame, width=50, state="disabled", justify="left")
        self.folder_label.pack(anchor="nw", pady=10)
        tk.Button(content_frame, text="Seleccionar Carpeta", width=18,
                  command=self.seleccionar_carpeta, bg="#ECE9D8").pack(anchor="nw", pady=5)
        self._crear_botones_navegacion(frame,
                                       volver=lambda: self.enseniar_frame(self.frame_welcome),
                                       siguiente=self.ir_a_acciones)

    """ Construye la interfaz principal con acciones, estadísticas y navegación. """
    def create_actions_frame(self):
        frame = self.frame_actions
        self._crear_top_bar(frame, f"{titulo_ventanas}")
        content_frame = tk.Frame(frame, bg="#ECE9D8")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._crear_panel_con_logo(content_frame)

        acciones_frame = tk.Frame(content_frame, bg="#ECE9D8")
        acciones_frame.pack(side="left", fill="both", expand=True, padx=20)
        tk.Label(acciones_frame, text="Acciones disponibles",
            font=("Tahoma", 12, "bold"), bg="#ECE9D8").pack(pady=10)

        acciones = [
            ("Organizar Archivos", self.organizar_archivos),
            ("Comprimir Carpeta", self.comprimir_carpeta),
            ("Archivos últimos 7 días", self.archivos_recientes),
            ("Deshacer Última Acción", self.deshacer)
        ]
        for texto, cmd in acciones:
            tk.Button(acciones_frame, text=texto, width=20, command=cmd, bg="#ECE9D8").pack(pady=5)

        stats_frame = tk.Frame(content_frame, bg="#D4D0C8", relief="sunken", borderwidth=2)
        stats_frame.pack(side="left", fill="y", padx=20, pady=5)
        tk.Label(stats_frame, text="Estadísticas \n de la ruta",
                 font=("Tahoma", 11, "bold"), bg="#D4D0C8").pack(pady=10)
        tk.Label(stats_frame, text="Archivos:", bg="#D4D0C8", font=("Tahoma", 10, "bold")).pack()
        self.txt_archivos = tk.Entry(stats_frame, width=15, state="disabled", justify="center")
        self.txt_archivos.pack(pady=5)
        tk.Label(stats_frame, text="Carpetas:", bg="#D4D0C8", font=("Tahoma", 10, "bold")).pack()
        self.txt_carpetas = tk.Entry(stats_frame, width=15, state="disabled", justify="center")
        self.txt_carpetas.pack(pady=5)
        tk.Label(stats_frame, text="Peso total:", bg="#D4D0C8", font=("Tahoma", 10, "bold")).pack()
        self.txt_peso = tk.Entry(stats_frame, width=15, state="disabled", justify="center")
        self.txt_peso.pack(pady=5)
        tk.Label(stats_frame, text="Número de subcarpetas:", bg="#D4D0C8", font=("Tahoma", 10, "bold")).pack()
        self.txt_niveles = tk.Entry(stats_frame, width=15, state="disabled", justify="center")
        self.txt_niveles.pack(pady=5)
        tk.Button(stats_frame, text="⟳", width=4,
                  command=self.actualizar_estadisticas, bg="#ECE9D8", font=("Tahoma", 12, "bold")).pack(pady=15)
        self.root.after(100, self.actualizar_estadisticas)

        self._crear_botones_navegacion(frame, volver=lambda: self.enseniar_frame(self.frame_select))

    # ------------------ MÉTODOS AUXILIARES ------------------
    """ Crea una barra superior con un título dentro del frame dado. """
    def _crear_top_bar(self, frame, titulo):
        top_bar = tk.Frame(frame, bg="#245EDC", height=40)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        tk.Label(top_bar, text=titulo, fg="white", bg="#245EDC",
                 font=("Tahoma", 12, "bold")).pack(anchor="w", padx=10, pady=8)

    """ Genera un panel lateral con el logo o un marcador en caso de no cargarlo. """
    def _crear_panel_con_logo(self, frame):
        image_frame = tk.Frame(frame, width=140, height=380, bg="#D4D0C8", relief="sunken", borderwidth=2)
        image_frame.pack(side="left", padx=10)
        image_frame.pack_propagate(False)
        try:
            img = tk.PhotoImage(file=f"{imagen_banner}")
            lbl_img = tk.Label(image_frame, image=img, bg="#D4D0C8")
            lbl_img.image = img
            lbl_img.pack(expand=True)
        except Exception:
            tk.Label(image_frame, text="Logo", bg="#D4D0C8", font=("Tahoma", 12, "bold")).pack(expand=True)

    """ Construye la barra inferior con botones de navegación. """
    def _crear_botones_navegacion(self, frame, volver=None, siguiente=None):
        btn_frame = tk.Frame(frame, bg="#D4D0C8", relief="raised", borderwidth=2)
        btn_frame.pack(side="bottom", fill="x")
        if volver:
            tk.Button(btn_frame, text="Volver", width=12, command=volver, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Salir", width=12, command=self.root.quit, bg="#ECE9D8").pack(side="left", padx=10, pady=10)
        if siguiente:
            tk.Button(btn_frame, text="Siguiente", width=12, command=siguiente, bg="#ECE9D8").pack(side="right", padx=10, pady=10)

    # ------------------ MÉTODOS DE ACCIÓN ------------------
    """ Permite elegir una carpeta y actualiza la interfaz con la ruta seleccionada. """
    def seleccionar_carpeta(self):
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "No has seleccionado ninguna carpeta.")
            return
        self.folder_label.config(state="normal")
        self.folder_label.delete(0, tk.END)
        self.folder_label.insert(0, self.folder_path)
        self.folder_label.config(state="disabled")
        self.actualizar_estadisticas()

    """ Organiza los archivos de la carpeta seleccionada. """
    def organizar_archivos(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        try:
            resultado = organizar_carpeta(self.folder_path)
            messagebox.showinfo("Éxito", resultado)
            self.actualizar_estadisticas()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    """ Comprime por completo la carpeta indicada y devuelve la ruta del ZIP. """
    def comprimir_carpeta_entera(self, carpeta):
        carpeta = Path(carpeta)
        zip_path = carpeta.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(carpeta):
                for file in files:
                    ruta = Path(root) / file
                    zipf.write(ruta, arcname=ruta.relative_to(carpeta))
        return zip_path

    """ Comprime la carpeta seleccionada y muestra la ruta del ZIP generado. """
    def comprimir_carpeta(self):
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        try:
            zip_path = self.comprimir_carpeta_entera(self.folder_path)
            messagebox.showinfo("Éxito", f"Carpeta comprimida correctamente:\n{zip_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    """ Muestra los archivos modificados en los ultimos 7 dias de la carpeta seleccionada """
    def archivos_recientes(self):
        
        if not self.folder_path:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta.")
            return
        recientes = obtener_archivos_recientes(self.folder_path)
        if not recientes:
            messagebox.showinfo("Archivos recientes", "No se encontraron archivos modificados en los últimos 7 días.")
        else:
            messagebox.showinfo("Archivos recientes", f"Archivos modificados en los últimos 7 días:\n\n" + "\n".join(recientes))

    ''' Informacion de la ruta seleccionada '''
    def deshacer(self):
        resultado = deshacer_accion()
        messagebox.showinfo("Deshacer", resultado)
        self.actualizar_estadisticas()
    
    """ Actualiza los campos de estadísticas mostrando la cantidad de archivos y carpetas en la carpeta seleccionada """
    def actualizar_estadisticas(self):
        if not self.folder_path:
            self._set_stat_fields("-", "-", "-", "-")
            return
        try:
            # Contar archivos ignorando desktop.ini y opcionalmente otros .ini para visualización
            num_archivos = len([f for f in Path(self.folder_path).iterdir() 
                                if f.is_file() and f.name.lower() != "desktop.ini" and f.suffix.lower() != ".ini"])
            # Contar carpetas normalmente
            num_carpetas = len([f for f in Path(self.folder_path).iterdir() if f.is_dir()])

            #Tamaño del archivo en la unidad que precise
            total_size = 0
            for f in Path(self.folder_path).glob("**/*"):
                if f.is_file():
                    try:
                        total_size += os.path.getsize(f)
                    except:
                        pass
            size_formatted = self._format_size(total_size)

            #Cantidad de subcarpetas en el archivo, por ejemplo, Carpeta1/Carpeta2/Carpeta3, nSubcarpetas=2
            profundidad = 0
            for f in Path(self.folder_path).glob("**/*"):
                if f.is_dir():
                    nivel = len(f.relative_to(Path(self.folder_path)).parts)
                    if nivel > profundidad:
                        profundidad = nivel

            self._set_stat_fields(num_archivos, num_carpetas, size_formatted, profundidad)

        except Exception:
            self._set_stat_fields("ERR", "ERR", "ERR", "ERR")

    """ Actualiza los campos de texto de estadísticas con la cantidad de archivos y carpetas """
    def _set_stat_fields(self, archivos, carpetas, peso, niveles):
        self.txt_archivos.config(state="normal")
        self.txt_carpetas.config(state="normal")
        self.txt_peso.config(state="normal")
        self.txt_niveles.config(state="normal")
        self.txt_archivos.delete(0, tk.END)
        self.txt_archivos.insert(0, str(archivos))
        self.txt_carpetas.delete(0, tk.END)
        self.txt_carpetas.insert(0, str(carpetas))
        self.txt_peso.delete(0, tk.END)
        self.txt_peso.insert(0, str(peso))
        self.txt_niveles.delete(0, tk.END)
        self.txt_niveles.insert(0, str(niveles))
        self.txt_archivos.config(state="disabled")
        self.txt_carpetas.config(state="disabled")
        self.txt_peso.config(state="disabled")
        self.txt_niveles.config(state="disabled")

    """ Cambia a la pantalla de acciones y actualiza las estadísticas """
    def ir_a_acciones(self):
        self.enseniar_frame(self.frame_actions)
        self.actualizar_estadisticas()

    """Da formato al peso del archivo"""
    def _format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 KB"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

# ------------------ EJECUCIÓN ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderWizardApp(root)
    root.mainloop()
