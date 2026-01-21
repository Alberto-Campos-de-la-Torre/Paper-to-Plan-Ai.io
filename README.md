# 🎯 PaperToPlan AI

**Gestión Inteligente de Proyectos con Inteligencia Artificial**

PaperToPlan AI es una aplicación desktop que transforma notas manuscritas, texto e imágenes en planes de implementación detallados utilizando modelos de IA locales.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

---

## ✨ Características

### 🖼️ **Captura Multiformato**
- 📸 **Webcam**: Captura notas directamente desde tu cámara
- 📱 **Mobile**: Sube imágenes desde tu teléfono
- ✍️ **Texto**: Escribe ideas directamente en la app

### 🤖 **Análisis Inteligente con IA**
- 🔍 **OCR Híbrido**: EasyOCR + Modelos de Visión (Qwen3-VL)
- 🧠 **Análisis Profundo**: Mistral 3 para análisis de viabilidad
- 📊 **Scoring Automático**: Evaluación de factibilidad 0-100
- ⏱️ **Estimación de Tiempo**: Corto, mediano o largo plazo
- 🛠️ **Stack Recomendado**: Tecnologías sugeridas por categoría

### 📋 **Gestión de Proyectos**
- 📈 **Dashboard Interactivo**: Visualiza todos tus proyectos
- 🎯 **Kanban Board**: Organiza por tiempo de implementación
- 🔎 **Búsqueda Avanzada**: Filtra por estado, tiempo, score
- 📝 **Edición en Tiempo Real**: Modifica notas sobre la marcha

### 🌐 **Servidor Mobile**
- 📱 **Companion App**: Acceso desde cualquier dispositivo móvil
- 🔗 **QR Code**: Conexión instantánea
- 🔐 **Autenticación**: Sistema de usuarios con PIN

### 🎨 **Interfaz Moderna**
- 🌙 **Dark Mode**: Modo oscuro elegante
- 🎨 **Diseño Cyberpunk**: Tema futurista opcional
- 📱 **Responsive**: Adapta a cualquier tamaño de pantalla
- ⚡ **Animaciones Suaves**: Micro-interacciones pulidas

---

## 🚀 Inicio Rápido

### Prerequisitos

```bash
# Python 3.10+
python3 --version

# Node.js 18+
node --version

# Ollama (para modelos de IA)
curl https://ollama.ai/install.sh | sh
```

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Alberto-Campos-de-la-Torre/Paper-to-Plan-Ai.io.git
cd Paper-to-Plan-Ai.io

# 2. Instalar dependencias de Python
pip install -r backend/requirements.txt

# 3. Descargar modelos de IA
ollama pull ministral-3:14b
ollama pull qwen3-vl:latest

# 4. Instalar dependencias de Node
cd desktop-app
npm install

# 5. Ejecutar en modo desarrollo
npm run tauri dev
```

---

## 📦 Build para Producción

### Método Rápido (Recomendado)

```bash
# Ejecutar script automatizado
./build-production.sh
```

### Método Manual

```bash
cd desktop-app
npm run tauri build
```

Los archivos se generarán en:
```
desktop-app/src-tauri/target/release/bundle/
```

**Ver guía completa**: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 🛠️ Configuración

### Configuración de IA

La aplicación soporta configuración personalizada de modelos de Ollama:

1. Abre **Configuración** desde el sidebar
2. Configura:
   - **Host**: URL de Ollama (default: `http://localhost:11434`)
   - **Logic Model**: Modelo para análisis (default: `ministral-3:14b`)
   - **Vision Model**: Modelo para OCR (default: `qwen3-vl:latest`)
3. Prueba la conexión con el botón **Probar Conexión**
4. Guarda los cambios

La configuración se persiste en `ai_config.json` y se carga automáticamente.

### Usuarios

- **Usuario por defecto**: Beto May
- **PIN**: 0295

