from flask import Flask, request, jsonify
import services
#import scrap
from databases import DatabaseManager  # Importa la clase DatabaseManager de tu archivo database
#from scrap import enviar_mensaje  # Importa la función enviar_mensaje desde el módulo scrap
import psycopg2
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from scracp2 import send_bulk_message, send_whatsapp_message, recordatorio_mensajes_whatsap, abrir_whatsapp_web
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

#from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from time import sleep




#from multiprocessing import Process
# Obtener las credenciales de Twilio desde las variables de entorno
TWILIO_ACCOUNT_SID = '************'
TWILIO_AUTH_TOKEN = '************'
TWILIO_PHONE_NUMBER = '************'

# Configurar el cliente de Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def opciones():

    response = ("\n\n Envie Hola para ver otra vez las opciones*")
        
    message = client.messages.create(
    body=response,  # Cuerpo del mensaje de respuesta
    from_='whatsapp:' + TWILIO_PHONE_NUMBER,  # Número de WhatsApp configurado en Twilio
    to=request.values.get('From')  # Número de WhatsApp del remitente original
    )


app = Flask(__name__)
CORS(app) 
scheduler = BackgroundScheduler()
scheduler.start()


@app.route('/abrir_whatsapp', methods=['GET'])
def abrir_whatsapp():
    driver = abrir_whatsapp_web()
    services.monitorear_mensajes(driver)


@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 'Hola mundo bigdateros, desde Flask'

@app.route('/webhook', methods=['POST'])
def whatsapp_bot():
        # Obtener el mensaje de WhatsApp recibido
        conn = psycopg2.connect(
                    dbname='chatbot_db',
                    user='postgres',
                    password='david1234',
                    host='localhost',
                    port='5432'
                )
        db_manager = DatabaseManager()
        #pagos_pendientes  = db_manager.consulta_productos('postgresql', conn)
        incoming_msg = request.values.get('Body', '').lower()
        from_number=request.values.get('From')
        
        # Crear una instancia de MessagingResponse para construir la respuesta
        resp = MessagingResponse()
        msg = resp.message()
        # Definir las opciones de respuesta
        options = {
            'hola': "¡Hola! ¿Cómo puedo ayudarte hoy?\n\n" +
                    "Puedes preguntarme sobre:\n" +
                    "1. *Productos*\n" +
                    "2. *Promociones*\n"+
                    "3. *Descuentos*\n"+
                    "4. *Generar Solicitud de Compra*",
            'adiós': "¡Adiós! Que tengas un buen día.",
            'productos': db_manager.consulta_productos2('postgresql', conn),
            'promociones':  db_manager.consulta_promociones_descuentos2('postgresql', conn),
            'descuentos':  db_manager.consulta_productos_con_descuentos2('postgresql', conn),

            #'solicitar': db_manager.generate_siguiente_solicitud_id('postgresql', conn)    # Añade tu lógica para las promociones
            'generar':"Buena elección! Puedes continuar con la Solicitud 🛒😊\n\n"+
                         "Por favor ingresa su consulta con el siguiente formato: \n\n*'Solicitar:  <Describa del problema, Nombre del producto>*' \n\n Para que nuestros asesores lo revisen 😊"                     
        
        }

        matched_option, score = process.extractOne(incoming_msg, options.keys(), scorer=fuzz.token_set_ratio)

        # Lógica para generar la respuesta según el mensaje recibido
        if score > 80:  # Umbral de coincidencia
            response = options[matched_option]
            
        elif 'solicitar' in incoming_msg :
            try:
                parts= incoming_msg.split(':')
                description, name= parts[1].split(',')

                solicitud_id = db_manager.generate_siguiente_solicitud_id2('postgresql', conn) 
                fecha_at = datetime.now() ##Importar datetime
                db_manager.create_solicitud_compra2('postgresql', conn, solicitud_id, 'Pendiente', fecha_at,'0000000000',name.strip(),description.strip())##Aqui falta ver los parametros que necesita el metodo,funcion
                response=f"*Perfecto, Se generó la solicitud*  *{solicitud_id}* ! Pronto nuestros asesores se comunicaran Contigo "
            except Exception as e:
                response="Hubo un error. Por favor, asegúrate de utlizar el formato correcto 'Solicitar:  <Ingresa breve descripción del problema, Nombre del producto>" 
              

        else:
            response = "Lo siento, no entiendo tu mensaje." +incoming_msg
        # Enviar mensaje de respuesta usando el cliente de Twilio
        message = client.messages.create(
            body=response,  # Cuerpo del mensaje de respuesta
            from_='whatsapp:' + TWILIO_PHONE_NUMBER,  # Número de WhatsApp configurado en Twilio
            to=request.values.get('From')  # Número de WhatsApp del remitente original
        )
        sleep(2)

        opciones()

        print(message.sid)  # opcional: imprimir el SID del mensaje enviado

        return str(resp)  # Devolver la respuesta generada como un string


