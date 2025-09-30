#!/bin/bash
echo "🤖 Iniciando WhatsApp Business Bot..."
echo "📱 Asegúrate de tener Termux actualizado"

# Actualizar paquetes
pkg update -y

# Instalar dependencias del sistema
pkg install -y python rust libexpat openssl libjpeg-turbo

# Instalar Chrome para Termux
pkg install -y chromium

# Instalar dependencias de Python
pip install -r requirements.txt

# Verificar instalación
python -c "import selenium; print('✅ Selenium instalado correctamente')"

echo "🚀 Ejecutando el bot..."
python bot.py
