import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from langdetect import detect, DetectorFactory
from pydub import AudioSegment
import os
from pathlib import Path
import uuid

# Fijar el seed para la detección de idioma para obtener resultados reproducibles
DetectorFactory.seed = 0

# Directorio temporal para archivos generados
TEMP_DIR = 'proyecto/views/static/archivostemporales/'
os.makedirs(TEMP_DIR, exist_ok=True)  # Crear el directorio si no existe

def mostrar_codigos_idiomas():
    return LANGUAGES

def preparar_audio(audio_path):
    """
    Verifica y convierte un archivo de audio al formato WAV (PCM) requerido por Google Speech Recognition.

    Args:
        audio_path (str): Ruta del archivo de audio original.

    Returns:
        str: Ruta del archivo convertido a WAV.
    """
    try:
        # Convertir el archivo al formato WAV si no es WAV
        if not audio_path.lower().endswith(".wav"):
            print(f"Convirtiendo {audio_path} al formato WAV...")
            audio_path = convertir_audio(audio_path, formato_destino="wav")
            print(f"Archivo convertido a WAV: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Error al preparar el audio: {e}")
        return None

def convertir_audio(audio_path, formato_destino='mp3'):
    """
    Convierte un archivo de audio al formato deseado.

    Args:
        audio_path (str): Ruta del archivo de audio original.
        formato_destino (str): Formato de destino (ej. 'mp3', 'wav', 'ogg').

    Returns:
        str: Ruta del archivo convertido.
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"El archivo {audio_path} no existe.")

        # Cargar el audio
        audio = AudioSegment.from_file(audio_path)

        # Definir la nueva ruta con el formato deseado
        archivo_convertido = os.path.splitext(audio_path)[0] + f".{formato_destino}"

        # Exportar el audio al nuevo formato
        audio.export(archivo_convertido, format=formato_destino)
        print(f"Archivo convertido a {archivo_convertido}")

        return archivo_convertido

    except Exception as e:
        print(f"Error al convertir el archivo de audio: {e}")
        return None

def transcribir_y_traducir(audio_path, idioma_entrada=None, idioma_salida='es', reproducir_audio=False):
    r = sr.Recognizer()
    translator = Translator()
    resultado = {}

    try:
        # Convertir el archivo al formato WAV si es necesario
        audio_path = preparar_audio(audio_path)
        if not audio_path:
            raise ValueError("No se pudo preparar el archivo de audio.")

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
    """
    Limpia los archivos temporales generados durante el proceso.
    """
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
