import React, { useState } from 'react';
import { HomeRunLeaders } from './components/HomeRunLeaders';
import { PlayersTable } from './components/PlayersTable';

function App() {
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const handlePlayerUpdated = () => {
    // Trigger refresh in both components by updating the key
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-dodger-blue text-white">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold">Diamond Metrics</h1>
          <p className="text-dodger-lightblue mt-2">
            Advanced Baseball Statistics & Analytics
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Home Run Leaders */}
        <HomeRunLeaders refreshKey={refreshKey} onPlayerUpdated={handlePlayerUpdated} />
        {/* Players Table */}
        <PlayersTable limit={100} refreshKey={refreshKey} onPlayerUpdated={handlePlayerUpdated} />
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t bg-muted/20">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>Diamond Metrics - Baseball Statistics Platform</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
