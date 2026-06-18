import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

describe('App Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the login state initially when no token is present', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /Secure Access/i })).toBeInTheDocument();
  });

  it('renders the initial empty state when authenticated', () => {
    localStorage.setItem('token', 'fake-jwt-token');
    render(<App />);
    
    // Check if header is rendered
    expect(screen.getByRole('heading', { name: /FinHelp/i })).toBeInTheDocument();

    // Check if the empty state message is rendered
    expect(screen.getByText(/Enter a ticker and click Execute/i)).toBeInTheDocument();
  });
});
