from setuptools import setup, find_packages

setup(
    name="OneClickDNS",
    version="1.0.1",
    author="gfrodriguez",
    description="Herramienta de código abierto para gestión segura de servidores DNS en Windows. Permite cambiar fácilmente entre proveedores de DNS confiables.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["dnspython"],
    entry_points={"gui_scripts": ["oneclickdns = main:main"]},
)
