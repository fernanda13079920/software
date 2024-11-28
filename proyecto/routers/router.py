from flask import Blueprint, flash, redirect, render_template, request, session, url_for, send_file, Flask, jsonify, send_from_directory
import threading
from datetime import datetime

# importamos los controladores de Usuario
from ..controllers import UserController, VideoController, AudioController, PresencialController, SuscripcionController
from ..controllers import PlansController

# importamos los Modelos de usuario
from ..models.User import User, Plan
from ..models.User import Subscription
import os
import time
from werkzeug.utils import secure_filename
from proyecto.database.connection import _fetch_all,_fecth_lastrow_id,_fetch_none,_fetch_one  #las funciones 
from werkzeug.security import generate_password_hash

# Funciones de la funcionalidad audio
AudioController.transcribir_y_traducir, AudioController.mostrar_codigos_idiomas, AudioController.limpiar_archivos_temporales, AudioController.TEMP_DIR

# Funciones de la funcionalidad Video
VideoController.convertir_video_a_wav, VideoController.transcribir_y_traducir, VideoController.mostrar_codigos_idiomas, VideoController.limpiar_archivos_temporales, VideoController.TEMP_DIR

# Funciones de la funcionalidad Presencial
PresencialController.recognize_and_translate, PresencialController.get_available_languages, PresencialController.voice_queue

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Configurar la carpeta de archivos temporales
app.config['TEMP_DIR'] = 'archivostemporales'


################################################################
app.config['UPLOAD_TRADUCCION'] = os.path.join(os.getcwd(), 'temporales')
os.makedirs(app.config['UPLOAD_TRADUCCION'], exist_ok=True)

shared_data = {
    "capture_audio": False,
    "recognized_texts": [],
    "translation_texts": [],
    "error_message": None,
    "speak_translations": False,
    "audio_path": None,
    "audio_processed": []  # Lista para almacenar los audios procesados
}

IDIOMAS = VideoController.mostrar_codigos_idiomas()

home = Blueprint("views", __name__)
# ----------------------HOME------------------------------
# funciones decoradas, (para que puedan ser usadas en otro archivo)
@home.route('/', methods=['GET'])
def home_():
    """
    Cargar Usuario Admin
    """
    user = User(name="admin", email="admin@gmail.com",password = generate_password_hash("12345678"), id_rol = 1, state= "activo", create_at= datetime.now() )
    if User.query.filter_by(email=user.email).first():
        print("Usuario Admin ya esta registrado")
        flash('Usuario Admin ya esta registrado', 'danger')
        
    else:   
        sql = "INSERT INTO roles (id, rol) VALUES (%s, %s);"
        _fetch_none(sql, (1, 'Administrador'))
        _fetch_none(sql, (2, 'Usuario'))
        sql2 = "INSERT INTO plans (id, name, description, monthly_price) VALUES (%s, %s, %s, %s)"
        _fetch_none(sql2,(1,'Basico', 'Este plan es el mas basico', 70))
        _fetch_none(sql2,(2,'Intermedio', 'Este plan es el mas Intermedio', 120))
        _fetch_none(sql2,(3,'Profesional', 'Este plan es el mas Profesional', 150))
        UserController.create(user)

    return render_template("home.html")

#ruta de login
@home.route('/login', methods=['GET', 'POST'])
def login():
    # si el metodo es post, es decir, si se envio el formulario
    if request.method == 'POST':
        data = request.form  # guardo todos los datos ingresados por formulario de la vista
        print('------datos ingresados por formulario-------')
        usuario = User(0, data['email'], data['password'],0 , 0, 0)  # capturo los datos del formulario y mando al modelo User
        # los 0 son nulos porque no metemos desde formulario

        logged_user = UserController.login(usuario)
        print('datos del login')
        print(logged_user)
        # si el usuario existe
        if logged_user != None:
            if logged_user.password_hash:
                # guardamos los datos del usuario en la sesion
                session['Esta_logeado'] = True  # Variable para saber si el usuario esta logeado
                # obtenemos todo los datos del usuario
                session['usuario_id'] = logged_user.id
                session['name'] = logged_user.name
                session['email'] = logged_user.email
                session['password'] = logged_user.password_hash
                session['id_rol'] = logged_user.id_rol
                session['state'] = logged_user.state
                session['create_at'] = logged_user.create_at
                if(logged_user.id_rol == 1):
                    return redirect(url_for('views.dashboard_admin'))
                   # return render_template("dashboardAdmin.html")
                else:
                    id = UserController.id_user(usuario)[0]
                    return redirect(url_for('views.dashboard', id = id))  # redirige dashboard que corresponde//////chinin estuvo aquí
            else:
                flash("Usuario o Contraseña invalida")  # Contraseña invalida
                return render_template("login.html")
        else:
            flash("Usuario o Contraseña invalida")  # Usuario no encontrado
            return render_template("login.html")
    else:
        return render_template("login.html")