@app.route('/envios', methods=['POST'])
def envios_masivos():
    try:

        text = "🛍️ ¡Oferta Especial! 🎉\n ¡Descuento del 20% en todos nuestros productos por tiempo limitado! 🎁🎉 Visita nuestra tienda en línea y aprovecha esta increíble oferta. ¿Qué esperas? ¡Contáctanos ya!\n📞 ¡Contáctanos ahora! 📱"


        # Establecer conexión a la base de datos PostgreSQL
        conn = psycopg2.connect(
            dbname='chatbot_db',
            user='postgres',
            password='david1234',
            host='localhost',
            port='5432'
        )

        # Obtener números de la base de datos
        db_manager = DatabaseManager()
        numbers = db_manager.envio_masivos_numeros('postgresql', conn)



        # Enviar mensaje usando pywhatkit para cada número
        for numero in numbers:
            # Enviar mensaje usando send_whatsapp_message para cada número
            #send_whatsapp_message(numero, text)
            send_whatsapp_message(numero, text)
            
            #enviar_mensaje(numero, text)
            sleep(15)

        # Cerrar la conexión a la base de datos
        conn.close()

        return 'enviado'
    except Exception as e:
        return 'no enviado ' + str(e)

@app.route('/promociones', methods=['GET'])
def get_promociones():
    conn = psycopg2.connect(
                dbname='chatbot_db',
                user='postgres',
                password='david1234',
                host='localhost',
                port='5432'
            )
    db_manager = DatabaseManager()
    promo=db_manager.consulta_promo_desc_json('postgresql',conn)
    return promo
   

@app.route('/envio_promociones', methods=['POST'])
def envios_masivo():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        timestamp = int(message['timestamp'])

        # Establecer conexión a la base de datos PostgreSQL
        # Obtener números de la base de datos  # Enviar mensaje usando send_whatsapp_message para cada número
        send_bulk_message()
        #enviar_mensaje(numero, text)
        sleep(15)
        # Cerrar la conexión a la base de datos
        return 'enviado'
    except Exception as e:
        return 'no enviado ' + str(e)


@app.route('/schedule', methods=['POST'])
def schedule():
    try:

        data = request.get_json()
        promocion_id = data['promocion_id']
        fecha_envio = data['fecha_envio']
        fecha_envio_dt = datetime.strptime(fecha_envio, '%Y-%m-%dT%H:%M')
        scheduler.add_job(send_bulk_message, 'date', run_date=fecha_envio_dt, args=[promocion_id])
        return jsonify({'message': 'Promoción agendada correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = services.replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        timestamp = int(message['timestamp'])

        services.administrar_chatbot(text, number,messageId,name,timestamp)
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

@app.route('/enviar_recordatorio', methods=['POST'])
def enviar_recodatorio():
    try:
          
        conn = psycopg2.connect(
                dbname='chatbot_db',
                user='postgres',
                password='david1234',
                host='localhost',
                port='5432'
            )
        db_manager = DatabaseManager()
        pagos_pendientes  = db_manager.recordatorios_pagos('postgresql', conn)
        #numero= db_manager.obtener_numeros_pagos('postgresql',conn)
        for number, nombre, saldo, fecha_vence in pagos_pendientes:
                mensaje = f"Hola {nombre}, tienes un pago pendiente de {saldo} que vence el {fecha_vence}. Por favor, realiza el pago lo antes posible para evitar cargos adicionales."
                
                recordatorio_mensajes_whatsap(number, mensaje)
        # Cerrar la conexión a la base de datos
        return 'enviado'
        
    except Exception as e:
        return 'no enviado ' + str(e)


if __name__ == '__main__':
    app.run()
    #driver = abrir_whatsapp_web()
    #services.monitorear_mensajes(driver)