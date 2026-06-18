import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Header } from '../components/Header';

describe('Header Component', () => {
  const defaultProps = {
    appMode: 'SINGLE',
    setAppMode: vi.fn(),
    showHistory: false,
    setShowHistory: vi.fn(),
    historyCount: 3,
    ticker: 'AAPL',
    setTicker: vi.fn(),
    watchlistTickers: [],
    setWatchlistTickers: vi.fn(),
    period: '2y',
    setPeriod: vi.fn(),
    loading: false,
    onAnalyze: vi.fn(),
    onCompare: vi.fn(),
    onLogout: vi.fn(),
  };

  it('renders ticker input and execute button in single mode', () => {
    render(<Header {...defaultProps} />);
    
    // Check input is present
    const input = screen.getByPlaceholderText(/Ticker/i);
    expect(input).toBeInTheDocument();
    expect(input.value).toBe('AAPL');

    // Check button is present
    const button = screen.getByRole('button', { name: /EXECUTE/i });
    expect(button).toBeInTheDocument();
  });

  it('calls onAnalyze when execute button is clicked in single mode', () => {
    render(<Header {...defaultProps} />);
    
    const button = screen.getByRole('button', { name: /EXECUTE/i });
    fireEvent.click(button);
    
    expect(defaultProps.onAnalyze).toHaveBeenCalledTimes(1);
  });
  
  it('toggles to watchlist mode when clicked', () => {
    render(<Header {...defaultProps} />);
    
    const watchlistBtn = screen.getByRole('button', { name: /Watchlist/i });
    fireEvent.click(watchlistBtn);
    
    expect(defaultProps.setAppMode).toHaveBeenCalledWith('WATCHLIST');
  });
});
