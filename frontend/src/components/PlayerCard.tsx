import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';

interface PlayerCardProps {
  playerId: number | null;
  playerName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onPlayerUpdated?: () => void;
}

interface CareerStats {
  id: number;
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
  caught_stealing: number;
  batting_avg: string;
  on_base_pct: string;
  slugging_pct: string;
  ops: string;
  singles: number;
  total_bases: number;
  extra_base_hits: number;
  power_speed_number: string;
  isolated_power: string;
  walk_to_strikeout_ratio: string;
  stolen_base_pct: string;
  home_run_rate: string;
  plate_appearances: number;
}

interface PlayerDetail {
  id: number;
  name: string;
  position: string;
  position_display: string;
  description: string;
  career_stats: CareerStats;
}

export function PlayerCard({ playerId, playerName, open, onOpenChange, onPlayerUpdated }: PlayerCardProps) {
  const [player, setPlayer] = useState<PlayerDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [formData, setFormData] = useState<CareerStats | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    if (open && playerId) {
      setLoading(true);
      setEditMode(false);
      fetch(`/api/players/${playerId}/`)
        .then(response => response.json())
        .then(data => {
          setPlayer(data);
          setFormData(data.career_stats);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching player details:', error);
          setLoading(false);
        });
    }
  }, [open, playerId]);

  const handleEdit = () => {
    setEditMode(true);
  };

  const handleCancel = () => {
    setFormData(player?.career_stats || null);
    setEditMode(false);
  };

  const handleSave = () => {
    if (!playerId || !formData) return;

    setSaving(true);
    fetch(`/api/players/${playerId}/update_stats/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
      .then(response => response.json())
      .then(data => {
        setPlayer(data);
        setFormData(data.career_stats);
        setEditMode(false);
        setSaving(false);
        // Notify parent component to refresh data
        if (onPlayerUpdated) {
          onPlayerUpdated();
        }
      })
      .catch(error => {
        console.error('Error saving player stats:', error);
        setSaving(false);
      });
  };

  const handleInputChange = (field: keyof CareerStats, value: string | number) => {
    if (!formData) return;
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  if (loading || !player) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <div className="py-8 text-center text-muted-foreground">
            Loading player details...
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-gradient-to-b from-white to-gray-50">
        {/* Baseball Card Header */}
        <div className="bg-dodger-blue text-white p-4 -m-6 mb-3 rounded-t-lg">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold text-center text-white">
                  {player.name}
                </DialogTitle>
                <div className="text-center text-dodger-lightblue text-sm mt-1">
                  {player.position_display}
                </div>
              </DialogHeader>
            </div>
            <div className="flex gap-2">
              {!editMode ? (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={handleEdit}
                >
                  Edit
                </Button>
              ) : (
                <>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleCancel}
                    disabled={saving}
                    className="bg-white/20 hover:bg-white/30 text-white"
                  >
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Player Description */}
        {player.description && (
          <div className="bg-white/90 border border-dodger-lightblue rounded-lg p-3 mb-3 mx-1 max-h-24 overflow-y-auto">
            <p className="text-xs text-gray-700 leading-relaxed">
              {player.description}
            </p>
          </div>
        )}

        {/* Main Stats Showcase */}
        <div className="grid grid-cols-3 gap-2 mb-3 px-1">
          <div className="text-center p-2 bg-white border-2 border-dodger-blue rounded-lg shadow-sm">
            {editMode && formData ? (
              <input
                type="text"
                value={formData.batting_avg}
                onChange={(e) => handleInputChange('batting_avg', e.target.value)}
                className="w-full text-center text-2xl font-bold text-dodger-blue border rounded px-1"
              />
            ) : (
              <div className="text-2xl font-bold text-dodger-blue">
                {player.career_stats.batting_avg}
              </div>
            )}
            <div className="text-[10px] text-muted-foreground uppercase">
              AVG
            </div>
          </div>
          <div className="text-center p-2 bg-white border-2 border-dodger-blue rounded-lg shadow-sm">
            {editMode && formData ? (
              <input
                type="number"
                value={formData.home_runs}
                onChange={(e) => handleInputChange('home_runs', parseInt(e.target.value) || 0)}
                className="w-full text-center text-2xl font-bold text-dodger-blue border rounded px-1"
              />
            ) : (
              <div className="text-2xl font-bold text-dodger-blue">
                {player.career_stats.home_runs}
              </div>
            )}
            <div className="text-[10px] text-muted-foreground uppercase">
              HR
            </div>
          </div>
          <div className="text-center p-2 bg-white border-2 border-dodger-blue rounded-lg shadow-sm">
            {editMode && formData ? (
              <input
                type="text"
                value={formData.ops}
                onChange={(e) => handleInputChange('ops', e.target.value)}
                className="w-full text-center text-2xl font-bold text-dodger-blue border rounded px-1"
              />
            ) : (
              <div className="text-2xl font-bold text-dodger-blue">
                {player.career_stats.ops}
              </div>
            )}
            <div className="text-[10px] text-muted-foreground uppercase">
              OPS
            </div>
          </div>
        </div>

        {/* Career Statistics */}
        <div className="bg-white border border-gray-200 rounded-lg p-3 mb-2">
          <h3 className="text-sm font-semibold text-dodger-blue mb-2 border-b pb-1">
            Career Statistics
          </h3>
          <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Games:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.games}
                  onChange={(e) => handleInputChange('games', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.games}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">At Bats:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.at_bats}
                  onChange={(e) => handleInputChange('at_bats', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.at_bats}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Runs:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.runs}
                  onChange={(e) => handleInputChange('runs', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.runs}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Hits:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.hits}
                  onChange={(e) => handleInputChange('hits', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.hits}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Doubles:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.doubles}
                  onChange={(e) => handleInputChange('doubles', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.doubles}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Triples:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.triples}
                  onChange={(e) => handleInputChange('triples', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.triples}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">RBIs:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.rbis}
                  onChange={(e) => handleInputChange('rbis', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.rbis}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Walks:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.walks}
                  onChange={(e) => handleInputChange('walks', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.walks}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Strikeouts:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.strikeouts}
                  onChange={(e) => handleInputChange('strikeouts', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.strikeouts}</span>
              )}
            </div>
            <div className="flex justify-between py-0.5 items-center">
              <span className="text-muted-foreground">Stolen Bases:</span>
              {editMode && formData ? (
                <input
                  type="number"
                  value={formData.stolen_bases}
                  onChange={(e) => handleInputChange('stolen_bases', parseInt(e.target.value) || 0)}
                  className="w-16 px-1 py-0.5 text-right border rounded text-xs font-semibold"
                />
              ) : (
                <span className="font-semibold">{player.career_stats.stolen_bases}</span>
              )}
            </div>
          </div>
        </div>

        {/* Advanced Metrics */}
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-dodger-blue mb-2 border-b pb-1">
            Advanced Metrics
          </h3>
          <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">On Base %:</span>
              <span className="font-semibold font-mono">{player.career_stats.on_base_pct}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">Slugging %:</span>
              <span className="font-semibold font-mono">{player.career_stats.slugging_pct}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">ISO Power:</span>
              <span className="font-semibold font-mono">{player.career_stats.isolated_power}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">BB/K Ratio:</span>
              <span className="font-semibold font-mono">{player.career_stats.walk_to_strikeout_ratio}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">SB %:</span>
              <span className="font-semibold font-mono">{player.career_stats.stolen_base_pct}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">HR Rate:</span>
              <span className="font-semibold font-mono">{player.career_stats.home_run_rate}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">Power-Speed:</span>
              <span className="font-semibold font-mono">{player.career_stats.power_speed_number}</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-muted-foreground">Total Bases:</span>
              <span className="font-semibold">{player.career_stats.total_bases}</span>
            </div>
          </div>
        </div>

        {/* Baseball Card Footer */}
        <div className="text-center text-[10px] text-muted-foreground mt-2 pt-2 border-t">
          Diamond Metrics • Career Statistics
        </div>
      </DialogContent>
    </Dialog>
  );
}
