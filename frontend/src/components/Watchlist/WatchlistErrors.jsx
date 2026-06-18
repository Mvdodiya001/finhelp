import React from 'react';

export function WatchlistErrors({ errors }) {
  if (!errors || Object.keys(errors).length === 0) return null;

  return (
    <div className="error-box mt-4">
      <strong><span className="icon">⚠️</span> Errors Encountered:</strong>
      <ul className="error-list">
        {Object.entries(errors).map(([t, err]) => (
          <li key={t}><strong>{t}:</strong> {err}</li>
        ))}
      </ul>
    </div>
  );
}
