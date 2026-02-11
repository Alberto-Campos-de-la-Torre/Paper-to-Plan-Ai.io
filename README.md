# MEGI Records

**Sistema de Expedientes Medicos Digitales** — Digitaliza, analiza y estructura documentos clinicos con IA 100% local.

## Descripcion

**MEGI Records** es una aplicacion de escritorio para profesionales de la salud que necesitan transformar documentos medicos fisicos (notas clinicas, recetas, resultados de laboratorio) en expedientes digitales estructurados y consultables, sin comprometer la privacidad del paciente.

Utiliza una estrategia hibrida de **Vision Multimodal** y **OCR** para interpretar documentos medicos manuscritos e impresos. Todo el procesamiento ocurre localmente usando **Ollama**, garantizando que los datos clinicos nunca salgan de tu equipo.

## Caracteristicas Principales

- **Privacidad Total (Local-First):** Ejecucion 100% offline. Los datos de pacientes no se suben a ninguna nube ni API de terceros.
- **Analisis SOAP Automatico:** La IA estructura documentos clinicos en formato SOAP (Subjetivo, Objetivo, Evaluacion, Plan) con codigos CIE-10 y score de confianza.
- **Gestion de Pacientes:** CRUD completo con datos demograficos, alergias, condiciones, tipo de sangre y contactos de emergencia.
- **Clasificacion de Documentos:** Deteccion automatica del tipo: consulta, receta, resultado de laboratorio o referencia.
- **Extraccion de Recetas:** Medicamentos con dosis, frecuencia, duracion e instrucciones extraidos automaticamente.
- **Resultados de Laboratorio:** Valores con unidades, rangos de referencia e indicador de anomalia.
- **Generacion de PDFs:** Notas medicas y recetas en formato PDF profesional listo para imprimir.
- **Tablero Kanban:** Flujo visual por estado: Pendiente, En Proceso, Procesado, Revisado.
- **Companion Movil:** Escanea un QR para usar tu celular como escaner de documentos.
- **Multi-Usuario:** Multiples doctores/staff con autenticacion PIN.

## Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Frontend | React 19 + TypeScript + Tailwind CSS v4 |
| Desktop | Tauri v2 (Rust) |
| Backend | FastAPI + Uvicorn |
| Base de Datos | SQLite (`megirecords.db`) |
| Motor de IA | Ollama (local) |
| Modelos IA | gemma3 (logica), qwen3-vl (vision) |
| OCR | EasyOCR + OpenCV |
| PDFs | fpdf2 |
| Tiempo Real | WebSockets |
| Movil | PWA (HTML5/JS via QR) |

## Requisitos Previos

