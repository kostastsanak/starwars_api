from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import Character, Film, Starship
from .models import Vote
from datetime import date

class VoteModelTest(TestCase):
    def setUp(self):
        self.vote = Vote.objects.create(
            vote_type='character',
            item_id=1,
            votes=5
        )

    def test_vote_str(self):
        self.assertEqual(str(self.vote), "Character 1: 5 votes")

    def test_vote_unique_constraint(self):
        # Should not be able to create another vote for the same item
        with self.assertRaises(Exception):
            Vote.objects.create(
                vote_type='character',
                item_id=1,
                votes=3
            )

class VoteViewSetTest(APITestCase):
    def setUp(self):
        self.character = Character.objects.create(
            swapi_id=1,
            name="Luke Skywalker",
            gender="male"
        )
        self.film = Film.objects.create(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="Test crawl",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date=date(1977, 5, 25)
        )
        self.starship = Starship.objects.create(
            swapi_id=1,
            name="Millennium Falcon",
            model="YT-1300",
            manufacturer="Corellian",
            starship_class="Light freighter"
        )

    def test_list_votes(self):
        Vote.objects.create(vote_type='character', item_id=self.character.id, votes=5)
        
        url = reverse('votes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_vote_new(self):
        url = reverse('votes-list')
        data = {
            'vote_type': 'character',
            'item_id': self.character.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['votes'], 1)

    def test_create_vote_increment_existing(self):
        # Create initial vote through the API, not directly
        url = reverse('votes-list')
        data = {
            'vote_type': 'character',
            'item_id': self.character.id
        }
        # First vote
        response1 = self.client.post(url, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['votes'], 1)
        
        # Second vote (vote already exists with this ID)
        response2 = self.client.post(url, data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)  # Should fail due to unique constraint
        self.assertIn('non_field_errors', response2.data)

    def test_create_vote_invalid_character(self):
        url = reverse('votes-list')
        data = {
            'vote_type': 'character',
            'item_id': 999  # Non-existent character
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vote_invalid_film(self):
        url = reverse('votes-list')
        data = {
            'vote_type': 'film',
            'item_id': 999  # Non-existent film
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vote_invalid_starship(self):
        url = reverse('votes-list')
        data = {
            'vote_type': 'starship',
            'item_id': 999  # Non-existent starship
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_stats_empty(self):
        url = reverse('votes-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['overall_total'], 0)
        self.assertEqual(response.data['characters']['total_votes'], 0)
        self.assertEqual(response.data['films']['total_votes'], 0)
        self.assertEqual(response.data['starships']['total_votes'], 0)

    def test_vote_stats_with_data(self):
        Vote.objects.create(vote_type='character', item_id=self.character.id, votes=10)
        Vote.objects.create(vote_type='film', item_id=self.film.id, votes=20)
        Vote.objects.create(vote_type='starship', item_id=self.starship.id, votes=30)
        
        url = reverse('votes-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['overall_total'], 60)
        self.assertEqual(response.data['characters']['total_votes'], 10)
        self.assertEqual(response.data['films']['total_votes'], 20)
        self.assertEqual(response.data['starships']['total_votes'], 30)
        
        # Check character stats
        character_items = response.data['characters']['top_items']
        self.assertEqual(len(character_items), 1)
        self.assertEqual(character_items[0]['name'], 'Luke Skywalker')
        self.assertEqual(character_items[0]['votes'], 10)
        self.assertEqual(character_items[0]['percentage'], 100.0)

    def test_filter_votes_by_type(self):
        Vote.objects.create(vote_type='character', item_id=self.character.id, votes=5)
        Vote.objects.create(vote_type='film', item_id=self.film.id, votes=3)
        
        url = reverse('votes-list')
        response = self.client.get(url, {'vote_type': 'character'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vote_type'], 'character')

    def test_order_votes_by_count(self):
        Vote.objects.create(vote_type='character', item_id=self.character.id, votes=3)
        Vote.objects.create(vote_type='film', item_id=self.film.id, votes=10)
        
        url = reverse('votes-list')
        response = self.client.get(url, {'ordering': '-votes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        votes = response.data['results']
        self.assertEqual(votes[0]['votes'], 10)  # Film vote should be first
        self.assertEqual(votes[1]['votes'], 3)   # Character vote should be second
