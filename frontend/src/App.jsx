import { useState, useEffect } from 'react';
import axios from 'axios';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import LibrarianPanel from './components/LibrarianPanel';

// Configure Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || '';

function App() {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('library_user')) || null);
  const [member, setMember] = useState(JSON.parse(localStorage.getItem('library_member')) || null);
  const [books, setBooks] = useState([]);
  const [loans, setLoans] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const logout = () => {
    setUser(null);
    setMember(null);
    localStorage.removeItem('library_user');
    localStorage.removeItem('library_member');
    showToast('Logged out successfully');
  };

  const fetchDashboardData = async () => {
    try {
      const booksRes = await axios.get('/api/books/');
      setBooks(booksRes.data);

      // Only fetch member data if user is a MEMBER
      if (user && user.user_type === 'MEMBER') {
        const membersRes = await axios.get('/api/members/');
        const myMember = membersRes.data.find(m => m.user__username === user.username);

        if (myMember) {
          setMember(myMember);
          localStorage.setItem('library_member', JSON.stringify(myMember));
          
          const [loansRes, reservationsRes] = await Promise.all([
            axios.get(`/api/loans/?member_id=${myMember.id}`),
            axios.get(`/api/reservations/list/?member_id=${myMember.id}`)
          ]);
          
          setLoans(loansRes.data);
          setReservations(reservationsRes.data);
        }
      }
    } catch (err) {
      console.error('Failed to fetch data', err);
    }
  };

  if (!user) {
    return (
      <>
        <Auth onLogin={setUser} showToast={showToast} />
        {toast && <div className={`toast show ${toast.type}`}>{toast.message}</div>}
      </>
    );
  }

  // Determine which dashboard to show based on user_type
  const isLibrarian = user.user_type === 'LIBRARIAN';

  return (
    <div id="app">
      <nav className="navbar">
        <div className="logo">Library<span className="highlight">Flow</span></div>
        <div className="nav-links">
          <span style={{ marginRight: '1rem', color: 'var(--text-secondary)' }}>
            {isLibrarian ? '👨‍💼 Librarian' : '👤 Member'}: {user.username}
          </span>
          <button onClick={logout}>Logout</button>
        </div>
      </nav>

      <main className="container">
        {isLibrarian ? (
          <LibrarianPanel showToast={showToast} refreshBooks={fetchDashboardData} />
        ) : (
          <Dashboard 
            user={user} 
            member={member} 
            books={books} 
            loans={loans} 
            reservations={reservations} 
            refreshData={fetchDashboardData}
            showToast={showToast}
          />
        )}
      </main>
      {toast && <div className={`toast show ${toast.type}`}>{toast.message}</div>}
    </div>
  );
}

export default App;
