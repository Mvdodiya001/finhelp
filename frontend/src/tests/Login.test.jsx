import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Login } from '../components/Login';

describe('Login Component', () => {
  const mockOnLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the login form correctly', () => {
    render(<Login onLogin={mockOnLogin} />);
    expect(screen.getByRole('heading', { name: /Secure Access/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Authenticate/i })).toBeInTheDocument();
  });

  it('shows error on failed login', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'API Error' })
      })
    );

    render(<Login onLogin={mockOnLogin} />);
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'admin' } });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'wrongpass' } });
    fireEvent.click(screen.getByRole('button', { name: /Authenticate/i }));

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
    expect(mockOnLogin).not.toHaveBeenCalled();
  });

  it('calls onLogin on successful authentication', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ access_token: 'test-token' }),
      })
    );

    render(<Login onLogin={mockOnLogin} />);
    fireEvent.change(screen.getByPlaceholderText(/Username/i), { target: { value: 'admin' } });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), { target: { value: 'pass123' } });
    fireEvent.click(screen.getByRole('button', { name: /Authenticate/i }));

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith('test-token');
      expect(localStorage.getItem('token')).toBe('test-token');
    });
  });
});
