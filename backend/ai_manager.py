import easyocr
import cv2
import ollama
import json
import logging
import os
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.reader = easyocr.Reader(['es', 'en'])
        self.client = ollama.Client(host='http://192.168.1.81:11434')
        self.vision_model = 'qwen3-vl:8b'
        self.logic_model = 'qwen3:8b'
        self.host = 'http://192.168.1.81:11434'

        self.medical_prompt = """
        Eres un asistente médico de IA especializado en análisis de documentos clínicos.
        Tu tarea es analizar el siguiente texto médico y generar un JSON estructurado con formato SOAP.

        Analiza el contenido y genera un JSON válido con los siguientes campos:

        1. "patient_info": {{
            "name": "nombre del paciente si se menciona, o 'No especificado'",
            "age": "edad si se menciona, o null",
            "gender": "género si se menciona, o null"
        }}
        2. "document_type": Uno de ["consultation", "prescription", "lab_result", "referral"].
           Clasifica según el contenido:
           - "consultation": notas clínicas, SOAP, exploración física
           - "prescription": recetas, medicamentos
           - "lab_result": resultados de laboratorio, estudios
           - "referral": referencias a especialistas
        3. "subjective": {{
            "chief_complaint": "motivo principal de consulta",
            "symptoms": ["síntoma 1", "síntoma 2"],
            "history": "antecedentes relevantes mencionados"
        }}
        4. "objective": {{
            "vitals": {{
                "blood_pressure": "si se menciona, o null",
                "heart_rate": "si se menciona, o null",
                "temperature": "si se menciona, o null",
                "weight": "si se menciona, o null",
                "height": "si se menciona, o null",
                "spo2": "si se menciona, o null"
            }},
            "findings": ["hallazgo 1", "hallazgo 2"]
        }}
        5. "assessment": {{
            "diagnoses": [
                {{"description": "diagnóstico principal", "cie10_code": "código CIE-10 si aplica"}}
            ],
            "differential_diagnoses": ["diagnóstico diferencial 1"]
        }}
        6. "plan": {{
            "medications": [
                {{
                    "drug_name": "nombre del medicamento",
                    "dose": "dosis",
                    "frequency": "frecuencia",
                    "duration": "duración",
                    "instructions": "instrucciones"
                }}
            ],
            "studies": ["estudio solicitado 1"],
            "referrals": ["referencia 1"],
            "follow_up": "indicaciones de seguimiento",
            "recommendations": ["recomendación 1"]
        }}
        7. "lab_values": [
            {{
                "test_name": "nombre del estudio",
                "value": "valor obtenido",
                "unit": "unidad",
                "reference_range": "rango de referencia",
                "is_abnormal": true o false
            }}
        ]
        8. "summary": Un resumen clínico conciso (2-3 oraciones en Español).
        9. "confidence_score": Un entero (0-100) indicando la confianza del análisis.
           - < 40: Texto muy ambiguo o ilegible
           - 40-60: Información parcial
           - 60-80: Documento clínico estándar
           - 80-100: Documento clínico detallado y completo

        Responde ÚNICAMENTE con el JSON válido. Sin bloques de código markdown.
        Si algún campo no tiene información, usa null para valores simples, [] para listas, o {{}} para objetos.

        Texto Médico a Analizar:
        {text_content}
        """

        self.classification_prompt = """
        Clasifica el siguiente texto médico en una de estas categorías y responde ÚNICAMENTE con un JSON:
        {{"document_type": "consultation|prescription|lab_result|referral", "confidence": 0-100, "reason": "breve explicación"}}

        Texto:
        {text_content}
        """

    def extract_text_from_image(self, image_path: str, examples: List[Dict[str, Any]] = []) -> str:
        try:
            logger.info(f"Starting text extraction for: {image_path}")

            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return "Error: Image file not found."

            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image with OpenCV: {image_path}")
                return "Error: Could not load image."

            results = self.reader.readtext(img)

            if not results:
                logger.info("EasyOCR found no text. Falling back to Vision Model.")
                return self._transcribe_with_vision(image_path, examples)

            text = ""
            confidences = []
            for (_, t, conf) in results:
                text += t + " "
                confidences.append(conf)

            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            logger.info(f"EasyOCR Average Confidence: {avg_conf:.2f}")

            if avg_conf >= 0.80:
                return text.strip()

            logger.info("Confidence too low (< 0.80). Falling back to Vision Model.")
            return self._transcribe_with_vision(image_path, examples)

        except Exception as e:
            logger.error(f"OCR Error: {e}")
            if "Connection refused" in str(e):
                return "Error: Ollama service is not running."
            return f"Error using Vision AI: {str(e)}"

    def _transcribe_with_vision(self, image_path: str, examples: List[Dict[str, Any]] = []) -> str:
        try:
            logger.info(f"Sending image to Ollama ({self.vision_model})...")

            prompt = (
                "Transcribe el texto en este documento médico exactamente como aparece. "
                "Incluye todos los datos clínicos, nombres de medicamentos, dosis, valores de laboratorio "
                "y cualquier información del paciente visible. No agregues comentarios."
            )

            if examples:
                prompt = "Aquí hay ejemplos de documentos previos y su transcripción correcta:\n\n"
                for i, ex in enumerate(examples[:10]):
                    prompt += f"Ejemplo {i+1}: '{ex['corrected_text']}'\n"
                prompt += "\nAhora, transcribe este nuevo documento médico con el mismo nivel de detalle.\n"

            response = self.client.chat(
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
            logger.error(f"Vision Model Transcription Error: {e}")
            return "Error during Vision Model transcription."

    def classify_document(self, text_content: str) -> Dict[str, Any]:
        if not text_content or text_content.strip() == "":
            return {"document_type": "consultation", "confidence": 0}

        try:
            formatted = self.classification_prompt.format(text_content=text_content)
            response = self.client.chat(
                model=self.logic_model,
                messages=[{'role': 'user', 'content': formatted}],
                format='json'
            )
            json_str = response['message']['content']
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"document_type": "consultation", "confidence": 0}

    def analyze_medical_text(self, text_content: str) -> Dict[str, Any]:
        if not text_content or text_content.strip() == "":
            return {"error": "No text content to analyze"}

        try:
            logger.info(f"Sending text to Ollama ({self.logic_model}) for medical analysis...")
            formatted_prompt = self.medical_prompt.format(text_content=text_content)

            response = self.client.chat(
                model=self.logic_model,
                messages=[
                    {'role': 'user', 'content': formatted_prompt}
                ],
                format='json'
            )

            json_str = response['message']['content']

            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            json_data = json.loads(json_str)

            if self.validate_response(json_data):
                return json_data
            else:
                return {
                    "document_type": "consultation",
                    "subjective": {"chief_complaint": "No se pudo analizar", "symptoms": [], "history": ""},
                    "objective": {"vitals": {}, "findings": []},
                    "assessment": {"diagnoses": [], "differential_diagnoses": []},
                    "plan": {"medications": [], "studies": [], "referrals": [], "follow_up": "", "recommendations": []},
                    "lab_values": [],
                    "summary": "La respuesta de la IA no contenía todos los campos requeridos.",
                    "confidence_score": 0
                }

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Ollama response.")
            return {
                "document_type": "consultation",
                "subjective": {"chief_complaint": "Error de análisis", "symptoms": [], "history": ""},
                "objective": {"vitals": {}, "findings": []},
                "assessment": {"diagnoses": [], "differential_diagnoses": []},
                "plan": {"medications": [], "studies": [], "referrals": [], "follow_up": "", "recommendations": []},
                "lab_values": [],
                "summary": "Error al parsear la respuesta de la IA.",
                "confidence_score": 0
            }
        except Exception as e:
            logger.error(f"Ollama Logic error: {e}")
            if "Connection refused" in str(e):
                return {"error": "Ollama service is not running. Please start 'ollama serve'."}
            return {"error": f"Analysis failed: {str(e)}"}

    def extract_prescriptions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        medications = []
        plan = analysis.get("plan", {})
        if isinstance(plan, dict):
            meds = plan.get("medications", [])
            if isinstance(meds, list):
                for med in meds:
                    if isinstance(med, dict) and med.get("drug_name"):
                        medications.append({
                            "drug_name": med.get("drug_name", ""),
                            "dose": med.get("dose", ""),
                            "frequency": med.get("frequency", ""),
                            "duration": med.get("duration", ""),
                            "instructions": med.get("instructions", "")
                        })
        return medications

    def extract_lab_results(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        lab_values = analysis.get("lab_values", [])
        if isinstance(lab_values, list):
            for lab in lab_values:
                if isinstance(lab, dict) and lab.get("test_name"):
                    results.append({
                        "test_name": lab.get("test_name", ""),
                        "value": lab.get("value", ""),
                        "unit": lab.get("unit", ""),
                        "reference_range": lab.get("reference_range", ""),
                        "is_abnormal": 1 if lab.get("is_abnormal", False) else 0
                    })
        return results

    def validate_response(self, data: Dict[str, Any]) -> bool:
        required_fields = [
            "document_type",
            "summary",
            "confidence_score"
        ]

        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing field in AI response: {field}")
                return False

        return True
