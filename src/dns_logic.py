# src/dns_logic.py
"""
dns_logic.py
Este módulo proporciona funciones para gestionar y aplicar configuraciones de servidores DNS en adaptadores de red de Windows. Incluye una lista de preajustes de DNS, validadores de direcciones IP y conectividad DNS, así como funciones para aplicar, quitar y registrar cambios de DNS en el sistema.
Funciones principales:
- es_ip_valida(ip): Verifica si una cadena es una dirección IP válida (IPv4 o IPv6).
- dns_responde(dns_ip): Comprueba si un servidor DNS responde correctamente a consultas A y AAAA.
- validar_preset(preset): Valida las direcciones IP y la respuesta de los servidores en un preajuste DNS.
- aplicar_dns(adaptador, preset): Aplica los servidores DNS especificados en el preajuste al adaptador de red dado.
- quitar_dns(adaptador): Restablece la configuración DNS del adaptador a DHCP.
- registrar_cambio(adaptador, preset_nombre): Registra en un archivo de log los cambios realizados en la configuración DNS.
Constantes:
- dns_presets: Lista de diccionarios con preajustes de servidores DNS populares y de protección familiar.
- CREATE_NO_WINDOW: Bandera para ejecutar procesos de consola sin mostrar ventana.
Requiere:
- Windows con utilidades 'netsh'.
- Paquetes: subprocess, ipaddress, dns.resolver, os, datetime.
"""

import subprocess
import ipaddress
import dns.resolver
import os
from datetime import datetime

CREATE_NO_WINDOW = 0x08000000

# ------------------- Lista de DNS -------------------
dns_presets = [
    {
        "nombre": "AdGuard - Servidores predeterminados",
        "ipv4": ["94.140.14.14", "94.140.15.15"],
        "ipv6": ["2a10:50c0::ad1:ff", "2a10:50c0::ad2:ff"],
    },
    {
        "nombre": "AdGuard - Servidores sin filtrado",
        "ipv4": ["94.140.14.140", "94.140.14.141"],
        "ipv6": ["2a10:50c0::1:ff", "2a10:50c0::2:ff"],
    },
    {
        "nombre": "AdGuard - Protección familiar",
        "ipv4": ["94.140.14.15", "94.140.15.16"],
        "ipv6": ["2a10:50c0::bad1:ff", "2a10:50c0::bad2:ff"],
    },
    {
        "nombre": "CleanBrowsing - Filtro familiar",
        "ipv4": ["185.228.168.168", "185.228.169.168"],
        "ipv6": ["2a0d:2a00:1::", "2a0d:2a00:2::"],
    },
    {
        "nombre": "CleanBrowsing - Filtro para adultos",
        "ipv4": ["185.228.168.10", "185.228.169.11"],
        "ipv6": ["2a0d:2a00:1::1", "2a0d:2a00:2::1"],
    },
    {
        "nombre": "OpenDNS - Protección familiar",
        "ipv4": ["208.67.222.123", "208.67.220.123"],
        "ipv6": [],
    },
    {
        "nombre": "Yandex - Protección familiar",
        "ipv4": ["77.88.8.7", "77.88.8.3"],
        "ipv6": ["2a02:6b8::feed:bad", "2a02:6b8:0:1::feed:bad"],
    },
    {
        "nombre": "Neustar - Protección familiar",
        "ipv4": ["156.154.70.3", "156.154.71.3"],
        "ipv6": [],
    },
]

# ------------------- Validadores -------------------


def es_ip_valida(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def dns_responde(dns_ip):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_ip]
    try:
        resolver.resolve("google.com", "A", lifetime=3)
        resolver.resolve("google.com", "AAAA", lifetime=3)
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False


def validar_preset(preset):
    errores = []
    for ip in preset["ipv4"]:
        if not es_ip_valida(ip):
            errores.append(f"{ip} tiene un formato inválido.")
        elif not dns_responde(ip):
            errores.append(f"{ip} no respondió correctamente.")
    for ip in preset["ipv6"]:
        if not es_ip_valida(ip):
            errores.append(f"{ip} tiene un formato inválido.")
    return errores


# ------------------- Aplicación de DNS -------------------


def aplicar_dns(adaptador, preset):
    subprocess.run(
        [
            "netsh",
            "interface",
            "ipv4",
            "set",
            "dns",
            f"name={adaptador}",
            "static",
            preset["ipv4"][0],
        ],
        shell=False,
        creationflags=CREATE_NO_WINDOW,
    )

    if len(preset["ipv4"]) > 1:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "add",
                "dns",
                f"name={adaptador}",
                preset["ipv4"][1],
                "index=2",
            ],
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )

    if preset["ipv6"]:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv6",
                "set",
                "dnsservers",
                adaptador,
                "static",
                preset["ipv6"][0],
            ],
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )
        if len(preset["ipv6"]) > 1:
            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "ipv6",
                    "add",
                    "dnsservers",
                    adaptador,
                    preset["ipv6"][1],
                    "index=2",
                ],
                shell=False,
                creationflags=CREATE_NO_WINDOW,
            )
    else:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv6",
                "set",
                "dnsservers",
                adaptador,
                "source=dhcp",
            ],
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )

    registrar_cambio(adaptador, preset["nombre"])


def quitar_dns(adaptador):
    subprocess.run(
        [
            "netsh",
            "interface",
            "ipv4",
            "set",
            "dnsservers",
            f"name={adaptador}",
            "source=dhcp",
        ],
        shell=False,
        creationflags=CREATE_NO_WINDOW,
    )
    subprocess.run(
        ["netsh", "interface", "ipv6", "set", "dnsservers", adaptador, "source=dhcp"],
        shell=False,
        creationflags=CREATE_NO_WINDOW,
    )
    registrar_cambio(adaptador, "DNS Restablecidos (DHCP)")


# ------------------- Logging -------------------


def registrar_cambio(adaptador, preset_nombre):
    log_dir = os.path.join(os.getenv("APPDATA"), "OneClickDNS")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "dns_changes.log")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {adaptador}: {preset_nombre}\n")
