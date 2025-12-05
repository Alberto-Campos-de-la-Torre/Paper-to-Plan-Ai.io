# 📦 Guía de Despliegue y Empaquetado - PaperToPlan AI

Esta guía explica cómo empaquetar la aplicación para producción en diferentes plataformas.

## 📋 Prerequisitos

### Para la Aplicación Desktop (Tauri)
- **Node.js** v18 o superior
- **Rust** (instalado automáticamente por Tauri CLI)
- **Sistema operativo específico**:
  - **Linux**: `sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev`
  - **Windows**: Visual Studio 2019+ con C++ tools
  - **macOS**: Xcode Command Line Tools

### Para el Backend (Python)
- **Python** 3.10+
- **Ollama** instalado y corriendo
- **Dependencias Python**: `pip install -r backend/requirements.txt`

---

## 🏗️ Empaquetado de la Aplicación Desktop

### 1. Preparar el entorno

```bash
cd desktop-app
npm install
```

### 2. Build de producción

```bash
# Opción 1: Build para tu plataforma actual
npm run tauri build

# Opción 2: Build específico para Linux
npm run tauri build -- --target x86_64-unknown-linux-gnu

# Opción 3: Build específico para Windows (desde Linux con cross-compilation)
# Requiere configuración adicional de mingw-w64
npm run tauri build -- --target x86_64-pc-windows-gnu
```

### 3. Ubicación de los archivos generados

Los archivos de distribución se generarán en:

**Linux**:
- **AppImage**: `desktop-app/src-tauri/target/release/bundle/appimage/desktop-app_0.1.0_amd64.AppImage`
- **DEB**: `desktop-app/src-tauri/target/release/bundle/deb/desktop-app_0.1.0_amd64.deb`

**Windows**:
- **MSI**: `desktop-app/src-tauri/target/release/bundle/msi/desktop-app_0.1.0_x64_en-US.msi`
- **EXE (NSIS)**: `desktop-app/src-tauri/target/release/bundle/nsis/desktop-app_0.1.0_x64-setup.exe`

**macOS**:
- **DMG**: `desktop-app/src-tauri/target/release/bundle/dmg/desktop-app_0.1.0_x64.dmg`
- **APP**: `desktop-app/src-tauri/target/release/bundle/macos/desktop-app.app`

---

## 🐍 Configuración del Backend para Producción

### Opción 1: Backend Integrado (Recomendado para Desktop)

El backend Python se inicia automáticamente con la app Tauri a través de `tauri_server.py`.

**Ventajas**:
- Todo-en-uno, el usuario solo ejecuta la app
- No requiere configuración adicional

**Desventajas**:
- El usuario debe tener Python y Ollama instalados
- Más complejo de distribuir

### Opción 2: Backend Standalone (Para servidor)

Ejecutar el backend como servicio independiente:

```bash
cd Paper-to-Plan-Ai.io
python -m backend.server
```

El servidor correrá en `http://0.0.0.0:8001`

---

## 🔧 Configuración Personalizada

### Personalizar nombre y versión

Edita `desktop-app/src-tauri/tauri.conf.json`:

```json
{
  "productName": "PaperToPlan AI",
  "version": "1.0.0",
  "identifier": "com.papertoplan.app",
  "app": {
    "windows": [{
      "title": "PaperToPlan AI - Gestión Inteligente de Proyectos",
      "width": 1400,
      "height": 900,
      "resizable": true,
      "fullscreen": false
    }]
  }
}
```

### Cambiar íconos

Reemplaza los iconos en `desktop-app/src-tauri/icons/` con tus propios iconos:
- `32x32.png`
- `128x128.png`
- `128x128@2x.png`
- `icon.icns` (macOS)
- `icon.ico` (Windows)

**Generar iconos automáticamente**:
```bash
npm install -g @tauri-apps/cli
cargo tauri icon path/to/your/icon.png
```

---

## 📦 Distribución Completa

### Crear un instalador que incluya todo

Para distribuir la aplicación con todas las dependencias:

#### Linux (AppImage)

