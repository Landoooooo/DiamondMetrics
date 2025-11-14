from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from api.models import Player, CareerStats


class PlayerModelTest(TestCase):
    """Test cases for the Player model"""

    def setUp(self):
        """Set up test data"""
        self.player = Player.objects.create(
            name="Test Player",
            position="CF",
            description="A legendary center fielder with incredible speed and power."
        )

    def test_player_creation(self):
        """Test that a player can be created successfully"""
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.position, "CF")
        self.assertEqual(self.player.description, "A legendary center fielder with incredible speed and power.")
        self.assertIsNotNone(self.player.created_at)
        self.assertIsNotNone(self.player.updated_at)

    def test_player_str_representation(self):
        """Test the string representation of a player"""
        expected = "Test Player (CF)"
        self.assertEqual(str(self.player), expected)

    def test_player_position_display(self):
        """Test that position display returns the full position name"""
        self.assertEqual(self.player.get_position_display(), "Center Field")

    def test_player_unique_name(self):
        """Test that player names must be unique"""
        with self.assertRaises(Exception):
            Player.objects.create(
                name="Test Player",
                position="1B"
            )

    def test_player_without_description(self):
        """Test that a player can be created without a description"""
        player = Player.objects.create(
            name="No Description Player",
            position="SS"
        )
        self.assertIsNone(player.description)


