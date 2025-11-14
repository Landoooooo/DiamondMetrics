from django.test import TestCase
from decimal import Decimal
from api.models import Player, CareerStats
from api.serializers import (
    CareerStatsSerializer,
    PlayerSerializer,
    PlayerListSerializer,
    ComparisonSerializer,
    LeaderboardSerializer
)


class CareerStatsSerializerTest(TestCase):
    """Test cases for the CareerStatsSerializer"""

    def setUp(self):
        """Set up test data"""
        self.player = Player.objects.create(
            name="Test Player",
            position="1B"
        )
        self.stats = CareerStats.objects.create(
            player=self.player,
            games=2000,
            at_bats=8000,
            runs=1500,
            hits=2500,
            doubles=500,
            triples=50,
            home_runs=600,
            rbis=1800,
            walks=1000,
            strikeouts=1500,
            stolen_bases=300,
            caught_stealing=50,
            batting_avg=Decimal('0.313'),
            on_base_pct=Decimal('0.400'),
            slugging_pct=Decimal('0.600'),
            ops=Decimal('1.000')
        )

    def test_career_stats_serialization(self):
        """Test that career stats are serialized correctly"""
        serializer = CareerStatsSerializer(self.stats)
        data = serializer.data

        self.assertEqual(data['games'], 2000)
        self.assertEqual(data['home_runs'], 600)
        self.assertEqual(data['batting_avg'], '0.313')
        self.assertEqual(data['ops'], '1.000')

    def test_calculated_fields_in_serialization(self):
        """Test that calculated fields are included in serialization"""
        serializer = CareerStatsSerializer(self.stats)
        data = serializer.data

        # Check calculated fields
        self.assertIn('singles', data)
        self.assertIn('total_bases', data)
        self.assertIn('extra_base_hits', data)
        self.assertIn('power_speed_number', data)
        self.assertIn('isolated_power', data)
        self.assertIn('walk_to_strikeout_ratio', data)
        self.assertIn('stolen_base_pct', data)
        self.assertIn('home_run_rate', data)
        self.assertIn('plate_appearances', data)

        # Verify values
        self.assertEqual(data['singles'], 1350)
        self.assertEqual(data['total_bases'], 4900)
        self.assertEqual(data['extra_base_hits'], 1150)


