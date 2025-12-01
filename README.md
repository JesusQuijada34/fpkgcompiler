# FlangCompiler IT

**FlangCompiler IT** es un compilador y empaquetador automático para el ecosistema Flarm que genera binarios ejecutables y paquetes de release para Windows (Knosthalij) y Linux (Danenone) a partir de repositorios de código fuente.

## 🎯 Características

*   **Análisis Automático de Metadatos**: Lee el archivo `details.xml` para extraer información del proyecto (publicador, aplicación, versión, plataforma).
*   **Compilación Multiplataforma**: Compila scripts Python a ejecutables usando PyInstaller, con soporte para Windows (.exe) y Linux.
*   **Gestión Inteligente de Plataformas**: 
    *   **AlphaCube**: Compila para Windows y Linux.
    *   **Knosthalij**: Compila solo para Windows.
    *   **Danenone**: Compila solo para Linux.
*   **Empaquetado Automático**: Crea paquetes con la estructura correcta, excluyendo archivos innecesarios según la plataforma.
*   **Actualización de Metadatos**: Actualiza automáticamente el campo `platform` en el `details.xml` de cada paquete.
*   **Iconos Personalizados**: Soporta iconos específicos para cada script (Windows).

## 📋 Requisitos

*   Python 3.8+
*   PyInstaller
*   Los archivos del repositorio a compilar deben incluir:
    *   `details.xml` en la raíz (con metadatos del proyecto).
    *   Scripts Python en la raíz (ej. `flarmhandler.py`, `updater.py`).
    *   Carpeta `app/` con iconos (opcional, para Windows).
    *   Carpeta `assets/` con recursos (opcional).

## 🔄 Modo de Fallback (Sin PyQt5)

Si PyQt5 no está instalado en el sistema, FlangCompiler IT automáticamente activa el **modo CLI de fallback**:

### Comportamiento del Fallback

Cuando ejecutas el programa sin argumentos y PyQt5 no está disponible:

1. **Detección Automática**: El programa usa el directorio actual como proyecto
2. **Compilación Temporal**: Crea binarios en un directorio temporal del sistema
3. **Empaquetado Automático**: Genera el archivo `.iflapp` 
4. **Ubicación de Salida**: Guarda el `.iflapp` en el directorio padre del proyecto
5. **Limpieza**: Elimina automáticamente los archivos temporales

### Ejemplo de Uso en Modo Fallback

```bash
# Navega al directorio de tu proyecto
cd /ruta/a/tu/proyecto

# Ejecuta el compilador (sin PyQt5)
python compiler_full.py

# El archivo .iflapp se creará en el directorio padre
# Ejemplo: /ruta/a/Publisher.App.v1.0.Knosthalij.iflapp
```

### Requisitos para Modo Fallback

- El directorio actual debe contener un `details.xml` válido
- Debe existir el script principal especificado en `details.xml`
- PyInstaller debe estar instalado


## 🚀 Uso

### Instalación de Dependencias

**En Linux:**

PyInstaller se instalará automáticamente si no está disponible. El compilador:
- Instalará `python3-full`, `python3-venv` y `pipx` mediante `apt` (requiere `sudo`)
- Creará un entorno virtual en `$HOME/venv-pyinstaller`
- Instalará PyInstaller en el entorno virtual

**En Windows:**

```bash
pip install pyinstaller
```

**Opcional (para interfaz gráfica en ambas plataformas):**

```bash
pip install PyQt5
```

### Ejecución del Compilador

**Modo 1: Con PyQt5 (Interfaz Gráfica)**

```bash
python compiler_full.py
# Abre la interfaz gráfica
```

**Modo 2: Sin PyQt5 (Fallback Automático - Directorio Actual)**

```bash
cd /ruta/a/proyecto
python compiler_full.py
# Compila automáticamente el directorio actual
# Salida: ../Publisher.App.Version.Platform.iflapp
```

**Modo 3: CLI Explícito (Con o sin PyQt5)**

```bash
python compiler_full.py <ruta_repositorio> [--output <ruta_salida>]
```

**Ejemplo:**

```bash
python compiler_full.py /home/ubuntu/flarmhandler --output /home/ubuntu/releases
```


## 📦 Estructura de Salida

El compilador genera paquetes con el siguiente formato de nombre:

```
{publicador}.{aplicación}.{versión}.{plataforma}
```

**Ejemplo:**

```
Influent.flarmhandler.v1.0-25.11-21.15.Danenone
Influent.flarmhandler.v1.0-25.11-21.15.Knosthalij
```

Cada paquete contiene:

*   Binarios compilados (ejecutables de Linux o .exe de Windows).
*   Scripts Python originales.
*   Archivos de configuración y documentación (`README.md`, `CHANGELOG.md`, `LICENSE`).
*   Carpetas de recursos (`assets/`, `app/`, `config/`, `docs/`, `source/`).
*   `details.xml` actualizado con la plataforma correcta.

## 🔧 Módulos

### `compiler.py`

Script principal que orquesta todo el proceso de compilación y empaquetado.

**Clases principales:**

*   `FlangCompiler`: Clase principal que maneja el análisis, compilación y empaquetado.

### `linux_compiler.py`

Módulo especializado para compilación en Linux (Danenone).

**Clases principales:**

*   `LinuxCompiler`: Maneja la compilación específica para Linux.

### `windows_compiler.py`

Módulo especializado para compilación en Windows (Knosthalij).

**Clases principales:**

*   `WindowsCompiler`: Maneja la compilación específica para Windows.

## 📝 Flujo de Trabajo

1.  **Análisis del XML**: Se lee `details.xml` para obtener metadatos.
2.  **Identificación de Scripts**: Se buscan scripts Python en la raíz del repositorio.
3.  **Compilación Condicional**:
    *   Si la plataforma es **AlphaCube**, se compila para Windows y Linux.
    *   Si la plataforma es **Knosthalij**, se compila solo para Windows.
    *   Si la plataforma es **Danenone**, se compila solo para Linux.
4.  **Empaquetado**: Se crea un paquete para cada plataforma con los binarios compilados.
5.  **Actualización de Metadatos**: Se actualiza el campo `platform` en el `details.xml` de cada paquete.

## 🔍 Detalles Técnicos

### Búsqueda de Iconos

Para cada script, el compilador busca iconos en la carpeta `app/`:

*   **Script Principal** (ej. `flarmhandler.py`):
    *   `app/flarmhandler-icon.ico`
    *   `app/app-icon.ico` (fallback)
*   **Scripts Secundarios** (ej. `updater.py`):
    *   `app/updater-icon.ico`

### Exclusión de Archivos

**Para Linux (Danenone):**

*   `*.bat`
*   `requirements.txt`
*   `*.exe`

**Para Windows (Knosthalij):**

*   `*.sh`
*   `requirements.txt`

### Compilación Multiplataforma

*   **En Linux**: Se puede compilar para Linux. Para Windows, se generan scripts batch (`build_windows.bat`) que deben ejecutarse en Windows.
*   **En Windows**: Se puede compilar para Windows. Para Linux, se generan scripts bash (`build_linux.sh`) que deben ejecutarse en Linux.

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado por **Manus AI** para el ecosistema Flarm.

---

**Nota**: FlangCompiler IT es una herramienta de desarrollo. Para obtener los mejores resultados, asegúrese de que su repositorio tenga una estructura adecuada con los archivos necesarios (`details.xml`, scripts Python, iconos, etc.).
