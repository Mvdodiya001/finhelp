import React, { useState, useEffect } from 'react';
import { ShieldPlus, KeyRound, User, Check, X } from 'lucide-react';
import { apiClient } from '../utils/api';
import './Login.css';

export function Register({ onRegisterSuccess, onSwitchToLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Password requirements state
  const [reqs, setReqs] = useState({
    length: false,
    upper: false,
    lower: false,
    number: false,
    special: false
  });

  useEffect(() => {
    setReqs({
      length: password.length >= 8,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[@$!%*?&]/.test(password)
    });
  }, [password]);

  const allReqsMet = Object.values(reqs).every(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!allReqsMet) {
      setError('Please meet all password requirements before registering.');
      return;
    }
    setError('');
    setIsLoading(true);

    try {
      await apiClient('/api/register', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      // Success, switch to login or directly log them in? 
      // The API doesn't return a token on register, just the User object.
      // So we switch to login with a success message, or we can auto-login them by calling /token.
      // For simplicity, we just trigger the callback which should switch to login view.
      onRegisterSuccess(username);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const RequirementItem = ({ met, text }) => (
    <div className={`req-item ${met ? 'met' : 'unmet'}`}>
      {met ? <Check size={14} className="req-icon text-green-400" /> : <X size={14} className="req-icon text-red-400" />}
      <span>{text}</span>
    </div>
  );

  return (
    <div className="login-container">
      <div className="login-card glass-panel" style={{ paddingBottom: '1.5rem' }}>
        <div className="login-header">
          <div className="login-icon-wrapper">
            <ShieldPlus size={48} className="shield-icon" />
          </div>
          <h2>Create Account</h2>
          <p>Join the FinHelp platform.</p>
        </div>
        
        {error && <div className="login-error">{error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <User size={20} className="input-icon" />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="input-group" style={{ marginBottom: '0.5rem' }}>
            <KeyRound size={20} className="input-icon" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="password-requirements mb-4 p-3 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.2)', fontSize: '0.85rem' }}>
            <div style={{ marginBottom: '0.5rem', fontWeight: 600, color: '#aaa' }}>Password must contain:</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem' }}>
              <RequirementItem met={reqs.length} text="8+ characters" />
              <RequirementItem met={reqs.upper} text="1 uppercase" />
              <RequirementItem met={reqs.lower} text="1 lowercase" />
              <RequirementItem met={reqs.number} text="1 number" />
              <RequirementItem met={reqs.special} text="1 special (@$!%*?&)" />
            </div>
          </div>

          <button type="submit" className="primary-btn login-btn" disabled={!allReqsMet || isLoading}>
            {isLoading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem' }}>
          <span style={{ color: '#aaa' }}>Already have an account? </span>
          <button onClick={onSwitchToLogin} className="link-btn" style={{ background: 'none', border: 'none', color: '#60a5fa', cursor: 'pointer', textDecoration: 'underline' }}>
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}
