/**
 * Utility for making API requests to the backend.
 * Automatically attaches the JWT authorization header if present.
 * 
 * @param {string} endpoint - The API endpoint starting with '/' (e.g. '/api/analyze')
 * @param {Object} options - Standard fetch options (method, body, etc.)
 * @returns {Promise<any>} The parsed JSON response
 */
export const apiClient = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = 'API Error';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }

  return response.json();
};
