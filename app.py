import os
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk

# Componentes Modulares
import hashing_engine
import export_manager

# Configuración del Tema de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HashFinderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la Ventana
        self.title("Escáner y Calculador de Hashes")
        self.geometry("1150x720")
        self.minsize(950, 600)
        
        # Variables de Estado
        self.files_data = []        # Lista original de archivos encontrados
        self.filtered_data = []     # Lista actualmente filtrada/ordenada
        self.scanning = False
        self.cancel_requested = False
        self.sort_column = 'nombre'
        self.sort_asc = True
        self.scan_start_time = None
        
        # Configurar Pesos de la Grilla (Grid)
        self.grid_rowconfigure(2, weight=1) # La sección de resultados está en la fila 2
        self.grid_columnconfigure(0, weight=1)
        
        # Crear Secciones de la Interfaz Gráfica
        self.create_header_section()
        self.create_controls_section()
        self.create_progress_section()
        self.create_results_section()
        self.create_footer_section()
        
        # Aplicar estilos personalizados para que el Treeview se integre con el modo oscuro
        self.apply_treeview_styles()

    def create_header_section(self):
        self.header_frame = ctk.CTkFrame(self, height=65, corner_radius=10, fg_color="#0e111a")
        self.header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        title_subframe = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_subframe.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        title_label = ctk.CTkLabel(title_subframe, text="Herramienta Validador de Hash", 
                                   font=ctk.CTkFont(family="Outfit", size=22, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(title_subframe, text="Generador de Integridad de Archivos", 
                                      font=ctk.CTkFont(size=11), text_color="#64748b")
        subtitle_label.grid(row=1, column=0, sticky="w")

    def create_controls_section(self):
        self.controls_frame = ctk.CTkFrame(self, corner_radius=10)
        self.controls_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        
        path_label = ctk.CTkLabel(self.controls_frame, text="Ruta de Archivo o Carpeta:", font=ctk.CTkFont(weight="bold"))
        path_label.grid(row=0, column=0, padx=20, pady=(12, 2), sticky="w")
        
        input_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        input_subframe.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        input_subframe.grid_columnconfigure(0, weight=1)
        
        self.path_entry = ctk.CTkEntry(input_subframe, placeholder_text="Selecciona o escribe una ruta de archivo o carpeta...",
                                       font=ctk.CTkFont(family="Consolas"))
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_folder_btn = ctk.CTkButton(input_subframe, text="Carpeta...", width=95, fg_color="#3b82f6", hover_color="#2563eb",
                                               command=self.browse_directory)
        self.browse_folder_btn.grid(row=0, column=1, sticky="e", padx=(0, 5))
        
        self.browse_file_btn = ctk.CTkButton(input_subframe, text="Archivo...", width=95, fg_color="#6366f1", hover_color="#4f46e5",
                                             command=self.browse_file)
        self.browse_file_btn.grid(row=0, column=2, sticky="e")
        
        options_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        options_subframe.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        options_subframe.grid_columnconfigure(1, weight=1)
        
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_checkbox = ctk.CTkCheckBox(options_subframe, text="Escanear recursivamente (subcarpetas)", 
                                                  variable=self.recursive_var, font=ctk.CTkFont(size=12))
        self.recursive_checkbox.grid(row=0, column=0, sticky="w")
        
        actions_subframe = ctk.CTkFrame(options_subframe, fg_color="transparent")
        actions_subframe.grid(row=0, column=2, sticky="e")
        
        self.scan_btn = ctk.CTkButton(actions_subframe, text="Iniciar Escaneo", font=ctk.CTkFont(weight="bold"),
                                      fg_color="#10b981", hover_color="#059669", width=140, command=self.start_scan)
        self.scan_btn.grid(row=0, column=0, padx=5)
        
        self.cancel_btn = ctk.CTkButton(actions_subframe, text="Cancelar", font=ctk.CTkFont(weight="bold"),
                                        fg_color="#ef4444", hover_color="#dc2626", width=140, command=self.cancel_scan)
        self.cancel_btn.grid(row=0, column=0, padx=5)
        self.cancel_btn.grid_remove()

    def create_progress_section(self):
        self.progress_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#0f172a")
        self.progress_frame.grid_rowconfigure(3, weight=1)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        labels_subframe = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        labels_subframe.grid(row=0, column=0, padx=20, pady=(12, 4), sticky="ew")
        labels_subframe.grid_columnconfigure(0, weight=1)
        
        self.progress_title = ctk.CTkLabel(labels_subframe, text="Escaneando archivos...", font=ctk.CTkFont(weight="bold", size=13))
        self.progress_title.grid(row=0, column=0, sticky="w")
        
        self.progress_percent_label = ctk.CTkLabel(labels_subframe, text="0%", font=ctk.CTkFont(weight="bold", size=14), text_color="#3b82f6")
        self.progress_percent_label.grid(row=0, column=1, sticky="e")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.current_file_label = ctk.CTkLabel(self.progress_frame, text="Archivo actual: Iniciando...",
                                               font=ctk.CTkFont(family="Consolas", size=11), text_color="#94a3b8", anchor="w")
        self.current_file_label.grid(row=2, column=0, padx=20, pady=(4, 10), sticky="ew")
        
        self.stats_subframe = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.stats_subframe.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="ew")
        for i in range(4):
            self.stats_subframe.grid_columnconfigure(i, weight=1)
            
        self.stat_files_lbl = self.create_stat_widget(self.stats_subframe, "Archivos", "0 / 0", 0)
        self.stat_size_lbl = self.create_stat_widget(self.stats_subframe, "Tamaño Procesado", "0 Bytes / 0 Bytes", 1)
        self.stat_speed_lbl = self.create_stat_widget(self.stats_subframe, "Velocidad", "0 arch/seg", 2)
        self.stat_time_lbl = self.create_stat_widget(self.stats_subframe, "Tiempo", "00:00", 3)

    def create_stat_widget(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color="#161a24", corner_radius=6, height=55)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont(size=9, weight="bold"), text_color="#64748b")
        lbl_title.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=12, weight="bold"))
        lbl_val.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        return lbl_val

    def create_results_section(self):
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        results_header = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        results_header.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        results_header.grid_columnconfigure(1, weight=1)
        
        title_sub = ctk.CTkFrame(results_header, fg_color="transparent")
        title_sub.grid(row=0, column=0, sticky="w")
        lbl_res = ctk.CTkLabel(title_sub, text="Resultados Obtenidos", font=ctk.CTkFont(weight="bold", size=14))
        lbl_res.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.badge_lbl = ctk.CTkLabel(title_sub, text="0 archivos", font=ctk.CTkFont(size=11, weight="bold"),
                                      fg_color="#1e1b4b", text_color="#818cf8", corner_radius=10, width=90, height=20)
        self.badge_lbl.grid(row=0, column=1, sticky="w")
        
        actions_sub = ctk.CTkFrame(results_header, fg_color="transparent")
        actions_sub.grid(row=0, column=1, sticky="e")
        self.search_entry = ctk.CTkEntry(actions_sub, placeholder_text="Buscar archivos...", width=200, height=28)
        self.search_entry.grid(row=0, column=0, padx=5, sticky="e")
        self.search_entry.bind("<KeyRelease>", self.apply_search)
        
        self.export_csv_btn = ctk.CTkButton(actions_sub, text="Exportar CSV", fg_color="#1a1f2c", text_color="#f8fafc",
                                            hover_color="#1e293b", border_width=1, border_color="#2d3748", width=100, height=28,
                                            state="disabled", command=self.export_to_csv)
        self.export_csv_btn.grid(row=0, column=1, padx=4)
        
        self.export_json_btn = ctk.CTkButton(actions_sub, text="Exportar JSON", fg_color="#1a1f2c", text_color="#f8fafc",
                                             hover_color="#1e293b", border_width=1, border_color="#2d3748", width=100, height=28,
                                             state="disabled", command=self.export_to_json)
        self.export_json_btn.grid(row=0, column=2, padx=4)
        
        self.clear_btn = ctk.CTkButton(actions_sub, text="Limpiar", fg_color="transparent", text_color="#94a3b8",
                                       hover_color="#1e293b", width=80, height=28, state="disabled", command=self.reset_app)
        self.clear_btn.grid(row=0, column=3, padx=4)
        
        table_container = ctk.CTkFrame(self.results_frame, fg_color="#11131c")
        table_container.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        columns = ("id", "nombre", "ruta_relativa", "tamano", "md5", "sha256", "fecha_creacion", "fecha_modificacion")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.tree.heading("id", text="#", anchor="center")
        self.tree.heading("nombre", text="Nombre", anchor="w", command=lambda: self.sort_by("nombre"))
        self.tree.heading("ruta_relativa", text="Ruta Relativa", anchor="w", command=lambda: self.sort_by("ruta_relativa"))
        self.tree.heading("tamano", text="Tamaño", anchor="w", command=lambda: self.sort_by("tamano"))
        self.tree.heading("md5", text="Hash MD5", anchor="w")
        self.tree.heading("sha256", text="Hash SHA-256", anchor="w")
        self.tree.heading("fecha_creacion", text="F. Creación", anchor="w", command=lambda: self.sort_by("fecha_creacion"))
        self.tree.heading("fecha_modificacion", text="F. Modificación", anchor="w", command=lambda: self.sort_by("fecha_modificacion"))
        
        self.tree.column("id", width=45, minwidth=45, stretch=False, anchor="center")
        self.tree.column("nombre", width=180, minwidth=120)
        self.tree.column("ruta_relativa", width=250, minwidth=150)
        self.tree.column("tamano", width=100, minwidth=80, stretch=False)
        self.tree.column("md5", width=150, minwidth=150, stretch=False)
        self.tree.column("sha256", width=220, minwidth=200, stretch=False)
        self.tree.column("fecha_creacion", width=130, minwidth=110, stretch=False)
        self.tree.column("fecha_modificacion", width=130, minwidth=110, stretch=False)
        
        scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=scrollbar_x.set)
        self.tree.bind("<Double-1>", self.copy_selected_hash)

    def create_footer_section(self):
        self.footer_frame = ctk.CTkFrame(self, height=35, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        footer_lbl = ctk.CTkLabel(self.footer_frame, text="", font=ctk.CTkFont(size=10), text_color="#475569")
        footer_lbl.pack(side="left", padx=10)
        
        self.toast_lbl = ctk.CTkLabel(self.footer_frame, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#10b981")
        self.toast_lbl.pack(side="right", padx=10)

    def apply_treeview_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", background="#0e111a", foreground="#cbd5e1", fieldbackground="#0e111a",
                        rowheight=30, borderwidth=0, font=("Segoe UI", 9))
        style.map("Custom.Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])
        style.configure("Custom.Treeview.Heading", background="#1e293b", foreground="#cbd5e1", borderwidth=1,
                        bordercolor="#2d3748", relief="flat", padding=6, font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview.Heading", background=[("active", "#334155")], foreground=[("active", "#ffffff")])

    def show_toast(self, message, is_error=False):
        color = "#ef4444" if is_error else "#10b981"
        self.toast_lbl.configure(text=message, text_color=color)
        self.after(3500, lambda: self.toast_lbl.configure(text=""))

    def browse_directory(self):
        selected = filedialog.askdirectory(title="Seleccionar Directorio")
        if selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected)

    def browse_file(self):
        selected = filedialog.askopenfilename(title="Seleccionar Archivo")
        if selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected)

    def start_scan(self):
        directory = self.path_entry.get().strip()
        if not directory or not os.path.exists(directory):
            self.show_toast("Por favor ingresa una ruta válida.", is_error=True)
            return
            
        self.scanning = True
        self.cancel_requested = False
        self.files_data, self.filtered_data = [], []
        
        self.scan_btn.grid_remove()
        self.cancel_btn.grid()
        self.path_entry.configure(state="disabled")
        self.browse_folder_btn.configure(state="disabled")
        self.browse_file_btn.configure(state="disabled")
        self.recursive_checkbox.configure(state="disabled")
        
        self.progress_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.controls_frame.grid_remove()
        
        self.progress_bar.set(0)
        self.progress_percent_label.configure(text="0%")
        self.current_file_label.configure(text="Iniciando análisis...")
        self.stat_files_lbl.configure(text="0 / 0")
        self.stat_size_lbl.configure(text="0 Bytes / 0 Bytes")
        self.stat_speed_lbl.configure(text="0 arch/seg")
        self.stat_time_lbl.configure(text="00:00")
        
        self.export_csv_btn.configure(state="disabled")
        self.export_json_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.scan_start_time = time.time()
        threading.Thread(target=self.scan_worker, args=(directory, self.recursive_var.get()), daemon=True).start()
        self.show_toast("Escaneo iniciado...")

    def cancel_scan(self):
        self.cancel_requested = True
        self.current_file_label.configure(text="Cancelando escaneo...")
        self.show_toast("Cancelando proceso...", is_error=True)

    def scan_worker(self, directory, recursive):
        try:
            found_files = hashing_engine.get_scanned_files_list(directory, recursive)
            total_files = len(found_files)
            total_bytes = sum(item[2] for item in found_files)
            
            if total_files == 0:
                self.invoke_safe(self.finish_scan_empty)
                return

            processed_files, processed_bytes = 0, 0

            for idx, (name, full_path, size) in enumerate(found_files):
                if self.cancel_requested:
                    break
                
                self.invoke_safe(self.update_progress_worker, full_path, processed_files, total_files, processed_bytes, total_bytes)
                
                md5, sha256, created_at, modified_at, err = hashing_engine.calculate_file_hashes_and_metadata(full_path)
                
                rel_path = os.path.basename(full_path) if os.path.isfile(directory) else os.path.relpath(full_path, directory).replace('\\', '/')
                
                self.files_data.append({
                    'id': idx + 1, 'nombre': name, 'ruta_relativa': rel_path, 'ruta_completa': full_path.replace('\\', '/'),
                    'tamano': size, 'md5': md5, 'sha256': sha256, 'fecha_creacion': created_at, 'fecha_modificacion': modified_at, 'error': err
                })
                processed_files += 1
                processed_bytes += size

            if self.cancel_requested:
                self.invoke_safe(self.finish_scan_cancelled)
            else:
                self.invoke_safe(self.finish_scan_success, processed_bytes)

        except Exception as e:
            self.invoke_safe(self.finish_scan_error, str(e))

    def update_progress_worker(self, current_file, processed, total, bytes_proc, bytes_total):
        progress = processed / total if total > 0 else 0
        self.progress_bar.set(progress)
        self.progress_percent_label.configure(text=f"{Math_Round_Custom(progress * 100)}%")
        
        norm_path = current_file.replace('\\', '/')
        if len(norm_path) > 75:
            norm_path = "..." + norm_path[-72:]
        self.current_file_label.configure(text=f"Archivo actual: {norm_path}")
        
        self.stat_files_lbl.configure(text=f"{processed} / {total}")
        self.stat_size_lbl.configure(text=f"{self.format_bytes_size(bytes_proc)} / {self.format_bytes_size(bytes_total)}")
        
        elapsed = time.time() - self.scan_start_time
        self.stat_time_lbl.configure(text=f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}")
        
        speed = Math_Round_Custom(processed / elapsed) if elapsed > 0 else 0
        self.stat_speed_lbl.configure(text=f"{speed} arch/seg")

    def finish_scan_success(self, total_bytes):
        self.scanning = False
        self.restore_controls_ui()
        self.show_toast("¡Escaneo finalizado con éxito!")
        self.apply_filters_and_render()

    def finish_scan_cancelled(self):
        self.scanning = False
        self.restore_controls_ui()
        self.show_toast("Escaneo cancelado.", is_error=True)
        self.apply_filters_and_render()

    def finish_scan_empty(self):
        self.scanning = False
        self.restore_controls_ui()
        self.show_toast("No se encontraron archivos.", is_error=True)
        self.badge_lbl.configure(text="0 archivos")

    def finish_scan_error(self, err_msg):
        self.scanning = False
        self.restore_controls_ui()
        self.show_toast(f"Error: {err_msg}", is_error=True)

    def restore_controls_ui(self):
        self.cancel_btn.grid_remove()
        self.scan_btn.grid()
        self.path_entry.configure(state="normal")
        self.browse_folder_btn.configure(state="normal")
        self.browse_file_btn.configure(state="normal")
        self.recursive_checkbox.configure(state="normal")
        
        self.progress_frame.grid_remove()
        self.controls_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

    def invoke_safe(self, func, *args):
        self.after(0, lambda: func(*args))

    def apply_search(self, event=None):
        self.apply_filters_and_render()

    def apply_filters_and_render(self):
        query = self.search_entry.get().lower().strip()
        if not query:
            self.filtered_data = list(self.files_data)
        else:
            self.filtered_data = [
                f for f in self.files_data 
                if query in f['nombre'].lower() or query in f['ruta_relativa'].lower() or 
                   query in f['md5'].lower() or query in f['sha256'].lower()
            ]

        count = len(self.filtered_data)
        self.badge_lbl.configure(text=f"{count} {'archivo' if count == 1 else 'archivos'}")
        self.sort_and_render()

    def sort_by(self, col):
        if self.sort_column == col:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_column, self.sort_asc = col, True
        self.sort_and_render()
        orden = "Ascendente" if self.sort_asc else "Descendente"
        col_es = {
            'nombre': "Nombre",
            'ruta_relativa': "Ruta Relativa",
            'tamano': "Tamaño",
            'fecha_creacion': "F. Creación",
            'fecha_modificacion': "F. Modificación"
        }.get(col, col.upper())
        self.show_toast(f"Ordenado por {col_es} ({orden})")

    def sort_and_render(self):
        col, is_asc = self.sort_column, self.sort_asc
        if col == 'tamano':
            self.filtered_data.sort(key=lambda x: x['tamano'], reverse=not is_asc)
        elif col in ('fecha_creacion', 'fecha_modificacion'):
            self.filtered_data.sort(key=lambda x: x[col].lower(), reverse=not is_asc)
        else:
            self.filtered_data.sort(key=lambda x: x[col].lower(), reverse=not is_asc)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, file in enumerate(self.filtered_data):
            size_fmt = self.format_bytes_size(file['tamano'])
            tag = "error_row" if file['error'] else ""
            
            md5_val = "Error" if file['error'] else file['md5']
            sha256_val = file['error'] if file['error'] else file['sha256']
            if len(sha256_val) > 35 and file['error']:
                sha256_val = "Acceso Denegado: " + file['error'][:25] + "..."

            self.tree.insert("", "end", iid=str(i), tags=(tag,), values=(
                i + 1, file['nombre'], file['ruta_relativa'], size_fmt, md5_val, sha256_val, file['fecha_creacion'], file['fecha_modificacion']
            ))

        state = "normal" if len(self.files_data) > 0 else "disabled"
        self.export_csv_btn.configure(state=state)
        self.export_json_btn.configure(state=state)
        self.clear_btn.configure(state=state)

    def copy_selected_hash(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        values = self.tree.item(selected_item, "values")
        if not values: return
        
        md5, sha256 = values[4], values[5]
        if md5 == "Error" or "Acceso Denegado" in sha256:
            self.show_toast("No hay hashes disponibles.", is_error=True)
            return

        self.clipboard_clear()
        self.clipboard_append(sha256)
        self.show_toast("¡Hash SHA-256 copiado!")

    def export_to_csv(self):
        if len(self.filtered_data) == 0: return
        filename = filedialog.asksaveasfilename(
            title="Guardar archivo CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=f"hashfinder_export_{time.strftime('%Y%m%d')}.csv"
        )
        if not filename: return
        try:
            export_manager.save_to_csv(filename, self.filtered_data)
            self.show_toast("¡CSV guardado con éxito!")
        except Exception as e:
            self.show_toast(f"Error: {str(e)}", is_error=True)

    def export_to_json(self):
        if len(self.filtered_data) == 0: return
        filename = filedialog.asksaveasfilename(
            title="Guardar archivo JSON", defaultextension=".json", filetypes=[("JSON", "*.json")],
            initialfile=f"hashfinder_export_{time.strftime('%Y%m%d')}.json"
        )
        if not filename: return
        try:
            export_manager.save_to_json(filename, self.filtered_data, self.path_entry.get())
            self.show_toast("¡JSON guardado con éxito!")
        except Exception as e:
            self.show_toast(f"Error: {str(e)}", is_error=True)

    def reset_app(self):
        self.files_data, self.filtered_data = [], []
        self.search_entry.delete(0, tk.END)
        self.badge_lbl.configure(text="0 archivos")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.export_csv_btn.configure(state="disabled")
        self.export_json_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.show_toast("Resultados limpiados.")

    def format_bytes_size(self, bytes_count):
        if bytes_count == 0: return "0 Bytes"
        k, sizes = 1024, ["Bytes", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(bytes_count) / math.log(k)))
        return f"{bytes_count / (k**i):.2f} {sizes[i]}"

def Math_Round_Custom(val):
    try: return int(round(val))
    except Exception: return 0

if __name__ == '__main__':
    app = HashFinderApp()
    app.mainloop()
