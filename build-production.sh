#!/bin/bash

# 🚀 Script de Build para Producción - PaperToPlan AI
# Este script automatiza el proceso de build para diferentes plataformas

set -e  # Exit on error

echo "╔════════════════════════════════════════════╗"
echo "║   PaperToPlan AI - Production Build        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -d "desktop-app" ]; then
    echo -e "${RED}Error: Este script debe ejecutarse desde el directorio raíz del proyecto${NC}"
    exit 1
fi

# Función para mostrar progreso
progress() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Verificar dependencias
echo "📦 Verificando dependencias..."

if ! command -v node &> /dev/null; then
    error "Node.js no está instalado. Instálalo desde https://nodejs.org/"
fi
progress "Node.js $(node --version)"

if ! command -v npm &> /dev/null; then
    error "npm no está instalado"
fi
progress "npm $(npm --version)"

if ! command -v cargo &> /dev/null; then
    warning "Rust no está instalado. Instalando..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
fi
progress "Rust $(rustc --version)"

# 2. Limpiar builds anteriores
echo ""
echo "🧹 Limpiando builds anteriores..."
cd desktop-app
rm -rf dist
rm -rf src-tauri/target/release/bundle
progress "Archivos antiguos eliminados"

# 3. Instalar dependencias de Node
echo ""
echo "📥 Instalando dependencias de npm..."
npm install || error "Falló la instalación de dependencias npm"
progress "Dependencias de npm instaladas"

# 4. Build del frontend
echo ""
echo "🏗️  Compilando frontend (Vite + React)..."
npm run build || error "Falló el build del frontend"
progress "Frontend compilado"

# 5. Build de Tauri
echo ""
echo "🦀 Compilando aplicación Tauri..."
npm run tauri build || error "Falló el build de Tauri"
progress "Aplicación Tauri compilada"

# 6. Mostrar archivos generados
echo ""
echo "📦 Archivos generados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "src-tauri/target/release/bundle" ]; then
    find src-tauri/target/release/bundle -type f \( \
        -name "*.AppImage" -o \
        -name "*.deb" -o \
        -name "*.rpm" -o \
        -name "*.dmg" -o \
        -name "*.msi" -o \
        -name "*.exe" \
    \) -exec ls -lh {} \; | awk '{print $9 " (" $5 ")"}'
else
    warning "No se encontraron archivos de bundle"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 7. Información de despliegue
echo ""
echo "🎉 ¡Build completado exitosamente!"
echo ""
echo "📍 Ubicación de los archivos:"
echo "   $(pwd)/src-tauri/target/release/bundle/"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Prueba el ejecutable localmente"
echo "   2. Verifica que todas las funcionalidades funcionen"
echo "   3. Distribuye los archivos según tu plataforma:"
echo ""
echo "   Linux:"
echo "   - AppImage: Ejecutable portable (recomendado)"
echo "   - DEB: Para Ubuntu/Debian"
echo ""
echo "   Windows:"
echo "   - MSI: Instalador de Windows"
echo "   - EXE: Instalador NSIS"
echo ""
echo "   macOS:"
echo "   - DMG: Imagen de disco de macOS"
echo "   - APP: Bundle de aplicación"
echo ""
echo "⚠️  Recuerda: Los usuarios necesitarán:"
echo "   - Python 3.10+"
echo "   - Ollama instalado"
echo "   - Modelos de Ollama descargados (ministral-3:14b, qwen3-vl:latest)"
echo ""
echo "📚 Para más información, consulta DEPLOYMENT.md"
echo ""
