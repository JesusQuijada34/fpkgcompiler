# Release Notes - FlangCompiler IT v1.1.0

**Fecha de Lanzamiento**: 30 de Noviembre, 2025

## 🎉 Novedades Principales

### Modo de Fallback Automático (Sin PyQt5)

FlangCompiler IT ahora funciona perfectamente **sin necesidad de PyQt5**. Si la librería no está instalada, el programa automáticamente activa un modo CLI inteligente que:

- ✅ Detecta el proyecto en el directorio actual
- ✅ Compila binarios en ubicación temporal
- ✅ Empaqueta todo en formato `.iflapp`
- ✅ Guarda el resultado en el directorio padre
- ✅ Limpia archivos temporales automáticamente

## 📋 Cambios Detallados

### Nuevas Funcionalidades

#### 1. Detección Inteligente de Entorno

El compilador ahora verifica la disponibilidad de PyQt5 al inicio:

```
[WARN] PyQt5 no está instalado.
[INFO] Activando modo CLI automático...
[INFO] Usando directorio actual como proyecto...
```

#### 2. Gestión de Directorios Temporales

- **Creación**: Usa `tempfile.mkdtemp()` para crear directorios seguros
- **Ubicación**: Sistema temp del OS (ej: `C:\Users\...\AppData\Local\Temp\flangcompiler_xxxxx\` en Windows, `/tmp/flangcompiler_xxxxx/` en Linux)
- **Limpieza**: Eliminación automática después de empaquetar

#### 3. Salida en Directorio Padre

Los archivos `.iflapp` se guardan automáticamente en el directorio padre:

```
Estructura:
/proyectos/
├── mi_app/              (directorio actual)
│   ├── details.xml
│   ├── app.py
│   └── assets/
└── Publisher.App.v1.0.Knosthalij.iflapp  ← Salida aquí
```

### Mejoras de Usabilidad

- **Mensajes Informativos**: Logs detallados sobre ubicaciones y procesos
- **Manejo de Errores**: Limpieza de temporales incluso si falla la compilación
- **Validación**: Verifica que el directorio actual tenga `details.xml` válido
- **Compatibilidad**: Funciona en Windows y Linux sin cambios

## 🚀 Guía de Uso

### Escenario 1: Con PyQt5 Instalado

```bash
python compiler_full.py
# Abre interfaz gráfica
```

### Escenario 2: Sin PyQt5 (Nuevo - Modo Fallback)

```bash
cd /ruta/a/tu/proyecto
python compiler_full.py
# Compila automáticamente y crea .iflapp en directorio padre
```

**Salida esperada:**
```
[WARN] PyQt5 no está instalado.
[INFO] Activando modo CLI automático...
[INFO] Usando directorio actual como proyecto...

[INFO] Directorio de proyecto: C:\Users\...\mi_proyecto
[INFO] Directorio temporal de compilación: C:\Users\...\Temp\flangcompiler_abc123
[INFO] Directorio de salida final: C:\Users\...\

--- Iniciando Compilación ---

[INFO] Metadatos extraídos:
  - Publicador: MiPublisher
  - Aplicación: MiApp
  - Versión: v1.0
  - Plataforma: Knosthalij

[INFO] Compilando script: MiApp...
[OK] MiApp compilado correctamente.
[INFO] Creando paquete para Windows...
[OK] Archivo .iflapp creado: ...

============================================================
[OK] ¡Compilación exitosa!
[OK] Paquete creado: C:\Users\...\MiPublisher.MiApp.v1.0.Knosthalij.iflapp
============================================================
[INFO] Directorio temporal limpiado
```

### Escenario 3: CLI Explícito

```bash
python compiler_full.py /ruta/proyecto --output /ruta/salida
# Funciona igual que antes
```

## 🔧 Detalles Técnicos

### Flujo de Fallback

1. **Detección**: Verifica `HAS_PYQT5` flag (línea 54)
2. **Validación**: Confirma que directorio actual tiene `details.xml`
3. **Temp Setup**: Crea `tempfile.mkdtemp(prefix="flangcompiler_")`
4. **Compilación**: Ejecuta PyInstaller en directorio temporal
5. **Empaquetado**: Crea `.iflapp` en directorio temporal
6. **Movimiento**: Mueve `.iflapp` a directorio padre
7. **Limpieza**: Elimina directorio temporal con `shutil.rmtree(ignore_errors=True)`

### Cambios en el Código

**Archivo modificado**: `compiler_full.py`

**Líneas modificadas**:
- Línea 42: Añadido `import tempfile`
- Líneas 1303-1377: Implementación completa del modo fallback

**Nuevas características**:
- Validación de `details.xml` en directorio actual
- Creación de directorio temporal seguro
- Movimiento de `.iflapp` a directorio padre
- Limpieza garantizada con bloques `try-except-finally`

### Compatibilidad

- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ Python 3.8+
- ✅ Con o sin PyQt5

## 📦 Requisitos

### Obligatorios
- Python 3.8 o superior
- PyInstaller

### Opcionales
- PyQt5 (para interfaz gráfica)

## 🐛 Correcciones

- Manejo correcto de rutas en diferentes sistemas operativos
- Limpieza de recursos temporales en caso de error
- Validación mejorada de estructura de proyecto
- Prevención de sobrescritura accidental de archivos `.iflapp` existentes

## 📝 Notas de Migración

### Desde v1.0.0

No se requieren cambios en proyectos existentes. La nueva funcionalidad es completamente retrocompatible.

### Comportamiento Modificado

**Antes (v1.0.0)**:
```bash
python compiler_full.py  # Sin PyQt5 → Error y salida
```

**Ahora (v1.1.0)**:
```bash
python compiler_full.py  # Sin PyQt5 → Compila directorio actual
```

Si no deseas este comportamiento, simplemente navega a un directorio sin `details.xml` o usa el modo CLI explícito.

## ⚠️ Notas Importantes

### Limpieza de Temporales

El programa limpia automáticamente los directorios temporales. Sin embargo, si el proceso es interrumpido abruptamente (ej: `Ctrl+C`, cierre forzado), pueden quedar archivos en:

- **Windows**: `C:\Users\<usuario>\AppData\Local\Temp\flangcompiler_*`
- **Linux**: `/tmp/flangcompiler_*`

Estos pueden ser eliminados manualmente sin problemas.

### Ubicación de Salida

El archivo `.iflapp` siempre se guarda en el **directorio padre** del proyecto, no en el directorio del proyecto mismo. Esto evita contaminar el directorio de trabajo.

## 🎯 Casos de Uso

### Desarrollo Local sin GUI

Ideal para desarrolladores que trabajan en servidores sin entorno gráfico o prefieren flujos de trabajo CLI:

```bash
cd ~/proyectos/mi_app
python ~/tools/compiler_full.py
# Resultado: ~/proyectos/Publisher.App.v1.0.Platform.iflapp
```

### Integración CI/CD

Perfecto para pipelines de integración continua donde PyQt5 no está disponible:

```yaml
# .github/workflows/build.yml
- name: Build Flarm Package
  run: |
    cd ${{ github.workspace }}/app
    python compiler_full.py
```

### Compilación Rápida

Para compilaciones rápidas sin necesidad de abrir la GUI:

```bash
cd mi_proyecto && python ../compiler_full.py && cd ..
```

## 🙏 Agradecimientos

Gracias a la comunidad Flarm por el feedback y sugerencias que hicieron posible esta mejora.

---

**Desarrollado por**: Manus AI  
**Licencia**: MIT  
**Versión**: 1.1.0  
**Fecha**: 30 de Noviembre, 2025
