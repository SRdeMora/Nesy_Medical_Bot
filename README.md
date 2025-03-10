# Nesy_Medical_Bot
# Nesy: Tu Bot de Gestión de Citas y Medicamentos en Telegram 

Nesy es un bot de Telegram diseñado para ayudarte a gestionar tus citas médicas y medicamentos de manera eficiente. Con Nesy, puedes añadir, consultar, modificar y eliminar citas, así como llevar un registro detallado de tus medicamentos y tratamientos.

## Funcionalidades Principales

- **Gestión de Citas**:
    - Añade nuevas citas con detalles como descripción, centro médico, especialista, fecha y hora.
    - Consulta tu lista de citas programadas.
    - Modifica citas existentes para actualizar cualquier detalle necesario.
    - Elimina citas que ya no necesitas.
- **Gestión de Medicamentos**:
    - Registra tus medicamentos con información detallada como nombre, tratamiento, dosis, y fechas de inicio y fin.
    - Consulta tu historial de medicamentos.
    - Modifica la información de medicamentos según sea necesario.
    - Elimina medicamentos de tu registro.
- **Información de Medicamentos**:
    - Obtén información detallada sobre medicamentos directamente desde la base de datos de la Agencia Española de Medicamentos y Productos Sanitarios (AEMPS).

## Cómo Usar Nesy

1. **Inicia la conversación con el bot**:
   - Busca "NesyBot" en Telegram y envía el mensaje "hola" para iniciar la conversación.
2. **Registro de usuario**:
   - Sigue las instrucciones del bot para registrar tu nombre, número de teléfono y correo electrónico.
3. **Navega por el menú principal**:
   - Utiliza los botones interactivos para seleccionar entre la gestión de citas, medicamentos o información de medicamentos.
4. **Interactúa con el bot**:
   - Sigue las indicaciones del bot para añadir, consultar, modificar o eliminar citas y medicamentos.

## Prerrequisitos
>[!IMPORTANT]
>Antes de ejecutar el bot, asegúrate de tener instalado lo siguiente:

- Python 3.6 o superior
- Librerías de Python:
  
        -firebase-admin==6.0.1
  
        -python-dotenv==1.0.0
  
        -flask==3.0.3
  
        -werkzeug==3.0.3
  
        -pypdf2==3.0.1
  
        -urllib3==1.26.16
  
        -python-telegram-bot==13.15
  
        -beautifulsoup4==4.12.2

- Token de bot de Telegram (puedes obtener uno hablando con @BotFather en Telegram)
- Archivo de credenciales de Firebase (Firebase.json)

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone [https://github.com/theodelrieu?tab=repositories](https://github.com/theodelrieu?tab=repositories)
   cd [nombre del repositorio]
2.  **Instala las dependencias**:
   pip install -r requirements.txt
3. **Configura las variables de entorno** :
   Crea un archivo .env en la raíz del proyecto y añade tu token de bot de Telegram y las credenciales de Firebase.
## API CIMA REST
    https://cima.aemps.es/cima/rest/
Es importante tener en cuenta que para utilizar esta API, debes consultar la documentación oficial de la AEMPS para obtener información detallada sobre los diferentes métodos disponibles y cómo utilizarlos correctamente. Puedes encontrar la documentación en el siguiente enlace:

1. **Documentación API CIMA REST**:
    https://sede.aemps.gob.es/docs/CIMA-REST-API_1_19.pdf
2. **Se proporcionan otros enlaces que pueden ser de utilidad**:
   
   -**Página principal de CIMA**: [https://cima.aemps.es/cima/publico/home.html](https://cima.aemps.es/cima/publico/home.html)
   
   -**Buscador avanzado de medicamentos CIMA**: [https://cima.aemps.es/cima/publico/buscadoravanzado.html](https://cima.aemps.es/cima/publico/buscadoravanzado.html)

