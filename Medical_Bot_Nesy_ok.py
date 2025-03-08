#!/usr/bin/env python
# coding: utf-8

import firebase_admin
from firebase_admin import credentials,firestore
from dotenv import load_dotenv
import os
dotenv_path = 'google.env'
load_dotenv(dotenv_path=dotenv_path)




cred_dict = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),  
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}


cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)


# In[4]:


from firebase_admin import firestore

db = firestore.client()


# In[5]:


import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
import json
import re
import uuid


# In[6]:


from telegram import Bot
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters,ConversationHandler,CallbackQueryHandler
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# In[7]:


load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")


# In[8]:


def verificar_y_añadir_usuario(usuario, num_telef, correo, nuevo_usuario_id, nuevo_usuario_data):
    try:
        usuarios_ref = db.collection('Usuario').document(usuario)
        documentos = usuarios_ref.get()
        if documentos.exists:
            datos = documentos.to_dict().get('datos', [])
            for data in datos:
                if data.get('nombre')==usuario and data.get('num_telef') != num_telef or data.get('correo') != correo:
                    return 'EXISTE'
                 
                
                elif data.get('num_telef') == num_telef or data.get('correo') == correo:
                    usuario_existente = data.get('nombre', 'Usuario')
                    return f'Bienvenido/a {usuario_existente} ¿cómo te puedo ayudar?'

        else:
            usuarios_ref.set(nuevo_usuario_data,merge=True)
            print('Usuario añadido correctamente')
            return f'Bienvenido, {usuario}.Tu usuario ha sido añadido correctamente.¿cómo te puedo ayudar?'
    except Exception as e:
        return f"Error al verificar o añadir el usuario: {str(e)}"


# In[9]:


(NOMBRE, TELEFONO, CORREO, CONFIRMACION, MENU, CITAS_MENU,AÑADIR_CITA,DESCRIPCION_CITA, CENTRO, 
ESPECIALISTA,FECHA,HORA,CONFIRMAR_CITA,CONSULTAR_CITA,LISTA_CITAS, OBTENER_CITA,MODIFICAR_CITA,SELECCIONAR_CITA,
NUEVA_DESCRIPCION, NUEVO_CENTRO, NUEVO_ESPECIALISTA, NUEVA_FECHA, NUEVA_HORA,ELIMINAR_CITA, SEL_ELIMINAR,CONFIRMAR_ELIMINAR,
 MEDICAMENTOS_MENU,DESCRIPCION_MED,MEDICAMENTO,TRATAMIENTO,FECHA_INICIO,FECHA_FINAL,CONFIRMAR_MEDICAMENTO,CONSULTAR_MEDICAMENTO,
 SELECCIONAR_MED,OBTENER_MED,NUEVA_DESCRIPCION_MED,NUEVO_MEDICAMENTO, NUEVO_TRATAMIENTO, NUEVA_FECHA_INICIO, NUEVA_FECHA_FINAL,
 ELIMINAR_MED,SEL_ELIMINAR_MED,CONFIRMAR_ELIMINAR_MED,INFO_MEDICAMENTO,NOMBRE_INFO,EXTRAER_PDF,EXTRAER_SECCIONES,MOSTRAR_SECCIONES
 
)=range(49)

