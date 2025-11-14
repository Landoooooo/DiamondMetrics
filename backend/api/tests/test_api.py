from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from api.models import Player, CareerStats


class PlayerAPITest(TestCase):
    """Test cases for the Player API endpoints"""

    def setUp(self):
        """Set up test data and API client"""
        self.client = APIClient()

        # Create test players with career stats
        self.player1 = Player.objects.create(
            name="Babe Ruth",
            position="OF",
            description="The Sultan of Swat, one of baseball's greatest legends."
        )
        self.stats1 = CareerStats.objects.create(
            player=self.player1,
            games=2503,
            at_bats=8399,
            runs=2174,
            hits=2873,
            doubles=506,
            triples=136,
            home_runs=714,
            rbis=2214,
            walks=2062,
            strikeouts=1330,
            stolen_bases=123,
            caught_stealing=117,
            batting_avg=Decimal('0.342'),
            on_base_pct=Decimal('0.474'),
            slugging_pct=Decimal('0.690'),
            ops=Decimal('1.164')
        )

        self.player2 = Player.objects.create(
            name="Hank Aaron",
            position="OF",
            description="Hammerin' Hank, the all-time home run king for decades."
        )
        self.stats2 = CareerStats.objects.create(
            player=self.player2,
            games=3298,
            at_bats=12364,
            runs=2174,
            hits=3771,
            doubles=624,
            triples=98,
            home_runs=755,
            rbis=2297,
            walks=1402,
            strikeouts=1383,
            stolen_bases=240,
            caught_stealing=73,
            batting_avg=Decimal('0.305'),
            on_base_pct=Decimal('0.374'),
            slugging_pct=Decimal('0.555'),
            ops=Decimal('0.929')
        )

        self.player3 = Player.objects.create(
            name="Willie Mays",
            position="CF",
            description="The Say Hey Kid, arguably the most complete player ever."
        )
        self.stats3 = CareerStats.objects.create(
            player=self.player3,
            games=2992,
            at_bats=10881,
            runs=2062,
            hits=3283,
            doubles=523,
            triples=140,
            home_runs=660,
            rbis=1903,
            walks=1464,
            strikeouts=1526,
            stolen_bases=338,
            caught_stealing=103,
            batting_avg=Decimal('0.302'),
            on_base_pct=Decimal('0.384'),
            slugging_pct=Decimal('0.557'),
            ops=Decimal('0.941')
        )

    def test_get_players_list(self):
        """Test retrieving the list of players"""
        url = reverse('player-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_players_list_ordering(self):
        """Test that players are ordered by name by default"""
        url = reverse('player-list')
        response = self.client.get(url)

        names = [player['name'] for player in response.data['results']]
        self.assertEqual(names, ['Babe Ruth', 'Hank Aaron', 'Willie Mays'])

    def test_get_players_list_with_home_runs_ordering(self):
        """Test ordering players by home runs"""
        url = reverse('player-list') + '?ordering=-career_stats__home_runs'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered: Hank Aaron (755), Babe Ruth (714), Willie Mays (660)
        names = [player['name'] for player in response.data['results']]
        self.assertEqual(names, ['Hank Aaron', 'Babe Ruth', 'Willie Mays'])

    def test_get_player_detail(self):
        """Test retrieving a single player's details"""
        url = reverse('player-detail', kwargs={'pk': self.player1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Babe Ruth')
        self.assertEqual(response.data['position'], 'OF')
        self.assertEqual(response.data['position_display'], 'Outfield')
        self.assertIn('career_stats', response.data)
        self.assertEqual(response.data['career_stats']['home_runs'], 714)

    def test_get_nonexistent_player(self):
        """Test retrieving a player that doesn't exist"""
        url = reverse('player-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_player_stats(self):
        """Test updating a player's career statistics"""
        url = reverse('player-update-stats', kwargs={'pk': self.player1.pk})
        data = {
            'games': 2504,
            'home_runs': 715,
            'batting_avg': '0.343',
            'ops': '1.165'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.stats1.refresh_from_db()
        self.assertEqual(self.stats1.games, 2504)
        self.assertEqual(self.stats1.home_runs, 715)
        self.assertEqual(self.stats1.batting_avg, Decimal('0.343'))
        self.assertEqual(self.stats1.ops, Decimal('1.165'))

    def test_update_stats_nonexistent_player(self):
        """Test updating stats for a player that doesn't exist"""
        url = reverse('player-update-stats', kwargs={'pk': 9999})
        data = {'games': 100}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leaderboard_home_runs(self):
        """Test the home runs leaderboard endpoint"""
        url = reverse('player-leaderboard') + '?stat=home_runs&limit=3'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stat'], 'home_runs')
        self.assertEqual(len(response.data['leaders']), 3)
        # Should be ordered: Hank Aaron (755), Babe Ruth (714), Willie Mays (660)
        self.assertEqual(response.data['leaders'][0]['name'], 'Hank Aaron')
        self.assertEqual(response.data['leaders'][0]['home_runs'], 755)

    def test_leaderboard_batting_average(self):
        """Test the batting average leaderboard endpoint"""
        url = reverse('player-leaderboard') + '?stat=batting_avg&limit=2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stat'], 'batting_avg')
        self.assertEqual(len(response.data['leaders']), 2)
        # Should be ordered: Babe Ruth (0.342), Hank Aaron (0.305)
        self.assertEqual(response.data['leaders'][0]['name'], 'Babe Ruth')

    def test_leaderboard_ops(self):
        """Test the OPS leaderboard endpoint"""
        url = reverse('player-leaderboard') + '?stat=ops&limit=3'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stat'], 'ops')
        # Should be ordered: Babe Ruth (1.164), Willie Mays (0.941), Hank Aaron (0.929)
        self.assertEqual(response.data['leaders'][0]['name'], 'Babe Ruth')
        self.assertEqual(response.data['leaders'][1]['name'], 'Willie Mays')

    def test_leaderboard_default_limit(self):
        """Test that leaderboard uses default limit of 10"""
        url = reverse('player-leaderboard') + '?stat=home_runs'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # We only have 3 players, so should return 3
        self.assertEqual(len(response.data['leaders']), 3)

    def test_leaderboard_invalid_stat(self):
        """Test leaderboard with invalid stat parameter defaults to home_runs"""
        url = reverse('player-leaderboard') + '?stat=invalid_stat'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Invalid stat defaults to home_runs
        self.assertEqual(response.data['stat'], 'invalid_stat')

    def test_compare_players(self):
        """Test comparing two players"""
        url = reverse('player-compare') + f'?player1={self.player1.pk}&player2={self.player2.pk}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['player1']['name'], 'Babe Ruth')
        self.assertEqual(response.data['player2']['name'], 'Hank Aaron')
        self.assertIn('comparison', response.data)

        # Check comparison data
        comparison = response.data['comparison']
        self.assertIn('home_runs', comparison)
        self.assertEqual(comparison['home_runs']['player1'], 714)
        self.assertEqual(comparison['home_runs']['player2'], 755)
        self.assertEqual(comparison['home_runs']['difference'], -41)

    def test_compare_missing_player_id(self):
        """Test comparison with missing player ID"""
        url = reverse('player-compare') + f'?player1={self.player1.pk}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_compare_nonexistent_player(self):
        """Test comparison with non-existent player"""
        url = reverse('player-compare') + f'?player1={self.player1.pk}&player2=9999'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_compare_same_player(self):
        """Test comparing a player with themselves"""
        url = reverse('player-compare') + f'?player1={self.player1.pk}&player2={self.player1.pk}'
        response = self.client.get(url)

        # Should still work, just show zero differences
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comparison = response.data['comparison']
        self.assertEqual(comparison['home_runs']['difference'], 0)

    def test_pagination(self):
        """Test pagination on the players list"""
        # Create more players to test pagination
        for i in range(15):
            player = Player.objects.create(
                name=f"Player {i}",
                position="SS"
            )
            CareerStats.objects.create(
                player=player,
                games=100,
                at_bats=400,
                runs=50,
                hits=120,
                doubles=20,
                triples=5,
                home_runs=10,
                rbis=50,
                walks=40,
                strikeouts=80,
                stolen_bases=10,
                caught_stealing=2,
                batting_avg=Decimal('0.300'),
                on_base_pct=Decimal('0.350'),
                slugging_pct=Decimal('0.450'),
                ops=Decimal('0.800')
            )

        url = reverse('player-list') + '?page=1&limit=10'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data.get('next'))

    def test_search_players(self):
        """Test searching for players by name"""
        url = reverse('player-list') + '?search=Ruth'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Babe Ruth')

    def test_filter_by_position(self):
        """Test filtering players by position"""
        url = reverse('player-list') + '?position=CF'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Willie Mays')
