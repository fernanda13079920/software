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

def dividir_audio(audio_path, duracion_fragmento=60 * 1000):
    """
    Divide un archivo de audio en fragmentos más pequeños.

    Args:
        audio_path (str): Ruta del archivo de audio original.
        duracion_fragmento (int): Duración máxima de cada fragmento en milisegundos.

    Returns:
        list: Lista de rutas a los fragmentos de audio generados.
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        duracion_total = len(audio)
        fragmentos = []

        for i in range(0, duracion_total, duracion_fragmento):
            inicio = i
            fin = min(i + duracion_fragmento, duracion_total)
            fragmento = audio[inicio:fin]

            # Guardar el fragmento en un archivo temporal
            fragmento_path = os.path.join(TEMP_DIR, f"fragmento_{i // duracion_fragmento}.wav")
            fragmento.export(fragmento_path, format="wav")
            fragmentos.append(fragmento_path)

        print(f"Audio dividido en {len(fragmentos)} fragmentos.")
        return fragmentos

    except Exception as e:
        print(f"Error al dividir el audio: {e}")
        return []

def transcribir_y_traducir(audio_path, idioma_entrada=None, idioma_salida='es', reproducir_audio=False):
    r = sr.Recognizer()
    translator = Translator()
    resultado = {
        "texto": "",
        "texto_traducido": "",
        "audio_traduccion": None,
        "resumen": ""  # Campo para el resumen
    }

    try:
        # Preparar y dividir audio si es necesario
        audio_path = preparar_audio(audio_path)
        if not audio_path:
            raise ValueError("No se pudo preparar el archivo de audio.")

        fragmentos = dividir_audio(audio_path) if len(AudioSegment.from_file(audio_path)) > 60 * 1000 else [audio_path]

        texto_completo = ""
        for fragmento_path in fragmentos:
            with sr.AudioFile(fragmento_path) as recurso:
                print(f"Procesando fragmento {fragmento_path}...")
                try:
                    audio = r.record(recurso)
                    texto_fragmento = r.recognize_google(audio, language=idioma_entrada) if idioma_entrada else r.recognize_google(audio)
                    texto_completo += texto_fragmento + " "
                    print(f"Texto transcrito del fragmento: {texto_fragmento}")
                except sr.UnknownValueError:
                    print(f"Advertencia: No se pudo transcribir el fragmento {fragmento_path}.")
                    continue

        if not texto_completo.strip():
            raise ValueError("No se pudo transcribir ningún texto del audio.")

        # Limpiar texto transcrito antes de cualquier procesamiento
        texto_completo = texto_completo.replace('\n', ' ').strip()

        print(f"Texto completo transcrito:\n{texto_completo[:500]}... (mostrando los primeros 500 caracteres)")

        # Detectar idioma si no se proporciona
        if not idioma_entrada:
            idioma_entrada = detect(texto_completo)
            print(f"Idioma detectado: {idioma_entrada}")

        # Traducción del texto completo
        texto_traducido = ""
        if texto_completo.strip():
            try:
                max_characters = 5000
                bloques = [texto_completo[i:i + max_characters] for i in range(0, len(texto_completo), max_characters)]

                for bloque in bloques:
                    traduccion = translator.translate(bloque, src=idioma_entrada, dest=idioma_salida).text
                    texto_traducido += traduccion + " "
                print(f"Texto traducido:\n{texto_traducido}")
                resultado['texto_traducido'] = texto_traducido.strip()
            except Exception as e:
                print(f"Error durante la traducción: {e}")
                resultado['texto_traducido'] = "Error al traducir el texto."

        # Crear archivo de audio para la traducción
        if texto_traducido.strip():
            try:
                if idioma_salida not in gTTS.LANGUAGES:
                    raise ValueError(f"El idioma de salida '{idioma_salida}' no es compatible con gTTS.")
                
                tts = gTTS(text=texto_traducido, lang=idioma_salida)
                audio_traduccion_filename = os.path.join(TEMP_DIR, f"audio_traduccion_{uuid.uuid4().hex}.mp3")
                tts.save(audio_traduccion_filename)
                resultado['audio_traduccion'] = audio_traduccion_filename
                print(f"Archivo de audio creado: {audio_traduccion_filename}")
            except ValueError as ve:
                print(f"Error de idioma en gTTS: {ve}")
                resultado['audio_traduccion'] = None
            except Exception as e:
                print(f"Error al generar el audio: {e}")
                resultado['audio_traduccion'] = None
        else:
            print("No hay texto traducido para generar audio.")

        # Crear el resumen del texto completo traducido
        if texto_completo.strip():
            try:
                print("Generando resumen del texto completo...")

                # Dividir el texto completo en bloques manejables
                max_characters = 3000  # Límite de caracteres por bloque
                bloques = [texto_completo[i:i + max_characters] for i in range(0, len(texto_completo), max_characters)]

                # Crear un resumen para cada bloque y combinarlos
                resumenes = []
                for idx, bloque in enumerate(bloques):
                    print(f"Procesando bloque {idx + 1}/{len(bloques)}...")
                    resumen_bloque = summarize_text(
                        text=bloque,         # Texto del bloque
                        sentence_count=5,    # Número de frases por resumen
                        target_lang=idioma_salida  # Idioma del resumen
                    )
                    resumenes.append(resumen_bloque)

                # Combinar los resúmenes de todos los bloques
                resultado['resumen'] = " ".join(resumenes)
                print(f"Resumen generado: {resultado['resumen']}")

            except Exception as e:
                print(f"Error al generar el resumen: {e}")
                resultado['resumen'] = f"Error al generar el resumen: {e}"

        resultado['texto'] = texto_completo


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
        for temp_file in Path(TEMP_DIR).glob('*'):
            try:
                temp_file.unlink()
                print(f"Archivo {temp_file} eliminado.")
            except FileNotFoundError:
                print(f"Archivo {temp_file} no encontrado.")
    except Exception as e:
        print(f"Error al limpiar archivos temporales: {e}")

def summarize_text(text, sentence_count=3, target_lang="en", max_characters=5000):
    """
    Resumen de texto con división en bloques si es necesario.

    Args:
        text (str): El texto a resumir.
        sentence_count (int): Número de frases en cada resumen.
        target_lang (str): Idioma del resumen final (por defecto, inglés).
        max_characters (int): Número máximo de caracteres por bloque.

    Returns:
        str: Resumen traducido al idioma objetivo.
    """
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from googletrans import Translator

        translator = Translator()

        # Detectar el idioma del texto original
        detected_lang = translator.detect(text).lang

        # Traducir al inglés si el texto no está en inglés
        if detected_lang != "en":
            print(f"Traduciendo texto de {detected_lang} a inglés para resumen...")
            text = translator.translate(text, src=detected_lang, dest="en").text

        # Dividir el texto en bloques si supera el límite de caracteres
        bloques = [text[i:i + max_characters] for i in range(0, len(text), max_characters)]

        # Generar resúmenes para cada bloque
        resumenes = []
        for i, bloque in enumerate(bloques):
            print(f"Procesando bloque {i+1}/{len(bloques)}...")
            parser = PlaintextParser.from_string(bloque, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, sentence_count)
            resumen_bloque = " ".join(str(sentence) for sentence in summary)
            resumenes.append(resumen_bloque)

        # Combinar los resúmenes en un único texto
        resumen_final = " ".join(resumenes)

        # Traducir el resumen al idioma objetivo si no es inglés
        if target_lang != "en":
            print(f"Traduciendo resumen combinado al idioma objetivo: {target_lang}...")
            resumen_final = translator.translate(resumen_final, src="en", dest=target_lang).text

        return resumen_final

    except Exception as e:
        print(f"Error al procesar el resumen: {e}")
        return "Error al procesar el resumen."

