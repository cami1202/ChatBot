import streamlit as st
from groq import Groq # Importar librerias

# configuracion de la ventana de la web
st.set_page_config(page_title="ChatBot", page_icon="👾")

#posicion            0           1                     2
MODELOS = ['llama3-8b-8192', 'llama3-70b-8192', 'mixtral-8x7b-32768']

# Nos conecta con la API, creando un usuario
def crerUsuarioGroq():
    claveSecreta = st.secrets["CLAVE_API"] # Obtenemos la clave de la API
    return Groq(api_key = claveSecreta)

#Selecciona el modelo de la IA
def configurarModelo(cliente, modelo, historial):
    historial = historial[-100:]  # Esto toma solo los últimos 100 elementos de la lista para evitar sobrecargar el historial
    mensajes_para_api = [{"role": msg["role"], "content": msg["content"]} for msg in historial] # Crea una lista de mensajes en el formato requerido (para coherencia)
    return cliente.chat.completions.create(
        model=modelo, #Seleccion el modelo de IA
        messages=mensajes_para_api,  # Pasa la lista de mensajes en el formato correcto (y limitada)
        stream=True #funcionalidad para q la IA me responda en tiempo real
    ) # Devuelve la respuesta que manda la IA

# Historial de mensaje
def inicializarEstado():
    #si NO existe "mensajes" entonces creamos un historial
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [] # [] -> historial vacio
        #                creo un espacio dentro de esa memoria q se llama mensajes

def configurarPagina():
    st.title("Chat de IA") #titulo
    st.sidebar.title("Configuración") # Barra de navegacion con un titulo
    opcion = st.sidebar.selectbox(
        # en la barra de navegacion hay un cuadrito de opciones para interactuar (titulo,opciones,valorPorDefecto)
        "Elegir modelo", #Titulo
        options = MODELOS, # opciones q Tienen q estar en una lista
        index = 1 # valor por defecto (de las opciones, segun su posicion)
        )
    return opcion #! AGREGAMOS ESTO PARA OBTENER EL NOMBRE DEL MODELO
    
def actualizarHistorial(rol,contenido,avatar):
    # Ingreso a esa memoria q existe en la pagina web y pido el valor q se llama mensajes. El append(dato) me agrega datos a la lista
    #                                   IA/User             mensaje      ícono q representa a c/u
    st.session_state.mensajes.append({"role" : rol, "content" : contenido, "avatar" : avatar}) #diccionario q guarda cada mensaje q despues va en el historial (linea 37)
    
def mostrarHistorial():
    # para cada mensaje dentro del historial:
    for mensaje in st.session_state.mensajes:
        #(With: agrega/agrupa operaciones/codigo). la función st.chat_message, crea una “burbuja” de chat visual en streamlit
        with st.chat_message(mensaje["role"], avatar= mensaje["avatar"]):
            st.markdown(mensaje["content"]) #Dentro de cada burbuja, y con lenguaje markdown (puede ser con un write simplemente) mostramos el contenido del mensaje
    
def areaChat(): # guarda la estructura visual del mensaje
    # variable guarda la configuracion del contenedor donde se guarden los mensajes
    contenedorDelChat = st.container(height= 600, border= True)
    # Abre el contenedor del chat y muestra el historial
    with contenedorDelChat: mostrarHistorial()

def generarRespuesta(chatCompleto):
    respuestaCompleta = "" # variable vacía
    for frase in chatCompleto:
        # (evitar un dato NONE)
        if frase.choices[0].delta.content: # si cada palabra q agarro tiene un contenido:
            respuestaCompleta += frase.choices[0].delta.content
            #                          para conseguir solo el contenido (palabras) y no todo el mensajote
            yield frase.choices[0].delta.content
    return respuestaCompleta

def main():
    #                                                        INVOCACION DE FUNCIONES!!!
    modelo = configurarPagina() # agarramos el modelo seleccionado
    clienteUsuario = crerUsuarioGroq() # se conecta con la API GROQ
    inicializarEstado() # se crea en memoria el historial vacio
    areaChat() # Se crea el contenedor/agrupación de los mensajes
    mensaje = st.chat_input("Escribí un mensaje...")
    
    #Verificar que cuando nos manden un mensaje tenga contenido (no este vacio):
    if mensaje:  #Si el mensaje es true (tiene contenido):
        # Añade el mensaje del usuario al historial
        actualizarHistorial("user", mensaje, "🤠") #Mostramos el mensaje por el chat
        chatCompleto = configurarModelo(clienteUsuario, modelo, st.session_state.mensajes) # Obtenemos la respuesta de la IA (Llama a la API con el historial completo en el formato adecuado)
        
        if chatCompleto: # verificar q la variable tenga algo (x si se rompe la api o algo)
            with st.chat_message("assistant"):
                respuestaCompleta = st.write_stream(generarRespuesta(chatCompleto))
                
                # Añade la respuesta de la IA al historial
                actualizarHistorial("assistant", respuestaCompleta, "🤖") #Mostramos el mensaje completo de la IA
                st.rerun()# actualizar (historial/chat) sin tocar f5

if __name__ == "__main__": # le digo a python q mi funcion principal es main() (siempre la va a correr)
    main()