1. **Python 3.10+**
2. **Node.js 18+** y npm
3. **Rust** (para compilar Tauri)
4. **Ollama** instalado y ejecutandose — [Descargar aqui](https://ollama.com)
5. Modelos descargados:
   ```bash
   ollama pull gemma3
   ollama pull qwen3-vl:8b
   ```

## Instalacion y Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Alberto-Campos-de-la-Torre/Paper-to-Plan-Ai.io.git
cd Paper-to-Plan-Ai.io
git checkout feat/megi-records
```

### 2. Backend (Python)

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python backend/server.py
```

### 3. Frontend (desarrollo)

```bash
cd desktop-app
npm install
npm run dev
```

### 4. Desktop (Tauri)

```bash
cd desktop-app
npm run tauri dev
```

## Estructura del Proyecto

```
├── backend/
│   ├── server.py              # API FastAPI (pacientes, consultas, documentos)
│   ├── ai_manager.py          # Prompts SOAP y clasificacion medica
│   ├── document_generator.py  # Generador de PDFs (notas y recetas)
│   └── session_manager.py     # Gestion de sesiones
├── database/
│   └── db_manager.py          # SQLite: patients, consultations, prescriptions, lab_results
├── desktop-app/
│   ├── src/
│   │   ├── api/client.ts      # Cliente API TypeScript
│   │   ├── components/
│   │   │   ├── Dashboard.tsx          # Vista principal de expedientes
│   │   │   ├── ConsultationDetail.tsx # Detalle SOAP con tabs
│   │   │   ├── PatientList.tsx        # Registro de pacientes
│   │   │   ├── PatientDetail.tsx      # Ficha completa del paciente
│   │   │   ├── PatientFormModal.tsx   # Crear/editar paciente
│   │   │   ├── PatientSelector.tsx    # Busqueda y vinculacion
│   │   │   ├── Kanban.tsx             # Tablero por estado
│   │   │   ├── Statistics.tsx         # Graficas medicas
│   │   │   ├── MedicalTags.tsx        # Tags: alergias, condiciones, CIE-10
│   │   │   ├── Sidebar.tsx            # Navegacion y filtros
│   │   │   ├── Login.tsx              # Autenticacion
│   │   │   ├── TextNoteModal.tsx      # Consulta manual
│   │   │   └── WebcamModal.tsx        # Captura de documentos
│   │   ├── App.tsx            # Rutas y estado global
│   │   └── index.css          # Tema MEGI (cream/forest-green)
│   └── src-tauri/             # Configuracion Tauri
└── requirements.txt
```

## Esquema de Base de Datos

| Tabla | Descripcion |
|-------|-------------|
| `users` | Doctores/staff con PIN |
| `patients` | Datos demograficos, alergias, condiciones, CIE-10 |
| `consultations` | Documentos medicos con analisis SOAP (JSON) y estado |
| `prescriptions` | Medicamentos vinculados a consulta y paciente |
| `lab_results` | Valores de laboratorio con rangos de referencia |
| `corrections` | Historial de correcciones OCR |

## Flujo de Trabajo

1. **Captura:** Sube imagen, usa webcam o escribe manualmente una consulta.
2. **OCR:** Extraccion de texto del documento fisico.
3. **Clasificacion:** La IA identifica el tipo de documento (consulta, receta, lab, referencia).
4. **Analisis SOAP:** Estructuracion en Subjetivo/Objetivo/Evaluacion/Plan con codigos CIE-10.
5. **Extraccion:** Recetas y valores de laboratorio se guardan en tablas dedicadas.
6. **Revision:** El doctor revisa, corrige si es necesario y marca como revisado.
7. **Exportacion:** Genera PDFs profesionales de notas medicas y recetas.

## API Endpoints

### Pacientes
- `GET/POST /api/patients` — Listar / crear pacientes
- `GET/PUT/DELETE /api/patients/{id}` — CRUD individual
- `GET /api/patients/search?q=` — Busqueda por nombre
- `GET /api/patients/{id}/consultations` — Historial del paciente
- `GET /api/patients/{id}/prescriptions` — Recetas del paciente
- `GET /api/patients/{id}/lab-results` — Laboratorios del paciente

### Consultas
- `GET /api/consultations` — Listar consultas
- `GET /api/consultations/{id}` — Detalle con analisis SOAP
- `POST /api/consultations/text` — Nueva consulta de texto
- `POST /api/consultations/{id}/regenerate` — Regenerar analisis
- `POST /api/consultations/{id}/review` — Marcar como revisado
- `POST /api/consultations/{id}/link-patient` — Vincular paciente
- `DELETE /api/consultations/{id}` — Eliminar

### Documentos PDF
- `GET /api/documents/medical-note/{id}` — Descargar nota medica
- `GET /api/documents/prescription/{id}` — Descargar receta

### Otros
- `POST /api/upload` — Subir imagen de documento
- `POST /api/capture_webcam` — Captura desde webcam
- `GET /api/stats` — Estadisticas medicas
- `WS /ws/{user_id}` — Actualizaciones en tiempo real

## Tema Visual

MEGI Records usa una paleta medica profesional:

- **Primary:** `#2d3b2d` (forest green)
- **Accent:** `#8b7355` (gold)
- **Background:** `#f5f3ee` (cream)
- **Fuentes:** Cormorant Garamond (titulos), DM Sans (cuerpo), JetBrains Mono (datos)
- Soporta modo claro y oscuro

## Licencia

Este proyecto esta bajo la Licencia MIT.
