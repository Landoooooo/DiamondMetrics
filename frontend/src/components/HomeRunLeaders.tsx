import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { PlayerCard } from './PlayerCard';

interface Player {
  id: number;
  name: string;
  position_display: string;
  home_runs: number;
}

interface HomeRunLeadersProps {
  refreshKey?: number;
  onPlayerUpdated?: () => void;
}

export function HomeRunLeaders({ refreshKey, onPlayerUpdated }: HomeRunLeadersProps) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<{ id: number; name: string } | null>(null);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  const handlePlayerClick = (player: Player) => {
    setSelectedPlayer({ id: player.id, name: player.name });
    setModalOpen(true);
  };

  useEffect(() => {
    // Only show loading on initial load, use refreshing for updates
    if (players.length === 0) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    fetch('/api/players/leaderboard/?stat=home_runs&limit=5')
      .then(response => response.json())
      .then(data => {
        setPlayers(data.leaders || []);
        setLoading(false);
        setRefreshing(false);
      })
      .catch(error => {
        console.error('Error fetching home run leaders:', error);
        setError('Failed to load home run leaders');
        setLoading(false);
        setRefreshing(false);
      });
  }, [refreshKey]);

  if (loading) {
    return (
      <Card className="mb-8">
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading home run leaders...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-8">
        <CardContent className="py-8">
          <p className="text-center text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle className="text-dodger-blue">Home Run Leaders</CardTitle>
        <CardDescription>Top 5 all-time career home run leaders</CardDescription>
      </CardHeader>
      <CardContent>
        {players.length > 0 ? (
          <div className={`grid grid-cols-1 md:grid-cols-5 gap-4 transition-opacity duration-200 ${refreshing ? 'opacity-90' : ''}`}>
            {players.map((player, index) => (
              <div
                key={player.id}
                className="flex flex-col items-center p-4 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                onClick={() => handlePlayerClick(player)}
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-lg mb-2">
                  {index + 1}
                </div>
                <h3 className="font-semibold text-center">{player.name}</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  {player.position_display}
                </p>
                <div className="text-3xl font-bold text-dodger-blue">
                  {player.home_runs}
                </div>
                <div className="text-xs text-muted-foreground">
                  Home Runs
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No players found</p>
        )}
      </CardContent>
      <PlayerCard
        playerId={selectedPlayer?.id || null}
        playerName={selectedPlayer?.name || ''}
        open={modalOpen}
        onOpenChange={setModalOpen}
        onPlayerUpdated={onPlayerUpdated}
      />
    </Card>
  );
}
