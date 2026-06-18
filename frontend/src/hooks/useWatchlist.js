import { useState } from 'react';
import { apiClient } from '../utils/api';

export function useWatchlist(saveToHistory) {
  const [watchlistTickers, setWatchlistTickers] = useState('RELIANCE.NS, TCS.NS, INFY.NS');
  const [watchlistData, setWatchlistData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWatchlist = async (e, period) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setWatchlistData(null);

    try {
      const tickers = watchlistTickers.split(',').map(t => t.trim().toUpperCase()).filter(Boolean);
      const json = await apiClient('/api/watchlist', {
        method: 'POST',
        body: JSON.stringify({ tickers, period })
      });

      setWatchlistData(json);
      
      // Save each successful result to history
      if (saveToHistory && json.results) {
        json.results.forEach(r => saveToHistory(r));
      }
    } catch (err) {
      setError(err.message || "Failed to fetch watchlist data.");
    } finally {
      setLoading(false);
    }
  };

  return {
    watchlistTickers,
    setWatchlistTickers,
    watchlistData,
    setWatchlistData,
    loading,
    error,
    fetchWatchlist,
  };
}
