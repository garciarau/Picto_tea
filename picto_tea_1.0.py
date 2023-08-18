import tkinter as tk
import PySimpleGUI as sg
from pathlib import Path
from PIL import Image
import logging
import re
import stanza
import inflect
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configurar el registro de mensajes de registro
logging.basicConfig(level=logging.INFO)

# Crear el modelo de procesamiento de lenguaje natural de Stanza en español una vez
stanza_model = stanza.Pipeline('es')

# Clase principal para generar pictogramas


class PictogramaGenerator:
    def __init__(self, nlp_model):
        # Guardar el modelo de procesamiento de lenguaje natural
        self.nlp = nlp_model
        # Instanciar el motor inflect para tratar con números y formas plurales
        self.p = inflect.engine()
        # Directorio donde se encuentran las imágenes de los pictogramas
        self.directorio_pictogramas = "Picto_tea_1.0/Images"
        # Diccionario de verbos irregulares y sus formas conjugadas
        self.verbos_irregulares = {
            "estoy": "estar",
            "estás": "estar",
            "está": "estar",
            "estamos": "estar",
            "estáis": "estar",
            "están": "estar",
            "soy": "ser",
            "eres": "ser",
            "es": "ser",
            "somos": "ser",
            "sois": "ser",
            "son": "ser",
            "salta": "saltar",
            "salto": "saltar",
            "después": "después",
            # Agrega más verbos y sus conjugaciones irregulares aquí
        }
       # Diccionario de palabras numéricas y sus representaciones en palabras
        self.word_to_number = {
            "cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
            "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
            "trece": 13, "catorce": 14, "quince": 15, "dieciséis": 16, "diecisiete": 17,
            "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidós": 22,
            "veintitrés": 23, "veinticuatro": 24, "veinticinco": 25, "veintiséis": 26, "veintisiete": 27,
            "veintiocho": 28, "veintinueve": 29, "treinta": 30, "treinta y uno": 31, "treinta y dos": 32,
            "treinta y tres": 33, "treinta y cuatro": 34, "treinta y cinco": 35, "treinta y seis": 36,
            "treinta y siete": 37, "treinta y ocho": 38, "treinta y nueve": 39, "cuarenta": 40,
            "cuarenta y uno": 41, "cuarenta y dos": 42, "cuarenta y tres": 43, "cuarenta y cuatro": 44,
            "cuarenta y cinco": 45, "cuarenta y seis": 46, "cuarenta y siete": 47, "cuarenta y ocho": 48,
            "cuarenta y nueve": 49, "cincuenta": 50
            # Agrega más números y sus representaciones en palabras aquí
        }
    # Método para obtener palabras importantes y lemas de un texto

    def obtener_palabras_importantes_con_lemas(self, texto):
        lemas_verbos = set()
        palabras_importantes = []
        numero_actual = None
        plurales = ["palomitas", "después"]

        doc = self.nlp(texto)
        for sent in doc.sentences:
            for word in sent.words:
                lema = word.lemma.lower()

                if lema == "despué":
                    lema = "después"

                if word.upos in ['VERB', 'AUX'] and lema not in lemas_verbos:
                    lemas_verbos.add(lema)
                    lema_infinitivo = self.obtener_infinitivo_verbo(word.text)
                    if lema_infinitivo:
                        palabras_importantes.append(lema_infinitivo)
                    else:
                        palabras_importantes.append(lema)
                elif word.upos in ['NOUN', 'ADJ', 'ADV', 'NUM']:
                    if lema in self.word_to_number:
                        numero_actual = self.word_to_number[lema]
                    elif re.match(r'^\d+$', word.text):
                        numero_actual = int(word.text)
                    else:
                        if numero_actual is not None:
                            palabras_importantes.append(str(numero_actual))
                            numero_actual = None
                        singular_form = self.p.singular_noun(word.text)
                        if singular_form:
                            lema = singular_form.lower()
                            for singular_form in plurales:
                                if singular_form in plurales:
                                    lema = singular_form
                                    break
                        palabras_importantes.append(lema)
                        if word.text.lower() == "y":
                            numero_actual = None

        if numero_actual is not None:
            palabras_importantes.append(str(numero_actual))

        return palabras_importantes

    # Método para obtener el infinitivo de un verbo, tratando verbos irregulares
    def obtener_infinitivo_verbo(self, verbo):
        if verbo in self.verbos_irregulares:
            return self.verbos_irregulares[verbo]
        try:
            doc = self.nlp(verbo)
            lema_infinitivo = doc.sentences[0].words[0].lemma
            if lema_infinitivo != verbo:
                return lema_infinitivo.lower()
        except:
            pass
        return None

    # Método para obtener la ruta de una imagen de pictograma según una palabra clave
    def obtener_pictograma(self, palabra_clave):
        imagen_path = Path(self.directorio_pictogramas) / \
            f"{palabra_clave}.png"
        if imagen_path.exists():
            logging.info(
                f"Imagen encontrada para la palabra clave '{palabra_clave}': {imagen_path}")
            return imagen_path
        logging.warning(
            f"No se encontró ninguna imagen para la palabra clave '{palabra_clave}'.")
        return None

