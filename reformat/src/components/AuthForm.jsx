import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthForm = ({ type }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    ...(type === 'signup' && { username: '' })
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const endpoint = type === 'signin' ? '/login' : '/register';
      const payload = type === 'signin' 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`http://localhost:5000/api${endpoint}`, payload, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Handle successful response
      if (response.data.token) {
        // Store the token in localStorage or context
        localStorage.setItem('authToken', response.data.token);
        
        // Store user data if available
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }

        // Redirect to home or dashboard
        navigate('/');
      } else {
        throw new Error('Authentication failed: No token received');
      }
    } catch (err) {
      setError(err.response?.data?.message || 
              err.message || 
              'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>{type === 'signin' ? 'Sign In' : 'Sign Up'}</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {type === 'signup' && (
        <div className="form-group">
          <label>Имя</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
      )}
      
      <div className="form-group">
        <label>Почта</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Пароль</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          minLength="6"
        />
      </div>
      
      <button 
        type="submit" 
        className="submit-btn"
        disabled={isLoading}
      >
        {isLoading ? 'Processing...' : type === 'signin' ? 'Sign In' : 'Sign Up'}
      </button>
    </form>
  );
};

export default AuthForm;