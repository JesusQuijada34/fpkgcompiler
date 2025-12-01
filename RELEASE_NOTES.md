# Release Notes - FlangCompiler IT v1.2.0

**Fecha de Lanzamiento**: 30 de Noviembre, 2025

## 🎉 Novedades Principales

### Instalación Automática de PyInstaller en Linux

FlangCompiler IT ahora **instala PyInstaller automáticamente** en sistemas Linux cuando no está disponible. Esta característica elimina la necesidad de configuración manual y mejora significativamente la experiencia del usuario.

#### Características Principales:

- ✅ Detección automática de PyInstaller antes de compilar
- ✅ Instalación de dependencias del sistema (`python3-full`, `python3-venv`, `pipx`)
- ✅ Creación de entorno virtual en `$HOME/venv-pyinstaller`
- ✅ Instalación de PyInstaller en el entorno virtual
- ✅ Uso automático del entorno virtual para compilaciones

## 📋 Cambios Detallados

### Nuevas Funcionalidades

#### 1. Verificación Automática de PyInstaller

El compilador ahora verifica la disponibilidad de PyInstaller antes de iniciar la compilación:

```
[INFO] PyInstaller encontrado: 6.3.0
```

O si no está instalado:

```
[INFO] PyInstaller no encontrado: [Errno 2] No such file or directory: 'pyinstaller'
[INFO] PyInstaller no encontrado. Iniciando instalación automática...
```

#### 2. Instalación Automática en Linux

Cuando PyInstaller no está disponible en Linux, el compilador ejecuta automáticamente:

```
[INFO] 🔧 Instalando PyInstaller en Linux...
[INFO] 🔧 Instalando python3-full, python3-venv y pipx...
[OK] ✅ Dependencias del sistema instaladas
[INFO] 🔧 Configurando pipx...
[INFO] 🧪 Creando entorno virtual en /home/usuario/venv-pyinstaller...
[OK] ✅ Entorno virtual creado
[INFO] 📦 Actualizando pip...
[INFO] 📦 Instalando PyInstaller...
[OK] ✅ PyInstaller instalado
[OK] ✅ PyInstaller instalado correctamente. Versión: 6.3.0
[INFO] 🎉 Entorno listo. PyInstaller disponible en el entorno virtual.
```

#### 3. Uso del Entorno Virtual

Una vez instalado, todas las compilaciones utilizan automáticamente el PyInstaller del entorno virtual, garantizando consistencia y aislamiento.

## 🚀 Guía de Uso

### En Linux (Primera Vez)

```bash
cd /ruta/a/tu/proyecto
python fpkgcompiler.py

# El programa solicitará sudo para instalar dependencias del sistema
# Después, todo se configura automáticamente
```

**Salida esperada:**
```
[INFO] PyInstaller no encontrado. Iniciando instalación automática...
[sudo] password for usuario: 
[INFO] 🔧 Instalando python3-full, python3-venv y pipx...
[OK] ✅ Dependencias del sistema instaladas
...
[OK] ✅ PyInstaller instalado correctamente. Versión: 6.3.0
[INFO] Iniciando compilación para Linux...
```

### En Linux (Usos Posteriores)

```bash
cd /ruta/a/tu/proyecto
python fpkgcompiler.py

# PyInstaller ya está instalado, la compilación inicia directamente
```

**Salida esperada:**
```
[INFO] PyInstaller encontrado: 6.3.0
[INFO] Iniciando compilación para Linux...
```

### En Windows

```bash
# En Windows, PyInstaller debe instalarse manualmente
pip install pyinstaller

python fpkgcompiler.py
```

## 🔧 Detalles Técnicos

### Nuevos Métodos en FlangCompiler

1. **`_check_pyinstaller_installed()`**
   - Verifica si PyInstaller está disponible ejecutando `pyinstaller --version`
   - Retorna `True` si está instalado, `False` en caso contrario

2. **`_install_pyinstaller_linux()`**
   - Instala dependencias del sistema usando `sudo apt install`
   - Crea entorno virtual en `$HOME/venv-pyinstaller`
   - Instala PyInstaller usando pip del entorno virtual
   - Verifica la instalación

