cat > install.sh << 'EOF'
#!/bin/bash
echo "🚀 INSTALADOR WHATSAPP BOT - TERMUX"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Actualizando paquetes...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}📥 Instalando dependencias del sistema...${NC}"
pkg install -y python wget

echo -e "${YELLOW}🌐 Instalando Chromium...${NC}"
pkg install -y chromium -y || {
    echo -e "${YELLOW}⚠️  Descargando Chromium alternativo...${NC}"
    wget https://termux.net/dists/stable/main/binary-aarch64/chromium_118.0.5993.65-1_aarch64.deb
    dpkg -i chromium_118.0.5993.65-1_aarch64.deb
}

echo -e "${YELLOW}🐍 Instalando dependencias Python...${NC}"
pip install selenium==4.15.0 webdriver-manager==4.0.1

echo -e "${YELLOW}📁 Creando estructura de archivos...${NC}"

# Crear training_data
mkdir -p training_data

# Crear intents.json
cat > training_data/intents.json << 'JSONEOF'
{
  "saludos": ["hola", "buenos días", "buenas tardes", "hey", "saludos", "qué tal"],
  "despedidas": ["adiós", "chao", "hasta luego", "nos vemos", "bye", "hasta pronto"],
  "productos": ["qué productos tienen", "qué venden", "catálogo", "productos", "mercancía"],
  "precios": ["precios", "cuánto cuesta", "valor", "costo", "precio"],
  "horario": ["horario de atención", "cuándo abren", "horarios", "atención al cliente"],
  "ubicacion": ["dónde están", "ubicación", "dirección", "local", "direccion"],
  "servicio": ["necesito ayuda", "soporte", "atención al cliente", "asistencia"],
  "agradecimientos": ["gracias", "muchas gracias", "te agradezco", "thanks"]
}
JSONEOF

# Crear responses.json
cat > training_data/responses.json << 'RESPEOF'
{
  "saludos": [
    "¡Hola! 👋 ¿En qué puedo ayudarte hoy?",
    "¡Buenos días! 🌞 Soy tu asistente virtual, ¿cómo puedo asistirte?",
    "¡Hola! 😊 Estoy aquí para ayudarte con lo que necesites"
  ],
  "despedidas": [
    "¡Hasta luego! 👋 Que tengas un excelente día",
    "¡Chao! 😊 Estamos para servirte cuando lo necesites",
    "¡Nos vemos! 💫 Que todo te vaya muy bien"
  ],
  "productos": [
    "Tenemos una amplia variedad de productos. ¿Qué tipo de producto te interesa? 📦",
    "Nuestro catálogo incluye diferentes categorías. ¿Buscas algo específico? 🛍️"
  ],
  "precios": [
    "Los precios varían según el producto. ¿Cuál te interesa para darte el precio exacto? 💰",
    "Puedo darte precios específicos. ¿Qué producto quieres consultar? 🏷️"
  ],
  "horario": [
    "⏰ Atendemos de lunes a viernes de 8:00 AM a 6:00 PM y sábados de 9:00 AM a 1:00 PM",
    "🕘 Nuestro horario de atención es: Lunes a Viernes 8:00-18:00, Sábados 9:00-13:00"
  ],
  "ubicacion": [
    "📍 Estamos ubicados en Av. Principal #123, Centro Comercial Plaza, Local 45",
    "🏢 Puedes encontrarnos en: Av. Principal #123, CC Plaza, Local 45"
  ],
  "servicio": [
    "🔧 Claro, estoy aquí para ayudarte. ¿En qué necesitas asistencia específicamente?",
    "💡 Cuéntame qué problema tienes o en qué necesitas ayuda para asistirte mejor"
  ],
  "agradecimientos": [
    "¡De nada! 😊 Estoy para ayudarte cuando lo necesites",
    "¡No hay problema! 🌟 Estamos aquí para servirte",
    "¡Gracias a ti! 💫 Que tengas un excelente día"
  ],
  "default": [
    "🤔 No estoy seguro de entender completamente. ¿Podrías reformular tu pregunta?",
    "💭 Todavía estoy aprendiendo. ¿Puedes ser más específico o usar otras palabras?",
    "🔍 No tengo una respuesta precisa para eso aún. ¿Puedes intentar preguntar de otra forma?"
  ]
}
RESPEOF

# Crear memory.json
cat > memory.json << 'MEMEOF'
{
  "conversations": [],
  "learned_patterns": {},
  "performance_metrics": {
    "total_messages": 0,
    "successful_responses": 0
  }
}
MEMEOF

echo -e "${GREEN}✅ Instalación completada!${NC}"
echo -e "${YELLOW}🚀 Para ejecutar: python bot_simple.py${NC}"
EOF

chmod +x install.sh
