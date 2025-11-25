import easyocr
import cv2
import ollama
import json
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.reader = easyocr.Reader(['es', 'en']) # Support Spanish and English
        self.vision_model = 'llava'
        self.logic_model = 'gemma3:4B'
        
        # Master Prompt for Feasibility Analysis
        self.master_prompt = """
        Eres un Arquitecto de Soluciones de IA y Project Manager Senior con décadas de experiencia.
        Tu tarea es realizar un análisis PROFUNDO, CRÍTICO y DETALLADO del siguiente texto, que describe una idea de software.

        Analiza el contenido y genera un JSON válido con los siguientes campos:

        1. "title": Un título profesional, innovador y en Español que capture la esencia del proyecto.
        2. "feasibility_score": Un entero (0-100). Sé ESTRICTO y VARIADO. NO uses 75 por defecto.
           - < 40: Ideas vagas, sin detalles técnicos o físicamente imposibles.
           - 40-60: Ideas posibles pero con enormes barreras de entrada o costos prohibitivos.
           - 60-80: Proyectos estándar, viables pero con desafíos claros.
           - 80-90: Proyectos bien definidos, con alcance claro y tecnología madura.
           - > 90: Proyectos triviales o extremadamente detallados y listos para implementar.
           *CRITERIO*: Si el texto es muy corto o ambiguo, el puntaje DEBE ser bajo (< 60).
        3. "technical_considerations": Lista detallada (en Español) de desafíos técnicos, seguridad y escalabilidad.
        4. "recommended_stack": Lista de tecnologías específicas y modernas.
        5. "implementation_time": Uno de ["Corto Plazo", "Mediano Plazo", "Largo Plazo"].
           *REGLA DE ORO*: Si el texto menciona explícitamente "corto plazo", "mediano plazo" o "largo plazo", DEBES usar esa clasificación.
           - Si no se menciona explícitamente:
             - "Corto Plazo": < 1 mes (Prototipos, scripts).
             - "Mediano Plazo": 1-4 meses (MVPs, apps CRUD).
             - "Largo Plazo": > 4 meses (Sistemas complejos, IA avanzada, plataformas globales).
        6. "summary": Un resumen ejecutivo persuasivo y claro (2-3 oraciones en Español).

        Responde ÚNICAMENTE con el JSON válido. Sin bloques de código markdown.

        Texto a Analizar:
        {text_content}
        """

    def extract_text_from_image(self, image_path: str, examples: List[Dict[str, Any]] = []) -> str:
        """
        Hybrid extraction strategy:
        1. Try EasyOCR.
        2. If average confidence > 0.8, return OCR text.
        3. Else, fallback to Ollama (LLaVA) for visual transcription.
        Uses 'examples' for few-shot prompting if available.
        """
        try:
            logger.info(f"Starting text extraction for: {image_path}")
            
            # 1. EasyOCR
            results = self.reader.readtext(image_path)
            
            if not results:
                logger.info("EasyOCR found no text. Falling back to LLaVA.")
                return self._transcribe_with_llava(image_path, examples)
            
            text = ""
            confidences = []
            for (_, t, conf) in results:
                text += t + " "
                confidences.append(conf)
            
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            logger.info(f"EasyOCR Average Confidence: {avg_conf:.2f}")

            if avg_conf >= 0.80:
                return text.strip()
            
            # 2. Fallback to LLaVA
            logger.info("Confidence too low (< 0.80). Falling back to LLaVA.")
            return self._transcribe_with_llava(image_path, examples)

        except Exception as e:
            logger.error(f"OCR Error: {e}")
            if "Connection refused" in str(e):
                return "Error: Ollama service is not running. Please start 'ollama serve'."
            return f"Error using Vision AI: {str(e)}"

    def _transcribe_with_llava(self, image_path: str, examples: List[Dict[str, Any]] = []) -> str:
        """
        Helper method to transcribe text using LLaVA.
        """
        try:
            logger.info("Sending image to Ollama (LLaVA)...")
            
            prompt = "Transcribe the handwritten text in this image exactly as it appears. Do not add any commentary."
            
            # Construct Few-Shot Prompt
            if examples:
                prompt = "Here are examples of this user's handwriting and the correct transcription:\n\n"
                for i, ex in enumerate(examples[:10]):  # Limit to 10 examples
                    prompt += f"Example {i+1}: '{ex['corrected_text']}'\n"
                
                prompt += "\nNow, transcribe this new image in the same handwriting style. Pay close attention to unique letter formations.\n"

            response = ollama.chat(
                model=self.vision_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path]
                    }
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"LLaVA Transcription Error: {e}")
            return "Error during LLaVA transcription."

    def analyze_text(self, text_content: str) -> Dict[str, Any]:
        """
        Sends text to Ollama (gemma:3b) for analysis using the Master Prompt.
        Returns a dictionary (parsed JSON).
        """
        if not text_content or text_content.strip() == "":
            return {"error": "No text content to analyze"}

        try:
            logger.info("Sending text to Ollama (gemma:3b) for analysis...")
            formatted_prompt = self.master_prompt.format(text_content=text_content)
            
            response = ollama.chat(
                model=self.logic_model,
                messages=[
                    {'role': 'user', 'content': formatted_prompt}
                ],
                format='json' # Force JSON mode if supported by the model/api, otherwise prompt handles it
            )
            
            json_str = response['message']['content']
            
            # Attempt to clean json string if model adds markdown
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
                
            json_data = json.loads(json_str)
            
            if self.validate_response(json_data):
                return json_data
            else:
                return {
                    "title": "Error de Validación",
                    "feasibility_score": 0,
                    "technical_considerations": ["La respuesta de la IA no contenía todos los campos requeridos."],
                    "recommended_stack": [],
                    "implementation_time": "Error",
                    "summary": "Respuesta incompleta de la IA."
                }

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Ollama response.")
            return {
                "title": "Analysis Failed",
                "feasibility_score": 0,
                "technical_considerations": ["Could not parse AI response"],
                "recommended_stack": [],
                "implementation_time": "Unknown",
                "summary": "The AI response was not in valid JSON format."
            }
        except Exception as e:
            logger.error(f"Ollama Logic error: {e}")
            if "Connection refused" in str(e):
                return {"error": "Ollama service is not running. Please start 'ollama serve'."}
            return {"error": f"Analysis failed: {str(e)}"}

    def validate_response(self, data: Dict[str, Any]) -> bool:
        """
        Validates that the JSON response contains all required fields.
        """
        required_fields = [
            "title", 
            "feasibility_score", 
            "technical_considerations", 
            "recommended_stack", 
            "implementation_time", 
            "summary"
        ]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing field in AI response: {field}")
                return False
            
            # Basic empty check
            if not data[field] and not isinstance(data[field], (int, float)):
                logger.warning(f"Empty field in AI response: {field}")
                # We might allow empty lists but let's be strict for now or just warn
                # return False # Optional: decide if empty fields are fatal
        
        return True
