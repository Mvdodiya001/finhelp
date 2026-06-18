import React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Terminal, Clock, List, LogOut, Briefcase, Activity, BarChart2 } from 'lucide-react';

export function Header({ 
  showHistory, setShowHistory, historyCount,
  ticker, setTicker,
  watchlistTickers, setWatchlistTickers,
  period, setPeriod,
  analysisLoading, watchlistLoading,
  onAnalyze, onCompare,
  onLogout
}) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleAnalyze = (e) => {
    e.preventDefault();
    onAnalyze(e);
    if (location.pathname !== '/analyze') {
      navigate('/analyze');
    }
  };

  const handleCompare = (e) => {
    e.preventDefault();
    onCompare(e, period);
    if (location.pathname !== '/watchlist') {
      navigate('/watchlist');
    }
  };

  return (
    <header className="main-header">
      <div className="header-top">
        <h1>
          <div className="logo-icon"><Terminal size={24} /></div>
          <span className="gradient-text">FinHelp</span>
        </h1>

        {/* Mode Toggle */}
        <div className="mode-toggles">
          <NavLink to="/analyze" className={({isActive}) => `toggle-btn ${isActive ? 'active' : ''}`}>
            Single Ticker
          </NavLink>
          <NavLink to="/watchlist" className={({isActive}) => `toggle-btn ${isActive ? 'active' : ''}`}>
            <List size={14} style={{marginRight: 6, verticalAlign: "middle"}} /> 
            Watchlist
          </NavLink>
          <NavLink to="/portfolio" className={({isActive}) => `toggle-btn ${isActive ? 'active' : ''}`}>
            <Briefcase size={14} style={{marginRight: 6, verticalAlign: "middle"}} /> 
            Portfolio
          </NavLink>
          <NavLink to="/backtest" className={({isActive}) => `toggle-btn ${isActive ? 'active' : ''}`}>
            <Activity size={14} style={{marginRight: 6, verticalAlign: "middle"}} /> 
            Backtest
          </NavLink>
          <NavLink to="/charts" className={({isActive}) => `toggle-btn ${isActive ? 'active' : ''}`}>
            <BarChart2 size={14} style={{marginRight: 6, verticalAlign: "middle"}} /> 
            Charts
          </NavLink>
          
          <button
            type="button"
            className={`toggle-btn history-btn ${showHistory ? 'active' : ''}`}
            onClick={() => setShowHistory(!showHistory)}
          >
            <Clock size={14} style={{marginRight: 6, verticalAlign: "middle"}} /> 
            History ({historyCount})
          </button>
          <button 
            type="button"
            className="toggle-btn logout-btn"
            onClick={onLogout}
            style={{ marginLeft: '1rem', color: '#ef4444' }}
          >
            <LogOut size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            Logout
          </button>
        </div>
      </div>

      <div className="header-bottom">
        {/* Single Ticker Mode */}
        {location.pathname === '/analyze' && (
          <form className="search-box" onSubmit={handleAnalyze}>
            <div className="input-wrapper">
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Ticker (e.g. RELIANCE.NS)"
                required
                list="popular-stocks"
                autoComplete="off"
              />
              <datalist id="popular-stocks">
                <option value="RELIANCE.NS">Reliance Industries</option>
                <option value="TCS.NS">Tata Consultancy Services</option>
                <option value="HDFCBANK.NS">HDFC Bank</option>
                <option value="INFY.NS">Infosys</option>
                <option value="ICICIBANK.NS">ICICI Bank</option>
                <option value="SBIN.NS">State Bank of India</option>
                <option value="BHARTIARTL.NS">Bharti Airtel</option>
                <option value="ITC.NS">ITC Limited</option>
                <option value="LT.NS">Larsen & Toubro</option>
                <option value="BAJFINANCE.NS">Bajaj Finance</option>
              </datalist>
            </div>
            
            <select className="glass-select" value={period} onChange={(e) => setPeriod(e.target.value)}>
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
            </select>
            
            <button className="primary-btn" type="submit" disabled={analysisLoading}>
              {analysisLoading ? <span>ANALYZING...</span> : "EXECUTE"}
            </button>
          </form>
        )}

        {/* Watchlist Mode */}
        {location.pathname === '/watchlist' && (
          <form className="search-box" onSubmit={handleCompare}>
            <div className="input-wrapper wide">
              <input
                type="text"
                value={watchlistTickers}
                onChange={(e) => setWatchlistTickers(e.target.value.toUpperCase())}
                placeholder="RELIANCE.NS, TCS.NS, INFY.NS"
                required
              />
            </div>
            
            <select className="glass-select" value={period} onChange={(e) => setPeriod(e.target.value)}>
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
            </select>
            
            <button className="primary-btn" type="submit" disabled={watchlistLoading}>
              {watchlistLoading ? <span>ANALYZING...</span> : "COMPARE"}
            </button>
          </form>
        )}
      </div>
    </header>
  );
}
