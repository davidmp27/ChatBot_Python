from flask import Flask, request
import pywhatkit
import pyautogui
import sett
import services
import time

from databases import DatabaseManager

app = Flask(__name__)



#Pasos 1 guardar numeros en un arreglo, luego un for por la cantidad de numeros seleccioinados, luego los numeros del 
# select deben ser reemplazados por number = services.replace_start(message['from'])
def enviar_mensaje(numero, mensaje):
    try:
        # Formato del número: '+1234567890'
        numero_formateado = f"+593{numero}".replace("(", "").replace(")", "").replace("'", "").replace(",", "")

        pywhatkit.sendwhatmsg_instantly(numero_formateado, mensaje)
        print(f"Mensaje enviado a {numero_formateado}")
        
        # Esperar un momento para asegurarse de que el mensaje se ha escrito
        time.sleep(20)
        #pyautogui.hotkey('ctrl', 'w')
        # Simular clic en el botón de enviar
        pyautogui.press('enter')
    except Exception as e:
        print(f"Error al enviar mensaje a {numero_formateado}: {e}")

if __name__ == '__main__':
    app.run()
