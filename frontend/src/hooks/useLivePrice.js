import { useState, useEffect } from 'react';
import { apiClient } from '../utils/api';

export function useLivePrice(ticker, initialPrice = null) {
  const [livePrice, setLivePrice] = useState(initialPrice);

  useEffect(() => {
    if (!ticker) return;

    const fetchLivePrice = async () => {
      try {
        const json = await apiClient(`/api/live_price?ticker=${ticker}`);
        setLivePrice(json.price);
      } catch (err) {
        console.error(`Failed to fetch live price for ${ticker}`, err);
      }
    };

    fetchLivePrice();
    const intervalId = setInterval(fetchLivePrice, 10000);
    return () => clearInterval(intervalId);
  }, [ticker]);

  return livePrice;
}
