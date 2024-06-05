from flask import Flask, request, session, make_response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from bbdd import *
from flask import jsonify
from historial_conversacion import *
from groq import Groq




app = Flask(__name__)
client = Groq(api_key="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")


def enviar_mensaje(mensaje):
    global historial
    historial.append({"role": "user", "content": mensaje})
    respuesta = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=historial,
        temperature=0.5,
        max_tokens=250
    )
    historial.append({"role": "assistant", "content": respuesta.choices[0].message.content})
    return respuesta.choices[0].message.content


#-----------------------------------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    message_body = request.form.get("Body")
    from_number = request.form.get("From")
    nombre = obtener_nombre_usuario(from_number)
    if message_body.lower() == "confirm":
        respuesta = mensaje_presentacion(nombre) 
    else:
        id_usuario = obtener_id_usuario(from_number)
        cargar_historial(nombre)
        agregar_preguntas_respuestas_al_historial(id_usuario)
        #print(obtener_ultimas_respuestas_usuario(id_usuario))
        
        respuesta = enviar_mensaje(message_body)   
        insertar_conversacion(message_body,respuesta,obtener_fecha_actual(),obtener_hora_actual(),id_usuario) 
    resp = MessagingResponse()
    resp.message(respuesta)
    for mensaje in historial:
        if mensaje["role"] == "assistant":
            print("")
            print(mensaje["content"])
    
    return str(resp)


#-----------------------------------------------------------------------------------------------------
if __name__=='__main__':
    app.run(debug=True, port=5000)
