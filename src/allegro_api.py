import os
import json
import requests

# Stałe adresy URL do API Allegro
ALLEGRO_AUTH_URL = "https://allegro.pl/auth/oauth/token"
ALLEGRO_API_URL = "https://api.allegro.pl/offers/listing"


class AllegroAPIClient:
    """
    Klient do obsługi API Allegro, który zarządza tokenem dostępowym
    i prawidłowo identyfikuje aplikację w zapytaniach.
    """

    def __init__(self):
        """Inicjalizuje klienta, ładując dane dostępowe."""
        self._load_credentials()
        self.access_token = None

    def _load_credentials(self):
        """Wewnętrzna funkcja do ładowania danych dostępowych z pliku."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        config_path = os.path.join(project_root, "config", "allegro_api.json")

        if not os.path.exists(config_path):
            raise FileNotFoundError("Nie znaleziono pliku konfiguracyjnego dla API Allegro: config/allegro_api.json")

        with open(config_path, 'r') as f:
            creds = json.load(f)
            if "client_id" not in creds or "client_secret" not in creds:
                raise ValueError("Plik konfiguracyjny API Allegro musi zawierać 'client_id' i 'client_secret'.")

            self.client_id = creds['client_id']
            self.client_secret = creds['client_secret']

    def _authenticate(self):
        """Pobiera token dostępowy i zapisuje go w instancji klasy."""
        print("Uwierzytelnianie w API Allegro...")
        try:
            auth_response = requests.post(
                ALLEGRO_AUTH_URL,
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials'}
            )
            auth_response.raise_for_status()
            self.access_token = auth_response.json().get('access_token')
            if self.access_token:
                print("Pomyślnie uzyskano token dostępowy.")
                return True
            return False

        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas autoryzacji w API Allegro: {e}")
            return False

    def search_offers(self, query):
        """
        Wyszukuje oferty na Allegro. Używa istniejącego tokenu lub pobiera nowy.
        """
        if not self.access_token:
            if not self._authenticate():
                return None

        # Definiujemy nagłówki zapytania
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.allegro.public.v1+json',

            # --- POPRAWKA: Kluczowy nagłówek identyfikujący Twoją aplikację ---
            # To rozwiązuje problem błędu 403 Forbidden.
            'User-Agent': 'SellingBot/1.0 (by Tirgul; contact: tomek.sieminski23@gmail.com)'
        }

        # Definiujemy parametry zapytania
        params = {
            'phrase': query
        }

        try:
            response = requests.get(ALLEGRO_API_URL, headers=headers, params=params)
            # Sprawdź, czy zapytanie się powiodło (zgłosi błąd dla statusów 4xx/5xx)
            response.raise_for_status()

            data = response.json()
            items = data.get('items', {}).get('promoted', []) + data.get('items', {}).get('regular', [])
            return items

        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas wyszukiwania ofert dla '{query}': {e}")
            # Jeśli mamy odpowiedź od serwera, pokażmy jej treść - to pomaga w diagnozie
            if e.response is not None:
                print(f"Treść odpowiedzi serwera: {e.response.text}")

            # Automatyczne odnawianie tokenu w przypadku błędu 401
            if e.response is not None and e.response.status_code == 401:
                print("Token mógł wygasnąć. Próbuję odnowić...")
                self.access_token = None
                return self.search_offers(query)  # Spróbuj ponownie z nowym tokenem

            return None