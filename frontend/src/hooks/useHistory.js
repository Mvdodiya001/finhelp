import { useState, useEffect } from 'react';

const STORAGE_KEY = 'finhelp_history';

export function useHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      setHistory(stored);
    } catch { 
      setHistory([]); 
    }
  }, []);

  const saveToHistory = (result) => {
    const entry = {
      ticker: result.ticker,
      signal: result.fusion.signal,
      score: result.fusion.final_score.toFixed(3),
      model: result.quant.model_name,
      timestamp: result.timestamp,
    };
    
    setHistory((prevHistory) => {
      const updated = [entry, ...prevHistory].slice(0, 20); // Keep last 20
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  return { history, saveToHistory };
}
