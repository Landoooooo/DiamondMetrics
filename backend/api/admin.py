from django.contrib import admin
from .models import Player, CareerStats


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'created_at')
    list_filter = ('position',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(CareerStats)
class CareerStatsAdmin(admin.ModelAdmin):
    list_display = (
        'player',
        'games',
        'at_bats',
        'hits',
        'home_runs',
        'batting_avg',
        'ops'
    )
    list_filter = ('player__position',)
    search_fields = ('player__name',)
    ordering = ('-home_runs',)
    readonly_fields = (
        'singles',
        'total_bases',
        'extra_base_hits',
        'power_speed_number',
        'isolated_power',
        'walk_to_strikeout_ratio',
        'stolen_base_pct',
        'home_run_rate'
    )

    fieldsets = (
        ('Player', {
            'fields': ('player',)
        }),
        ('Basic Stats', {
            'fields': ('games', 'at_bats', 'runs', 'hits')
        }),
        ('Hit Types', {
            'fields': ('doubles', 'triples', 'home_runs')
        }),
        ('Advanced Stats', {
            'fields': ('rbis', 'walks', 'strikeouts')
        }),
        ('Base Running', {
            'fields': ('stolen_bases', 'caught_stealing')
        }),
        ('Percentages', {
            'fields': ('batting_avg', 'on_base_pct', 'slugging_pct', 'ops')
        }),
        ('Calculated Metrics', {
            'fields': (
                'singles',
                'total_bases',
                'extra_base_hits',
                'power_speed_number',
                'isolated_power',
                'walk_to_strikeout_ratio',
                'stolen_base_pct',
                'home_run_rate'
            ),
            'classes': ('collapse',)
        }),
    )