Puedes crear nuevos usuarios desde la configuración.

---

## 📱 Servidor Mobile

### Activar el Servidor

1. Click en **SERVIDOR MÓVIL** en el sidebar
2. Escanea el código QR con tu teléfono
3. Accede a la interfaz web móvil

### URL Manual

Si el QR no funciona, accede manualmente:
```
http://TU_IP_LOCAL:8001
```

---

## 🏗️ Arquitectura

```
Paper-to-Plan-Ai.io/
├── backend/              # Backend Python (FastAPI)
│   ├── server.py        # API REST y WebSockets
│   ├── ai_manager.py    # Motor de IA (OCR + Análisis)
│   ├── config_manager.py # Gestión de configuración
│   └── tauri_server.py  # Servidor para Tauri
├── desktop-app/         # Frontend (React + Tauri)
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── api/         # Cliente API
│   │   └── App.tsx      # Aplicación principal
│   └── src-tauri/       # Backend Rust (Tauri)
├── database/            # Gestión de base de datos
│   └── db_manager.py    # SQLite manager
├── web/                 # Interfaz web móvil
│   └── mobile_index.html
└── captures/            # Imágenes capturadas
```

---

## 🔧 Stack Tecnológico

### Frontend
- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **Tauri** - Desktop Framework
- **Lucide Icons** - Iconography

### Backend
- **Python 3.10+** - Language
- **FastAPI** - API Framework
- **SQLite** - Database
- **Ollama** - AI Models
- **EasyOCR** - Optical Character Recognition
- **OpenCV** - Image Processing

### AI Models
- **Mistral 3 14B** - Logic & Analysis
- **Qwen3-VL** - Vision & OCR

---

## 🧪 Desarrollo

### Estructura de Ramas

- `main` - Producción estable
- `feat-ui-redesign` - Desarrollo activo
- `feature/*` - Nuevas características
- `fix/*` - Correcciones de bugs

### Comandos de Desarrollo

```bash
# Desarrollo con hot-reload
cd desktop-app
npm run tauri dev

# Build de producción
npm run tauri build

# Linter
npm run lint

# Type check
npm run type-check
```

### Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd desktop-app
npm test
```

---

## 📊 Roadmap

### v1.0 (Actual)
- [x] OCR híbrido (EasyOCR + Vision Models)
- [x] Análisis con IA local (Ollama)
- [x] Dashboard y Kanban
- [x] Servidor mobile
- [x] Sistema de configuración persistente
- [x] Manejo de notas con estructura compleja

### v1.1 (Próximo)
- [ ] Exportar proyectos a Markdown/PDF
- [ ] Colaboración multi-usuario en tiempo real
- [ ] Integración con GitHub/GitLab
- [ ] Templates de proyecto predefinidos
- [ ] Análisis de tendencias y estadísticas

### v2.0 (Futuro)
- [ ] Fine-tuning de modelos personalizados
- [ ] Asistente de voz
- [ ] Integración con Jira/Trello
- [ ] App móvil nativa
- [ ] Sync en la nube

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Alberto Campos de la Torre**

- GitHub: [@Alberto-Campos-de-la-Torre](https://github.com/Alberto-Campos-de-la-Torre)

---

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) - Modelos de IA locales
- [Tauri](https://tauri.app/) - Framework desktop
- [FastAPI](https://fastapi.tiangolo.com/) - Framework backend
- [Mistral AI](https://mistral.ai/) - Modelos de lenguaje
- [Qwen](https://github.com/QwenLM) - Modelos de visión

---

## 📞 Soporte

¿Problemas? ¿Preguntas?

- 📧 Email: [email protected]
- 🐛 Issues: [GitHub Issues](https://github.com/Alberto-Campos-de-la-Torre/Paper-to-Plan-Ai.io/issues)
- 📖 Docs: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

<p align="center">
  Hecho con ❤️ y 🤖 por Alberto Campos de la Torre
</p>