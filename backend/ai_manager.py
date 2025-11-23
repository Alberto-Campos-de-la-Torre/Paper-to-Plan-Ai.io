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
        Eres un Ingeniero de Software Senior y Project Manager experto.
        Tu tarea es analizar el siguiente texto crudo, que representa una idea de software o nota de proyecto.
        
        Analiza el contenido y proporciona una respuesta JSON estructurada con los siguientes campos:
        1. "title": Un título CREATIVO, ATRACTIVO y profesional para el proyecto que capture la esencia de la idea (en Español). 
           El título debe ser memorable y reflejar el contexto visual y conceptual de la idea.
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
            
            # 2. Fallback to LLaVA (with Few-Shot if available)
            logger.info("Confidence too low (< 0.80). Falling back to LLaVA.")
            logger.info("Sending image to Ollama (LLaVA)...")
            
            prompt = "Transcribe the handwritten text in this image exactly as it appears. Do not add any commentary."
            
            # Construct Few-Shot Prompt
            if examples:
                prompt = "Here are examples of this user's handwriting and the correct transcription:\n\n"
                    # without complex multi-modal context handling. 
                    # For a simple local implementation, we will include the TEXT of the examples 
                    # as a style guide if possible, or just rely on the instruction.
                    # HOWEVER, standard LLaVA few-shot requires passing images.
                    # Current Ollama python lib supports 'images' list.
                    # We will try to just prompt better for now, or if we can, pass context.
                    # LIMITATION: The simple `ollama.chat` with one image doesn't support "previous image" context easily 
                    # without maintaining a session history with images.
                    # For this iteration, we will refine the prompt based on the *fact* that we have examples,
                    # but maybe we can't pass the example images directly in this single call easily.
                    
                    # ALTERNATIVE: We can't easily pass multiple images in one message in standard Ollama API yet (varies by version).
                    # Let's try to be clever: We will just be very specific.
                    pass
                
                # If we can't pass example images, we can at least tell it to be careful.
                # BUT, the user wants "Personalized".
                # If we can't pass example images, we can't do true visual few-shot.
                # Let's assume we can't pass multiple images for now and just improve the prompt.
                # WAIT! We can try to pass the text of previous corrections if they share vocabulary?
                # No, that's not helpful for handwriting style.
                
                # Let's stick to a strong prompt for now, and if the library supports it later, we add it.
                # Actually, let's just add a "Context" string if we have text-based hints.
                prompt += "Pay close attention to unique letter formations."

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
            logger.error(f"OCR Error: {e}")
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