#ruta de registro de usuario
@home.route('/register', methods=['GET', 'POST'])
def register():
    time_creacion = datetime.now()  # guardamos la fecha y hora en la que se registrará
    # si el metodo es post, es decir, si se envio el formulario
    if request.method == "POST":
        data = request.form
        print('------datos ingresados por formulario-------')
        print(data)
        usuario = User(data['name'], data['email'], data['password'], data['id_rol'], data['state'], time_creacion)
        # capturo los datos del formulario y mando al modelo User
        # los 0 son nulos porque no metemos desde formulario
        UserController.create(usuario)
        flash('Usuario registrado con exito')
        return redirect(url_for('views.login'))

    return render_template('register.html')

#ruta de dasboard
@home.route('/dashboard/<int:id>')
def dashboard(id):
    if 'Esta_logeado' in session:
        user_subscription = Subscription.query.filter_by(user_id=id).first()

        if user_subscription:
            subscription_data = {
                "subscriptions": "Activa",
                "planname": user_subscription.plan.name,
                "monthly_price": f"${user_subscription.plan.monthly_price:.2f}",
                "start_date": user_subscription.start_date.strftime("%d-%m-%Y"),
                "end_date": user_subscription.end_date.strftime("%d-%m-%Y") if user_subscription.end_date else "Indefinido"
            }
        else:
            subscription_data = {
                "subscriptions": "Subscripción inexistente",
                "planname": "N/A",
                "monthly_price": "N/A",
                "start_date": "N/A",
                "end_date": "N/A"
            }

        parametros = {
            "title": "Bienvenido(a) " + session['name'],
            "name": session['name'],
            "email": session['email'],
            **subscription_data
        }
        return render_template("dashboard.html", id=id, **parametros)  # Pasar `id` al contexto
    return redirect(url_for('views.login'))

#ruta dashboard administrador
@home.route('/dashboard_admin')
def dashboard_admin():
    if 'Esta_logeado' in session:
        parametros = {"title": "Bienvenido(a) " + session['name'],
                      "name": session['name'],
                      "email": session['email']
                      }
        return render_template("dashboardAdmin.html", **parametros)
    return redirect(url_for('views.login'))

#ruta a logaut 
@home.route('/logout')
def logout():
    if 'Esta_logeado' in session:  # Si el usuario esta logeado entonces realiza funcionalidades permitidas
        session.pop('Esta_logeado', None)
        session.pop('name', None)
        return redirect(url_for('views.home_'))
    return redirect(url_for('views.login'))

#ruta principal de planes 
@home.route('/plans/<int:id>',methods=['GET', 'POST'])
def plans(id):
    if 'Esta_logeado' in session:  # Si el usuario esta logeado entonces realiza funcionalidades permitidas
        planes = PlansController.getAll()
        print(planes)  # Verificación de datos
        return render_template("plans.html", plans=planes, id =id)
    return redirect(url_for('views.login'))

#ruta de los administracion de planes
@home.route('/admin_plans/')
def admin_plans():
    if 'Esta_logeado' in session:  # Si el usuario está logeado entonces realiza funcionalidades permitidas
        planes = PlansController.getAll()
        print(planes)  # Verificación de datos
        return render_template("admin_plans.html", plans=planes)
    return redirect(url_for('views.login'))

#ruta de creacion de Planes
@home.route('/admin_plans/create', methods=['GET', 'POST'])
def create_plan():
    if 'Esta_logeado' in session:
        if request.method == 'POST':
            plan_data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'monthly_price': request.form['monthly_price']
            }
            PlansController.create(plan_data)
            return redirect(url_for('views.admin_plans'))
        return render_template("create_plan.html")
    return redirect(url_for('views.login'))

#ruta de actualizacion de los planes 
@home.route('/admin_plans/update/<int:id>', methods=['GET', 'POST'])
def update_plan(id):
    if 'Esta_logeado' in session:
        if request.method == 'POST':
            plan_data = {
                'id': id,
                'name': request.form['name'],
                'description': request.form['description'],
                'monthly_price': request.form['monthly_price']
            }
            PlansController.update(plan_data)
            return redirect(url_for('views.admin_plans'))
        plan = PlansController.getById(id)
        return render_template("update_plan.html", plan=plan)
    return redirect(url_for('views.login'))

#ruta para para eliminar planes 
@home.route('/admin_plans/delete/<int:id>', methods=['POST'])
def delete_plan(id):
    if 'Esta_logeado' in session:
        PlansController.delete(id)
        return redirect(url_for('views.admin_plans'))
    return redirect(url_for('views.login'))

