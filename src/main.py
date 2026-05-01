# src/main.py
"""
OneClickDNS - Gestor de DNS
Este módulo implementa una aplicación gráfica para Windows que permite gestionar de forma sencilla los servidores DNS de los adaptadores de red del sistema. Incluye funciones para aplicar y restablecer configuraciones DNS, así como una interfaz gráfica basada en Tkinter y un icono de bandeja del sistema usando pystray.
Funciones principales:
- Elevación automática de privilegios de administrador.
- Obtención de adaptadores de red disponibles mediante 'netsh'.
- Aplicación y restablecimiento de DNS usando presets definidos externamente.
- Validación de presets DNS antes de aplicar cambios.
- Interfaz gráfica para seleccionar adaptador y proveedor DNS.
- Integración con la bandeja del sistema para minimizar la ventana principal.
Dependencias:
- pystray
- Pillow (PIL)
- tkinter
- dns_logic (módulo propio con lógica de DNS)
"""

import os
import sys
import ctypes
import subprocess
import pystray
import threading
from PIL import Image
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from dns_logic import dns_presets, aplicar_dns, quitar_dns, validar_preset

CREATE_NO_WINDOW = 0x08000000


# --- Elevación automática ---
def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not es_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1
    )
    sys.exit()


# --- Obtener adaptadores ---
def obtener_adaptadores():
    try:
        resultado = subprocess.run(
            ["netsh", "interface", "show", "interface"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=False,
            check=True,
            creationflags=CREATE_NO_WINDOW,
        )
        adaptadores = []
        for linea in resultado.stdout.splitlines()[3:]:
            if "Conectado" in linea or "Connected" in linea:
                partes = linea.split()
                if len(partes) >= 4:
                    nombre = " ".join(partes[3:])
                    adaptadores.append(nombre)
        return adaptadores if adaptadores else ["Ethernet", "Wi-Fi"]
    except subprocess.CalledProcessError:
        estado.set("No se pudieron obtener adaptadores.")
        return []


# --- Acciones GUI ---
def aplicar_dns_gui():
    adaptador = adaptador_seleccionado.get()
    preset_nombre = dns_seleccionado.get()
    if not adaptador or not preset_nombre:
        estado.set("Seleccione un adaptador y un proveedor de DNS.")
        return

    preset = next((p for p in dns_presets if p["nombre"] == preset_nombre), None)
    if not preset:
        estado.set("Proveedor DNS no encontrado")
        return

    errores = validar_preset(preset)
    if errores:
        estado.set(f"Error en preset: {errores[0]}")
        return

    aplicar_dns(adaptador, preset)
    estado.set(f"DNS de '{preset_nombre}' aplicados correctamente.")


def quitar_dns_gui():
    adaptador = adaptador_seleccionado.get()
    if not adaptador:
        estado.set("Seleccione un adaptador de red.")
        return
    quitar_dns(adaptador)
    estado.set(f"DNS restablecidos en {adaptador}.")


def refrescar_adaptadores():
    adaptadores = obtener_adaptadores()

    if not adaptadores:
        ventana.quit()
        return
    menu_adaptadores["menu"].delete(0, "end")
    for adaptador in adaptadores:
        menu_adaptadores["menu"].add_command(
            label=adaptador,
            command=lambda valor=adaptador: adaptador_seleccionado.set(valor),
        )
    adaptador_seleccionado.set(adaptadores[0])


# --- GUI ---
def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ICON_MAIN = resource_path("assets/icons/icon.ico")
ICON_TRAY = resource_path("assets/icons/tray_icon.ico")


# Clase ToolTip mejorada
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# --- Ventana principal ---
ventana = tk.Tk()
ventana.title("OneClickDNS - Gestor de DNS")
try:
    ventana.iconbitmap(ICON_MAIN)
except Exception:
    pass
ventana.geometry("350x250")
ventana.resizable(False, False)

# Adaptador de red
adaptador_seleccionado = tk.StringVar()
tk.Label(ventana, text="Adaptador de red:").pack(pady=5)
menu_adaptadores = tk.OptionMenu(ventana, adaptador_seleccionado, "")
menu_adaptadores.config(width=50)
menu_adaptadores.pack(pady=5)
tk.Button(ventana, text="Refrescar adaptadores", command=refrescar_adaptadores).pack(
    pady=5
)

# Proveedor de DNS
dns_seleccionado = tk.StringVar()
tk.Label(ventana, text="Proveedor de DNS:").pack(pady=5)
menu_dns = tk.OptionMenu(ventana, dns_seleccionado, *[p["nombre"] for p in dns_presets])
menu_dns.config(width=50)
menu_dns.pack(pady=5)

# Frame para los botones
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

btn_aplicar = tk.Button(frame_botones, text="Aplicar DNS", command=aplicar_dns_gui)
btn_aplicar.grid(row=0, column=0, padx=5)
ToolTip(btn_aplicar, "Aplica el DNS seleccionado al adaptador elegido.")

btn_restablecer = tk.Button(
    frame_botones, text="Restablecer DNS (DHCP)", command=quitar_dns_gui
)
btn_restablecer.grid(row=0, column=1, padx=5)
ToolTip(btn_restablecer, "Restablece el DNS del adaptador a DHCP.")

# Label de estado en la parte inferior
estado = tk.StringVar()
estado.set("Listo")
label_estado = tk.Label(ventana, textvariable=estado, anchor="w", relief="sunken")
label_estado.pack(side="bottom", fill="x")


# --- Icono de bandeja ---
def crear_icono_tray():
    image = Image.open(ICON_TRAY)
    menu = pystray.Menu(
        pystray.MenuItem("Abrir OneClickDNS", lambda: abrir_app()),
        pystray.MenuItem("Salir", lambda: salir_app()),
    )
    return pystray.Icon("OneClickDNS", image, "OneClickDNS - Gestor de DNS", menu)


def abrir_app():
    ventana.deiconify()  # Muestra la ventana
    icono_tray.stop()  # Elimina el ícono de la bandeja


def salir_app():
    icono_tray.stop()  # Detiene el ícono
    ventana.destroy()  # Cierra la aplicación


# --- Icono de bandeja ---
def minimizar_a_tray():
    ventana.withdraw()  # Oculta la ventana principal
    global icono_tray
    icono_tray = crear_icono_tray()
    threading.Thread(
        target=icono_tray.run, daemon=True
    ).start()  # Ejecuta el icono en segundo plano


refrescar_adaptadores()
ventana.protocol("WM_DELETE_WINDOW", minimizar_a_tray)
ventana.mainloop()
