from rest_framework import serializers
from .models import Player, CareerStats


class CareerStatsSerializer(serializers.ModelSerializer):
    """Serializer for career statistics with calculated fields"""
    # Calculated fields
    singles = serializers.ReadOnlyField()
    total_bases = serializers.ReadOnlyField()
    extra_base_hits = serializers.ReadOnlyField()
    power_speed_number = serializers.ReadOnlyField()
    isolated_power = serializers.ReadOnlyField()
    walk_to_strikeout_ratio = serializers.ReadOnlyField()
    stolen_base_pct = serializers.ReadOnlyField()
    home_run_rate = serializers.ReadOnlyField()
    plate_appearances = serializers.ReadOnlyField()
    hits_per_game = serializers.ReadOnlyField()

    class Meta:
        model = CareerStats
        fields = [
            'id',
            # Basic stats
            'games', 'at_bats', 'runs', 'hits',
            # Hit types
            'doubles', 'triples', 'home_runs',
            # Advanced stats
            'rbis', 'walks', 'strikeouts',
            # Base running
            'stolen_bases', 'caught_stealing',
            # Percentages
            'batting_avg', 'on_base_pct', 'slugging_pct', 'ops',
            # Calculated fields
            'singles', 'total_bases', 'extra_base_hits',
            'power_speed_number', 'isolated_power',
            'walk_to_strikeout_ratio', 'stolen_base_pct',
            'home_run_rate', 'plate_appearances', 'hits_per_game',
            # Timestamps
            'created_at', 'updated_at'
        ]


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for player with nested career stats"""
    career_stats = CareerStatsSerializer(read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)

    class Meta:
        model = Player
        fields = [
            'id',
            'name',
            'position',
            'position_display',
            'description',
            'career_stats',
            'created_at',
            'updated_at'
        ]


class PlayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for player lists"""
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    home_runs = serializers.IntegerField(source='career_stats.home_runs', read_only=True)
    batting_avg = serializers.DecimalField(
        source='career_stats.batting_avg',
        max_digits=5,
        decimal_places=3,
        read_only=True
    )
    ops = serializers.DecimalField(
        source='career_stats.ops',
        max_digits=5,
        decimal_places=3,
        read_only=True
    )
    hits_per_game = serializers.DecimalField(
        source='career_stats.hits_per_game',
        max_digits=5,
        decimal_places=3,
        read_only=True
    )

    class Meta:
        model = Player
        fields = [
            'id',
            'name',
            'position',
            'position_display',
            'home_runs',
            'batting_avg',
            'ops',
            'hits_per_game',
        ]


class ComparisonSerializer(serializers.Serializer):
    """Serializer for player comparison"""
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    comparison = serializers.DictField()


class LeaderboardSerializer(serializers.Serializer):
    """Serializer for leaderboard data"""
    stat_name = serializers.CharField()
    leaders = PlayerListSerializer(many=True)
