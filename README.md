# **PaperToPlan AI 🧠📝**

**De Papel a Ejecución:** Digitaliza, Analiza y Estructura tus ideas manuscritas con IA 100% Local.

## **📋 Descripción**

**PaperToPlan AI** es una aplicación de escritorio diseñada para desarrolladores y gestores que necesitan transformar el caos de las notas manuscritas en planes de proyecto estructurados y ejecutables sin comprometer la privacidad.

A diferencia de los OCR tradicionales que fallan con la caligrafía humana, PaperToPlan utiliza una estrategia híbrida de **Visión Multimodal (LLaVA/Moondream)** y **OCR** para interpretar diagramas y texto manuscrito. Todo el procesamiento ocurre localmente en tu máquina utilizando **Ollama**, garantizando que tus datos sensibles o propiedad intelectual nunca salgan de tu ordenador.

## **✨ Características Principales**

* **🔐 Privacidad Total (Local-First):** Ejecución 100% offline. Tus ideas no se suben a ninguna nube ni API de terceros.  
* **👁️ Visión Inteligente:** Integración con modelos multimodales (LLaVA) para entender el contexto visual de una nota, flechas y listas desordenadas, no solo caracteres sueltos.  
* **📊 Análisis de Factibilidad Automático:** La IA evalúa tu idea y genera un reporte JSON con:  
  * Score de factibilidad (0-100).  
  * Consideraciones técnicas y stack recomendado.  
  * Tiempo estimado de implementación.  
* **🗂️ Gestión Temporal:** Clasificación automática de notas en el dashboard según su complejidad: *Corto, Medio o Largo Plazo*.  
* **🎨 UI Moderna:** Interfaz oscura, limpia y responsiva construida con CustomTkinter.

## **🛠️ Stack Tecnológico**

* **Lenguaje:** Python 3.10+  
* **Interfaz Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
* **Motor de IA:** [Ollama](https://ollama.com/) (API Local)  
* **Modelos IA:**  
  * *Cerebro (Lógica):* llama3 o phi3  
  * *Ojos (Visión):* llava (para GPUs potentes) o moondream (para eficiencia)  
* **OCR Rápido:** EasyOCR \+ OpenCV (Pre-procesamiento de imagen)  
* **Persistencia:** SQLite

## **⚙️ Requisitos Previos**

Antes de instalar la aplicación, necesitas preparar el entorno de IA local:

1. **Python 3.10** o superior.  
2. **Ollama** instalado y ejecutándose. [Descargar aquí](https://ollama.com).  
3. Modelos descargados:  
   Abre tu terminal y ejecuta:  
   ollama pull llama3  
   ollama pull llava  
   \# Opcional: para equipos con menos RAM/GPU  
   ollama pull moondream

## **🚀 Instalación y Uso**

1. **Clonar el repositorio:**  
   git clone \[https://github.com/tu-usuario/PaperToPlan.git\](https://github.com/tu-usuario/PaperToPlan.git)  
   cd PaperToPlan

2. **Crear un entorno virtual:**  
   python \-m venv venv  
   \# En Windows:  
   .\\venv\\Scripts\\activate  
   \# En macOS/Linux:  
   source venv/bin/activate

3. **Instalar dependencias:**  
   pip install \-r requirements.txt

   *(El archivo requirements.txt debe incluir: customtkinter, ollama, easyocr, opencv-python, pillow)*  
4. Ejecutar la aplicación:  
   Asegúrate de que ollama serve esté corriendo en otra terminal o en segundo plano.  
   python main.py

## **📖 Guía de Uso Rápida**

1. **Nueva Nota:** Haz clic en el botón "+" y selecciona una foto de tu libreta o servilleta.  
2. **Procesamiento:** La app intentará leerla primero con OCR rápido. Si es confusa, usará LLaVA (esto puede tardar unos segundos dependiendo de tu GPU).  
3. **Revisión:** Verás la tarjeta de la nota en el tablero. Haz clic para ver el "Plan de Mejora" generado por la IA.  
4. **Filtrado:** Usa los filtros laterales para ver solo proyectos de "Corto Plazo" para victorias rápidas.

## **🗺️ Roadmap**

* \[ \] **Fase 1:** Backend Core (Conexión Python-Ollama y Prompts JSON).  
* \[ \] **Fase 2:** Módulo de Visión Híbrido (EasyOCR \+ LLaVA fallback).  
* \[ \] **Fase 3:** Interfaz Gráfica (Dashboard y Detalles).  
* \[ \] **Fase 4:** Base de datos y optimización de hilos (Threading).  
* \[ \] **Futuro:** Exportación a PDF/Markdown y soporte para notas de voz (Whisper).

## **🤝 Contribución**

¡Las contribuciones son bienvenidas\! Si tienes ideas para mejorar los prompts del sistema o la eficiencia del OCR, por favor abre un *issue* o envía un *pull request*.

## **📄 Licencia**

Este proyecto está bajo la Licencia MIT \- eres libre de usarlo y modificarlo.