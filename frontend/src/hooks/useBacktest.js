import { useState, useCallback } from 'react';
import { apiClient } from '../utils/api';

export function useBacktest() {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [period, setPeriod] = useState('5y');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchBacktest = useCallback(async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await apiClient('/api/backtest', {
        method: 'POST',
        body: JSON.stringify({ ticker, period })
      });
      setData(result);
    } catch (err) {
      setError(err.message || "Failed to fetch backtest");
    } finally {
      setLoading(false);
    }
  }, [ticker, period]);

  return {
    ticker, setTicker,
    period, setPeriod,
    data, loading, error,
    fetchBacktest
  };
}