#ruta de administracion de Usuarios
@home.route('/admin_users', methods=['GET', 'POST'])
def admin_users():
    if 'Esta_logeado' in session:
        users = UserController.getAll()
        return render_template('admin_users_index.html', users=users)
    return redirect(url_for('views.login'))

#ruta de adminstrador para actualizar los usuarios
@home.route('/admin_users/update/<int:id>', methods=['GET', 'POST'])
def update_user_state(id):
    if 'Esta_logeado' in session:
        if request.method == 'POST':
            user_data = {
                'id': id,
                'state': request.form['state']
            }
            print("Form submitted:", user_data)
            UserController.update_state(user_data)
            return redirect(url_for('views.admin_users'))
        user = UserController.getById(id)
        return render_template("admin_users.html", user=user)
    return redirect(url_for('views.login'))

#ruta paara ralizar los pagos de los planes 
@home.route('/card/<int:id>/<int:plan_id>', methods=['GET', 'POST'])
def card(id, plan_id):
    return render_template("card.html", id = id, plan_id = plan_id)


@home.route('/cardBusiness/')
def cardBusiness():
    return render_template("cardBusiness.html")


@home.route('/profile/')
def profile():
    if 'Esta_logeado' in session:
        # Aqui ponemos Titulo y descripcion
        parametros = {"title": "Bienvenido(a) " + session['name'],
                      "name": session['name'],
                      "email": session['email'],
                      "start_date": session['create_at']
                      }
        return render_template("profile.html", **parametros)
    return redirect(url_for('views.login'))


@home.route('/perfil/', methods=['POST', 'GET'])
def perfil():
    if 'Esta_logeado' in session:
        # Aqui ponemos Titulo y descripcion
        parametros = {"name": session['name'],
                      "email": session['email']
                      }
        return render_template("editar_perfil.html", **parametros)
    return redirect(url_for('views.login'))


@home.route('/update_profile/', methods=['GET', 'POST'])
def update_profile():
    if 'Esta_logeado' in session:
        if request.method == "POST":
            data = request.form
        return redirect(url_for('perfil'))
    return redirect(url_for('views.login'))


######## Funcionalidad Audio #################################
@home.route('/audio/<int:id>', methods=['POST', 'GET'])
def audio(id):
    return render_template("audio.html", id = id, idiomas=IDIOMAS)

@home.route('/upload-audio/<int:id>', methods=['POST'])
def upload_audio(id):
    AudioController.limpiar_archivos_temporales()  # Limpiar archivos temporales antes de procesar un nuevo audio

    if 'audioFile' not in request.files:
        return redirect(request.url)
    
    file = request.files['audioFile']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        idioma_entrada = request.form.get('idioma_entrada', '')
        idioma_salida = request.form.get('idioma_salida', 'es')
        reproducir_audio = request.form.get('reproducir_audio', 'n') == 's'

        resultado = AudioController.transcribir_y_traducir(filepath, idioma_entrada, idioma_salida, reproducir_audio)

        audio_traduccion = resultado.get('audio_traduccion', '')
        print('Valor de audio_traduccion:', audio_traduccion)

        return render_template(
            'audio.html',
            id=id,
            idiomas=IDIOMAS,
            transcripcion=resultado.get('texto', ''),  # Texto transcrito
            traduccion=resultado.get('texto_traducido', ''),  # Texto traducido
            audio_traduccion=audio_traduccion,  # Archivo de audio traducido
            resumen=resultado.get('resumen', '')  # Resumen generado
        )
    return redirect(request.url)



@home.route('/descargar-audio/<filename>')
def descargar_audioFile(filename):
    file_path = None
    # Buscar el archivo en el directorio temporal
    for root, dirs, files in os.walk(app.config['TEMP_DIR']):
        if filename in files:
            file_path = os.path.join(root, filename)
            break
    if file_path:
        return send_file(file_path, as_attachment=True)
    return "Archivo no encontrado", 404


######### Funcionalidad Video ##################################

@home.route('/video/<int:id>', methods=['POST', 'GET'])
def index(id):
    return render_template('video.html', id = id, idiomas=IDIOMAS)


