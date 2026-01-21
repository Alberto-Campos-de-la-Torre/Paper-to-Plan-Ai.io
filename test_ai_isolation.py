import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.ai_manager import AIEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_analysis():
    print("--- Starting AI Isolation Test ---")
    
    try:
        engine = AIEngine()
        print(f"Initialized AIEngine with host: {engine.client._client.base_url}")
        print(f"Logic Model: {engine.logic_model}")
        
        test_text = "Una aplicación móvil para gestionar el inventario de una pequeña tienda de abarrotes, con alertas de stock bajo y reportes de ventas diarios."
        print(f"\nTest Text: {test_text}")
        
        print("\nSending to Ollama...")
        result = engine.analyze_text(test_text)
        
        print("\n--- Analysis Result ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "error" in result:
            print("\n[FAIL] Analysis returned an error.")
        elif result.get("title") == "Error de Validación":
             print("\n[FAIL] Validation failed.")
        else:
            print("\n[SUCCESS] Analysis returned valid JSON structure.")
            
    except Exception as e:
        print(f"\n[CRITICAL FAIL] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_analysis()
