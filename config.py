import json
import os

class Config:
    # Configuración de WhatsApp Web
    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    
    # Configuración del bot
    BOT_NAME = "Asistente Business"
    RESPONSE_DELAY = 2  # segundos
    
    # Rutas de archivos
    MEMORY_FILE = "memory.json"
    TRAINING_DATA_DIR = "training_data"
    
    # Configuración de aprendizaje
    LEARNING_RATE = 0.1
    MAX_MEMORY_SIZE = 1000
    
    @classmethod
    def load_training_data(cls):
        intents_path = os.path.join(cls.TRAINING_DATA_DIR, "intents.json")
        responses_path = os.path.join(cls.TRAINING_DATA_DIR, "responses.json")
        
        with open(intents_path, 'r', encoding='utf-8') as f:
            intents = json.load(f)
        
        with open(responses_path, 'r', encoding='utf-8') as f:
            responses = json.load(f)
            
        return intents, responses
