import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';

// Hooks
import { useHistory } from './hooks/useHistory';
import { useAnalysis } from './hooks/useAnalysis';
import { useWatchlist } from './hooks/useWatchlist';
import { usePortfolio } from './hooks/usePortfolio';
import { useBacktest } from './hooks/useBacktest';
import { useCharts } from './hooks/useCharts';

// Components
import { Header } from './components/Header';
import { HistoryPanel } from './components/HistoryPanel';
import { Watchlist } from './components/Watchlist/index';
import { SingleTicker } from './components/SingleTicker/index';
import { Portfolio } from './components/Portfolio/index';
import { Backtest } from './components/Backtest/index';
import { Charts } from './components/Charts/index';
import { EmptyState } from './components/EmptyState';
import { Login } from './components/Login';
import { Register } from './components/Register';

function AppContent() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('token'));
  const [authMode, setAuthMode] = useState('LOGIN');

  const { history, saveToHistory } = useHistory();
  const { 
    ticker, setTicker, period, setPeriod, 
    data, loading: analysisLoading, error: analysisError, fetchAnalysis 
  } = useAnalysis(saveToHistory);
  
  const { 
    watchlistTickers, setWatchlistTickers, 
    watchlistData, loading: watchlistLoading, error: watchlistError, fetchWatchlist 
  } = useWatchlist(saveToHistory);

  const { 
    data: portfolioData, historyData, loading: portfolioLoading, error: portfolioError, fetchPortfolio, executeTrade 
  } = usePortfolio();

  const {
    ticker: btTicker, setTicker: setBtTicker, period: btPeriod, setPeriod: setBtPeriod,
    data: btData, loading: btLoading, error: btError, fetchBacktest
  } = useBacktest();

  const chartsState = useCharts();
  const [showHistory, setShowHistory] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('finhelp_history');
    window.location.reload();
  };

  if (!authToken) {
    if (authMode === 'REGISTER') {
      return (
        <Register 
          onSwitchToLogin={() => setAuthMode('LOGIN')}
          onRegisterSuccess={(username) => {
            alert(`Account for ${username} created successfully! Please log in.`);
            setAuthMode('LOGIN');
          }}
        />
      );
    }
    return <Login onLogin={setAuthToken} onSwitchToRegister={() => setAuthMode('REGISTER')} />;
  }

  return (
    <div className="app-container">
      <Header 
        showHistory={showHistory}
        setShowHistory={setShowHistory}
        historyCount={history.length}
        ticker={ticker}
        setTicker={setTicker}
        watchlistTickers={watchlistTickers}
        setWatchlistTickers={setWatchlistTickers}
        period={period}
        setPeriod={setPeriod}
        onAnalyze={fetchAnalysis}
        onCompare={fetchWatchlist}
        onLogout={handleLogout}
        analysisLoading={analysisLoading}
        watchlistLoading={watchlistLoading}
      />

      {showHistory && <HistoryPanel history={history} />}

      <Routes>
        <Route path="/" element={<Navigate to="/analyze" replace />} />
        
        <Route path="/analyze" element={
          <>
            {analysisError && <ErrorBanner error={analysisError} />}
            {analysisLoading && !data && <LoadingSkeleton />}
            {!analysisLoading && data && <SingleTicker data={data} executeTrade={executeTrade} portfolioData={portfolioData} />}
            {!analysisLoading && !data && !analysisError && <EmptyState setTicker={setTicker} setWatchlistMode={() => window.location.href='/watchlist'} />}
          </>
        } />

        <Route path="/watchlist" element={
          <>
            {watchlistError && <ErrorBanner error={watchlistError} />}
            {watchlistLoading && !watchlistData && <LoadingSkeleton />}
            {!watchlistLoading && watchlistData && <Watchlist watchlistData={watchlistData} executeTrade={executeTrade} />}
            {!watchlistLoading && !watchlistData && !watchlistError && <EmptyState setTicker={setTicker} setWatchlistMode={() => {}} />}
          </>
        } />

        <Route path="/portfolio" element={
          <>
            {portfolioError && <ErrorBanner error={portfolioError} />}
            <Portfolio portfolioData={portfolioData} historyData={historyData} fetchPortfolio={fetchPortfolio} executeTrade={executeTrade} loading={portfolioLoading} />
          </>
        } />

        <Route path="/charts" element={
          <>
            {chartsState.error && <ErrorBanner error={chartsState.error} />}
            {chartsState.loading && !chartsState.chartData && <LoadingSkeleton />}
            <Charts 
              ticker={chartsState.ticker} setTicker={chartsState.setTicker}
              period={chartsState.period} setPeriod={chartsState.setPeriod}
              fetchChart={chartsState.fetchChart}
              data={chartsState.chartData} loading={chartsState.loading} error={chartsState.error}
            />
          </>
        } />

        <Route path="/backtest" element={
          <>
            {btError && <ErrorBanner error={btError} />}
            {btLoading && !btData && <LoadingSkeleton />}
            <Backtest 
              ticker={btTicker} setTicker={setBtTicker} 
              period={btPeriod} setPeriod={setBtPeriod} 
              fetchBacktest={fetchBacktest} 
              data={btData} loading={btLoading} error={btError} 
            />
          </>
        } />
      </Routes>
    </div>
  );
}

function ErrorBanner({ error }) {
  return (
    <div className="card error-banner mb-4">
      <div className="error-icon">⚠️</div>
      <div>
        <h3 className="error-title">System Error</h3>
        <p className="error-message">{error}</p>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div>
      <div className="skeleton skeleton-hero mb-4"></div>
      <div className="grid">
        <div className="skeleton skeleton-card"></div>
        <div className="skeleton skeleton-card"></div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
