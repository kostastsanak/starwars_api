from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
from datetime import date
from core.models import Character, Film, Starship, DataSyncStatus
from core.services import SWAPIService, SWAPIError
from requests.exceptions import RequestException

class CharacterModelTest(TestCase):
    def setUp(self):
        self.film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="It is a period of civil war...",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )
        self.starship = Starship.objects.create(
            swapi_id=1,
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            manufacturer="Corellian Engineering Corporation",
            starship_class="Light freighter"
        )
        self.character = Character.objects.create(
            swapi_id=1,
            name="Luke Skywalker",
            height="172",
            mass="77",
            hair_color="blond",
            gender="male"
        )

    def test_character_str(self):
        self.assertEqual(str(self.character), "Luke Skywalker")

    def test_character_relationships(self):
        self.character.films.add(self.film)
        self.character.starships.add(self.starship)
        
        self.assertEqual(self.character.films.count(), 1)
        self.assertEqual(self.character.starships.count(), 1)
        self.assertIn(self.film, self.character.films.all())
        self.assertIn(self.starship, self.character.starships.all())

class FilmModelTest(TestCase):
    def setUp(self):
        self.film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="It is a period of civil war...",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )

    def test_film_str(self):
        self.assertEqual(str(self.film), "Episode 4: A New Hope")

    def test_film_ordering(self):
        film2 = Film.objects.create(
            swapi_id=2,
            title="The Empire Strikes Back",
            episode_id=5,
            opening_crawl="Another crawl...",
            director="Irvin Kershner",
            producer="Gary Kurtz",
            release_date=date(1980, 5, 17)
        )
        films = Film.objects.all()
        self.assertEqual(films[0], self.film)  # Episode 4 should come first
        self.assertEqual(films[1], film2)     # Episode 5 should come second

class StarshipModelTest(TestCase):
    def setUp(self):
        self.starship = Starship.objects.create(
            swapi_id=1,
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            manufacturer="Corellian Engineering Corporation",
            starship_class="Light freighter"
        )

    def test_starship_str(self):
        self.assertEqual(str(self.starship), "Millennium Falcon")