# Función para iniciar la conversación
def greet(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('¡Hola! Soy Nesy tu bot de gestión de citas. Por favor, introduce tu nombre:')
    return NOMBRE

# Función para manejar el nombre
def handle_nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    update.message.reply_text('Gracias. Ahora, introduce tu número de teléfono:')
    return TELEFONO

# Función para manejar el número de teléfono
def handle_telefono(update: Update, context: CallbackContext) -> int:
    context.user_data['num_telef'] = update.message.text
    update.message.reply_text('Por último, introduce tu correo electrónico:')
    return CORREO

# Función para manejar el correo electrónico
def handle_correo(update: Update, context: CallbackContext) -> int:
    context.user_data['correo'] = update.message.text

    usuario = context.user_data['nombre']
    num_telef = context.user_data['num_telef']
    correo = context.user_data['correo']
    update.message.reply_text(
        f'Estos son sus datos:\n'
        f'Nombre: {usuario}\n'
        f'Teléfono: {num_telef}\n'
        f'Correo: {correo}\n'
        f'¿Es correcto? (sí/no)'
    )
    return CONFIRMACION

# Función para manejar la confirmación
def handle_confirmacion(update: Update, context: CallbackContext) -> int:
    confirmacion = update.message.text.lower().strip()
    respuestas_afirmativas = ['si', 'sí', 'sí, es correcto', 'correcto', 'claro', 'por supuesto', 'exacto', 'afirmativo', 'eso es', 'ok', 'vale', 'confirmado']
    respuestas_negativas = ['no', 'n', 'no, no es correcto', 'incorrecto', 'cancelar', 'cancelado']

    if confirmacion in respuestas_afirmativas:
        usuario = context.user_data['nombre']
        num_telef = context.user_data['num_telef']
        correo = context.user_data['correo']
        nuevo_usuario_id = str(uuid.uuid4())
        nuevo_usuario_data = {
            'datos': firestore.ArrayUnion([
                {
                    'user_id': nuevo_usuario_id, 
                    'nombre': usuario,
                    'num_telef': num_telef,
                    'correo': correo
                }
            ])
        }
        try:
            response = verificar_y_añadir_usuario(usuario, num_telef, correo, nuevo_usuario_id, nuevo_usuario_data)
            if response=='EXISTE':
                update.message.reply_text('Este usuario ya existe. Prueba con otro nombre.')
                return greet(update, context) 
            update.message.reply_text(response)
            if 'Bienvenido' in response:
                return send_card_menu(update, context)
        except Exception as e:
            update.message.reply_text(f"Error al verificar o añadir el usuario: {e}")
            
    elif confirmacion in respuestas_negativas:
        update.message.reply_text('Operación cancelada. Por favor, inicia de nuevo el proceso si deseas registrar tus datos.')
        return greet(update, context) 
    else:
        update.message.reply_text('Respuesta no reconocida. Por favor, responde con "sí" o "no".')
        return CONFIRMACION  # Vuelve a pedir la confirmación si la respuesta no es válida

    return ConversationHandler.END  # Terminar la conversación


# # MENU GENERAL #

# In[11]:


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
#funcion para menu general
def send_card_menu(update: Update, context: CallbackContext)->int:
    keyboard = [
        [InlineKeyboardButton("CITAS", callback_data='citas')],
        [InlineKeyboardButton("MEDICAMENTOS", callback_data='medicamentos')],
        [InlineKeyboardButton("FARMACIA", callback_data='info_medicamento')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        image_path = "enfermera.png"
        with open(image_path, 'rb') as image_file:
            usuario = context.user_data['nombre']
            if update.message:
                update.message.reply_photo(
                    photo=image_file,
                    caption=f'Bienvenido/a {usuario}, ¿cómo te puedo ayudar?',
                    reply_markup=reply_markup
                )
            #update.message.reply_photo(photo=image_file, caption=f'Bienvenido/a {usuario} ¿cómo te puedo ayudar?', reply_markup=reply_markup)
            elif update.callback_query:
                update.callback_query.message.reply_photo(
                    photo=image_file,
                    caption=f'Bienvenido/a {usuario}, ¿cómo te puedo ayudar?',
                    reply_markup=reply_markup)
                
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")
        
        return MENU
    return MENU
# Función para manejar las opciones del menú
def button(update: Update, context: CallbackContext)->int:
    query = update.callback_query
    query.answer()
    #chat_id = query.message.chat_id
    if query.data == 'citas':
        print ('mostrando citas')
        return  show_citas_menu(query)
    if query.data == 'medicamentos':
        return show_medicamento_menu(query)
    elif query.data == 'info_medicamento':
        query.message.reply_text('Introduce el nombre completo del medicamento y el laboratorio ("Paracetamol Kern Pharma"): ')
        return INFO_MEDICAMENTO
# Aquí se añadirían los controladores de mensajes


# # MENU CITAS # 

# In[13]:


#funcion para el menu de citas
def show_citas_menu(query)-> int:
    citas_keyboard = [
        [InlineKeyboardButton("Añadir cita", callback_data='añadir_cita')],
        [InlineKeyboardButton("Consultar cita", callback_data='consultar_cita')],
        [InlineKeyboardButton("Modificar cita", callback_data='modificar_cita')],
        [InlineKeyboardButton("Eliminar cita", callback_data='eliminar_cita')],
        [InlineKeyboardButton("Menu principal", callback_data='menu_principal')]
    ]
    
    reply_markup = InlineKeyboardMarkup(citas_keyboard)
    try:
        image_path = "cuaderno.png"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"La imagen no se encuentra en la ruta especificada: {image_path}")
        with open(image_path, 'rb') as image_file:
                query.message.reply_photo(photo=image_file, caption="¿Cómo te puedo ayudar con tus citas?:",reply_markup=reply_markup)
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")
        
        return CITAS_MENU

    return CITAS_MENU


# # Añadir cita #

# In[15]:


#funcion para manejar la descripcion de la cita 
def handle_descripcion_cita(update, context):
    context.user_data['descripcion_cita'] = update.message.text
    update.message.reply_text('¿Nombre del centro?')
    return CENTRO
#funcion para manejar el centro
def handle_centro(update, context):
    context.user_data['centro'] = update.message.text
    update.message.reply_text('¿Especialista?')
    return ESPECIALISTA
#funcion para manejar el especialista
def handle_especialista(update, context):
    context.user_data['especialista'] = update.message.text
    update.message.reply_text('Introduce la fecha:')
    return FECHA
#funcion para manejar la fecha
def handle_fecha(update, context):
    context.user_data['fecha'] = update.message.text
    update.message.reply_text('Introduce la hora:')
    return HORA
#funcion para manejar la hora
def handle_hora(update, context):
    context.user_data['hora'] = update.message.text
    descripcion= context.user_data['descripcion_cita']
    centro= context.user_data['centro']
    especialista= context.user_data['especialista']
    fecha = context.user_data['fecha']
    hora= context.user_data['hora']
    update.message.reply_text(
        f'Estas es la cita:\n'
        f'Descripción: {descripcion}\n'
        f'Centro: {centro}\n'
        f'Especialista: {especialista}\n'
        f'Fecha: {fecha}\n'
        f'Hora: {hora}\n'
        f'¿Es correcto? (sí/no)'
    )
    return CONFIRMAR_CITA


# In[16]:


#funcion para manejar la confirmacion de la cita
def handle_confirmacion_cita(update: Update, context: CallbackContext) -> int:
    confirmacion = update.message.text.lower().strip()
    respuestas_afirmativas = ['si', 'sí', 'sí, es correcto', 'correcto', 'claro', 'por supuesto', 'exacto', 'afirmativo', 'eso es', 'ok', 'vale', 'confirmado']
    respuestas_negativas = ['no', 'n', 'no, no es correcto', 'incorrecto', 'cancelar', 'cancelado']

    if confirmacion in respuestas_afirmativas:
        try:
            usuario=context.user_data['nombre']
            cita_id = str(uuid.uuid4())
            usuario_ref = db.collection('Usuario').document(usuario)
            descripcion= context.user_data['descripcion_cita']
            centro= context.user_data['centro']
            especialista= context.user_data['especialista']
            fecha = context.user_data['fecha']
            hora= context.user_data['hora']
            usuario_data = {
            
                'citas': firestore.ArrayUnion([
                    {
                        'descripcion':descripcion,
                        'id': cita_id,
                        'centro': centro,
                        'especialista': especialista,
                        'fecha': fecha,
                        'hora': hora
                    }
                ])}
            usuario_ref.set(usuario_data,merge=True)
            update.message.reply_text("Cita añadida exitosamente.")
            return send_card_menu(update, context)
        except Exception as e:
            print(f"Error al añadir la cita: {e}")
    elif confirmacion in respuestas_negativas:
        update.message.reply_text('Operación cancelada. Por favor, inicia de nuevo el proceso para añadir cita.')
        return show_citas_menu(query) 
    else:
        update.message.reply_text('Respuesta no reconocida. Por favor, responde con "sí" o "no".')
        return CONFIRMAR_CITA  # Vuelve a pedir la confirmación si la respuesta no es válida

    return ConversationHandler.END# Terminar la conversación
           


# # Consultar citas #

# In[18]:


#funcion para manejar la consulta de citas
def consultar_cita (update: Update, context: CallbackContext,query) -> int:
        try:
            usuario=context.user_data['nombre']      
            usuario_ref = db.collection('Usuario').document(usuario)
            usuario_cita = usuario_ref.get()
            if usuario_cita.exists:
                citas = usuario_cita.to_dict().get('citas',[])
                if not citas:
                    query.message.reply_text ('No se encontraron citas')
                else:
                    citas_format=[]
                    for i, cita in enumerate (citas,1):
                        citas_format.append(
                        f"*Cita {i}:*\n"
                        f"- **Descripción:** {cita['descripcion']}\n"
                        f"- **Fecha:** {cita['fecha']}\n"
                        f"- **Hora:** {cita['hora']}\n"
                        f"- **Centro:** {cita['centro']}\n"
                        f"- **Especialista:** {cita['especialista']}\n"
                    )
                    query.message.reply_text('\n\n'.join(citas_format), parse_mode='Markdown')
                    
                    return  show_citas_menu(query)
            else: 
                query.message.reply_text("Usuario no encontrado.")
        except Exception as e:
                query.message.reply_text(f'Error al consultar citas: {e}')
                return CONSULTAR_CITA
        return ConversationHandler.END
    
    


# # Modificar citas #

# In[20]:


#funcion para modificar las citas
#funcion para obtener las citas y manejarlas
def obtener_cita(update: Update, context: CallbackContext,query):
    try:
        query.message.reply_text('Aqui tienes todas tus citas.')
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario = usuario_ref.get()
        
        if usuario.exists:
            citas = usuario.to_dict().get('citas', [])
            lista1=[]
            for i,cita in enumerate(citas,1):
                lista=[i, cita["descripcion"], cita["fecha"], cita["id"]]
                lista1.append(lista)
                query.message.reply_text (f'{i}: {cita["descripcion"]}:{cita["especialista"]}:{cita["fecha"]}: {cita["id"]}')
            context.user_data['lista1']=lista1
            keyboard = [[str(i + 1)] for i in range(len(lista))]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            query.message.reply_text(
                "Selecciona el número de la cita que quieres modificar:",
                reply_markup=reply_markup
            )
            return SELECCIONAR_CITA
        else:
            query.message.reply_text ("Usuario no encontrado.")
    except Exception as e:
        print(f'Error al obtener citas: {e}')
        return show_citas_menu(query)


# In[21]:


##funcion para manejar la seleccion de cita 
def select_cita(update: Update, context: CallbackContext):
    try:
        cita_seleccionada = update.message.text
        cita_seleccionada = int(cita_seleccionada)

        lista_citas = context.user_data.get('lista1', [])
        if 1 <= cita_seleccionada <= len(lista_citas):
            sel = cita_seleccionada - 1
            cita_sel = lista_citas[sel]
            context.user_data['cita_sel']=cita_sel
            update.message.reply_text(f"\n✅ Has seleccionado: {cita_sel}")
            update.message.reply_text("Introduce una nueva descripcion para tu cita:")
            return NUEVA_DESCRIPCION
            # Aquí puedes añadir la lógica para modificar la cita
        else:
            update.message.reply_text("Número de cita no válido.")
            return show_citas_menu(query)
    except Exception as e:
        
        update.message.reply_text("Ocurrió un error al modificar la cita.")
        return ConversationHandler.END


# In[22]:


#funcion para manejar la nueva descripcion de cita
def nueva_descripcion(update: Update, context: CallbackContext):
    
    context.user_data['nueva_descripcion'] = update.message.text
    update.message.reply_text("Introduce el centro para tu cita:")
    return NUEVO_CENTRO
##funcion para manejar el nuevo centro
def nuevo_centro(update: Update, context: CallbackContext):
    
    context.user_data['nuevo_centro'] = update.message.text
    update.message.reply_text("Introduce el especialista para tu cita:")
    return NUEVO_ESPECIALISTA
#funcion para manejar el nuevo especialista
def nuevo_especialista(update: Update, context: CallbackContext):
    
    context.user_data['nuevo_especialista'] = update.message.text
    update.message.reply_text("Introduce la fecha para tu cita (formato: AAAA-MM-DD):")
    return NUEVA_FECHA
#funcion para manejar la nueva_fecha
def nueva_fecha(update: Update, context: CallbackContext):
    
    context.user_data['nueva_fecha'] = update.message.text
    update.message.reply_text("Introduce la hora para tu cita (formato: HH:MM):")
    return NUEVA_HORA
#funcion para manejar la nueva_hora
def nueva_hora(update: Update, context: CallbackContext):
    hora = update.message.text
    context.user_data['nueva_hora'] = hora
    
    cita_sel = context.user_data.get('cita_sel', [])
    nueva_descripcion = context.user_data['nueva_descripcion']
    nuevo_centro = context.user_data['nuevo_centro']
    nuevo_especialista = context.user_data['nuevo_especialista']
    nueva_fecha = context.user_data['nueva_fecha']
    nueva_hora = context.user_data['nueva_hora']
    
    try:
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario_doc = usuario_ref.get()
        if usuario_doc.exists:
            citas1 = usuario_doc.to_dict().get('citas', [])
            for cita in citas1:
                if cita_sel[3] == cita['id']:
                    coincidencia=cita
                    usuario_data = {
                                'descripcion':nueva_descripcion,
                                'centro': nuevo_centro,
                                'especialista': nuevo_especialista,
                                'fecha': nueva_fecha,
                                'hora': nueva_hora
                            }
                    cita.update(usuario_data)
                    usuario_ref.update({'citas':citas1})
                    print("Cita modificada exitosamente.")
                    update.message.reply_text(f"\n✅ Cita actualizada:\nDescripción: {nueva_descripcion}\nCentro: {nuevo_centro}\nEspecialista: {nuevo_especialista}\nFecha: {nueva_fecha}\nHora: {nueva_hora}")
                    return send_card_menu(update, context)
                else:
                    print("Cita no encontrada.")
                    return send_card_menu(update, context)
        
    except Exception as e:
        print(f"Error al modificar la cita: {e}")

           
    return ConversationHandler.END
    


# # Eliminar cita #

# In[24]:


# funcion para eliminar una cita
def eliminar_cita(update: Update, context: CallbackContext,query):
    try:
        query.message.reply_text('Aqui tienes todas tus citas.')
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario = usuario_ref.get()
        
        if usuario.exists:
            citas = usuario.to_dict().get('citas', [])
            lista1=[]
            for i,cita in enumerate(citas,1):
                lista=[i, cita["descripcion"], cita["fecha"], cita["id"]]
                lista1.append(lista)
                query.message.reply_text (f'{i}: {cita["descripcion"]}:{cita["especialista"]}:{cita["fecha"]}: {cita["id"]}')
            context.user_data['lista1']=lista1
            keyboard = [[str(i + 1)] for i in range(len(lista))]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            query.message.reply_text(
                "Selecciona el número de la cita que quieres eliminar:",
                reply_markup=reply_markup
            )
            return SEL_ELIMINAR
        else:
            query.message.reply_text ("Usuario no encontrado.")
    except Exception as e:
        print(f'Error al obtener citas: {e}')
        return ELIMINAR_CITA
#funcion para seleccionar una cita para eliminar        
def sel_eliminar(update: Update, context: CallbackContext):
    try:
        eliminar_cita = update.message.text
        eliminar_cita= int(eliminar_cita)
        lista_citas= context.user_data['lista1']
        #cita_seleccionada = int(input("Selecciona el número de la cita que deseas eliminar: "))
        if 1 <= eliminar_cita <= len(lista_citas):
            sel=eliminar_cita - 1
            cita_sel=(lista_citas[eliminar_cita - 1])
            context.user_data['cita_sel']= cita_sel
            update.message.reply_text(f"\n✅ Has seleccionado: {lista_citas[eliminar_cita- 1]})")
            update.message.reply_text("¿Estás seguro de que deseas eliminar esta cita? (s/n): ")
            return CONFIRMAR_ELIMINAR
        else:
            update.message.reply_text("Número de cita no válido.")
            return SEL_ELIMINAR
        update.message.reply_text("¿Estás seguro de que deseas eliminar esta cita? (s/n): ")
    except Exception as e:
        print(f'Error al eliminar cita: {e}')
        return SEL_ELIMINAR 
#funcion para confirmar cita a eliminar
def confirmar_eliminar(update: Update, context: CallbackContext)->int:
    try:
        confirmacion=update.message.text
        respuestas_afirmativas = ['si', 'sí', 'sí, es correcto', 'correcto', 'claro', 'por supuesto', 'exacto', 'afirmativo', 'eso es', 'ok', 'vale', 'confirmado']
        if confirmacion.lower() in respuestas_afirmativas:
            usuario1=context.user_data['nombre']
            usuario_ref = db.collection('Usuario').document(usuario1)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                citas1 = usuario_doc.to_dict().get('citas', [])
                cita_sel=context.user_data['cita_sel']
                for cita in citas1:
                    if cita_sel[3] == cita['id']:
                        coincidencia=cita
                        #print(cita)
                        citas1.remove(cita)
                        usuario_ref.update({'citas': citas1})
                        update.message.reply_text("Cita eliminada exitosamente.")
                        return send_card_menu(update, context)
                    else:
                        update.message.reply_text("No se pudo eliminar la cita.")
                        return  ConversationHandler.END
            update.message.reply_text("Intentalo de nuevo.")
            
    except Exception as e:
        print(f"Error al eliminar la cita: {e}")
        return  ConversationHandler.END


# In[25]:


#funcion para manejar los botones del menu de citas
def button_citas(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'añadir_cita':
        query.message.reply_text("Por favor, proporciona la descripción de la cita:")
        return DESCRIPCION_CITA
    elif query.data== 'consultar_cita':
        query.message.reply_text("Aqui tienes todas tus citas: ")
        return consultar_cita(update,context,query)
    elif query.data == 'modificar_cita':
        return obtener_cita(update,context,query)
    elif query.data == 'eliminar_cita':
        return eliminar_cita(update,context,query)
    elif query.data =='menu_principal':
        return send_card_menu(update, context)


# # MEDICAMENTOS #
# ## Menu Medicamentos ##

# In[27]:


#funcion para manejar el menu de medicamentos
def show_medicamento_menu(query)-> int:
    medicamento_keyboard = [
        [InlineKeyboardButton("Añadir medicamento", callback_data='añadir_medicamento')],
        [InlineKeyboardButton("Consultar medicamento", callback_data='consultar_medicamento')],
        [InlineKeyboardButton("Modificar medicamento", callback_data='modificar_medicamento')],
        [InlineKeyboardButton("Eliminar medicamento", callback_data='eliminar_medicamento')],
        [InlineKeyboardButton("Menu principal", callback_data='menu_principal')]
        
    ]
    
    reply_markup = InlineKeyboardMarkup(medicamento_keyboard)
    try:
        image_path = "medicinas.png"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"La imagen no se encuentra en la ruta especificada: {image_path}")
        with open(image_path, 'rb') as image_file:
                query.message.reply_photo(photo=image_file, caption="¿Cómo te puedo ayudar con tus medicamentos?:",reply_markup=reply_markup)
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")
        
        return MEDICAMENTOS_MENU

    return MEDICAMENTOS_MENU


# In[28]:


#funcion para manejar la botonera del menu medicamentos
def button_medicamentos(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'añadir_medicamento':
        query.message.reply_text("Por favor, proporciona la descripción de tu medicamento:")
        return DESCRIPCION_MED
    elif query.data== 'consultar_medicamento':
        query.message.reply_text("Aqui tienes todos tus medicamentos: ")
        return consultar_med(update,context,query)
    elif query.data == 'modificar_medicamento':
        return obtener_medicamento(update,context,query)
    elif query.data == 'eliminar_medicamento':
        return eliminar_med(update,context,query)
    elif query.data =='menu_principal':
        return send_card_menu(update, context)


# ## AÑADIR MEDICAMENTO ##

# In[30]:


#funcion para manejar la descripcion del medicamento
def handle_descripcion_med(update, context):
    context.user_data['descripcion_med'] = update.message.text
    update.message.reply_text('¿Nombre del medicamento?')
    return MEDICAMENTO
#funcion para manejar el nombre del medicamento
def handle_med_name(update, context):
    context.user_data['nombre_med'] = update.message.text
    update.message.reply_text('Introduce el tratamiento:')
    return TRATAMIENTO
#funcion para manejar el tratamiento
def handle_tratamiento(update, context):
    context.user_data['tratamiento'] = update.message.text
    update.message.reply_text('Introduce la fecha de inicio del tratamiento:')
    return FECHA_INICIO
#funcion para manejar el inicio del tratamiento
def handle_fecha_inicio(update, context):
    context.user_data['fecha_inicio'] = update.message.text
    update.message.reply_text('Introduce la ficha del fin del tratamiento:')
    return FECHA_FINAL
#funcion para manejar el fin del tratamiento
def handle_fecha_final(update, context):
    context.user_data['fecha_final'] = update.message.text
    descripcion_med= context.user_data['descripcion_med']
    medicamento= context.user_data['nombre_med']
    tratamiento= context.user_data['tratamiento']
    fecha_inicio = context.user_data['fecha_inicio']
    fecha_final= context.user_data['fecha_final']
    update.message.reply_text(
        f'Estas es la cita:\n'
        f'Descripción: {descripcion_med}\n'
        f'Medicamento: {medicamento}\n'
        f'Tratamiento: {tratamiento}\n'
        f'Fecha de inicio: {fecha_inicio}\n'
        f'Fecha de finalizacion: {fecha_final}\n'
        f'¿Es correcto? (sí/no)'
    )
    return CONFIRMAR_MEDICAMENTO


# In[31]:


#funcion para manejar la confirmacion del medicamento
def handle_confirmacion_medicamento(update: Update, context: CallbackContext) -> int:
    confirmacion = update.message.text.lower().strip()
    respuestas_afirmativas = ['si', 'sí', 'sí, es correcto', 'correcto', 'claro', 'por supuesto', 'exacto', 'afirmativo', 'eso es', 'ok', 'vale', 'confirmado']
    respuestas_negativas = ['no', 'n', 'no, no es correcto', 'incorrecto', 'cancelar', 'cancelado']

    if confirmacion in respuestas_afirmativas:
        try:
            usuario=context.user_data['nombre']
            medicamento_id = str(uuid.uuid4())
            usuario_ref = db.collection('Usuario').document(usuario)
            descripcion_med= context.user_data['descripcion_med']
            medicamento= context.user_data['nombre_med']
            tratamiento= context.user_data['tratamiento']
            fecha_inicio = context.user_data['fecha_inicio']
            fecha_final= context.user_data['fecha_final']
            usuario_data = {
            
                'medicamentos': firestore.ArrayUnion([
                    {
                        'descripcion':descripcion_med,
                        'id': medicamento_id,
                        'medicamento':medicamento ,
                        'tratamiento': tratamiento,
                        'fecha de inicio': fecha_inicio,
                        'fecha de fin': fecha_final
                    }
                ])}
            usuario_ref.set(usuario_data,merge=True)
            update.message.reply_text("Medicamento añadido exitosamente.")
            return send_card_menu(update, context)
        except Exception as e:
            print(f"Error al añadir tu medicamento: {e}")
    elif confirmacion in respuestas_negativas:
        update.message.reply_text('Operación cancelada. Por favor, inicia de nuevo el proceso para añadir medicamento.')
        return show_citas_menu(query) 
    else:
        update.message.reply_text('Respuesta no reconocida. Por favor, responde con "sí" o "no".')
        return CONFIRMAR_MEDICAMENTO  # Vuelve a pedir la confirmación si la respuesta no es válida

    return ConversationHandler.END# Terminar la conversación


# # Consultar medicamentos #

# In[33]:


#funcion para manejar la consulta de medicamentos
def consultar_med (update: Update, context: CallbackContext,query) -> int:
        try:
            usuario=context.user_data['nombre']      
            usuario_ref = db.collection('Usuario').document(usuario)
            usuario_med = usuario_ref.get()
            if usuario_med.exists:
                meds = usuario_med.to_dict().get('medicamentos',[])
                if not meds:
                    query.message.reply_text ('No se encontraron medicamentos')
                else:
                    medicamentos_format=[]
                    for i, med in enumerate (meds,1):
                        medicamentos_format.append(
                        f"*Medicamento {i}:*\n"
                        f"- **Descripción:** {med['descripcion']}\n"
                        f"- **Nombre del medicamento:** {med['medicamento']}\n"
                        f"- **Tratamiento:**{med['tratamiento']}\n"
                        f"- **Fecha de inicio:** {med['fecha de inicio']}\n"
                        f"- **Fecha de fin:** {med['fecha de fin']}\n"
                       
                    )
                    query.message.reply_text('\n\n'.join(medicamentos_format), parse_mode='Markdown')
                    
                    return  show_medicamento_menu(query)
            else: 
                query.message.reply_text("Usuario no encontrado.")
        except Exception as e:
                query.message.reply_text(f'Error al consultar medicamentos: {e}')
                return CONSULTAR_MEDICAMENTO
        return ConversationHandler.END


# # Modificar medicamento #

# In[35]:


#funcion para manejar la modificacion de medicamentos
#funcion para obtener medicamentos
def obtener_medicamento(update: Update, context: CallbackContext,query):
    try:
        query.message.reply_text('Aqui tienes todos tus medicamentos.')
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario = usuario_ref.get()
        
        if usuario.exists:
            meds = usuario.to_dict().get('medicamentos', [])
            lista_med=[]
            for i,med in enumerate(meds,1):
                lista=[i, med["descripcion"], med["medicamento"], med["id"]]
                lista_med.append(lista)
                query.message.reply_text (f'{i}: {med["descripcion"]}:{med["medicamento"]}:{med["id"]}')
            context.user_data['lista_med']=lista_med
            keyboard = [[str(i + 1)] for i in range(len(lista))]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            query.message.reply_text(
                "Selecciona el número del medicamento que quieres modificar:",
                reply_markup=reply_markup
            )
            return SELECCIONAR_MED
        else:
            query.message.reply_text ("Usuario no encontrado.")
    except Exception as e:
        print(f'Error al obtener medicamentos: {e}')
        return show_medicamento_menu(query)


# In[36]:


#funcion para manejar seleccion de medicamentos
def select_med(update: Update, context: CallbackContext):
    try:
        med_seleccionado = update.message.text
        med_seleccionado = int(med_seleccionado)

        lista_med = context.user_data.get('lista_med', [])
        if 1 <= med_seleccionado <= len(lista_med):
            sel = med_seleccionado - 1
            med_sel = lista_med[sel]
            context.user_data['med_sel']=med_sel
            update.message.reply_text(f"\n✅ Has seleccionado: {med_sel}")
            update.message.reply_text("Introduce una nueva descripcion para tu cita:")
            return NUEVA_DESCRIPCION_MED
            # Aquí puedes añadir la lógica para modificar la cita
        else:
            update.message.reply_text("Número de medicamento no válido.")
            return ConversationHandler.END
    except Exception as e:
        
        update.message.reply_text("Ocurrió un error al modificar el medicamento.")
        return ConversationHandler.END


# In[37]:


#funcion para manerjar la nueva descripcion del medicamento
def nueva_descripcion_med(update: Update, context: CallbackContext):
    
    context.user_data['nueva_descripcion_med'] = update.message.text
    update.message.reply_text("Introduce el nuevo medicamento:")
    return NUEVO_MEDICAMENTO
#funcion para manejar el nuevo nombre de medicamento
def nuevo_medicamento(update: Update, context: CallbackContext):
    
    context.user_data['nuevo_medicamento'] = update.message.text
    update.message.reply_text("Introduce el tratamiento:")
    return NUEVO_TRATAMIENTO
#funcion para manejar el nuevo tratamiento
def nuevo_tratamiento(update: Update, context: CallbackContext):
    
    context.user_data['nuevo_tratamiento'] = update.message.text
    update.message.reply_text("Introduce la fecha de inicio del tratamiento (formato: DD-MM-AAAA):")
    return NUEVA_FECHA_INICIO
#funcion para manejar la nueva fecha de inicio
def nueva_fecha_inicio(update: Update, context: CallbackContext):
    
    context.user_data['nueva_fecha_inicio'] = update.message.text
    update.message.reply_text("Introduce la fecha del final del tratamiento (formato: DD-MM-AAAA):")
    return NUEVA_FECHA_FINAL
#funcion para manejar la nueva fecha de fin
def nueva_fecha_final(update: Update, context: CallbackContext):
    final = update.message.text
    context.user_data['nueva_fecha_final'] = final

    med_sel = context.user_data.get('med_sel', [])
    nueva_descripcion_med = context.user_data['nueva_descripcion_med']
    nuevo_medicamento = context.user_data['nuevo_medicamento']
    nuevo_tratamiento = context.user_data['nuevo_tratamiento']
    nueva_fecha_inicio = context.user_data['nueva_fecha_inicio']
    nueva_fecha_final = context.user_data['nueva_fecha_final']
    
    try:
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario_doc = usuario_ref.get()
        if usuario_doc.exists:
            meds = usuario_doc.to_dict().get('medicamentos', [])
            for med in meds:
                if med_sel[3] == med['id']:
                    coincidencia=med
                    usuario_data = {
                                'descripcion':nueva_descripcion_med,
                                'medicamento': nuevo_medicamento,
                                'tratamiento': nuevo_tratamiento,
                                'fecha de inicio': nueva_fecha_inicio,
                                'fecha de fin': nueva_fecha_final
                            }
                    med.update(usuario_data)
                    usuario_ref.update({'medicamentos':meds})
                    print("Medicamento modificada exitosamente.")
                    update.message.reply_text(f"\n✅ Medicamento actualizado:\nDescripción: {nueva_descripcion}\n: {nuevo_medicamento}\nEspecialista: {nuevo_tratamiento}\nFecha de inicio: {nueva_fecha_inicio}\nFecha de fin: {nueva_fecha_final}")
                    return send_card_menu(update, context)
                else:
                    print("Medicamento no encontrada.")
                    return send_card_menu(update, context)
        
    except Exception as e:
        print(f"Error al modificar el medicamento: {e}")

           
    return ConversationHandler.END
    


# # eliminar medicamento #

# In[39]:


#funcion pora manejar la eliminacion de medicamentos
def eliminar_med(update: Update, context: CallbackContext,query):
    try:
        query.message.reply_text('Aqui tienes todos tus medicamentos.')
        usuario1=context.user_data['nombre'] 
        usuario_ref = db.collection('Usuario').document(usuario1)
        usuario = usuario_ref.get()
        
        if usuario.exists:
            meds = usuario.to_dict().get('medicamentos', [])
            lista_med=[]
            for i,med in enumerate(meds,1):
                lista=[i, med["descripcion"], med["medicamento"], med["id"]]
                lista_med.append(lista)
                query.message.reply_text (f'{i}: {med["descripcion"]}:{med["medicamento"]}:{med["fecha de inicio"]}/ {med["fecha de fin"]} : {med["id"]}')
            context.user_data['lista_med']=lista_med
            keyboard = [[str(i + 1)] for i in range(len(lista))]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            query.message.reply_text(
                "Selecciona el número de la cita que quieres eliminar:",
                reply_markup=reply_markup
            )
            return SEL_ELIMINAR_MED
        else:
            query.message.reply_text ("Usuario no encontrado.")
    except Exception as e:
        print(f'Error al obtener citas: {e}')
        return ELIMINAR_MED
#funcion para manejar la seleccion de medicamento a eliminar      
def sel_eliminar_med(update: Update, context: CallbackContext):
    try:
        eliminar_med = update.message.text
        eliminar_med= int(eliminar_med)
        lista_med= context.user_data['lista_med']
        #cita_seleccionada = int(input("Selecciona el número de la cita que deseas eliminar: "))
        if 1 <= eliminar_med <= len(lista_med):
            sel=eliminar_med - 1
            med_sel=(lista_med[eliminar_med - 1])
            context.user_data['med_sel']= med_sel
            update.message.reply_text(f"\n✅ Has seleccionado: {lista_med[eliminar_med- 1]})")
            update.message.reply_text("¿Estás seguro de que deseas eliminar este medicamento? (si/no): ")
            return CONFIRMAR_ELIMINAR_MED
        else:
            update.message.reply_text("Número de cita no válido.")
            return SEL_ELIMINAR_MED
        update.message.reply_text("¿Estás seguro de que deseas eliminar este medicamento? (si/no): ")
    except Exception as e:
        print(f'Error al eliminar cita: {e}')
        return SEL_ELIMINAR_MED
#funcion para manejar la confirmacion de eliminacion de medicamentos
def confirmar_eliminar_med(update: Update, context: CallbackContext)->int:
    try:
        confirmacion=update.message.text
        respuestas_afirmativas = ['si', 'sí', 'sí, es correcto', 'correcto', 'claro', 'por supuesto', 'exacto', 'afirmativo', 'eso es', 'ok', 'vale', 'confirmado']
        if confirmacion.lower() in respuestas_afirmativas:
            usuario1=context.user_data['nombre']
            usuario_ref = db.collection('Usuario').document(usuario1)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                meds = usuario_doc.to_dict().get('medicamentos', [])
                med_sel=context.user_data['med_sel']
                for med in meds:
                    if med_sel[3] == med['id']:
                        coincidencia=med
                        #print(cita)
                        meds.remove(med)
                        usuario_ref.update({'medicamento': meds})
                        update.message.reply_text("Medicamento eliminado exitosamente.")
                        return send_card_menu(update, context)
                    else:
                        update.message.reply_text("No se pudo eliminar el medicamento.")
                        return  ConversationHandler.END
            update.message.reply_text("Intentalo de nuevo.")
            
    except Exception as e:
        print(f"Error al eliminar el medicamento: {e}")
        return  ConversationHandler.END


# # INFO MEDICAMENTO #

# In[ ]:





# In[41]:


from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


# In[42]:


# Función para dividir el texto en fragmentos más pequeños basados en la cantidad máxima de tokens.
def split_text(text, max_tokens, tokenizer):
   tokens = tokenizer.encode(text)
   chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
   return [tokenizer.decode(chunk) for chunk in chunks]
# Función para resumir cada fragmento de texto utilizando un modelo de resumen.
def summarize_text(text_chunks, summarizer):
   summaries = []
   for chunk in text_chunks:
       summary = summarizer(chunk, max_length=50, min_length=20, do_sample=False)
       summaries.append(summary[0]['summary_text'])
   return summaries

# Función para controlar la longitud del texto final asegurándose de que no supere una longitud máxima.
def controlar_longitud_texto(texto, longitud_maxima=4000):
   if len(texto) > longitud_maxima:
       texto = texto[:longitud_maxima]
   return texto
# Función para controlar la longitud del texto final asegurándose de que no supere una longitud máxima.
def resumen(resumir, context):
   max_tokens = 512
   model_name = "t5-small"
   
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   summarizer = pipeline("summarization", model=model_name, tokenizer=tokenizer)
   
   text_chunks = split_text(resumir, max_tokens, tokenizer)
   summaries = summarize_text(text_chunks, summarizer)
   
   final_summary = " ".join(summaries)
   
   # Controlar la longitud del texto final
   final_summary = controlar_longitud_texto(final_summary)
   
   context.user_data['final_summary'] = final_summary
  
   
   return final_summary


# In[43]:


#funcion para extraer pdf del prospecto
def extraer_pdf(url,context: CallbackContext):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Lanza una excepción si la descarga falla

    pdf_file = io.BytesIO(response.content)
    lector = PyPDF2.PdfReader(pdf_file)
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
        
    return texto


# In[44]:


#funcion para extraer las secciones del prospecto y su contenido
def extraer_secciones(text:str,update: Update, context: CallbackContext):
    prospecto1=context.user_data['prospecto']
  
    pattern = r'\n([0-9]+\.\s.*?)(?=\n[0-9]+\.\s|$)'
    matches = re.findall(pattern, prospecto1, re.DOTALL)
    secciones_strip={}
    
    for i, match in enumerate(matches):
        title_content = match.split('\n', 1)
        titulo = title_content[0]
        titulo_1= ' '.join(titulo.split()) 
        contenido1 = title_content[1].strip() if len(title_content) > 1 else ""
        # Si el título ya existe y el contenido está vacío, reemplazarlo
        if titulo in secciones_strip:
            if contenido:
                secciones_strip[titulo_1]=contenido1
        else:
            secciones_strip[titulo_1]=contenido1
    context.user_data['secciones_strip'] = secciones_strip
    keyboard = [ [titulo] for titulo in secciones_strip.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    # Mostrar el teclado de selección
    update.message.reply_text(
        "Selecciona la sección que quieres ver:",
        reply_markup=reply_markup
    )
    
    return  ConversationHandler.END
    


# In[45]:


#funcion para obtener informacion del medicamento por su nombre 
def info_medicamento(update: Update, context: CallbackContext):
    context.user_data['info_medicamento'] = update.message.text
    info_medicamento=context.user_data['info_medicamento']
   
    
    url = "https://cima.aemps.es/cima/rest/medicamentos"
    params = {
        "nombre": info_medicamento
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        datos = response.json()
        if datos.get("resultados"):
            if 'docs' in datos['resultados'][1]:
                url_doc = datos['resultados'][1]['docs'][1]['url']
                context.user_data['url_doc']=url_doc
                prospecto1=extraer_pdf(url_doc,context)
                context.user_data['prospecto'] = prospecto1
                sec=extraer_secciones(prospecto1,update,context)
                return MOSTRAR_SECCIONES
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontró información del prospecto.")
                return send_card_menu(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontraron resultados para el medicamento.")
            return send_card_menu(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error al acceder a la API de CIMA.")
        return send_card_menu(update, context)


# In[46]:


#funcion para mostra contenido de la seccion seleccionada
def mostrar_secciones(update: Update, context: CallbackContext):
    query = update.message.text
    url_doc = context.user_data.get('url_doc')
    secciones_strip=context.user_data['secciones_strip']
    if query in secciones_strip:
        if len(secciones_strip[query]) >4096:
            update.message.reply_text("Un momento.Estoy buscando la informacion")
            resumir=secciones_strip[query]
            summa=resumen(resumir,context)
            update.message.reply_text(f"{summa}\n\nMás información aquí: {url_doc}")
            return send_card_menu(update, context)
        else:
            update.message.reply_text(f"Contenido: {secciones_strip[query]}\n\nMás información aquí: {url_doc}")
            return send_card_menu(update, context)
    else:
        update.message.reply_text("Índice no válido.")
        return send_card_menu(update, context)

    
        update.message.reply_text("Sección no encontrada.")

    return ConversationHandler.END
    
   


# In[47]:


# Función para manejar cancelaciones
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Operación cancelada. ¡Hasta luego!')
    return ConversationHandler.END


# In[ ]:


# Configura el bot
def main() -> None:
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    # Configura el manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(hola|Hola)$'), greet)
                     ],
                      
        states={
            NOMBRE: [MessageHandler(Filters.text & ~Filters.command, handle_nombre)],
            TELEFONO: [MessageHandler(Filters.text & ~Filters.command, handle_telefono)],
            CORREO: [MessageHandler(Filters.text & ~Filters.command, handle_correo)],
            CONFIRMACION:[MessageHandler(Filters.text & ~Filters.command, handle_confirmacion)],
            MENU: [CallbackQueryHandler(button)],
            CITAS_MENU:[CallbackQueryHandler(button_citas)],
            DESCRIPCION_CITA: [MessageHandler(Filters.text & ~Filters.command, handle_descripcion_cita)],
            CENTRO: [MessageHandler(Filters.text & ~Filters.command, handle_centro)],
            ESPECIALISTA: [MessageHandler(Filters.text & ~Filters.command, handle_especialista)],
            FECHA:[MessageHandler(Filters.text & ~Filters.command, handle_fecha)],
            HORA:[MessageHandler(Filters.text & ~Filters.command, handle_hora)],
            CONFIRMAR_CITA: [MessageHandler(Filters.text & ~Filters.command, handle_confirmacion_cita)],
            CONSULTAR_CITA: [MessageHandler(Filters.text & ~Filters.command, consultar_cita)],
            LISTA_CITAS: [MessageHandler(Filters.text & ~Filters.command, consultar_cita)],
            OBTENER_CITA:[MessageHandler(Filters.text & ~Filters.command, obtener_cita)],
            SELECCIONAR_CITA:[MessageHandler(Filters.text & ~Filters.command, select_cita)],
            NUEVA_DESCRIPCION: [MessageHandler(Filters.text & ~Filters.command, nueva_descripcion)],
            NUEVO_CENTRO: [MessageHandler(Filters.text & ~Filters.command, nuevo_centro)],
            NUEVO_ESPECIALISTA: [MessageHandler(Filters.text & ~Filters.command, nuevo_especialista)],
            NUEVA_FECHA: [MessageHandler(Filters.text & ~Filters.command, nueva_fecha)],
            NUEVA_HORA: [MessageHandler(Filters.text & ~Filters.command, nueva_hora)],
            ELIMINAR_CITA: [MessageHandler(Filters.text & ~Filters.command, eliminar_cita)],
            SEL_ELIMINAR:[MessageHandler(Filters.text & ~Filters.command, sel_eliminar)],
            CONFIRMAR_ELIMINAR:[MessageHandler(Filters.text & ~Filters.command, confirmar_eliminar)],
            MEDICAMENTOS_MENU:[CallbackQueryHandler(button_medicamentos)],
            DESCRIPCION_MED:[MessageHandler(Filters.text & ~Filters.command, handle_descripcion_med)],
            MEDICAMENTO:[MessageHandler(Filters.text & ~Filters.command, handle_med_name)],
            TRATAMIENTO:[MessageHandler(Filters.text & ~Filters.command, handle_tratamiento)],
            FECHA_INICIO:[MessageHandler(Filters.text & ~Filters.command, handle_fecha_inicio)],
            FECHA_FINAL:[MessageHandler(Filters.text & ~Filters.command, handle_fecha_final)],
            CONFIRMAR_MEDICAMENTO:[MessageHandler(Filters.text & ~Filters.command, handle_confirmacion_medicamento)],
            CONSULTAR_MEDICAMENTO: [MessageHandler(Filters.text & ~Filters.command, consultar_med)],
            OBTENER_MED:[MessageHandler(Filters.text & ~Filters.command, obtener_medicamento)],
            SELECCIONAR_MED:[MessageHandler(Filters.text & ~Filters.command, select_med)],
            NUEVA_DESCRIPCION_MED:[MessageHandler(Filters.text & ~Filters.command, nueva_descripcion_med)],
            NUEVO_MEDICAMENTO:[MessageHandler(Filters.text & ~Filters.command, nuevo_medicamento)],
            NUEVO_TRATAMIENTO:[MessageHandler(Filters.text & ~Filters.command, nuevo_tratamiento)],
            NUEVA_FECHA_INICIO:[MessageHandler(Filters.text & ~Filters.command, nueva_fecha_inicio)],
            NUEVA_FECHA_FINAL:[MessageHandler(Filters.text & ~Filters.command, nueva_fecha_final)],
            ELIMINAR_MED: [MessageHandler(Filters.text & ~Filters.command, eliminar_med)],
            SEL_ELIMINAR_MED:[MessageHandler(Filters.text & ~Filters.command, sel_eliminar_med)],
            CONFIRMAR_ELIMINAR_MED:[MessageHandler(Filters.text & ~Filters.command, confirmar_eliminar_med)],
            INFO_MEDICAMENTO:[MessageHandler(Filters.text & ~Filters.command, info_medicamento)],
            NOMBRE_INFO:[MessageHandler(Filters.text & ~Filters.command, info_medicamento)],
            EXTRAER_PDF:[MessageHandler(Filters.text & ~Filters.command, extraer_pdf)],
            EXTRAER_SECCIONES:[MessageHandler(Filters.text & ~Filters.command, extraer_secciones)],
            MOSTRAR_SECCIONES:[MessageHandler(Filters.text & ~Filters.command, mostrar_secciones)]
           
 
          
    
            
    
        
           
           
            
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    dispatcher.add_handler(conv_handler)

    # Inicia el bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


# In[ ]:




