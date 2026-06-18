import { useState, useCallback } from 'react';
import { apiClient } from '../utils/api';

export function usePortfolio() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [historyData, setHistoryData] = useState(null);

  const fetchPortfolio = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient('/api/portfolio');
      setData(result);
      
      // Fetch history for graph
      try {
        const histResult = await apiClient('/api/portfolio/history?days=30');
        setHistoryData(histResult.history);
      } catch (histErr) {
        console.error("Failed to fetch history data", histErr);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const executeTrade = useCallback(async (ticker, action, shares, price) => {
    try {
      const result = await apiClient('/api/portfolio/trade', {
        method: 'POST',
        body: JSON.stringify({ ticker, action, shares, price })
      });
      
      // Refresh portfolio after trade
      await fetchPortfolio();
      return { success: true, message: result.message };
    } catch (err) {
      return { success: false, message: err.message };
    }
  }, [fetchPortfolio]);

  return { data, historyData, loading, error, fetchPortfolio, executeTrade };
}
