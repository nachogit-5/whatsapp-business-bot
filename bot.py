from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import os
from config import Config

# Descargar recursos de NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class LearningBot:
    def __init__(self):
        self.driver = None
        self.memory = self.load_memory()
        self.intents, self.responses = Config.load_training_data()
        self.vectorizer = TfidfVectorizer()
        self.stop_words = set(stopwords.words('spanish'))
        self.setup_driver()
        
    def setup_driver(self):
        """Configura el driver de Chrome para Termux"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')  # Remover esta línea si quieres ver el navegador
        
        # Para Termux en Android
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def preprocess_text(self, text):
        """Preprocesa el texto para el análisis"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words and token not in string.punctuation]
        return ' '.join(tokens)
    
    def load_memory(self):
        """Carga la memoria del bot desde el archivo JSON"""
        try:
            with open(Config.MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"conversations": [], "learned_patterns": {}}
    
    def save_memory(self):
        """Guarda la memoria del bot en el archivo JSON"""
        with open(Config.MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def classify_intent(self, message):
        """Clasifica la intención del mensaje usando aprendizaje automático"""
        processed_msg = self.preprocess_text(message)
        
        # Crear corpus de entrenamiento
        corpus = []
        intent_labels = []
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                corpus.append(self.preprocess_text(pattern))
                intent_labels.append(intent)
        
        # Entrenar el vectorizador
        try:
            X = self.vectorizer.fit_transform(corpus)
            message_vec = self.vectorizer.transform([processed_msg])
            
            # Calcular similitud
            similarities = cosine_similarity(message_vec, X)
            best_match_idx = np.argmax(similarities)
            best_score = similarities[0, best_match_idx]
            
            if best_score > 0.3:  # Umbral de confianza
                return intent_labels[best_match_idx], best_score
            else:
                return "default", best_score
        except:
            return "default", 0.0
    
    def get_response(self, intent, confidence):
        """Obtiene una respuesta basada en la intención clasificada"""
        if intent in self.responses and confidence > 0.3:
            responses = self.responses[intent]
            return np.random.choice(responses)
        else:
            return self.responses["default"][0]
    
    def learn_from_feedback(self, message, user_feedback):
        """Aprende del feedback del usuario"""
        if user_feedback.lower() in ['incorrecto', 'mal', 'error', 'no']:
            # El bot clasificó incorrectamente, aprender del error
            correct_intent = input("¿Cuál debería haber sido la intención correcta? ")
            
            if correct_intent not in self.intents:
                self.intents[correct_intent] = []
                self.responses[correct_intent] = [input("¿Cuál debería ser la respuesta? ")]
            
            self.intents[correct_intent].append(message)
            self.save_training_data()
            
            print(f"✅ Aprendí que '{message}' pertenece a '{correct_intent}'")
    
    def save_training_data(self):
        """Guarda los datos de entrenamiento actualizados"""
        intents_path = os.path.join(Config.TRAINING_DATA_DIR, "intents.json")
        responses_path = os.path.join(Config.TRAINING_DATA_DIR, "responses.json")
        
        with open(intents_path, 'w', encoding='utf-8') as f:
            json.dump(self.intents, f, ensure_ascii=False, indent=2)
        
        with open(responses_path, 'w', encoding='utf-8') as f:
            json.dump(self.responses, f, ensure_ascii=False, indent=2)
    
    def connect_whatsapp(self):
        """Conecta a WhatsApp Web"""
        print("🔗 Conectando a WhatsApp Web...")
        self.driver.get(Config.WHATSAPP_WEB_URL)
        
        # Esperar a que el usuario escanee el código QR
        input("📱 Escanea el código QR de WhatsApp Web y presiona Enter cuando estés conectado...")
        print("✅ Conectado a WhatsApp!")
    
    def find_unread_messages(self):
        """Encuentra mensajes no leídos"""
        try:
            # Buscar chats no leídos
            unread_chats = self.driver.find_elements(By.XPATH, '//div[@class="_2H6nH"]')
            return unread_chats
        except Exception as e:
            print(f"❌ Error buscando mensajes: {e}")
            return []
    
    def send_message(self, chat_element, message):
        """Envía un mensaje al chat"""
        try:
            chat_element.click()
            time.sleep(2)
            
            # Encontrar la caja de texto
            message_box = self.driver.find_element(By.XPATH, '//div[@title="Escribe un mensaje"]')
            message_box.send_keys(message)
            
            # Enviar mensaje
            send_button = self.driver.find_element(By.XPATH, '//button[@data-tab="10"]')
            send_button.click()
            
            print(f"💬 Mensaje enviado: {message}")
            time.sleep(Config.RESPONSE_DELAY)
            
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
    
    def run(self):
        """Ejecuta el bot principal"""
        print("🚀 Iniciando WhatsApp Business Bot...")
        self.connect_whatsapp()
        
        try:
            while True:
                # Buscar mensajes no leídos
                unread_chats = self.find_unread_messages()
                
                for chat in unread_chats:
                    try:
                        chat.click()
                        time.sleep(2)
                        
                        # Obtener el último mensaje
                        messages = self.driver.find_elements(By.XPATH, '//div[@class="_1Gy50"]')
                        if messages:
                            last_message = messages[-1].text
                            print(f"📩 Mensaje recibido: {last_message}")
                            
                            # Procesar mensaje
                            intent, confidence = self.classify_intent(last_message)
                            response = self.get_response(intent, confidence)
                            
                            # Enviar respuesta
                            self.send_message(chat, response)
                            
                            # Guardar en memoria
                            self.memory["conversations"].append({
                                "timestamp": time.time(),
                                "message": last_message,
                                "intent": intent,
                                "confidence": float(confidence),
                                "response": response
                            })
                            
                            # Mantener tamaño limitado de memoria
                            if len(self.memory["conversations"]) > Config.MAX_MEMORY_SIZE:
                                self.memory["conversations"] = self.memory["conversations"][-Config.MAX_MEMORY_SIZE:]
                            
                            self.save_memory()
                            
                    except Exception as e:
                        print(f"❌ Error procesando chat: {e}")
                
                time.sleep(5)  # Esperar 5 segundos entre verificaciones
                
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo bot...")
        finally:
            self.driver.quit()
            self.save_memory()

if __name__ == "__main__":
    bot = LearningBot()
    bot.run()
