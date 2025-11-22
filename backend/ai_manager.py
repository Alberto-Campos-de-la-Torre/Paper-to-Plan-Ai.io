import easyocr
import cv2
import ollama
import json
import logging
from typing import Dict, Any, Optional

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
        Eres un Ingeniero de Software Senior y Project Manager experto.
        Tu tarea es analizar el siguiente texto crudo, que representa una idea de software o nota de proyecto.
        
        Analiza el contenido y proporciona una respuesta JSON estructurada con los siguientes campos:
        1. "title": Un título conciso y profesional para el proyecto (en Español).
        2. "feasibility_score": Un entero de 0 a 100 indicando qué tan factible es el proyecto basado en tecnología actual y complejidad.
        3. "technical_considerations": Una lista de desafíos técnicos clave, requisitos o decisiones de arquitectura (en Español).
        4. "recommended_stack": Una lista de tecnologías recomendadas (lenguajes, frameworks, bases de datos).
        5. "implementation_time": Uno de ["Short Term", "Medium Term", "Long Term"]. 
           - Short Term: < 1 mes (Scripts simples, herramientas básicas)
           - Medium Term: 1-3 meses (MVPs, apps web/móviles estándar)
           - Long Term: > 3 meses (Sistemas complejos, IA pesada, investigación requerida)
        6. "summary": Un breve resumen ejecutivo de la idea (máximo 2 oraciones, en Español).

        Salida SOLAMENTE JSON válido. No incluyas formato markdown como ```json ... ```.
        
        Texto Crudo a Analizar:
        {text_content}
        """

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Hybrid extraction strategy:
        1. Try EasyOCR.
        2. If average confidence > 0.8, return OCR text.
        3. Else, fallback to Ollama (LLaVA) for visual transcription.
        """
        try:
            logger.info(f"Starting text extraction for: {image_path}")
            
            # 1. EasyOCR
            results = self.reader.readtext(image_path)
            
            if not results:
                logger.info("EasyOCR found no text. Falling back to LLaVA.")
                return self._transcribe_with_llava(image_path)

            total_confidence = 0
            extracted_text_parts = []
            
            for (_, text, conf) in results:
                extracted_text_parts.append(text)
                total_confidence += conf
            
            avg_confidence = total_confidence / len(results) if results else 0
            logger.info(f"EasyOCR Average Confidence: {avg_confidence:.2f}")

            if avg_confidence > 0.80:
                return "\n".join(extracted_text_parts)
            else:
                logger.info("Confidence too low (< 0.80). Falling back to LLaVA.")
                return self._transcribe_with_llava(image_path)

        except Exception as e:
            logger.error(f"Error in extraction pipeline: {e}")
            return f"Error extracting text: {str(e)}"

    def _transcribe_with_llava(self, image_path: str) -> str:
        """
        Uses Ollama with LLaVA model to transcribe handwritten text.
        """
        try:
            logger.info("Sending image to Ollama (LLaVA)...")
            response = ollama.chat(
                model=self.vision_model,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Transcribe este texto manuscrito literalmente. Solo devuelve el texto, sin comentarios adicionales.',
                        'images': [image_path]
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama LLaVA error: {e}")
            # Check if it's a connection error
            if "Connection refused" in str(e):
                return "Error: Ollama service is not running. Please start 'ollama serve'."
            return f"Error using Vision AI: {str(e)}"

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
                
            return json.loads(json_str)

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