# Clase para mostrar las imágenes de los pictogramas en una ventana


class ImageWindow:
    def __init__(self):
        self.root = None
        self.fig, self.ax = None, None
        self.canvas = None

    def crear_ventana_imagen(self):
        if self.root is None:
            self.root = tk.Toplevel()
            self.root.title("Pictogramas")
            self.root.geometry("800x600")

    def agregar_imagenes(self, img_data_list):
        self.crear_ventana_imagen()
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        num_images = len(img_data_list)
        self.fig = plt.figure(figsize=(4 * num_images, 4))
        self.ax = [self.fig.add_subplot(1, num_images, i+1)
                   for i in range(num_images)]

        self.canvas = FigureCanvasTkAgg(
            self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        for i, img_data in enumerate(img_data_list):
            ax = self.ax[i]
            ax.imshow(img_data)
            ax.axis('off')

        self.fig.tight_layout()
        self.canvas.draw()

    def mostrar_ventana_imagen(self):
        if self.root is not None:
            self.root.mainloop()

    def limpiar_ventana_imagen(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
        if self.root is not None:
            self.root.destroy()
            self.root = None

# Función principal que controla la interfaz gráfica


def main(pictograma_generator, window):
    while True:
        event, values = window.read()
        if event == "Salir" or event == sg.WINDOW_CLOSED:
            if pictograma_generator.image_window is not None:
                pictograma_generator.image_window.limpiar_ventana_imagen()
            break
        elif event == "Limpiar":
            window["-FRASE-"].update("")
            window["-PALABRAS_IMPORTANTES_LEMAS-"].update("")
            if pictograma_generator.image_window is not None:
                pictograma_generator.image_window.limpiar_ventana_imagen()
        elif event == "Mostrar pictogramas":
            frase = values["-FRASE-"]
            lemas_importantes = pictograma_generator.obtener_palabras_importantes_con_lemas(
                frase)
            lemas_texto = " ".join(lemas_importantes)
            window["-PALABRAS_IMPORTANTES_LEMAS-"].update(lemas_texto)

            nivel = values["-NIVEL-"]
            pictogramas = []
            for lema in lemas_importantes:
                if nivel == "Nivel 0":
                    pictogram = pictograma_generator.obtener_pictograma(
                        lema + "_BN")
                    if not pictogram:
                        pictogram = pictograma_generator.obtener_pictograma(
                            lema)
                else:  # Nivel 1
                    pictogram = pictograma_generator.obtener_pictograma(
                        lema)

                if pictogram:
                    try:
                        img_data = Image.open(pictogram)
                        pictogramas.append(img_data)
                    except Exception as e:
                        logging.error("Error al procesar la imagen:", e)

            if pictograma_generator.image_window is None:
                pictograma_generator.image_window = ImageWindow()
            pictograma_generator.image_window.agregar_imagenes(pictogramas)
            pictograma_generator.image_window.mostrar_ventana_imagen()
    window.close()


# Definición del diseño de la interfaz gráfica
LAYOUT = [
    [sg.Text("Ingresa una frase: "), sg.InputText(key="-FRASE-")],
    [sg.Button("Mostrar pictogramas"), sg.Button(
        "Limpiar"), sg.Button("Salir")],
    [sg.Text("Palabras relevantes y sus lemas: ")],
    [sg.Multiline(
        size=(50, 10), key="-PALABRAS_IMPORTANTES_LEMAS-", disabled=True)],
    [sg.Text("Selecciona el nivel: "), sg.Combo(
        ["Nivel 0", "Nivel 1"], key="-NIVEL-", default_value="Nivel 0")]
]

# Función para mostrar la interfaz gráfica


def mostrar_interfaz(pictograma_generator):
    window = sg.Window("Convertir frases a pictogramas", LAYOUT)
    main(pictograma_generator, window)
    window.close()


if __name__ == '__main__':
    # Crear una instancia del generador de pictogramas
    # # Crear una instancia del generador de pictogramas y pasar el modelo de Stanza
    pictograma_generator = PictogramaGenerator(stanza_model)
    # Crear una instancia de la ventana de imágenes
    image_window = ImageWindow()
    # Asignar la instancia de ImageWindow a la instancia de PictogramaGenerator
    pictograma_generator.image_window = image_window
    # Mostrar la interfaz gráfica
    mostrar_interfaz(pictograma_generator)
