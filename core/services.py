import requests
import logging
from django.utils import timezone
from .models import Character, Film, Starship, DataSyncStatus
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SWAPIError(Exception):
    """Custom exception for SWAPI-related errors"""
    pass

class SWAPIService:
    BASE_URL = "https://swapi.info/api"  # Updated to working API
    TIMEOUT = 30
    
    @staticmethod
    def extract_id_from_url(url: str) -> int:
        """Extract ID from SWAPI URL"""
        try:
            return int(url.rstrip('/').split('/')[-1])
        except (ValueError, IndexError):
            raise SWAPIError(f"Invalid SWAPI URL format: {url}")
    
    @staticmethod
    def make_request(url: str) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, timeout=SWAPIService.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"SWAPI request failed for {url}: {e}")
            raise SWAPIError(f"Failed to fetch data from SWAPI: {e}")
    
    @staticmethod
    def update_sync_status(resource_type: str, is_syncing: bool = False, total_records: int = 0):
        """Update synchronization status"""
        status, created = DataSyncStatus.objects.get_or_create(
            resource_type=resource_type,
            defaults={'total_records': total_records, 'is_syncing': is_syncing}
        )
        if not created:
            status.is_syncing = is_syncing
            status.total_records = total_records
            if not is_syncing:
                status.last_sync = timezone.now()
            status.save()
        return status
    
    @staticmethod
    def fetch_all_films() -> List[Film]:
        """Fetch all films from SWAPI and store in database"""
        SWAPIService.update_sync_status('films', is_syncing=True)
        
        try:
            url = f"{SWAPIService.BASE_URL}/films"
            films_data = SWAPIService.make_request(url)
            
            if not films_data:
                raise SWAPIError("Invalid response from SWAPI films endpoint")
            
            created_films = []
            
            for film_data in films_data:
                try:
                    swapi_id = SWAPIService.extract_id_from_url(film_data['url'])
                    film, created = Film.objects.get_or_create(
                        swapi_id=swapi_id,
                        defaults={
                            'title': film_data.get('title', ''),
                            'episode_id': film_data.get('episode_id', 0),
                            'opening_crawl': film_data.get('opening_crawl', ''),
                            'director': film_data.get('director', ''),
                            'producer': film_data.get('producer', ''),
                            'release_date': datetime.strptime(
                                film_data.get('release_date', '1977-05-25'), 
                                '%Y-%m-%d'
                            ).date(),
                        }
                    )
                    if created:
                        created_films.append(film)
                        logger.info(f"Created film: {film.title}")
                except Exception as e:
                    logger.error(f"Error creating film {film_data.get('title', 'Unknown')}: {e}")
                    continue
            
            SWAPIService.update_sync_status('films', is_syncing=False, total_records=Film.objects.count())
            return created_films
            
        except Exception as e:
            SWAPIService.update_sync_status('films', is_syncing=False)
            raise SWAPIError(f"Failed to fetch films: {e}")
    
    @staticmethod
    def fetch_all_starships() -> List[Starship]:
        """Fetch all starships from SWAPI"""
        SWAPIService.update_sync_status('starships', is_syncing=True)
        
        try:
            url = f"{SWAPIService.BASE_URL}/starships"
            starships_data = SWAPIService.make_request(url)
            
            if not starships_data:
                raise SWAPIError("Invalid response from SWAPI starships endpoint")
            
            created_starships = []
            
            for starship_data in starships_data:
                try:
                    swapi_id = SWAPIService.extract_id_from_url(starship_data['url'])
                    starship, created = Starship.objects.get_or_create(
                        swapi_id=swapi_id,
                        defaults={
                            'name': starship_data.get('name', ''),
                            'model': starship_data.get('model', ''),
                            'manufacturer': starship_data.get('manufacturer', ''),
                            'cost_in_credits': starship_data.get('cost_in_credits', 'unknown'),
                            'length': starship_data.get('length', 'unknown'),
                            'max_atmosphering_speed': starship_data.get('max_atmosphering_speed', 'unknown'),
                            'crew': starship_data.get('crew', 'unknown'),
                            'passengers': starship_data.get('passengers', '0'),
                            'cargo_capacity': starship_data.get('cargo_capacity', 'unknown'),
                            'hyperdrive_rating': starship_data.get('hyperdrive_rating', 'unknown'),
                            'starship_class': starship_data.get('starship_class', 'unknown'),
                        }
                    )
                    if created:
                        created_starships.append(starship)
                        logger.info(f"Created starship: {starship.name}")
                except Exception as e:
                    logger.error(f"Error creating starship {starship_data.get('name', 'Unknown')}: {e}")
                    continue
            
            SWAPIService.update_sync_status('starships', is_syncing=False, total_records=Starship.objects.count())
            return created_starships
            
        except Exception as e:
            SWAPIService.update_sync_status('starships', is_syncing=False)
            raise SWAPIError(f"Failed to fetch starships: {e}")
    
    @staticmethod
    def fetch_all_characters() -> List[Character]:
        """Fetch all characters from SWAPI with relationships"""
        SWAPIService.update_sync_status('characters', is_syncing=True)
        
        try:
            url = f"{SWAPIService.BASE_URL}/people"
            characters_data = SWAPIService.make_request(url)
            
            if not characters_data:
                raise SWAPIError("Invalid response from SWAPI people endpoint")
            
            created_characters = []
            
            for char_data in characters_data:
                try:
                    swapi_id = SWAPIService.extract_id_from_url(char_data['url'])
                    character, created = Character.objects.get_or_create(
                        swapi_id=swapi_id,
                        defaults={
                            'name': char_data.get('name', ''),
                            'height': char_data.get('height', 'unknown'),
                            'mass': char_data.get('mass', 'unknown'),
                            'hair_color': char_data.get('hair_color', 'unknown'),
                            'skin_color': char_data.get('skin_color', 'unknown'),
                            'eye_color': char_data.get('eye_color', 'unknown'),
                            'birth_year': char_data.get('birth_year', 'unknown'),
                            'gender': char_data.get('gender', 'unknown'),
                        }
                    )
                    
                    if created:
                        # Add film relationships
                        for film_url in char_data.get('films', []):
                            try:
                                film_id = SWAPIService.extract_id_from_url(film_url)
                                try:
                                    film = Film.objects.get(swapi_id=film_id)
                                    character.films.add(film)
                                except Film.DoesNotExist:
                                    logger.warning(f"Film with swapi_id {film_id} not found for character {character.name}")
                            except Exception as e:
                                logger.error(f"Error adding film relationship: {e}")
                        
                        # Add starship relationships
                        for starship_url in char_data.get('starships', []):
                            try:
                                starship_id = SWAPIService.extract_id_from_url(starship_url)
                                try:
                                    starship = Starship.objects.get(swapi_id=starship_id)
                                    character.starships.add(starship)
                                except Starship.DoesNotExist:
                                    logger.warning(f"Starship with swapi_id {starship_id} not found for character {character.name}")
                            except Exception as e:
                                logger.error(f"Error adding starship relationship: {e}")
                        
                        created_characters.append(character)
                        logger.info(f"Created character: {character.name}")
                        
                except Exception as e:
                    logger.error(f"Error creating character {char_data.get('name', 'Unknown')}: {e}")
                    continue
            
            SWAPIService.update_sync_status('characters', is_syncing=False, total_records=Character.objects.count())
            return created_characters
            
        except Exception as e:
            SWAPIService.update_sync_status('characters', is_syncing=False)
            raise SWAPIError(f"Failed to fetch characters: {e}")

    @staticmethod
    def populate_all_data():
        """Populate all required data from SWAPI"""
        logger.info("Starting SWAPI data population...")
        
        try:
            # First populate films and starships (no dependencies)
            films = SWAPIService.fetch_all_films()
            starships = SWAPIService.fetch_all_starships()
            
            # Then populate characters (depends on films and starships)
            characters = SWAPIService.fetch_all_characters()
            
            return {
                'films_created': len(films),
                'starships_created': len(starships),
                'characters_created': len(characters),
                'total_films': Film.objects.count(),
                'total_starships': Starship.objects.count(),
                'total_characters': Character.objects.count(),
            }
            
        except Exception as e:
            logger.error(f"Failed to populate SWAPI data: {e}")
            raise SWAPIError(f"Data population failed: {e}")
