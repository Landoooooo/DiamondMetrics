from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    """Baseball player model"""
    POSITION_CHOICES = [
        ('P', 'Pitcher'),
        ('C', 'Catcher'),
        ('1B', 'First Base'),
        ('2B', 'Second Base'),
        ('3B', 'Third Base'),
        ('SS', 'Shortstop'),
        ('LF', 'Left Field'),
        ('CF', 'Center Field'),
        ('RF', 'Right Field'),
        ('OF', 'Outfield'),
        ('DH', 'Designated Hitter'),
    ]

    name = models.CharField(max_length=100, unique=True)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"{self.name} ({self.position})"


class CareerStats(models.Model):
    """Career statistics for a player"""
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name='career_stats'
    )

    # Basic Stats
    games = models.IntegerField(validators=[MinValueValidator(0)])
    at_bats = models.IntegerField(validators=[MinValueValidator(0)])
    runs = models.IntegerField(validators=[MinValueValidator(0)])
    hits = models.IntegerField(validators=[MinValueValidator(0)])

    # Hit Types
    doubles = models.IntegerField(validators=[MinValueValidator(0)])
    triples = models.IntegerField(validators=[MinValueValidator(0)])
    home_runs = models.IntegerField(validators=[MinValueValidator(0)])

    # Advanced Stats
    rbis = models.IntegerField(validators=[MinValueValidator(0)], help_text="Runs Batted In")
    walks = models.IntegerField(validators=[MinValueValidator(0)])
    strikeouts = models.IntegerField(validators=[MinValueValidator(0)])

    # Base Running
    stolen_bases = models.IntegerField(validators=[MinValueValidator(0)])
    caught_stealing = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)

    # Calculated Percentages
    batting_avg = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Batting Average"
    )
    on_base_pct = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="On-Base Percentage"
    )
    slugging_pct = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text="Slugging Percentage"
    )
    ops = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text="On-Base Plus Slugging"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Career Stats"
        verbose_name_plural = "Career Stats"
        indexes = [
            models.Index(fields=['-home_runs']),
            models.Index(fields=['-batting_avg']),
            models.Index(fields=['-ops']),
        ]

    def __str__(self):
        return f"{self.player.name} Career Stats"

    @property
    def singles(self):
        """Calculate singles from hits"""
        return self.hits - (self.doubles + self.triples + self.home_runs)

    @property
    def total_bases(self):
        """Calculate total bases"""
        return (self.singles + (self.doubles * 2) +
                (self.triples * 3) + (self.home_runs * 4))

    @property
    def extra_base_hits(self):
        """Calculate extra base hits"""
        return self.doubles + self.triples + self.home_runs

    @property
    def power_speed_number(self):
        """
        Calculate Power-Speed Number
        PSN = (2 * HR * SB) / (HR + SB)
        """
        if self.home_runs + self.stolen_bases == 0:
            return 0
        return round((2 * self.home_runs * self.stolen_bases) /
                     (self.home_runs + self.stolen_bases), 2)

    @property
    def isolated_power(self):
        """
        Calculate Isolated Power (ISO)
        ISO = SLG - AVG
        """
        return round(float(self.slugging_pct - self.batting_avg), 3)

    @property
    def walk_to_strikeout_ratio(self):
        """Calculate BB/K ratio"""
        if self.strikeouts == 0:
            return float(self.walks)
        return round(self.walks / self.strikeouts, 3)

    @property
    def stolen_base_pct(self):
        """Calculate stolen base success percentage"""
        total_attempts = self.stolen_bases + (self.caught_stealing or 0)
        if total_attempts == 0:
            return 0
        return round((self.stolen_bases / total_attempts) * 100, 1)

    @property
    def home_run_rate(self):
        """Home runs per at-bat"""
        if self.at_bats == 0:
            return 0
        return round((self.home_runs / self.at_bats) * 100, 2)
    
    @property
    def hits_per_game(self):
        """Average of hits per game"""
        if not self.hits > 0:
            return 0
        
        return self.hits / self.games


    @property
    def plate_appearances(self):
        """Estimate plate appearances (simplified)"""
        return self.at_bats + self.walks
