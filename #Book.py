import requests
import webbrowser
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.core.window import Window

# Inserisci qui la tua chiave API di Google Books (facoltativo)
API_KEY = "AIzaSyCukJmIi3vEIM3qV-TZl5l7W9ehzR3xfIQ"  # Facoltativo

# Memorizzazione delle case editrici e libri
publishers = {}
books = {}

class MyBookApp(App):
    def build(self):
        # Imposta il colore dello sfondo
        Window.clearcolor = (0.1, 0.2, 0.3, 1)  # Blu scuro per uno sfondo elegante

        # Layout principale
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Avvia con la prima parte (ricerca libri)
        self.show_first_part()

        return self.main_layout

    # Funzione per mostrare la prima parte (ricerca libri)
    def show_first_part(self, *args):
        # Pulisci il layout
        self.main_layout.clear_widgets()

        # Layout superiore con il logo e il titolo
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=20)
        title_label = Label(text="Book Finder App", font_size='36sp', bold=True, color=(1, 1, 1, 1))
        top_layout.add_widget(title_label)

        self.main_layout.add_widget(top_layout)

        # Layout di ricerca
        search_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        # Campo di input per la ricerca
        self.search_input = TextInput(hint_text="Inserisci il titolo del libro", size_hint=(0.8, None), height=40, multiline=False)
        self.search_input.bind(on_text_validate=self.on_enter)  # Aggiunta di ricerca con il tasto Invio
        search_layout.add_widget(self.search_input)

        # Pulsante di ricerca
        search_button = Button(text="Cerca", size_hint=(0.2, None), height=40, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        search_button.bind(on_press=self.perform_search)
        search_layout.add_widget(search_button)

        self.main_layout.add_widget(search_layout)

        # ScrollView per mostrare i risultati
        self.results_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_view.add_widget(self.results_layout)
        self.main_layout.add_widget(scroll_view)

        # Pulsante per passare alla seconda parte
        manage_publishers_button = Button(text="Vai alla Gestione Case Editrici e Libri", size_hint=(1, 0.1), height=40, background_color=(0.5, 0.3, 0.8, 1), color=(1, 1, 1, 1))
        manage_publishers_button.bind(on_press=self.show_second_part)
        self.main_layout.add_widget(manage_publishers_button)

    # Funzione per fare la ricerca quando si preme invio
    def on_enter(self, instance):
        self.perform_search(instance)

    # Funzione per cercare i libri tramite Google Books API
    def perform_search(self, instance):
        query = self.search_input.text.strip().lower()
        if query:
            # Pulisci i risultati precedenti
            self.results_layout.clear_widgets()

            # Cerca i libri tramite Google Books API
            self.search_google_books(query)
        else:
            self.results_layout.clear_widgets()
            self.results_layout.add_widget(Label(text="Per favore, inserisci un titolo valido."))

    # Funzione per cercare i dettagli tramite Google Books API e mostrare i primi 5 risultati
    def search_google_books(self, book_title):
        api_url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": book_title, "maxResults": 5}  # Mostra solo 5 risultati
        if API_KEY:
            params["key"] = API_KEY  # Usa l'API Key se disponibile

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Se ci sono risultati
            if data["totalItems"] > 0:
                for item in data["items"]:
                    book_info = item["volumeInfo"]

                    # Ottieni il titolo e la descrizione (se disponibili)
                    title = book_info.get("title", "Titolo non disponibile")
                    description = book_info.get("description", "Descrizione non disponibile")
                    authors = ", ".join(book_info.get("authors", ["Autori non disponibili"]))
                    
                    # Ottieni il link al libro (es. Google Books link)
                    book_url = book_info.get("infoLink", "")

                    # Ottieni l'immagine della copertina (se disponibile)
                    image_links = book_info.get("imageLinks", {})
                    thumbnail_url = image_links.get("thumbnail", None)

                    # Layout per ogni risultato (immagine a sinistra, testo a destra)
                    result_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=150, spacing=10)

                    # Controllo se thumbnail_url è valido prima di creare AsyncImage
                    if thumbnail_url:
                        cover_image = AsyncImage(source=thumbnail_url, size_hint=(0.3, 1))
                        cover_image.bind(on_touch_down=lambda instance, touch, url=book_url: self.open_url(touch, instance, url))
                        result_layout.add_widget(cover_image)
                    else:
                        # In caso di URL dell'immagine non disponibile, aggiungi un messaggio o un'immagine predefinita
                        no_image_label = Label(text="Immagine non disponibile", size_hint=(0.3, 1), color=(1, 1, 1, 1))
                        result_layout.add_widget(no_image_label)

                    # Mostra il testo con il titolo, gli autori e la descrizione (cliccabile)
                    result_text = f"Titolo: {title}\nAutori: {authors}\nDescrizione: {description[:200]}..."  # Mostra i primi 200 caratteri della descrizione
                    result_label = Label(text=result_text, font_size='16sp', color=(1, 1, 1, 1), size_hint_y=None)
                    result_label.bind(on_touch_down=lambda instance, touch, url=book_url: self.open_url(touch, instance, url))
                    result_layout.add_widget(result_label)

                    # Aggiungi il layout del risultato alla visualizzazione
                    self.results_layout.add_widget(result_layout)
            else:
                self.results_layout.add_widget(Label(text="Nessun libro trovato."))
        else:
            self.results_layout.add_widget(Label(text="Errore durante la ricerca del libro."))

    # Funzione per aprire il link del libro nel browser
    def open_url(self, touch, instance, url):
        if instance.collide_point(*touch.pos):
            if url:
                webbrowser.open(url)

    # Funzione per mostrare la seconda parte (gestione case editrici e libri)
    def show_second_part(self, *args):
        # Pulisci il layout
        self.main_layout.clear_widgets()

        # Layout superiore con il logo e il titolo
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=20)
        title_label = Label(text="Gestione Case Editrici e Libri", font_size='36sp', bold=True, color=(1, 1, 1, 1))
        top_layout.add_widget(title_label)

        self.main_layout.add_widget(top_layout)

        # Layout per cercare e selezionare la casa editrice
        publisher_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.publisher_input = TextInput(hint_text="Inserisci il nome della casa editrice", size_hint=(0.6, None), height=40)
        search_publisher_button = Button(text="Conferma Casa Editrice", size_hint=(0.4, None), height=40, background_color=(0.3, 0.6, 0.3, 1), color=(1, 1, 1, 1))
        search_publisher_button.bind(on_press=lambda x: self.select_publisher(self.publisher_input.text))

        publisher_layout.add_widget(self.publisher_input)
        publisher_layout.add_widget(search_publisher_button)
        self.main_layout.add_widget(publisher_layout)

        # Casella per mostrare la casa editrice selezionata
        self.publisher_label = Label(text="Nessuna casa editrice selezionata", size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        self.main_layout.add_widget(self.publisher_label)

        # Layout per cercare il libro (verrà abilitato solo dopo che una casa editrice è stata selezionata)
        self.book_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.book_input = TextInput(hint_text="Inserisci il titolo del libro", size_hint=(0.6, None), height=40, disabled=True)
        self.book_input.bind(on_text_validate=lambda instance: self.add_book(self.book_input.text, self.publisher_label.text))  # Invio cerca il libro
        add_book_button = Button(text="Cerca Libro", size_hint=(0.4, None), height=40, background_color=(0.3, 0.6, 0.3, 1), color=(1, 1, 1, 1), disabled=True)
        add_book_button.bind(on_press=lambda x: self.add_book(self.book_input.text, self.publisher_label.text))

        self.book_layout.add_widget(self.book_input)
        self.book_layout.add_widget(add_book_button)
        self.main_layout.add_widget(self.book_layout)

        # Pulsante per tornare alla prima parte
        back_to_search_button = Button(text="Torna a MyBook", size_hint=(1, 0.1), height=40, background_color=(0.5, 0.3, 0.8, 1), color=(1, 1, 1, 1))
        back_to_search_button.bind(on_press=self.show_first_part)
        self.main_layout.add_widget(back_to_search_button)

    # Funzione per simulare la selezione della casa editrice nell'app senza Google
    def select_publisher(self, publisher_name):
        if publisher_name:
            self.publisher_label.text = f"Casa editrice selezionata: {publisher_name}"
            self.book_input.disabled = False
            for widget in self.book_layout.children:
                widget.disabled = False
        else:
            self.publisher_label.text = "Nessuna casa editrice selezionata"
            self.book_input.disabled = True

    # Funzione per aggiungere un libro collegato alla casa editrice
    def add_book(self, book_title, publisher_name):
        if publisher_name and publisher_name != "Nessuna casa editrice selezionata":
            # Logica per aggiungere il libro alla casa editrice selezionata
            if publisher_name in publishers:
                publishers[publisher_name].append(book_title)
            else:
                publishers[publisher_name] = [book_title]
            books[book_title] = publisher_name
            # Simula l'apertura del sito della casa editrice con il libro trovato
            search_url = f"https://www.google.com/search?q={book_title}+{publisher_name}"
            webbrowser.open(search_url)
        else:
            self.main_layout.add_widget(Label(text="Seleziona prima una casa editrice.", font_size='16sp', color=(1, 0, 0, 1)))

if __name__ == "__main__":
    MyBookApp().run()
