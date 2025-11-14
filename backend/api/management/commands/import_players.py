import json
from django.core.management.base import BaseCommand
from api.models import Player, CareerStats


class Command(BaseCommand):
    help = 'Import baseball players from JSON data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file with player data',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            CareerStats.objects.all().delete()
            Player.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        # Default data if no file provided
        if options['file']:
            with open(options['file'], 'r') as f:
                data = json.load(f)
        else:
            # Use the data from the user's message
            data = self.get_default_data()

        created_count = 0
        updated_count = 0
        error_count = 0

        for player_data in data:
            try:
                # Create or get player
                player, created = Player.objects.get_or_create(
                    name=player_data['Player name'],
                    defaults={'position': player_data['position']}
                )

                if not created:
                    player.position = player_data['position']
                    player.save()
                    updated_count += 1
                else:
                    created_count += 1

                # Handle caught stealing -- (null value)
                caught_stealing = player_data.get('Caught stealing')
                if caught_stealing == '--':
                    caught_stealing = None

                # Create or update career stats
                CareerStats.objects.update_or_create(
                    player=player,
                    defaults={
                        'games': player_data['Games'],
                        'at_bats': player_data['At-bat'],
                        'runs': player_data['Runs'],
                        'hits': player_data['Hits'],
                        'doubles': player_data['Double (2B)'],
                        'triples': player_data['third baseman'],
                        'home_runs': player_data['home run'],
                        'rbis': player_data['run batted in'],
                        'walks': player_data['a walk'],
                        'strikeouts': player_data['Strikeouts'],
                        'stolen_bases': player_data['stolen base'],
                        'caught_stealing': caught_stealing,
                        'batting_avg': player_data['AVG'],
                        'on_base_pct': player_data['On-base Percentage'],
                        'slugging_pct': player_data['Slugging Percentage'],
                        'ops': player_data['On-base Plus Slugging'],
                    }
                )

                self.stdout.write(
                    self.style.SUCCESS(f'✓ {player.name}')
                )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error with {player_data.get("Player name", "Unknown")}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Import complete!'))
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        self.stdout.write('='*50)

    def get_default_data(self):
        """Return the default baseball data"""
        # This is the data from the user's JSON - truncated for brevity in code
        # In practice, you'd load this from a file
        return []  # We'll pass data via file or use fixtures