class CharacterViewSetTest(APITestCase):
    def setUp(self):
        self.film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="Test crawl",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )
        self.character = Character.objects.create(
            swapi_id=1,
            name="Luke Skywalker",
            height="172",
            gender="male"
        )
        self.character.films.add(self.film)

    def test_list_characters(self):
        url = reverse('characters-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Luke Skywalker')

    def test_retrieve_character(self):
        url = reverse('characters-detail', args=[self.character.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Luke Skywalker')
        self.assertEqual(len(response.data['films']), 1)

    def test_search_characters(self):
        url = reverse('characters-search')
        response = self.client.get(url, {'q': 'Luke'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_characters_no_query(self):
        url = reverse('characters-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_characters(self):
        url = reverse('characters-list')
        response = self.client.get(url, {'gender': 'male'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_order_characters(self):
        Character.objects.create(swapi_id=2, name="Darth Vader", gender="male")
        url = reverse('characters-list')
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [char['name'] for char in response.data['results']]
        self.assertEqual(names, ['Darth Vader', 'Luke Skywalker'])

    def test_create_character_not_allowed(self):
        url = reverse('characters-list')
        data = {'name': 'Test Character'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_character_not_allowed(self):
        url = reverse('characters-detail', args=[self.character.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class FilmViewSetTest(APITestCase):
    def setUp(self):
        self.film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="It is a period of civil war...",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )

    def test_list_films(self):
        url = reverse('films-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_film(self):
        url = reverse('films-detail', args=[self.film.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'A New Hope')

    def test_search_films(self):
        url = reverse('films-search')
        response = self.client.get(url, {'q': 'Hope'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_films_by_episode(self):
        url = reverse('films-list')
        response = self.client.get(url, {'episode_id': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class StarshipViewSetTest(APITestCase):
    def setUp(self):
        self.starship = Starship.objects.create(
            swapi_id=1,
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            manufacturer="Corellian Engineering Corporation",
            starship_class="Light freighter"
        )

    def test_list_starships(self):
        url = reverse('starships-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_starship(self):
        url = reverse('starships-detail', args=[self.starship.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Millennium Falcon')

    def test_search_starships(self):
        url = reverse('starships-search')
        response = self.client.get(url, {'q': 'Falcon'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class SWAPIServiceTest(TestCase):
    def test_extract_id_from_url(self):
        url = "https://swapi.info/api/people/1/"
        result = SWAPIService.extract_id_from_url(url)
        self.assertEqual(result, 1)

    def test_extract_id_from_invalid_url(self):
        with self.assertRaises(SWAPIError):
            SWAPIService.extract_id_from_url("invalid-url")

    @patch('core.services.requests.get')
    def test_make_request_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = SWAPIService.make_request('https://test.com')
        self.assertEqual(result, {'test': 'data'})


    @patch('core.services.requests.get')
    def test_make_request_failure(self, mock_get):
        mock_get.side_effect = RequestException('Connection error')
        
        with self.assertRaises(SWAPIError):
            SWAPIService.make_request('https://test.com')

    @patch.object(SWAPIService, 'make_request')
    def test_fetch_all_films(self, mock_request):
        mock_request.return_value = [
            {
                'title': 'A New Hope',
                'episode_id': 4,
                'opening_crawl': 'Test crawl',
                'director': 'George Lucas',
                'producer': 'Gary Kurtz',
                'release_date': '1977-05-25',
                'url': 'https://swapi.info/api/films/1/'
            }
        ]

        films = SWAPIService.fetch_all_films()
        self.assertEqual(len(films), 1)
        self.assertEqual(films[0].title, 'A New Hope')

    @patch.object(SWAPIService, 'make_request')
    def test_fetch_all_starships(self, mock_request):
        mock_request.return_value = [
            {
                'name': 'Millennium Falcon',
                'model': 'YT-1300',
                'manufacturer': 'Corellian',
                'starship_class': 'Light freighter',
                'cost_in_credits': 'unknown',
                'length': 'unknown',
                'max_atmosphering_speed': 'unknown',
                'crew': 'unknown',
                'passengers': '0',
                'cargo_capacity': 'unknown',
                'hyperdrive_rating': 'unknown',
                'url': 'https://swapi.info/api/starships/1/'
            }
        ]

        starships = SWAPIService.fetch_all_starships()
        self.assertEqual(len(starships), 1)
        self.assertEqual(starships[0].name, 'Millennium Falcon')

    @patch.object(SWAPIService, 'make_request')
    def test_fetch_all_characters(self, mock_request):
        # Create a film first for the relationship
        film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="Test crawl",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )

        mock_request.return_value = [
            {
                'name': 'Luke Skywalker',
                'height': '172',
                'mass': '77',
                'hair_color': 'blond',
                'skin_color': 'fair',
                'eye_color': 'blue',
                'birth_year': '19BBY',
                'gender': 'male',
                'films': ['https://swapi.info/api/films/1/'],
                'starships': [],
                'url': 'https://swapi.info/api/people/1/'
            }
        ]

        characters = SWAPIService.fetch_all_characters()
        self.assertEqual(len(characters), 1)
        self.assertEqual(characters[0].name, 'Luke Skywalker')

class SWAPIViewSetTest(APITestCase):
    @patch.object(SWAPIService, 'populate_all_data')
    def test_populate_all_success(self, mock_populate):
        mock_populate.return_value = {
            'films_created': 6,
            'starships_created': 36,
            'characters_created': 82,
            'total_films': 6,
            'total_starships': 36,
            'total_characters': 82
        }

        url = reverse('swapi-populate-all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch.object(SWAPIService, 'populate_all_data')
    def test_populate_all_failure(self, mock_populate):
        mock_populate.side_effect = SWAPIError('Connection failed')

        url = reverse('swapi-populate-all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(response.data['success'])

    def test_sync_status(self):
        DataSyncStatus.objects.create(resource_type='films', total_records=6)
        
        url = reverse('swapi-sync-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)