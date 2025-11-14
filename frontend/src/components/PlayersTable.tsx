import React, { useState, useEffect } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnDef,
  flexRender,
  SortingState,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { PlayerCard } from './PlayerCard';
import { PlayerComparison } from './PlayerComparison';

interface Player {
  id: number;
  name: string;
  position: string;
  position_display: string;
  home_runs: number;
  batting_avg: string;
  ops: string;
}

interface PlayersTableProps {
  limit?: number;
  refreshKey?: number;
  onPlayerUpdated?: () => void;
}

export function PlayersTable({ limit = 20, refreshKey, onPlayerUpdated }: PlayersTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<{ id: number; name: string } | null>(null);
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [hasNext, setHasNext] = useState<boolean>(false);
  const [hasPrevious, setHasPrevious] = useState<boolean>(false);

  // Comparison mode state
  const [comparisonPlayers, setComparisonPlayers] = useState<{ id: number; name: string }[]>([]);
  const [comparisonMode, setComparisonMode] = useState<boolean>(false);

  const handlePlayerClick = (player: Player, event: React.MouseEvent) => {
    // Shift-click for comparison mode
    if (event.shiftKey) {
      if (comparisonPlayers.length < 2) {
        const newPlayers = [...comparisonPlayers, { id: player.id, name: player.name }];
        setComparisonPlayers(newPlayers);

        // If we have 2 players, open comparison mode
        if (newPlayers.length === 2) {
          setComparisonMode(true);
        }
      }
    } else {
      // Normal click - open single player card
      setSelectedPlayer({ id: player.id, name: player.name });
      setModalOpen(true);
    }
  };

  const handleComparisonClose = () => {
    setComparisonMode(false);
    setComparisonPlayers([]);
  };

  useEffect(() => {
    // Only show loading state on initial load, use refreshing for updates
    if (players.length === 0) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    fetch(`/api/players/?ordering=-career_stats__home_runs&limit=${limit}&page=${currentPage}`)
      .then(response => response.json())
      .then(data => {
        setPlayers(data.results || data || []);
        setTotalCount(data.count || 0);
        setHasNext(!!data.next);
        setHasPrevious(!!data.previous);
        setLoading(false);
        setRefreshing(false);
      })
      .catch(error => {
        console.error('Error fetching players:', error);
        setError('Failed to load players');
        setLoading(false);
        setRefreshing(false);
      });
  }, [limit, currentPage, refreshKey]);

  const handleNextPage = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (hasNext) {
      setLoading(true);
      setCurrentPage(prev => prev + 1);
      // Clear comparison selection when changing pages
      setComparisonPlayers([]);
      setComparisonMode(false);
    }
  };

  const handlePreviousPage = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (hasPrevious) {
      setLoading(true);
      setCurrentPage(prev => prev - 1);
      // Clear comparison selection when changing pages
      setComparisonPlayers([]);
      setComparisonMode(false);
    }
  };

  const columns: ColumnDef<Player>[] = [
    {
      accessorKey: 'name',
      header: 'Player Name',
      cell: ({ row }) => (
        <div className="font-semibold">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'position_display',
      header: 'Position',
      cell: ({ row }) => (
        <div className="text-sm">{row.getValue('position_display')}</div>
      ),
    },
    {
      accessorKey: 'home_runs',
      header: ({ column }) => {
        return (
          <div
            className="flex items-center cursor-pointer hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Home Runs
            {column.getIsSorted() && (
              <span className="ml-2">
                {column.getIsSorted() === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </div>
        );
      },
      cell: ({ row }) => (
        <div className="font-bold text-dodger-blue">
          {row.getValue('home_runs')}
        </div>
      ),
    },
    {
      accessorKey: 'batting_avg',
      header: ({ column }) => {
        return (
          <div
            className="flex items-center cursor-pointer hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            AVG
            {column.getIsSorted() && (
              <span className="ml-2">
                {column.getIsSorted() === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </div>
        );
      },
      cell: ({ row }) => (
        <div className="font-mono">{row.getValue('batting_avg')}</div>
      ),
    },
    {
      accessorKey: 'ops',
      header: ({ column }) => {
        return (
          <div
            className="flex items-center cursor-pointer hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            OPS
            {column.getIsSorted() && (
              <span className="ml-2">
                {column.getIsSorted() === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </div>
        );
      },
      cell: ({ row }) => (
        <div className="font-mono font-semibold">{row.getValue('ops')}</div>
      ),
    },
    {
      accessorKey: "hits_per_game",
      header: ({ column }) => {
        return (
          <div
            className="flex items-center cursor-pointer hover:text-foreground"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Hits Per Game
            {column.getIsSorted() && (
              <span className="ml-2">
                {column.getIsSorted() === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </div>
        );
      }
    }
  ];

  const table = useReactTable({
    data: players,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
  });

  if (loading && players.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading players table...</p>
        </CardContent>
      </Card>
    );
  }

  if (error && players.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-dodger-blue">Top Players</CardTitle>
        <CardDescription>
          Click column headers to sort. Shift+Click to compare players (select 2)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className={`rounded-md border transition-opacity duration-200 ${loading ? 'opacity-50 pointer-events-none' : refreshing ? 'opacity-90' : ''}`}>
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => {
                  const isSelectedForComparison = comparisonPlayers.some(p => p.id === row.original.id);
                  return (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && 'selected'}
                    onClick={(e) => handlePlayerClick(row.original, e)}
                    className={`cursor-pointer hover:bg-accent/50 select-none ${isSelectedForComparison ? 'bg-dodger-blue/10 border-l-4 border-dodger-blue' : ''}`}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center"
                  >
                    No players found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between px-2 py-4">
          <div className="text-sm text-muted-foreground">
            Showing page {currentPage} of {Math.ceil(totalCount / limit)} ({totalCount} total players)
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePreviousPage}
              disabled={!hasPrevious || loading}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextPage}
              disabled={!hasNext || loading}
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>

      {/* Single Player Card Modal */}
      <PlayerCard
        playerId={selectedPlayer?.id || null}
        playerName={selectedPlayer?.name || ''}
        open={modalOpen && !comparisonMode}
        onOpenChange={setModalOpen}
        onPlayerUpdated={onPlayerUpdated}
      />

      {/* Comparison Mode - Show side-by-side comparison */}
      {comparisonMode && comparisonPlayers.length === 2 && (
        <PlayerComparison
          player1Id={comparisonPlayers[0].id}
          player2Id={comparisonPlayers[1].id}
          open={comparisonMode}
          onOpenChange={handleComparisonClose}
        />
      )}
    </Card>
  );
}
