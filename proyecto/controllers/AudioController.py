import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from langdetect import detect, DetectorFactory
import os
from pathlib import Path
import uuid

# Controlador de la funcionalidad audio.
# Fijar el seed para la detección de idioma para obtener resultados reproducibles
DetectorFactory.seed = 0

TEMP_DIR = 'proyecto/views/static/archivostemporales/'
os.makedirs(TEMP_DIR, exist_ok=True)  # Crear el directorio si no existe

def mostrar_codigos_idiomas():
    return LANGUAGES

def transcribir_y_traducir(audio_path, idioma_entrada=None, idioma_salida='es', reproducir_audio=False):
    r = sr.Recognizer()
    translator = Translator()
    resultado = {}

    try:
        with sr.AudioFile(audio_path) as recurso:
            print("Leyendo archivo de audio...")
            audio = r.record(recurso)
            if idioma_entrada:
                texto = r.recognize_google(audio, language=idioma_entrada)
                print(f"Texto en {idioma_entrada}: {texto}")
            else:
                texto = r.recognize_google(audio)
                print(f"Texto transcrito: {texto}")

                # Detección del idioma si no se proporciona
                idioma_entrada = detect(texto)
                print(f"Idioma detectado: {idioma_entrada}")

            # Verificar que los idiomas sean válidos
            if idioma_entrada not in LANGUAGES:
                raise ValueError(f"Idioma de entrada no válido: {idioma_entrada}")
            if idioma_salida not in LANGUAGES:
                raise ValueError(f"Idioma de salida no válido: {idioma_salida}")

            # Traducción
            texto_traducido = translator.translate(texto, src=idioma_entrada, dest=idioma_salida).text
            print(f"Texto traducido a {idioma_salida}: {texto_traducido}")

            resultado['texto'] = texto
            resultado['texto_traducido'] = texto_traducido

            # Crear archivo de audio a partir del texto traducido
            tts = gTTS(text=texto_traducido, lang=idioma_salida)
            """ audio_traduccion_filename = os.path.join(TEMP_DIR, f"traduccion_{uuid.uuid4().hex}.mp3") """
            audio_traduccion_filename = os.path.join(TEMP_DIR, f"audio_traduccion.mp3")
            tts.save(audio_traduccion_filename)
            print(f"Archivo {audio_traduccion_filename} creado")
            resultado['audio_traduccion'] = audio_traduccion_filename

    except sr.UnknownValueError:
        print("Error: No se pudo entender el audio")
    except sr.RequestError as e:
        print(f"Error: Problema en la solicitud a Google Speech Recognition: {e}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return resultado

def limpiar_archivos_temporales():
    try:
        Path(os.path.join(TEMP_DIR, "temporal.wav")).unlink()
        print("Archivo temporal.wav eliminado.")
    except FileNotFoundError:
        print("Archivo temporal.wav no encontrado.")

    for temp_file in Path(TEMP_DIR).glob('traduccion_*.mp3'):
        try:
            temp_file.unlink()
            print(f"Archivo {temp_file} eliminado.")
        except FileNotFoundError:
            print(f"Archivo {temp_file} no encontrado.")
