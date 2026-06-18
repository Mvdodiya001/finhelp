import { useState } from 'react';
import { apiClient } from '../utils/api';

export function useAnalysis(saveToHistory) {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [period, setPeriod] = useState('2y');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const json = await apiClient('/api/analyze', {
        method: "POST",
        body: JSON.stringify({ ticker: ticker.toUpperCase(), period })
      });

      setData(json);
      if (saveToHistory) saveToHistory(json);
    } catch (err) {
      setError(err.message || "Failed to fetch data from backend.");
    } finally {
      setLoading(false);
    }
  };

  return {
    ticker,
    setTicker,
    period,
    setPeriod,
    data,
    setData,
    loading,
    error,
    fetchAnalysis,
  };
}
