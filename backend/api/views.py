from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Count, Q
from .models import Player, CareerStats
from .serializers import (
    PlayerSerializer,
    PlayerListSerializer,
    CareerStatsSerializer,
    ComparisonSerializer
)


class PlayerPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100


@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({'status': 'ok', 'message': 'Baseball API is running!'})


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing players

    Endpoints:
    - /players/ - List all players
    - /players/{id}/ - Get specific player
    - /players/leaderboard/ - Get statistical leaderboards
    - /players/compare/ - Compare two players
    - /players/stats_summary/ - Get aggregate statistics
    """
    queryset = Player.objects.all().select_related('career_stats')
    pagination_class = PlayerPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['position']
    search_fields = ['name']
    ordering_fields = [
        'name',
        'career_stats__home_runs',
        'career_stats__batting_avg',
        'career_stats__ops',
        'career_stats__hits',
        'career_stats__runs',
        'career_stats__rbis'
    ]
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return PlayerListSerializer
        return PlayerSerializer

    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """
        Update career statistics for a player

        Only updates base stats, calculated fields are auto-updated
        """
        from decimal import Decimal

        player = self.get_object()
        career_stats = player.career_stats

        # Update only the base stat fields
        integer_fields = [
            'games', 'at_bats', 'runs', 'hits', 'doubles', 'triples',
            'home_runs', 'rbis', 'walks', 'strikeouts', 'stolen_bases',
            'caught_stealing'
        ]

        decimal_fields = [
            'batting_avg', 'on_base_pct', 'slugging_pct', 'ops'
        ]

        # Update integer fields
        for field in integer_fields:
            if field in request.data:
                setattr(career_stats, field, int(request.data[field]))

        # Update decimal fields
        for field in decimal_fields:
            if field in request.data:
                setattr(career_stats, field, Decimal(str(request.data[field])))

        career_stats.save()

        # Return updated player data
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """
        Get leaderboards for various statistics

        Query params:
        - stat: home_runs, batting_avg, ops, hits, stolen_bases, etc.
        - limit: number of players (default: 10)
        """
        stat = request.query_params.get('stat', 'home_runs')
        limit = int(request.query_params.get('limit', 10))

        # Map user-friendly stat names to model fields
        stat_field_map = {
            'home_runs': 'career_stats__home_runs',
            'batting_avg': 'career_stats__batting_avg',
            'ops': 'career_stats__ops',
            'hits': 'career_stats__hits',
            'runs': 'career_stats__runs',
            'rbis': 'career_stats__rbis',
            'stolen_bases': 'career_stats__stolen_bases',
            'walks': 'career_stats__walks',
            'strikeouts': 'career_stats__strikeouts',
            'doubles': 'career_stats__doubles',
            'triples': 'career_stats__triples',
            'slugging': 'career_stats__slugging_pct',
            'obp': 'career_stats__on_base_pct',
        }

        order_field = stat_field_map.get(stat, 'career_stats__home_runs')

        leaders = self.queryset.order_by(f'-{order_field}')[:limit]
        serializer = PlayerListSerializer(leaders, many=True)

        return Response({
            'stat': stat,
            'limit': limit,
            'leaders': serializer.data
        })

    @action(detail=False, methods=['get'])
    def compare(self, request):
        """
        Compare two players

        Query params:
        - player1: player ID
        - player2: player ID
        """
        player1_id = request.query_params.get('player1')
        player2_id = request.query_params.get('player2')

        if not player1_id or not player2_id:
            return Response(
                {'error': 'Both player1 and player2 IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            player1 = Player.objects.select_related('career_stats').get(id=player1_id)
            player2 = Player.objects.select_related('career_stats').get(id=player2_id)
        except Player.DoesNotExist:
            return Response(
                {'error': 'One or both players not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate comparison metrics
        stats1 = player1.career_stats
        stats2 = player2.career_stats

        comparison = {
            'home_runs': {
                'player1': stats1.home_runs,
                'player2': stats2.home_runs,
                'difference': stats1.home_runs - stats2.home_runs
            },
            'batting_avg': {
                'player1': float(stats1.batting_avg),
                'player2': float(stats2.batting_avg),
                'difference': float(stats1.batting_avg - stats2.batting_avg)
            },
            'ops': {
                'player1': float(stats1.ops),
                'player2': float(stats2.ops),
                'difference': float(stats1.ops - stats2.ops)
            },
            'stolen_bases': {
                'player1': stats1.stolen_bases,
                'player2': stats2.stolen_bases,
                'difference': stats1.stolen_bases - stats2.stolen_bases
            },
            'power_speed_number': {
                'player1': stats1.power_speed_number,
                'player2': stats2.power_speed_number,
                'difference': stats1.power_speed_number - stats2.power_speed_number
            },
            'walks_vs_strikeouts': {
                'player1': stats1.walk_to_strikeout_ratio,
                'player2': stats2.walk_to_strikeout_ratio,
                'difference': stats1.walk_to_strikeout_ratio - stats2.walk_to_strikeout_ratio
            }
        }

        return Response({
            'player1': PlayerSerializer(player1).data,
            'player2': PlayerSerializer(player2).data,
            'comparison': comparison
        })

    @action(detail=False, methods=['get'])
    def stats_summary(self, request):
        """
        Get aggregate statistics across all players or filtered by position

        Query params:
        - position: filter by position (optional)
        """
        position = request.query_params.get('position')

        queryset = CareerStats.objects.all()
        if position:
            queryset = queryset.filter(player__position=position)

        summary = queryset.aggregate(
            total_players=Count('id'),
            avg_home_runs=Avg('home_runs'),
            max_home_runs=Max('home_runs'),
            min_home_runs=Min('home_runs'),
            avg_batting_avg=Avg('batting_avg'),
            max_batting_avg=Max('batting_avg'),
            avg_ops=Avg('ops'),
            max_ops=Max('ops'),
            avg_stolen_bases=Avg('stolen_bases'),
            max_stolen_bases=Max('stolen_bases'),
        )

        # Get players with max stats
        max_hr_player = queryset.order_by('-home_runs').first()
        max_avg_player = queryset.order_by('-batting_avg').first()
        max_ops_player = queryset.order_by('-ops').first()

        return Response({
            'position': position or 'all',
            'summary': {
                'total_players': summary['total_players'],
                'home_runs': {
                    'average': round(summary['avg_home_runs'], 2) if summary['avg_home_runs'] else 0,
                    'max': summary['max_home_runs'],
                    'min': summary['min_home_runs'],
                    'leader': max_hr_player.player.name if max_hr_player else None
                },
                'batting_average': {
                    'average': round(float(summary['avg_batting_avg']), 3) if summary['avg_batting_avg'] else 0,
                    'max': float(summary['max_batting_avg']) if summary['max_batting_avg'] else 0,
                    'leader': max_avg_player.player.name if max_avg_player else None
                },
                'ops': {
                    'average': round(float(summary['avg_ops']), 3) if summary['avg_ops'] else 0,
                    'max': float(summary['max_ops']) if summary['max_ops'] else 0,
                    'leader': max_ops_player.player.name if max_ops_player else None
                },
                'stolen_bases': {
                    'average': round(summary['avg_stolen_bases'], 2) if summary['avg_stolen_bases'] else 0,
                    'max': summary['max_stolen_bases'],
                }
            }
        })

    @action(detail=False, methods=['get'])
    def unique_stats(self, request):
        """
        Get unique statistical representations and analysis

        Returns players with unique combinations of power/speed,
        efficiency metrics, and interesting statistical profiles
        """
        players = self.queryset.all()

        # Calculate unique metrics for all players
        unique_profiles = []

        for player in players[:20]:  # Limit for performance
            stats = player.career_stats

            profile = {
                'name': player.name,
                'position': player.get_position_display(),
                'metrics': {
                    'power_speed_number': stats.power_speed_number,
                    'isolated_power': stats.isolated_power,
                    'bb_k_ratio': stats.walk_to_strikeout_ratio,
                    'stolen_base_success': stats.stolen_base_pct,
                    'home_run_rate': stats.home_run_rate,
                    'total_bases': stats.total_bases,
                    'extra_base_hits': stats.extra_base_hits,
                }
            }

            # Add special classifications
            classifications = []
            if stats.power_speed_number > 200:
                classifications.append('Elite Power-Speed')
            if stats.isolated_power > 0.250:
                classifications.append('Power Hitter')
            if stats.walk_to_strikeout_ratio > 1.0:
                classifications.append('Disciplined Hitter')
            if stats.stolen_base_pct > 80:
                classifications.append('Efficient Base Stealer')
            if stats.batting_avg > 0.300 and stats.home_runs > 400:
                classifications.append('Elite All-Around Hitter')

            profile['classifications'] = classifications
            unique_profiles.append(profile)

        return Response({
            'unique_statistical_profiles': unique_profiles,
            'description': 'Advanced metrics and classifications for players'
        })

    @action(detail=False, methods=['get'])
    def hall_of_fame_candidates(self, request):
        """
        Identify potential Hall of Fame candidates based on statistical thresholds

        Criteria:
        - 500+ home runs OR
        - .300+ career average with 3000+ hits OR
        - OPS > 0.900 with 400+ home runs
        """
        candidates = []

        # 500 HR club
        hr_club = self.queryset.filter(career_stats__home_runs__gte=500)

        # 3000 hit club with .300 average
        hit_club = self.queryset.filter(
            career_stats__hits__gte=3000,
            career_stats__batting_avg__gte=0.300
        )

        # Elite OPS with power
        ops_club = self.queryset.filter(
            career_stats__ops__gte=0.900,
            career_stats__home_runs__gte=400
        )

        return Response({
            '500_home_run_club': {
                'count': hr_club.count(),
                'players': PlayerListSerializer(hr_club, many=True).data
            },
            '3000_hit_300_avg_club': {
                'count': hit_club.count(),
                'players': PlayerListSerializer(hit_club, many=True).data
            },
            'elite_ops_power_club': {
                'count': ops_club.count(),
                'players': PlayerListSerializer(ops_club, many=True).data
            }
        })
