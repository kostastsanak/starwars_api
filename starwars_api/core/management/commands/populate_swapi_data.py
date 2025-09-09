from django.core.management.base import BaseCommand, CommandError
from core.services import SWAPIService, SWAPIError

class Command(BaseCommand):
    help = 'Populate database with SWAPI data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--resource',
            type=str,
            help='Specify resource type to populate: films, starships, characters, or all (default: all)',
            choices=['films', 'starships', 'characters', 'all'],
            default='all'
        )

    def handle(self, *args, **options):
        resource = options['resource']
        
        self.stdout.write(
            self.style.HTTP_INFO('Populating SWAPI data...')
        )
        
        try:
            if resource == 'all':
                self.stdout.write('Populating all SWAPI data...')
                result = SWAPIService.populate_all_data()
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully populated data:')
                )
                self.stdout.write(f"- Films: {result['films_created']} new, {result['total_films']} total")
                self.stdout.write(f"- Starships: {result['starships_created']} new, {result['total_starships']} total")
                self.stdout.write(f"- Characters: {result['characters_created']} new, {result['total_characters']} total")
                
            elif resource == 'films':
                films = SWAPIService.fetch_all_films()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully populated {len(films)} films')
                )
                
            elif resource == 'starships':
                starships = SWAPIService.fetch_all_starships()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully populated {len(starships)} starships')
                )
                
            elif resource == 'characters':
                characters = SWAPIService.fetch_all_characters()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully populated {len(characters)} characters')
                )
                
        except SWAPIError as e:
            self.stdout.write(
                self.style.ERROR(f'Population failed: {e}')
            )
            raise CommandError(f'SWAPI population failed: {e}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
            raise CommandError(f'Unexpected error during population: {e}')