@home.route('/upload-video/<int:id>', methods=['POST'])
def upload_video(id):
    VideoController.limpiar_archivos_temporales()  # Limpiar archivos temporales antes de procesar un nuevo video

    if 'videoFile' not in request.files:
        return redirect(request.url)

    file = request.files['videoFile']
    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        output_wav_path = os.path.join(VideoController.TEMP_DIR, "temporal.wav")
        VideoController.convertir_video_a_wav(filepath, output_wav_path)

        if os.path.exists(output_wav_path):
            idioma_entrada = request.form.get('idioma_entrada', '')
            idioma_salida = request.form.get('idioma_salida', 'es')
            reproducir_audio = request.form.get('reproducir_audio', 'n') =='s'

            resultado = VideoController.transcribir_y_traducir(output_wav_path, idioma_entrada, idioma_salida, reproducir_audio)
            
            audio_traduccion = resultado.get('audio_traduccion', '')
            print('Valor de audio_traduccion:', audio_traduccion)

            return render_template('video.html',id = id, idiomas=IDIOMAS, transcripcion=resultado.get('texto', ''), traduccion=resultado.get('texto_traducido', ''), audio_traduccion=audio_traduccion)
            
    return redirect(request.url)


@home.route('/descargar_audio<filename>')
def descargar_audio(filename):
    file_path = None
    # Buscar el archivo en el directorio temporal
    for root, dirs, files in os.walk(app.config['TEMP_DIR']):
        if filename in files:
            file_path = os.path.join(root, filename)
            break
    if file_path:
        return send_file(file_path, as_attachment=True)
    return "Archivo no encontrado", 404

@home.route('/suscripcion_create/<int:id>', methods=['POST', 'GET'])
def suscripcion_create(id):
    if 'Esta_logeado' in session:
        if request.method == 'POST':
            subs = {
                'id_user': request.form['id'],
                'id_plan': request.form['id_plan'],
                'start_date': datetime.now(),
                'state': request.form['state']
            }
            SuscripcionController.create(subs)
            data = SuscripcionController.getById(id)
            print(data)
            return render_template('suscripcion.html', id = id, data = data)
        return render_template("plans.html", id = id)
    return redirect(url_for('views.login'))


@home.route('/suscripcion/<int:id>', methods=['POST', 'GET'])
def suscripcion(id):
    if 'Esta_logeado' in session:
        data = SuscripcionController.getById(id)
        return render_template('suscripcion.html', id = id, data = data)
    return redirect(url_for('views.login'))


######## Funcionalidad Presencial #########################

@home.route('/presencial/<int:id>')
def presencial(id):
    languages = PresencialController.get_available_languages()
    return render_template('presencial.html', id = id, languages=languages)

@home.route('/start_capture', methods=['POST'])
def start_capture():
    global shared_data
    source_lang = request.json['sourceLang']
    target_lang = request.json['targetLang']
    speak_translations = request.json.get('speakTranslations', False)
    shared_data["capture_audio"] = True
    shared_data["speak_translations"] = speak_translations

    capture_audio_thread, error_message = PresencialController.recognize_and_translate(source_lang, target_lang, shared_data)
    shared_data["error_message"] = error_message

    def run_in_background():
        audio_thread = threading.Thread(target=capture_audio_thread, args=(shared_data,))
        audio_thread.start()
        audio_thread.join()

    threading.Thread(target=run_in_background).start()

    return jsonify({"status": "Capture started"})

@home.route('/get_translations')
def get_translations():
    global shared_data
    recognized_texts = shared_data['recognized_texts']
    translation_texts = shared_data['translation_texts']
    error_message = shared_data['error_message']
    audio_path = shared_data['audio_path']
    
    return jsonify({
        "recognized_texts": recognized_texts,
        "translation_texts": translation_texts,
        "error_message": error_message,
        "audio_path": audio_path
    })

@home.route('/temporales/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_TRADUCCION'], filename)

@home.route('/stop_capture', methods=['POST'])
def stop_capture():
    global shared_data
    shared_data["capture_audio"] = False
    PresencialController.voice_queue.put(None)  # Detener el trabajador de voz

    # Esperar a que se procesen las transcripciones y traducciones pendientes
    while shared_data.get("capture_processing", False):
        time.sleep(0.1)  # Esperar un pequeño intervalo para completar el procesamiento

    # Obtener el idioma de salida desde la solicitud
    target_lang = request.json.get("targetLang", "en")

    # Generar el resumen
    recognized_texts = " ".join(shared_data["recognized_texts"])  # Combinar todos los textos reconocidos
    if recognized_texts.strip():  # Verificar que haya texto reconocido
        summary = PresencialController.summarize_text(recognized_texts, target_lang=target_lang)  # Resumir y traducir
    else:
        summary = "No hay suficientes datos para generar un resumen."  # Manejo en caso de texto vacío

    # Almacenar el resumen en `shared_data`
    shared_data["summary"] = summary

    # Enviar los datos acumulados hasta el momento
    return jsonify({
        "status": "Audio capture stopped.",
        "recognized_texts": shared_data["recognized_texts"],
        "translation_texts": shared_data["translation_texts"],
        "summary": summary
    })