3. **`_ensure_pyinstaller()`**
   - Orquesta la verificación e instalación
   - Se ejecuta automáticamente antes de cada compilación

### Flujo de Instalación

1. **Verificación**: Ejecuta `pyinstaller --version`
2. **Detección de SO**: Si no está instalado, verifica que sea Linux
3. **Instalación de Sistema**: `sudo apt install -y python3-full python3-venv pipx`
4. **Configuración de pipx**: `pipx ensurepath`
5. **Entorno Virtual**: `python3 -m venv $HOME/venv-pyinstaller`
6. **Actualización de pip**: `$HOME/venv-pyinstaller/bin/pip install --upgrade pip`
7. **Instalación de PyInstaller**: `$HOME/venv-pyinstaller/bin/pip install pyinstaller`
8. **Verificación**: `$HOME/venv-pyinstaller/bin/pyinstaller --version`

### Cambios en el Código

**Archivo modificado**: `fpkgcompiler.py`

**Nuevos atributos**:
- `self.venv_path`: Almacena la ruta del entorno virtual

**Métodos modificados**:
- `compile_binaries()`: Llama a `_ensure_pyinstaller()` antes de compilar
- `_compile_linux_binary()`: Usa PyInstaller del entorno virtual si está disponible
- `_compile_windows_binary()`: Usa PyInstaller del entorno virtual si está disponible (en Linux)

## 📦 Requisitos

### Linux
- Python 3.8 o superior
- `sudo` para instalación de dependencias del sistema (solo primera vez)
- PyInstaller se instala automáticamente

### Windows
- Python 3.8 o superior
- PyInstaller (instalación manual): `pip install pyinstaller`

### Opcional (Ambas Plataformas)
- PyQt5 (para interfaz gráfica): `pip install PyQt5`

## ⚠️ Notas Importantes

### Permisos de Sudo

La primera vez que se ejecuta en Linux sin PyInstaller, el programa solicitará la contraseña de sudo para instalar:
- `python3-full`
- `python3-venv`
- `pipx`

Estos paquetes son necesarios para crear el entorno virtual.

### Ubicación del Entorno Virtual

El entorno virtual se crea en: `$HOME/venv-pyinstaller`

Este directorio persiste entre ejecuciones, por lo que la instalación solo ocurre una vez.

### Compatibilidad

- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ Linux Mint 20+
- ✅ Otras distribuciones basadas en Debian/Ubuntu con `apt`
- ⚠️ Distribuciones no basadas en Debian requieren instalación manual de PyInstaller

## 🐛 Correcciones

- Manejo robusto de errores durante la instalación de PyInstaller
- Verificación de versión después de la instalación
- Mensajes informativos mejorados durante el proceso

## 📝 Notas de Migración

### Desde v1.1.0

No se requieren cambios. La nueva funcionalidad es completamente retrocompatible.

### Usuarios de Linux

Si ya tienen PyInstaller instalado globalmente o en un entorno virtual activado, el compilador lo detectará y usará esa instalación sin crear un nuevo entorno virtual.

## 🎯 Casos de Uso

### Desarrollo en Servidores Linux

Ideal para compilar en servidores Linux sin configuración previa:

```bash
ssh usuario@servidor
cd ~/proyecto
python ~/tools/fpkgcompiler.py
# Primera vez: instala PyInstaller automáticamente
# Siguientes veces: usa PyInstaller del entorno virtual
```

### Integración CI/CD

Perfecto para pipelines de integración continua en Linux:

```yaml
# .github/workflows/build.yml
- name: Build Flarm Package
  run: |
    cd ${{ github.workspace }}
    python fpkgcompiler.py
    # PyInstaller se instala automáticamente si es necesario
```

### Entornos Limpios

Útil para trabajar en entornos limpios sin contaminar el sistema con dependencias globales.

---

**Desarrollado por**: Manus AI  
**Licencia**: MIT  
**Versión**: 1.2.0  
**Fecha**: 30 de Noviembre, 2025