class CareerStatsModelTest(TestCase):
    """Test cases for the CareerStats model"""

    def setUp(self):
        """Set up test data"""
        self.player = Player.objects.create(
            name="Stats Test Player",
            position="RF"
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

    def test_career_stats_creation(self):
        """Test that career stats can be created successfully"""
        self.assertEqual(self.stats.player, self.player)
        self.assertEqual(self.stats.games, 2000)
        self.assertEqual(self.stats.home_runs, 600)
        self.assertEqual(self.stats.batting_avg, Decimal('0.313'))

    def test_career_stats_str_representation(self):
        """Test the string representation of career stats"""
        expected = "Stats Test Player Career Stats"
        self.assertEqual(str(self.stats), expected)

    def test_singles_calculation(self):
        """Test that singles are calculated correctly"""
        expected_singles = self.stats.hits - (self.stats.doubles + self.stats.triples + self.stats.home_runs)
        self.assertEqual(self.stats.singles, expected_singles)
        self.assertEqual(self.stats.singles, 1350)

    def test_total_bases_calculation(self):
        """Test that total bases are calculated correctly"""
        expected_tb = (self.stats.singles +
                      (self.stats.doubles * 2) +
                      (self.stats.triples * 3) +
                      (self.stats.home_runs * 4))
        self.assertEqual(self.stats.total_bases, expected_tb)
        self.assertEqual(self.stats.total_bases, 4900)

    def test_extra_base_hits_calculation(self):
        """Test that extra base hits are calculated correctly"""
        expected_xbh = self.stats.doubles + self.stats.triples + self.stats.home_runs
        self.assertEqual(self.stats.extra_base_hits, expected_xbh)
        self.assertEqual(self.stats.extra_base_hits, 1150)

    def test_power_speed_number_calculation(self):
        """Test that power-speed number is calculated correctly"""
        # PSN = (2 * HR * SB) / (HR + SB)
        # PSN = (2 * 600 * 300) / (600 + 300) = 360000 / 900 = 400
        self.assertEqual(self.stats.power_speed_number, 400.0)

    def test_power_speed_number_with_zero_values(self):
        """Test power-speed number when HR and SB are both zero"""
        stats = CareerStats.objects.create(
            player=Player.objects.create(name="No Power Speed", position="P"),
            games=100, at_bats=200, runs=10, hits=50,
            doubles=5, triples=0, home_runs=0,
            rbis=10, walks=20, strikeouts=80,
            stolen_bases=0, caught_stealing=0,
            batting_avg=Decimal('0.250'),
            on_base_pct=Decimal('0.300'),
            slugging_pct=Decimal('0.275'),
            ops=Decimal('0.575')
        )
        self.assertEqual(stats.power_speed_number, 0)

    def test_isolated_power_calculation(self):
        """Test that isolated power (ISO) is calculated correctly"""
        # ISO = SLG - AVG = 0.600 - 0.313 = 0.287
        self.assertEqual(self.stats.isolated_power, 0.287)

    def test_walk_to_strikeout_ratio(self):
        """Test that BB/K ratio is calculated correctly"""
        # BB/K = 1000 / 1500 = 0.667
        self.assertEqual(self.stats.walk_to_strikeout_ratio, 0.667)

    def test_walk_to_strikeout_ratio_no_strikeouts(self):
        """Test BB/K ratio when strikeouts are zero"""
        stats = CareerStats.objects.create(
            player=Player.objects.create(name="No Strikeouts", position="2B"),
            games=100, at_bats=400, runs=50, hits=120,
            doubles=20, triples=5, home_runs=10,
            rbis=50, walks=40, strikeouts=0,
            stolen_bases=10, caught_stealing=2,
            batting_avg=Decimal('0.300'),
            on_base_pct=Decimal('0.350'),
            slugging_pct=Decimal('0.450'),
            ops=Decimal('0.800')
        )
        self.assertEqual(stats.walk_to_strikeout_ratio, 40.0)

    def test_stolen_base_percentage(self):
        """Test that stolen base percentage is calculated correctly"""
        # SB% = (300 / (300 + 50)) * 100 = 85.7%
        self.assertEqual(self.stats.stolen_base_pct, 85.7)

    def test_stolen_base_percentage_no_attempts(self):
        """Test SB% when there are no steal attempts"""
        stats = CareerStats.objects.create(
            player=Player.objects.create(name="No Steals", position="1B"),
            games=100, at_bats=400, runs=50, hits=120,
            doubles=30, triples=0, home_runs=25,
            rbis=80, walks=40, strikeouts=100,
            stolen_bases=0, caught_stealing=0,
            batting_avg=Decimal('0.300'),
            on_base_pct=Decimal('0.350'),
            slugging_pct=Decimal('0.550'),
            ops=Decimal('0.900')
        )
        self.assertEqual(stats.stolen_base_pct, 0)

    def test_home_run_rate(self):
        """Test that home run rate is calculated correctly"""
        # HR Rate = (600 / 8000) * 100 = 7.5%
        self.assertEqual(self.stats.home_run_rate, 7.5)

    def test_home_run_rate_no_at_bats(self):
        """Test HR rate when at_bats are zero"""
        stats = CareerStats.objects.create(
            player=Player.objects.create(name="No At Bats", position="P"),
            games=10, at_bats=0, runs=0, hits=0,
            doubles=0, triples=0, home_runs=0,
            rbis=0, walks=5, strikeouts=0,
            stolen_bases=0, caught_stealing=0,
            batting_avg=Decimal('0.000'),
            on_base_pct=Decimal('1.000'),
            slugging_pct=Decimal('0.000'),
            ops=Decimal('1.000')
        )
        self.assertEqual(stats.home_run_rate, 0)

    def test_plate_appearances(self):
        """Test that plate appearances are calculated correctly"""
        # PA = AB + BB = 8000 + 1000 = 9000
        self.assertEqual(self.stats.plate_appearances, 9000)

    def test_negative_values_validation(self):
        """Test that negative values are not allowed"""
        with self.assertRaises(ValidationError):
            stats = CareerStats(
                player=Player.objects.create(name="Negative Stats", position="3B"),
                games=-10,
                at_bats=100,
                runs=10,
                hits=30,
                doubles=5,
                triples=0,
                home_runs=2,
                rbis=10,
                walks=10,
                strikeouts=20,
                stolen_bases=5,
                caught_stealing=1,
                batting_avg=Decimal('0.300'),
                on_base_pct=Decimal('0.350'),
                slugging_pct=Decimal('0.400'),
                ops=Decimal('0.750')
            )
            stats.full_clean()

    def test_one_to_one_relationship(self):
        """Test that a player can only have one set of career stats"""
        with self.assertRaises(Exception):
            CareerStats.objects.create(
                player=self.player,
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
