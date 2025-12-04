import { useState } from 'react';
import axios from 'axios';

function Auth({ onLogin, showToast }) {
  const [mode, setMode] = useState('login'); // login, signup

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);

    try {
      if (mode === 'login') {
        const res = await axios.post('/api/signin/', data);
        // Pass complete user object including user_type for routing
        onLogin({ 
          id: res.data.user_id, 
          username: res.data.username,
          user_type: res.data.user_type 
        });
        localStorage.setItem('library_user', JSON.stringify({ 
          id: res.data.user_id, 
          username: res.data.username,
          user_type: res.data.user_type 
        }));
        showToast('Login successful');
      } else {
        await axios.post('/api/signup/', data);
        showToast('Account created! Please sign in.');
        setMode('login');
      }
    } catch (err) {
      showToast(err.response?.data?.error || 'Authentication failed', 'error');
    }
  };

  return (
    <div className="container" id="auth-container">
      <div className="auth-box">
        <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input type="text" name="username" required />
          </div>
          {mode === 'signup' && (
            <>
              <div className="form-group">
                <label>Email</label>
                <input type="email" name="email" required />
              </div>
              <div className="form-group">
                <label>I am a</label>
                <select name="user_type" required defaultValue="MEMBER">
                  <option value="MEMBER">Member (Borrow Books)</option>
                  <option value="LIBRARIAN">Librarian (Manage Library)</option>
                </select>
              </div>
            </>
          )}
          <div className="form-group">
            <label>Password</label>
            <input type="password" name="password" required />
          </div>
          <button type="submit" className="btn">
            {mode === 'login' ? 'Sign In' : 'Sign Up'}
          </button>
        </form>
        <div className="auth-switch">
          {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
          <span onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
            {mode === 'login' ? 'Sign Up' : 'Sign In'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default Auth;
