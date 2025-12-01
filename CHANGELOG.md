# Changelog - FlangCompiler IT

Todas las mejoras y cambios notables en este proyecto serán documentados en este archivo.

## [v1.1.0] - 2025-11-30

### ✨ Añadido

*   **Modo de Fallback Automático sin PyQt5**:
    *   Detección automática cuando PyQt5 no está instalado
    *   Uso del directorio actual como proyecto cuando no se proporciona argumento
    *   Compilación en directorio temporal del sistema (`tempfile.mkdtemp()`)
    *   Empaquetado automático en archivo `.iflapp`
    *   Salida del `.iflapp` en directorio padre del proyecto
    *   Limpieza automática de archivos temporales con `shutil.rmtree()`

*   **Mejoras en CLI**:
    *   Mensajes informativos detallados sobre el modo de fallback
    *   Indicadores de progreso para ubicaciones de directorios
    *   Validación de `details.xml` en directorio actual
    *   Mensajes de error mejorados con opciones de solución

### ⚡ Mejorado

*   Experiencia de usuario cuando PyQt5 no está disponible
*   Gestión de directorios temporales con limpieza automática
*   Mensajes de log más descriptivos para debugging
*   Manejo robusto de errores con limpieza garantizada

### 🔧 Técnico

*   Importación del módulo `tempfile` para directorios temporales seguros
*   Separación de directorio de compilación y directorio de salida final
*   Movimiento automático de `.iflapp` al directorio padre
*   Limpieza con `shutil.rmtree()` con manejo de errores (`ignore_errors=True`)
*   Validación de existencia de archivos antes de sobrescribir

---

## [v1.0.0] - 2025-11-29

### ✨ Añadido

*   **Compilador Principal (`compiler.py`)**:
    *   Análisis automático de `details.xml` para extraer metadatos del proyecto.
    *   Identificación de scripts Python en la raíz del repositorio.
    *   Búsqueda inteligente de iconos en la carpeta `app/` para cada script.
    *   Compilación condicional basada en la plataforma especificada (AlphaCube, Knosthalij, Danenone).
    *   Creación de paquetes con estructura correcta para cada plataforma.
    *   Actualización automática del campo `platform` en el `details.xml` de cada paquete.

*   **Módulo de Compilación para Linux (`linux_compiler.py`)**:
    *   Compilación de scripts Python a ejecutables de Linux usando PyInstaller.
    *   Copia de binarios compilados al paquete.
    *   Exclusión de archivos innecesarios para Linux (`.bat`, `requirements.txt`, `.exe`).

*   **Módulo de Compilación para Windows (`windows_compiler.py`)**:
    *   Compilación de scripts Python a ejecutables de Windows (.exe) usando PyInstaller.
    *   Soporte para iconos personalizados en Windows.
    *   Copia de ejecutables compilados al paquete.
    *   Exclusión de archivos innecesarios para Windows (`.sh`, `requirements.txt`).

*   **Gestión de Plataformas**:
    *   **AlphaCube**: Compila para Windows (Knosthalij) y Linux (Danenone).
    *   **Knosthalij**: Compila solo para Windows.
    *   **Danenone**: Compila solo para Linux.

*   **Empaquetado Automático**:
    *   Copia de archivos relevantes (scripts, recursos, documentación) al paquete.
    *   Exclusión inteligente de archivos de compilación y configuración.
    *   Actualización de metadatos en el `details.xml` de cada paquete.

*   **Documentación**:
    *   `README.md` con instrucciones de uso y características.
    *   `CHANGELOG.md` para documentar cambios.

### ⚡ Mejorado

*   Detección automática de la plataforma actual (Windows, Linux, Darwin).
*   Generación de scripts de compilación para plataformas cruzadas (cuando se compila en una plataforma diferente a la de destino).
*   Manejo robusto de errores y excepciones durante la compilación.

### 🐛 Corregido

*   Validación de la existencia de `details.xml` antes de procesarlo.
*   Manejo correcto de rutas en diferentes sistemas operativos.

---

## Notas de Desarrollo

*   El compilador está diseñado para ser extensible. Se pueden agregar nuevos módulos de compilación para soportar otras plataformas.
*   La lógica de exclusión de archivos se puede personalizar según las necesidades del proyecto.
*   Se recomienda usar un entorno virtual de Python para evitar conflictos de dependencias.

---

**Autor**: Manus AI  
**Licencia**: MIT
