import { useState } from 'react';
import { apiClient } from '../utils/api';

export function useCharts() {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [period, setPeriod] = useState('1y');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchChart = async (e, customPeriod) => {
    if (e) e.preventDefault();
    if (!ticker) return;

    const currentPeriod = customPeriod || period;
    
    setLoading(true);
    setError(null);
    setChartData(null);
    
    try {
      const json = await apiClient(`/api/chart?ticker=${ticker}&period=${currentPeriod}`);
      
      setChartData(json);
      // update state if customPeriod was used (from shortcut buttons)
      if (customPeriod && customPeriod !== period) {
          setPeriod(customPeriod);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    ticker, setTicker,
    period, setPeriod,
    chartData, setChartData,
    loading, error,
    fetchChart
  };
}
