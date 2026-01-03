import customtkinter as ctk
import psutil
import platform
import threading
import socket
import time
import subprocess
import os
import webbrowser  # Para abrir links en el Acerca De

# --- CONFIGURACIÓN INICIAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MatiSpecsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- VENTANA PRINCIPAL ---
        self.title("Mati-Specs | Suite de Diagnóstico Pro")
        self.geometry("1000x650")

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- VARIABLES DE ESTADO ---
        self.refresh_rate = 1.0  # Velocidad de actualización por defecto (1 segundo)

        # Variables de Red
        try:
            net_io = psutil.net_io_counters()
            self.last_upload = net_io.bytes_sent
            self.last_download = net_io.bytes_recv
        except:
            self.last_upload = 0
            self.last_download = 0

        # --- 1. MENÚ LATERAL ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)  # Empujar botones al fondo

        # Logo
        ctk.CTkLabel(self.sidebar, text="MATI-SPECS", font=("Arial", 22, "bold")).grid(
            row=0, column=0, padx=20, pady=(30, 20)
        )

        # Botones de Navegación
        self.crear_boton_menu("📊 Resumen Técnico", self.mostrar_resumen, 1)
        self.crear_boton_menu("🧠 Procesador (CPU)", self.mostrar_cpu, 2)
        self.crear_boton_menu("💾 Memoria (RAM)", self.mostrar_ram, 3)
        self.crear_boton_menu("💿 Almacenamiento", self.mostrar_disco, 4)
        self.crear_boton_menu("📡 Red e Internet", self.mostrar_red, 5)

        # Separador visual
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray40").grid(
            row=6, column=0, sticky="ew", padx=20, pady=10
        )

        self.crear_boton_menu("🛠️ Herramientas", self.mostrar_herramientas, 7)
        self.crear_boton_menu("⚙️ Configuración", self.mostrar_config, 8)

        # --- 2. ÁREA DE CONTENIDO (FRAMES) ---
        self.frames = {}  # Diccionario para guardar los frames
        for nombre in [
            "resumen",
            "cpu",
            "ram",
            "disco",
            "red",
            "herramientas",
            "config",
        ]:
            self.frames[nombre] = ctk.CTkFrame(
                self, corner_radius=0, fg_color="transparent"
            )

        # Iniciar
        self.mostrar_resumen()

        # --- HILO BACKGROUND ---
        self.running = True
        self.thread = threading.Thread(target=self.actualizar_datos, daemon=True)
        self.thread.start()

    def crear_boton_menu(self, texto, comando, fila):
        btn = ctk.CTkButton(
            self.sidebar,
            text=texto,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40,
            command=comando,
        )
        btn.grid(row=fila, column=0, padx=10, pady=5, sticky="ew")

    def ocultar_todo(self):
        for frame in self.frames.values():
            frame.grid_forget()

    # --- UTILIDAD: DETECTIVE RAM ---
    def obtener_info_ram_avanzada(self):
        try:
            comando = "wmic memorychip get Speed, SMBIOSMemoryType"
            proceso = subprocess.Popen(
                comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            salida, _ = proceso.communicate()
            datos = salida.decode("utf-8", errors="ignore").strip().split("\n")[1:]

            if not datos:
                return "Desconocido", "Desconocido"

            tipos = []
            mapa_ddr = {
                "20": "DDR",
                "21": "DDR2",
                "24": "DDR3",
                "26": "DDR4",
                "30": "DDR5",
                "34": "DDR5",
            }

            for linea in datos:
                partes = linea.split()
                tipo = "RAM"
                velocidad = ""
                for p in partes:
                    if p in mapa_ddr:
                        tipo = mapa_ddr[p]
                    elif p.isdigit() and int(p) > 400:
                        velocidad = f"{p} MHz"
                if velocidad:
                    tipo += f" - {velocidad}"
                tipos.append(tipo)

            return (
                tipos[0] if tipos else "Genérica"
            ), f"{len([d for d in datos if d.strip()])} Módulos"
        except:
            return "Genérica", "Sin datos"

    # ================= VISTAS =================

    def mostrar_resumen(self):
        self.ocultar_todo()
        f = self.frames["resumen"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="RESUMEN TÉCNICO", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )

        info = platform.uname()
        mem = psutil.virtual_memory()
        uptime_s = time.time() - psutil.boot_time()
        horas = int(uptime_s // 3600)

        # Detectives
        tipo_ram, slots = self.obtener_info_ram_avanzada()
        try:
            cmd = "wmic path win32_VideoController get Name"
            gpu = (
                subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
            )
        except:
            gpu = "Integrada"

        # Tarjetas
        self.crear_seccion(f, "Sistema")
        self.crear_tarjeta(f, "Equipo", info.node, "#2b2b2b")
        self.crear_tarjeta(f, "OS", f"{info.system} {info.release}", "#2b2b2b")
        self.crear_tarjeta(
            f,
            "Uptime",
            f"{horas} Horas, {int((uptime_s%3600)//60)} Min",
            "#eab308" if horas > 48 else "#2b2b2b",
        )

        self.crear_seccion(f, "Hardware")
        self.crear_tarjeta(f, "CPU", platform.processor(), "#1f6aa5")
        self.crear_tarjeta(f, "GPU", gpu, "#2b2b2b")
        self.crear_tarjeta(
            f, "RAM", f"{round(mem.total/(1024**3),2)} GB ({tipo_ram})", "#10b981"
        )

    def mostrar_cpu(self):
        self.ocultar_todo()
        f = self.frames["cpu"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="MONITOR DE CPU", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )
        self.crear_tarjeta(f, "Modelo", platform.processor(), "#1f6aa5")
        self.crear_tarjeta(
            f,
            "Núcleos",
            f"{psutil.cpu_count(False)} Físicos / {psutil.cpu_count(True)} Lógicos",
            "#2b2b2b",
        )

        ctk.CTkLabel(f, text="Carga:").pack(pady=(20, 5), anchor="w")
        self.prog_cpu = ctk.CTkProgressBar(
            f, width=500, height=25, progress_color="#3b82f6"
        )
        self.prog_cpu.pack(anchor="w")
        self.lbl_cpu = ctk.CTkLabel(f, text="...", font=("Arial", 16, "bold"))
        self.lbl_cpu.pack(anchor="w")

    def mostrar_ram(self):
        self.ocultar_todo()
        f = self.frames["ram"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="MEMORIA RAM", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )
        mem = psutil.virtual_memory()
        self.crear_tarjeta(f, "Total", f"{round(mem.total/(1024**3),2)} GB", "#10b981")

        ctk.CTkLabel(f, text="Uso:").pack(pady=(20, 5), anchor="w")
        self.prog_ram = ctk.CTkProgressBar(
            f, width=500, height=25, progress_color="#10b981"
        )
        self.prog_ram.pack(anchor="w")
        self.lbl_ram = ctk.CTkLabel(f, text="...", font=("Arial", 14))
        self.lbl_ram.pack(anchor="w")

    def mostrar_disco(self):
        self.ocultar_todo()
        f = self.frames["disco"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="ALMACENAMIENTO (C:)", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )
        try:
            d = psutil.disk_usage("C:\\")
            color = (
                "#10b981"
                if d.percent < 60
                else "#eab308" if d.percent < 85 else "#ef4444"
            )
            self.crear_tarjeta(
                f, "Total", f"{round(d.total/(1024**3),2)} GB", "#eab308"
            )
            self.crear_tarjeta(f, "Libre", f"{round(d.free/(1024**3),2)} GB", "#2b2b2b")
            self.crear_tarjeta(
                f, "Ocupado", f"{round(d.used/(1024**3),2)} GB ({d.percent}%)", color
            )
        except:
            ctk.CTkLabel(f, text="Error disco").pack()

    def mostrar_red(self):
        self.ocultar_todo()
        f = self.frames["red"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="CONECTIVIDAD", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "--"

        self.crear_tarjeta(f, "Equipo", platform.node(), "#2b2b2b")
        self.crear_tarjeta(f, "IP Local", ip, "#1f6aa5")

        self.lbl_down = ctk.CTkLabel(
            f, text="Bajada: ...", font=("Arial", 24, "bold"), text_color="#10b981"
        )
        self.lbl_down.pack(pady=20)
        self.lbl_up = ctk.CTkLabel(
            f, text="Subida: ...", font=("Arial", 24, "bold"), text_color="#3b82f6"
        )
        self.lbl_up.pack(pady=5)

    # --- NUEVA VISTA: HERRAMIENTAS ---
    def mostrar_herramientas(self):
        self.ocultar_todo()
        f = self.frames["herramientas"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="CAJA DE HERRAMIENTAS", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )
        ctk.CTkLabel(
            f, text="Accesos directos útiles para reparación:", text_color="gray"
        ).pack(pady=(0, 20), anchor="w")

        # Grid de botones
        grid_tools = ctk.CTkFrame(f, fg_color="transparent")
        grid_tools.pack(fill="x", expand=True)

        self.crear_btn_tool(grid_tools, "🛠️ Admin. de Dispositivos", "devmgmt.msc", 0, 0)
        self.crear_btn_tool(grid_tools, "📈 Admin. de Tareas", "taskmgr", 0, 1)
        self.crear_btn_tool(grid_tools, "🎛️ Panel de Control", "control", 1, 0)
        self.crear_btn_tool(grid_tools, "🧹 Liberar Espacio", "cleanmgr", 1, 1)
        self.crear_btn_tool(grid_tools, "🔧 Servicios", "services.msc", 2, 0)
        self.crear_btn_tool(grid_tools, "🔋 Energía", "powercfg.cpl", 2, 1)

    def crear_btn_tool(self, parent, text, command, r, c):
        btn = ctk.CTkButton(
            parent,
            text=text,
            height=50,
            font=("Arial", 14),
            fg_color="#2b2b2b",
            hover_color="#3b82f6",
            command=lambda: subprocess.Popen(command, shell=True),
        )
        btn.grid(row=r, column=c, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    # --- NUEVA VISTA: CONFIGURACIÓN Y ACERCA DE ---
    def mostrar_config(self):
        self.ocultar_todo()
        f = self.frames["config"]
        f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="CONFIGURACIÓN", font=("Arial", 20, "bold")).pack(
            pady=10, anchor="w"
        )

        # Opción 1: Tema
        ctk.CTkLabel(f, text="Apariencia de la Interfaz:").pack(
            anchor="w", pady=(10, 5)
        )
        seg_theme = ctk.CTkSegmentedButton(
            f,
            values=["Dark", "Light", "System"],
            command=lambda v: ctk.set_appearance_mode(v),
        )
        seg_theme.set("Dark")
        seg_theme.pack(fill="x", pady=5)

        # Opción 2: Velocidad
        ctk.CTkLabel(
            f, text="Velocidad de Actualización (Más rápido consume más CPU):"
        ).pack(anchor="w", pady=(20, 5))
        slider = ctk.CTkSlider(
            f, from_=0.2, to=3.0, number_of_steps=10, command=self.cambiar_velocidad
        )
        slider.set(self.refresh_rate)
        slider.pack(fill="x", pady=5)
        self.lbl_speed = ctk.CTkLabel(
            f, text=f"Actualizando cada: {self.refresh_rate} seg"
        )
        self.lbl_speed.pack()

        # --- SECCIÓN ACERCA DE ---
        ctk.CTkFrame(f, height=2, fg_color="gray40").pack(fill="x", pady=40)
        ctk.CTkLabel(f, text="ACERCA DE MATI-SPECS", font=("Arial", 16, "bold")).pack()
        ctk.CTkLabel(f, text="Desarrollado por Matías Fralasco © 2026").pack()
        ctk.CTkLabel(f, text="Versión 2.0 Gold Edition").pack()

        link = ctk.CTkLabel(
            f, text="github.com/matiasfralasco", text_color="#3b82f6", cursor="hand2"
        )
        link.pack(pady=5)
        link.bind(
            "<Button-1>", lambda e: webbrowser.open("https://github.com/matiasfralasco")
        )

    def cambiar_velocidad(self, valor):
        self.refresh_rate = round(valor, 1)
        self.lbl_speed.configure(text=f"Actualizando cada: {self.refresh_rate} seg")

    # --- LOGICA COMPARTIDA ---
    def crear_seccion(self, p, t):
        ctk.CTkLabel(p, text=t, font=("Arial", 14, "bold"), text_color="gray").pack(
            pady=(15, 5), anchor="w"
        )

    def crear_tarjeta(self, p, t, v, c):
        f = ctk.CTkFrame(p, fg_color=c, corner_radius=8)
        f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=t, font=("Arial", 12)).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(f, text=v, font=("Arial", 14, "bold")).pack(
            side="right", padx=15, pady=10
        )

    # --- BUCLE BACKEND ---
    def actualizar_datos(self):
        while self.running:
            try:
                # Usamos la variable de velocidad
                time.sleep(self.refresh_rate)

                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory()
                net = psutil.net_io_counters()

                up = (net.bytes_sent - self.last_upload) / 1024
                down = (net.bytes_recv - self.last_download) / 1024
                # Ajustamos la velocidad según el tiempo transcurrido (si refresco cada 2s, divido por 2)
                up /= self.refresh_rate
                down /= self.refresh_rate

                self.last_upload = net.bytes_sent
                self.last_download = net.bytes_recv

                if hasattr(self, "prog_cpu"):
                    self.prog_cpu.set(cpu / 100)
                    self.lbl_cpu.configure(text=f"{cpu}%")
                if hasattr(self, "prog_ram"):
                    self.prog_ram.set(mem.percent / 100)
                    self.lbl_ram.configure(
                        text=f"{round(mem.used/(1024**3),2)} GB / {round(mem.total/(1024**3),2)} GB"
                    )
                if hasattr(self, "lbl_down"):
                    self.lbl_up.configure(
                        text=(
                            f"Subida: {up:.1f} KB/s"
                            if up < 1000
                            else f"{up/1024:.1f} MB/s"
                        )
                    )
                    self.lbl_down.configure(
                        text=(
                            f"Bajada: {down:.1f} KB/s"
                            if down < 1000
                            else f"{down/1024:.1f} MB/s"
                        )
                    )
            except:
                pass

    def destroy(self):
        self.running = False
        super().destroy()


if __name__ == "__main__":
    app = MatiSpecsApp()
    app.mainloop()
