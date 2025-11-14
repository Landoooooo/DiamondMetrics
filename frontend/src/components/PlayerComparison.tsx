import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

interface PlayerComparisonProps {
  player1Id: number;
  player2Id: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface CareerStats {
  games: number;
  at_bats: number;
  runs: number;
  hits: number;
  doubles: number;
  triples: number;
  home_runs: number;
  rbis: number;
  walks: number;
  strikeouts: number;
  stolen_bases: number;
  batting_avg: string;
  on_base_pct: string;
  slugging_pct: string;
  ops: string;
  isolated_power: string;
  walk_to_strikeout_ratio: string;
  stolen_base_pct: string;
  home_run_rate: string;
  power_speed_number: string;
  total_bases: number;
}

interface PlayerData {
  id: number;
  name: string;
  position_display: string;
  career_stats: CareerStats;
}

interface ComparisonData {
  player1: PlayerData;
  player2: PlayerData;
  comparison: {
    home_runs: { player1: number; player2: number; difference: number };
    batting_avg: { player1: number; player2: number; difference: number };
    ops: { player1: number; player2: number; difference: number };
    stolen_bases: { player1: number; player2: number; difference: number };
    power_speed_number: { player1: number; player2: number; difference: number };
    walks_vs_strikeouts: { player1: number; player2: number; difference: number };
  };
}

export function PlayerComparison({ player1Id, player2Id, open, onOpenChange }: PlayerComparisonProps) {
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (open && player1Id && player2Id) {
      setLoading(true);
      fetch(`/api/players/compare/?player1=${player1Id}&player2=${player2Id}`)
        .then(response => response.json())
        .then(comparisonData => {
          setData(comparisonData);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching comparison:', error);
          setLoading(false);
        });
    }
  }, [open, player1Id, player2Id]);

  if (loading || !data) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-6xl">
          <div className="py-8 text-center text-muted-foreground">
            Loading comparison...
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  const getWinner = (diff: number) => {
    if (diff > 0) return 'player1';
    if (diff < 0) return 'player2';
    return 'tie';
  };

  const formatDiff = (diff: number, decimals: number = 0) => {
    const sign = diff > 0 ? '+' : '';
    return decimals > 0 ? `${sign}${diff.toFixed(decimals)}` : `${sign}${diff}`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl bg-gradient-to-b from-white to-gray-50">
        <div className="flex gap-4">
          {/* Player 1 Card */}
          <div className="flex-1 max-w-md">
            <div className="bg-dodger-blue text-white p-4 rounded-t-lg">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold text-center text-white">
                  {data.player1.name}
                </DialogTitle>
                <div className="text-center text-dodger-lightblue text-sm mt-1">
                  {data.player1.position_display}
                </div>
              </DialogHeader>
            </div>

            <div className="bg-white p-4 rounded-b-lg border-x border-b">
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player1.career_stats.batting_avg}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">AVG</div>
                </div>
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player1.career_stats.home_runs}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">HR</div>
                </div>
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player1.career_stats.ops}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">OPS</div>
                </div>
              </div>

              <div className="space-y-1 text-xs">
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">SB:</span>
                  <span className="font-semibold">{data.player1.career_stats.stolen_bases}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">RBI:</span>
                  <span className="font-semibold">{data.player1.career_stats.rbis}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">Runs:</span>
                  <span className="font-semibold">{data.player1.career_stats.runs}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Comparison Column */}
          <div className="w-72 flex flex-col justify-center">
            <div className="bg-dodger-blue text-white p-3 rounded-t-lg">
              <h3 className="text-lg font-bold text-center">Head to Head</h3>
            </div>

            <div className="bg-white p-4 rounded-b-lg border-x border-b space-y-2">
              <div className="bg-gray-50 border rounded p-2">
                <div className="text-xs font-semibold text-center text-dodger-blue mb-1">Home Runs</div>
                <div className="text-center">
                  <span className={`text-xl font-bold ${getWinner(data.comparison.home_runs.difference) === 'player1' ? 'text-green-600' : getWinner(data.comparison.home_runs.difference) === 'player2' ? 'text-red-600' : 'text-gray-600'}`}>
                    {formatDiff(data.comparison.home_runs.difference)}
                  </span>
                </div>
              </div>

              <div className="bg-gray-50 border rounded p-2">
                <div className="text-xs font-semibold text-center text-dodger-blue mb-1">Batting Avg</div>
                <div className="text-center">
                  <span className={`text-xl font-bold ${getWinner(data.comparison.batting_avg.difference) === 'player1' ? 'text-green-600' : getWinner(data.comparison.batting_avg.difference) === 'player2' ? 'text-red-600' : 'text-gray-600'}`}>
                    {formatDiff(data.comparison.batting_avg.difference, 3)}
                  </span>
                </div>
              </div>

              <div className="bg-gray-50 border rounded p-2">
                <div className="text-xs font-semibold text-center text-dodger-blue mb-1">OPS</div>
                <div className="text-center">
                  <span className={`text-xl font-bold ${getWinner(data.comparison.ops.difference) === 'player1' ? 'text-green-600' : getWinner(data.comparison.ops.difference) === 'player2' ? 'text-red-600' : 'text-gray-600'}`}>
                    {formatDiff(data.comparison.ops.difference, 3)}
                  </span>
                </div>
              </div>

              <div className="bg-gray-50 border rounded p-2">
                <div className="text-xs font-semibold text-center text-dodger-blue mb-1">Stolen Bases</div>
                <div className="text-center">
                  <span className={`text-xl font-bold ${getWinner(data.comparison.stolen_bases.difference) === 'player1' ? 'text-green-600' : getWinner(data.comparison.stolen_bases.difference) === 'player2' ? 'text-red-600' : 'text-gray-600'}`}>
                    {formatDiff(data.comparison.stolen_bases.difference)}
                  </span>
                </div>
              </div>

              <div className="bg-gray-50 border rounded p-2">
                <div className="text-xs font-semibold text-center text-dodger-blue mb-1">BB/K Ratio</div>
                <div className="text-center">
                  <span className={`text-xl font-bold ${getWinner(data.comparison.walks_vs_strikeouts.difference) === 'player1' ? 'text-green-600' : getWinner(data.comparison.walks_vs_strikeouts.difference) === 'player2' ? 'text-red-600' : 'text-gray-600'}`}>
                    {formatDiff(data.comparison.walks_vs_strikeouts.difference, 2)}
                  </span>
                </div>
              </div>

              <div className="text-center text-[10px] text-muted-foreground mt-3 pt-2 border-t">
                <span className="text-green-600">Green</span> = Left player ahead
              </div>
            </div>
          </div>

          {/* Player 2 Card */}
          <div className="flex-1 max-w-md">
            <div className="bg-dodger-blue text-white p-4 rounded-t-lg">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold text-center text-white">
                  {data.player2.name}
                </DialogTitle>
                <div className="text-center text-dodger-lightblue text-sm mt-1">
                  {data.player2.position_display}
                </div>
              </DialogHeader>
            </div>

            <div className="bg-white p-4 rounded-b-lg border-x border-b">
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player2.career_stats.batting_avg}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">AVG</div>
                </div>
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player2.career_stats.home_runs}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">HR</div>
                </div>
                <div className="text-center p-2 border-2 border-dodger-blue rounded-lg">
                  <div className="text-2xl font-bold text-dodger-blue">
                    {data.player2.career_stats.ops}
                  </div>
                  <div className="text-[10px] text-muted-foreground uppercase">OPS</div>
                </div>
              </div>

              <div className="space-y-1 text-xs">
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">SB:</span>
                  <span className="font-semibold">{data.player2.career_stats.stolen_bases}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">RBI:</span>
                  <span className="font-semibold">{data.player2.career_stats.rbis}</span>
                </div>
                <div className="flex justify-between py-0.5">
                  <span className="text-muted-foreground">Runs:</span>
                  <span className="font-semibold">{data.player2.career_stats.runs}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
