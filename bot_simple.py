cat > bot_simple.py << 'EOF'
#!/usr/bin/env python3
"""
WhatsApp Business Bot - Versión Simple para Termux
"""
import time
import json
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class WhatsAppBusinessBot:
    def __init__(self):
        self.driver = None
        self.memory_file = "memory.json"
        self.training_dir = "training_data"
        
        # Cargar datos
        self.intents = self.load_json_file(f"{self.training_dir}/intents.json")
        self.responses = self.load_json_file(f"{self.training_dir}/responses.json")
        self.memory = self.load_json_file(self.memory_file)
        
        # Inicializar driver
        self.setup_driver()
        
        logging.info("🤖 Bot inicializado correctamente")
    
    def load_json_file(self, filepath):
        """Cargar archivo JSON con manejo de errores"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"📄 Archivo {filepath} no encontrado, usando datos por defecto")
            return self.get_default_data(filepath)
        except Exception as e:
            logging.error(f"❌ Error cargando {filepath}: {e}")
            return self.get_default_data(filepath)
    
    def get_default_data(self, filepath):
        """Datos por defecto si hay error"""
        if "intents" in filepath:
            return {
                "saludos": ["hola", "buenos días", "buenas tardes"],
                "despedidas": ["adiós", "chao", "hasta luego"],
                "productos": ["productos", "qué venden", "catálogo"],
                "precios": ["precio", "cuánto cuesta", "valor"]
            }
        elif "responses" in filepath:
            return {
                "saludos": ["¡Hola! ¿En qué puedo ayudarte?"],
                "despedidas": ["¡Hasta luego! Que tengas buen día"],
                "productos": ["Tenemos diversos productos. ¿Qué te interesa?"],
                "precios": ["Los precios varían. ¿Qué producto específico?"],
                "default": ["No entendí. ¿Puedes reformular?"]
            }
        else:  # memory.json
            return {"conversations": [], "performance": {"total": 0, "success": 0}}
    
    def save_memory(self):
        """Guardar memoria en archivo"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"❌ Error guardando memoria: {e}")
    
    def setup_driver(self):
        """Configurar Chrome WebDriver para Termux"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # Configuraciones específicas para Termux
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--user-data-dir=/data/data/com.termux/files/home/chrome_profile')
            
            # Intentar con Chrome normal primero
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ Chrome WebDriver configurado")
            
        except Exception as e:
            logging.error(f"❌ Error configurando Chrome: {e}")
            raise
    
    def classify_message(self, message):
        """Clasificar mensaje usando método simple"""
        message_lower = message.lower().strip()
        
        # Buscar coincidencias exactas primero
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return intent, 0.9
        
        # Buscar por palabras clave
        keyword_map = {
            "saludos": ["hola", "buenos", "buenas", "saludo", "hey"],
            "despedidas": ["adiós", "chao", "hasta", "bye", "nos vemos"],
            "productos": ["producto", "catálogo", "venden", "mercancía", "artículo"],
            "precios": ["precio", "cuesta", "valor", "costo", "cuánto"],
            "horario": ["horario", "hora", "abren", "atención", "cuándo"],
            "ubicacion": ["dónde", "ubicación", "dirección", "local", "direccion"],
            "servicio": ["ayuda", "soporte", "asistencia", "problema", "error"],
            "agradecimientos": ["gracias", "agradezco", "thank you", "thanks"]
        }
        
        for intent, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent, 0.7
        
        return "default", 0.0
    
    def get_bot_response(self, intent, confidence):
        """Obtener respuesta del bot"""
        if intent in self.responses and confidence > 0.5:
            response = random.choice(self.responses[intent])
            self.update_metrics("success")
            return response
        else:
            self.update_metrics("fail")
            return random.choice(self.responses.get("default", ["No entendí"]))
    
    def update_metrics(self, result):
        """Actualizar métricas de rendimiento"""
        if "performance" not in self.memory:
            self.memory["performance"] = {"total": 0, "success": 0, "fail": 0}
        
        self.memory["performance"]["total"] += 1
        if result == "success":
            self.memory["performance"]["success"] += 1
        else:
            self.memory["performance"]["fail"] += 1
        
        # Guardar cada 10 mensajes
        if self.memory["performance"]["total"] % 10 == 0:
            self.save_memory()
    
    def connect_whatsapp(self):
        """Conectar a WhatsApp Web"""
        logging.info("🔗 Conectando a WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        # Esperar a que el usuario escanee el QR
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            logging.info("✅ WhatsApp Web conectado correctamente")
        except TimeoutException:
            logging.warning("⏰ Tiempo de espera agotado. Verifica la conexión.")
    
    def find_unread_chats(self):
        """Encontrar chats con mensajes no leídos"""
        try:
            # Buscar el indicador de mensajes no leídos (punto verde/círculo)
            unread_indicators = self.driver.find_elements(
                By.XPATH, '//div[@class="_2H6nH"]//span[@data-testid="icon-unread-count"]'
            )
            
            chats = []
            for indicator in unread_indicators:
                try:
                    chat = indicator.find_element(By.XPATH, './ancestor::div[@role="row"]')
                    chats.append(chat)
                except NoSuchElementException:
                    continue
            
            return chats
        except Exception as e:
            logging.error(f"❌ Error buscando chats: {e}")
            return []
    
    def process_chat(self, chat_element):
        """Procesar un chat individual"""
        try:
            # Hacer clic en el chat
            chat_element.click()
            time.sleep(3)
            
            # Obtener el último mensaje recibido
            messages = self.driver.find_elements(
                By.XPATH, '//div[contains(@class, "message-in")]//div[contains(@class, "_21Ahp")]'
            )
            
            if not messages:
                return
            
            last_message = messages[-1].text
            logging.info(f"📩 Mensaje recibido: {last_message}")
            
            # Procesar y responder
            intent, confidence = self.classify_message(last_message)
            response = self.get_bot_response(intent, confidence)
            
            # Enviar respuesta
            self.send_message(response)
            
            # Guardar en historial
            self.save_conversation(last_message, response, intent, confidence)
            
        except Exception as e:
            logging.error(f"❌ Error procesando chat: {e}")
    
    def send_message(self, message):
        """Enviar mensaje en el chat actual"""
        try:
            # Buscar la caja de texto
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Escribe un mensaje"]'))
            )
            
            # Escribir y enviar mensaje
            message_box.send_keys(message)
            
            send_button = self.driver.find_element(
                By.XPATH, '//button[@data-testid="compose-btn-send"]'
            )
            send_button.click()
            
            logging.info(f"💬 Respuesta enviada: {message}")
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"❌ Error enviando mensaje: {e}")
    
    def save_conversation(self, user_message, bot_response, intent, confidence):
        """Guardar conversación en memoria"""
        conversation = {
            "timestamp": time.time(),
            "user_message": user_message,
            "bot_response": bot_response,
            "intent": intent,
            "confidence": confidence
        }
        
        if "conversations" not in self.memory:
            self.memory["conversations"] = []
        
        self.memory["conversations"].append(conversation)
        
        # Mantener máximo 100 conversaciones
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        
        self.save_memory()
    
    def run(self):
        """Ejecutar el bot principal"""
        logging.info("🚀 Iniciando WhatsApp Business Bot...")
        
        try:
            self.connect_whatsapp()
            
            while True:
                # Buscar chats no leídos
                unread_chats = self.find_unread_chats()
                
                if unread_chats:
                    logging.info(f"🔍 Encontrados {len(unread_chats)} chats nuevos")
                    
                    for chat in unread_chats:
                        self.process_chat(chat)
                
                # Esperar antes de revisar nuevamente
                time.sleep(10)
                
        except KeyboardInterrupt:
            logging.info("\n🛑 Bot detenido por el usuario")
        except Exception as e:
            logging.error(f"❌ Error crítico: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            self.save_memory()
            logging.info("💾 Memoria guardada. ¡Hasta pronto!")

if __name__ == "__main__":
    bot = WhatsAppBusinessBot()
    bot.run()
EOF
