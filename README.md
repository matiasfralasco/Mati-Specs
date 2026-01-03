# Mati-Specs | Suite de Diagnóstico de Hardware

**Mati-Specs** es una herramienta portátil de diagnóstico y monitoreo de hardware desarrollada en Python. Diseñada para técnicos y entusiastas, ofrece una interfaz moderna y oscura para visualizar el estado de la PC en tiempo real.

![Estado del Proyecto](https://img.shields.io/badge/Estado-Terminado-green) ![Python](https://img.shields.io/badge/Python-3.14-blue)

## 🚀 Características

* **📊 Resumen Técnico:** Detección automática de SO, Uptime (tiempo encendido), y hardware principal.
* **🧠 Monitor de CPU:** Visualización de núcleos lógicos/físicos y carga en tiempo real.
* **💾 Analizador de RAM:** Identifica tecnología (DDR3/DDR4/DDR5), velocidad (MHz) y módulos instalados.
* **💿 Salud de Almacenamiento:** Sistema de "Semáforo" (Verde/Naranja/Rojo) según la ocupación del disco.
* **📡 Velocímetro de Red:** Medidor de subida y bajada en vivo (KB/s o MB/s) e IP Local.
* **🛠️ Caja de Herramientas:** Accesos directos a utilidades de Windows (Admin de Tareas, Servicios, Panel de Control).
* **⚙️ Personalización:** Modo Claro/Oscuro y control de velocidad de refresco.

## 🛠️ Tecnologías Usadas

* **Python 3.14** (Lenguaje base)
* **CustomTkinter** (Interfaz gráfica moderna)
* **Psutil** (Lectura de sensores y hardware)
* **WMI / Subprocess** (Consultas profundas al sistema)

## 📥 Instalación y Uso

### Opción A: Ejecutable Portable (Recomendado)
Descarga el archivo `Mati-Specs.exe` desde la sección de **Releases** (próximamente). No requiere instalación.

### Opción B: Código Fuente
1.  Clona el repositorio:
    ```bash
    git clone [https://github.com/matiasfralasco/Mati-Specs.git](https://github.com/matiasfralasco/Mati-Specs.git)
    ```
2.  Instala las dependencias:
    ```bash
    pip install customtkinter psutil
    ```
3.  Ejecuta el programa:
    ```bash
    python main.py
    ```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.

---
Desarrollado con ❤️ por **Matías Fralasco**.