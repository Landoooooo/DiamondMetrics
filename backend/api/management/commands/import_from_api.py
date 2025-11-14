from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Player, CareerStats
from decimal import Decimal
import requests


class Command(BaseCommand):
    help = 'Import baseball player data from external API'

    def handle(self, *args, **options):
        api_url = 'https://api.hirefraction.com/api/test/baseball'

        self.stdout.write('Fetching data from API...')

        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch data from API: {str(e)}'))
            return

        if not isinstance(data, list):
            self.stdout.write(self.style.ERROR('API response is not a list'))
            return

        self.stdout.write(f'Fetched {len(data)} players from API')

        # Track statistics
        created_count = 0
        updated_count = 0
        error_count = 0

        # Position mapping from API to our choices
        position_map = {
            'LF': 'LF',
            'CF': 'CF',
            'RF': 'RF',
            '1B': '1B',
            '2B': '2B',
            '3B': '3B',
            'SS': 'SS',
            'C': 'C',
            'P': 'P',
            'DH': 'DH',
            'OF': 'OF',
        }

        for idx, player_data in enumerate(data, 1):
            try:
                with transaction.atomic():
                    # Extract and clean player name
                    name = player_data.get('Player name', '').strip()
                    if not name:
                        self.stdout.write(self.style.WARNING(f'[{idx}/{len(data)}] Skipping player with no name'))
                        error_count += 1
                        continue

                    # Map position
                    api_position = player_data.get('position', 'OF').strip()
                    position = position_map.get(api_position, 'OF')

                    # Get or create player
                    player, created = Player.objects.get_or_create(
                        name=name,
                        defaults={'position': position}
                    )

                    # Update position if it changed
                    if not created and player.position != position:
                        player.position = position
                        player.save()

                    # Handle caught_stealing which can be "--"
                    caught_stealing_value = player_data.get('Caught stealing', 0)
                    if caught_stealing_value == '--' or caught_stealing_value == '':
                        caught_stealing_value = None
                    else:
                        try:
                            caught_stealing_value = int(caught_stealing_value)
                        except (ValueError, TypeError):
                            caught_stealing_value = None

                    # Create or update career stats
                    stats_data = {
                        'games': int(player_data.get('Games', 0)),
                        'at_bats': int(player_data.get('At-bat', 0)),
                        'runs': int(player_data.get('Runs', 0)),
                        'hits': int(player_data.get('Hits', 0)),
                        'doubles': int(player_data.get('Double (2B)', 0)),
                        'triples': int(player_data.get('third baseman', 0)),
                        'home_runs': int(player_data.get('home run', 0)),
                        'rbis': int(player_data.get('run batted in', 0)),
                        'walks': int(player_data.get('a walk', 0)),
                        'strikeouts': int(player_data.get('Strikeouts', 0)),
                        'stolen_bases': int(player_data.get('stolen base', 0)),
                        'caught_stealing': caught_stealing_value,
                        'batting_avg': Decimal(str(player_data.get('AVG', 0.0))),
                        'on_base_pct': Decimal(str(player_data.get('On-base Percentage', 0.0))),
                        'slugging_pct': Decimal(str(player_data.get('Slugging Percentage', 0.0))),
                        'ops': Decimal(str(player_data.get('On-base Plus Slugging', 0.0))),
                    }

                    # Update or create stats
                    CareerStats.objects.update_or_create(
                        player=player,
                        defaults=stats_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'[{idx}/{len(data)}] Created {name}')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            f'[{idx}/{len(data)}] Updated {name}'
                        )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[{idx}/{len(data)}] Error processing {player_data.get("Player name", "Unknown")}: {str(e)}')
                )
                continue

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(f'Created: {created_count} players')
        self.stdout.write(f'Updated: {updated_count} players')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'Errors: {error_count}'))
        self.stdout.write('='*50)