class PlayerSerializerTest(TestCase):
    """Test cases for the PlayerSerializer"""

    def setUp(self):
        """Set up test data"""
        self.player = Player.objects.create(
            name="Babe Ruth",
            position="OF",
            description="The Great Bambino"
        )
        self.stats = CareerStats.objects.create(
            player=self.player,
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

    def test_player_serialization(self):
        """Test that a player is serialized correctly"""
        serializer = PlayerSerializer(self.player)
        data = serializer.data

        self.assertEqual(data['name'], 'Babe Ruth')
        self.assertEqual(data['position'], 'OF')
        self.assertEqual(data['position_display'], 'Outfield')
        self.assertEqual(data['description'], 'The Great Bambino')

    def test_nested_career_stats(self):
        """Test that career stats are nested in player serialization"""
        serializer = PlayerSerializer(self.player)
        data = serializer.data

        self.assertIn('career_stats', data)
        self.assertEqual(data['career_stats']['home_runs'], 714)
        self.assertEqual(data['career_stats']['batting_avg'], '0.342')

    def test_player_without_description(self):
        """Test serialization of a player without a description"""
        player = Player.objects.create(
            name="No Description",
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

        serializer = PlayerSerializer(player)
        data = serializer.data

        self.assertIsNone(data['description'])


class PlayerListSerializerTest(TestCase):
    """Test cases for the PlayerListSerializer"""

    def setUp(self):
        """Set up test data"""
        self.player = Player.objects.create(
            name="Willie Mays",
            position="CF"
        )
        self.stats = CareerStats.objects.create(
            player=self.player,
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

    def test_lightweight_serialization(self):
        """Test that PlayerListSerializer returns only essential fields"""
        serializer = PlayerListSerializer(self.player)
        data = serializer.data

        # Should have these fields
        self.assertEqual(data['name'], 'Willie Mays')
        self.assertEqual(data['position'], 'CF')
        self.assertEqual(data['position_display'], 'Center Field')
        self.assertEqual(data['home_runs'], 660)
        self.assertEqual(data['batting_avg'], '0.302')
        self.assertEqual(data['ops'], '0.941')

        # Should NOT have full career_stats object
        self.assertNotIn('career_stats', data)

    def test_multiple_players_serialization(self):
        """Test serializing multiple players"""
        player2 = Player.objects.create(
            name="Hank Aaron",
            position="OF"
        )
        CareerStats.objects.create(
            player=player2,
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

        players = Player.objects.all()
        serializer = PlayerListSerializer(players, many=True)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Hank Aaron')
        self.assertEqual(data[1]['name'], 'Willie Mays')


class ComparisonSerializerTest(TestCase):
    """Test cases for the ComparisonSerializer"""

    def setUp(self):
        """Set up test data"""
        self.player1 = Player.objects.create(
            name="Player 1",
            position="1B",
            description="First player"
        )
        self.stats1 = CareerStats.objects.create(
            player=self.player1,
            games=2000,
            at_bats=8000,
            runs=1500,
            hits=2500,
            doubles=500,
            triples=50,
            home_runs=600,
            rbis=1800,
            walks=1000,
            strikeouts=1500,
            stolen_bases=300,
            caught_stealing=50,
            batting_avg=Decimal('0.313'),
            on_base_pct=Decimal('0.400'),
            slugging_pct=Decimal('0.600'),
            ops=Decimal('1.000')
        )

        self.player2 = Player.objects.create(
            name="Player 2",
            position="OF",
            description="Second player"
        )
        self.stats2 = CareerStats.objects.create(
            player=self.player2,
            games=2500,
            at_bats=9000,
            runs=1600,
            hits=2700,
            doubles=550,
            triples=60,
            home_runs=700,
            rbis=2000,
            walks=1100,
            strikeouts=1600,
            stolen_bases=250,
            caught_stealing=60,
            batting_avg=Decimal('0.300'),
            on_base_pct=Decimal('0.380'),
            slugging_pct=Decimal('0.580'),
            ops=Decimal('0.960')
        )

    def test_comparison_serialization(self):
        """Test that comparison data is serialized correctly"""
        comparison_data = {
            'home_runs': {
                'player1': 600,
                'player2': 700,
                'difference': -100
            }
        }

        data = {
            'player1': self.player1,
            'player2': self.player2,
            'comparison': comparison_data
        }

        serializer = ComparisonSerializer(data)
        result = serializer.data

        self.assertIn('player1', result)
        self.assertIn('player2', result)
        self.assertIn('comparison', result)
        self.assertEqual(result['player1']['name'], 'Player 1')
        self.assertEqual(result['player2']['name'], 'Player 2')
        self.assertEqual(result['comparison']['home_runs']['difference'], -100)


class LeaderboardSerializerTest(TestCase):
    """Test cases for the LeaderboardSerializer"""

    def setUp(self):
        """Set up test data"""
        self.players = []
        for i in range(3):
            player = Player.objects.create(
                name=f"Player {i+1}",
                position="SS"
            )
            CareerStats.objects.create(
                player=player,
                games=1000 + (i * 100),
                at_bats=4000 + (i * 400),
                runs=500 + (i * 50),
                hits=1200 + (i * 120),
                doubles=200 + (i * 20),
                triples=50 + (i * 5),
                home_runs=100 + (i * 100),
                rbis=500 + (i * 50),
                walks=400 + (i * 40),
                strikeouts=800 + (i * 80),
                stolen_bases=100 + (i * 10),
                caught_stealing=20 + (i * 2),
                batting_avg=Decimal('0.300'),
                on_base_pct=Decimal('0.350'),
                slugging_pct=Decimal('0.450'),
                ops=Decimal('0.800')
            )
            self.players.append(player)

    def test_leaderboard_serialization(self):
        """Test that leaderboard data is serialized correctly"""
        data = {
            'stat_name': 'home_runs',
            'leaders': Player.objects.all()
        }

        serializer = LeaderboardSerializer(data)
        result = serializer.data

        self.assertEqual(result['stat_name'], 'home_runs')
        self.assertIn('leaders', result)
        self.assertEqual(len(result['leaders']), 3)
        # Leaders should be serialized with PlayerListSerializer
        self.assertIn('name', result['leaders'][0])
        self.assertIn('home_runs', result['leaders'][0])