```bash
# 1. Build la app
npm run tauri build

# 2. El AppImage ya incluye la app completa
# Distribuye el archivo .AppImage

# 3. Crear script de instalación de dependencias
```

Crea un script `install-dependencies.sh`:

```bash
#!/bin/bash
echo "Instalando dependencias de PaperToPlan AI..."

# Python
sudo apt install -y python3 python3-pip python3-venv

# Ollama
curl https://ollama.ai/install.sh | sh

# Dependencias Python
pip3 install -r requirements.txt

# Descargar modelos de Ollama
ollama pull ministral-3:14b
ollama pull qwen3-vl:latest

echo "✅ Instalación completa!"
```

#### Windows (MSI/EXE)

Para Windows, considera usar **Inno Setup** o **NSIS** para crear un instalador que:
1. Instale la app Tauri
2. Instale Python (usa el instalador embebido)
3. Instale Ollama
4. Configure las dependencias Python

#### macOS (DMG)

Similar a Linux, crea un script de post-instalación para dependencias.

---

## 🚀 Despliegue del Servidor Mobile

Para hacer accesible el servidor mobile en red local:

### 1. Configurar firewall

```bash
# Linux (UFW)
sudo ufw allow 8001/tcp

# Linux (firewalld)
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

### 2. Obtener IP local

```bash
# Linux/macOS
ip addr show | grep inet

# Windows
ipconfig
```

### 3. Configurar en la app

Ve a **Configuración** → **Configuración de Servidor Móvil** y establece:
```
http://TU_IP_LOCAL:8001
```

---

## 🔍 Verificación del Build

### Comprobar el build

```bash
# Ver el tamaño del bundle
ls -lh desktop-app/src-tauri/target/release/bundle/

# Probar el ejecutable (Linux)
./desktop-app/src-tauri/target/release/desktop-app

# Probar AppImage
./desktop-app/src-tauri/target/release/bundle/appimage/*.AppImage
```

### Comprobar dependencias (Linux)

```bash
# Ver librerías dinámicas requeridas
ldd desktop-app/src-tauri/target/release/desktop-app
```

---

## 📝 Checklist Pre-Release

- [ ] Actualizar versión en `package.json`
- [ ] Actualizar versión en `tauri.conf.json`
- [ ] Actualizar versión en `Cargo.toml`
- [ ] Cambiar íconos de la aplicación
- [ ] Personalizar nombre y título de ventana
- [ ] Probar build en modo release
- [ ] Verificar que el backend inicia correctamente
- [ ] Probar conexión con Ollama
- [ ] Verificar que la configuración persiste
- [ ] Probar creación de notas (texto, imagen, webcam)
- [ ] Verificar servidor mobile en red local
- [ ] Crear documentación de usuario
- [ ] Crear script de instalación de dependencias

---

## 🐛 Solución de Problemas

### Error: "webkit2gtk-4.1 not found"
```bash
sudo apt install libwebkit2gtk-4.1-dev
```

### Error: "Rust not installed"
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Error: "Python module not found"
```bash
cd Paper-to-Plan-Ai.io
pip install -r backend/requirements.txt
```

### Error: "Ollama not responding"
```bash
# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# Si no está corriendo
ollama serve
```

---

## 📊 Optimizaciones de Producción

### Reducir tamaño del bundle

1. **Minimizar frontend**:
```json
// vite.config.ts
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
}
```

2. **Stripe debug symbols** (Linux):
```bash
strip desktop-app/src-tauri/target/release/desktop-app
```

3. **Optimizar Rust build**:
```toml
# Cargo.toml
[profile.release]
opt-level = "z"     # Optimize for size
lto = true          # Link-time optimization
codegen-units = 1   # Better optimization
strip = true        # Strip symbols
```

---

## 🌐 Recursos Adicionales

- [Tauri Documentation](https://tauri.app/v1/guides/)
- [Distributing Tauri Apps](https://tauri.app/v1/guides/distribution/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Python Packaging Guide](https://packaging.python.org/)

---

**¡Listo para producción! 🚀**
