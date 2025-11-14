from django.core.management.base import BaseCommand
from api.models import Player
import anthropic
import os
import time


class Command(BaseCommand):
    help = 'Generate AI descriptions for players who do not have one'

    def handle(self, *args, **options):
        # Get all players without descriptions
        players = Player.objects.filter(description__isnull=True) | Player.objects.filter(description='')

        if not players.exists():
            self.stdout.write(self.style.SUCCESS('All players already have descriptions!'))
            return

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('ANTHROPIC_API_KEY environment variable not set'))
            return

        client = anthropic.Anthropic(api_key=api_key)

        total = players.count()
        self.stdout.write(f'Generating descriptions for {total} players...\n')

        for idx, player in enumerate(players, 1):
            try:
                stats = player.career_stats

                # Build prompt for Claude
                prompt = f"""Generate a 3-5 sentence description for baseball player {player.name}, who plays {player.get_position_display()}.

Career Statistics:
- Games: {stats.games}
- Batting Average: {stats.batting_avg}
- Home Runs: {stats.home_runs}
- RBIs: {stats.rbis}
- Stolen Bases: {stats.stolen_bases}
- OPS: {stats.ops}

Write an engaging, informative description that highlights their career achievements, playing style, and significance in baseball history. Focus on what makes them unique or memorable. Keep it between 3-5 sentences."""

                message = client.messages.create(
                    model="claude-3-7-sonnet-latest",
                    max_tokens=300,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                description = message.content[0].text
                player.description = description
                player.save()

                self.stdout.write(
                    self.style.SUCCESS(f'[{idx}/{total}] Generated description for {player.name}')
                )

                # Add a small delay to avoid rate limits
                if idx < total:
                    time.sleep(0.5)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[{idx}/{total}] Failed to generate description for {player.name}: {str(e)}')
                )
                continue

        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Generated descriptions for {total} players.'))
