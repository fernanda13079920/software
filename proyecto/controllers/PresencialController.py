import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import threading
import queue
import os
import sumy

recognizer = sr.Recognizer()  # Inicializa el reconocedor de voz
translator = Translator()  # Inicializa el traductor
voice_queue = queue.Queue()  # Cola para manejar las traducciones a voz

# Función para obtener los idiomas disponibles
def get_available_languages():
    return LANGUAGES

# Función que se ejecuta en un hilo separado para procesar la cola de voz
def voice_worker():
    while True:
        text = voice_queue.get()
        if text is None:
            break
        tts = gTTS(text, lang='en')  # Ajusta el idioma según tus necesidades
        audio_path = os.path.join('temporales', 'translation_current.mp3')
        tts.save(audio_path)
        # os.system(f"mpg123 {audio_path}")  # Comentado si no es necesario
        voice_queue.task_done()

# Inicializa y arranca el hilo del trabajador de voz
voice_thread = threading.Thread(target=voice_worker)
voice_thread.daemon = True
voice_thread.start()

# Función para reconocer y traducir el audio
def recognize_and_translate(source_lang, target_lang, shared_data):
    error_message = None

    # Función interna para capturar audio en un hilo separado
    def capture_audio_thread(shared_data):
        nonlocal error_message

        with sr.Microphone() as source:
            print("Speak now...")
            while shared_data["capture_audio"]:
                try:
                    # Captura el audio del micrófono
                    audio = recognizer.listen(source, timeout=5)

                    if audio is not None:
                        # Reconoce el texto en el audio
                        text = recognizer.recognize_google(audio, language=source_lang)
                        shared_data['recognized_texts'].append(text)

                        # Traduce el texto reconocido
                        translation = translator.translate(text, dest=target_lang).text
                        shared_data['translation_texts'].append(translation)
                        print("You said: {}".format(text))
                        print("Translation: {}".format(translation))

                        # Verificar y crear la carpeta 'temporales' si no existe
                        if not os.path.exists('temporales'):
                            os.makedirs('temporales')

                        # Guardar la traducción como archivo de audio
                        audio_filename = f'translation_{len(shared_data["translation_texts"])}.mp3'
                        audio_path = os.path.join('temporales', audio_filename)
                        translation_audio = gTTS(translation, lang=target_lang)  # Crear el archivo de audio aquí
                        translation_audio.save(audio_path)

                        # Verificar si el archivo de audio se ha guardado correctamente
                        if not os.path.exists(audio_path):
                            print("El archivo de audio no se ha guardado correctamente.")
                        else:
                            print("El archivo de audio se ha guardado correctamente en", audio_path)
                            shared_data['audio_path'] = audio_filename
                            shared_data['audio_processed'].append(audio_path)  # Añadir a los procesados

                        # Enqueue the translation for speaking
                        if shared_data.get("speak_translations", False):
                            voice_queue.put(translation)

                except sr.UnknownValueError:
                    print("Sorry! Could not understand audio.")
                except sr.RequestError as e:
                    print("Error with the request; {0}".format(e))
                except Exception as e:
                    print("Error: {0}".format(e))

    return capture_audio_thread, error_message
def summarize_text(text, sentence_count=3, target_lang="en"):
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer

    # Resumir el texto
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    summary_text = " ".join(str(sentence) for sentence in summary)

    # Traducir el resumen al idioma de salida
    translator = Translator()
    translated_summary = translator.translate(summary_text, dest=target_lang).text

    return translated_summary
