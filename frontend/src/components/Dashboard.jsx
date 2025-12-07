import { useState } from 'react';
import axios from 'axios';

function Dashboard({ user, member, books, loans, reservations, refreshData, showToast }) {
  const [view, setView] = useState('books');
  const [search, setSearch] = useState('');
  const [selectedBook, setSelectedBook] = useState(null);

  const filteredBooks = books.filter(b => 
    b.title.toLowerCase().includes(search.toLowerCase()) || 
    b.author.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  const handleReserve = async (bookId) => {
    try {
      await axios.post('/api/reservations/', {
        book_id: bookId,
        library_id: member.library_id
      });
      showToast('Book reserved successfully');
      refreshData();
      setSelectedBook(null);
    } catch (err) {
      showToast(err.response?.data?.error || 'Reservation failed', 'error');
    }
  };

  const handleCancelReservation = async (reservationId) => {
    try {
      await axios.post(`/api/reservations/${reservationId}/cancel/`);
      showToast('Reservation cancelled successfully');
      refreshData();
    } catch (err) {
      showToast(err.response?.data?.error || 'Cancellation failed', 'error');
    }
  };

  return (
    <div id="dashboard-container">
      <header className="dashboard-header">
        <h1>Welcome, <span id="user-name">{user.username}</span></h1>
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Active Loans</h3>
            <p>{loans.filter(l => l.status === 'ACTIVE').length}</p>
          </div>
          <div className="stat-card">
            <h3>Reservations</h3>
            <p>{reservations.filter(r => r.status === 'PENDING').length}</p>
          </div>
          <div className="stat-card">
            <h3>Library ID</h3>
            <p style={{ fontSize: '1.2rem' }}>{member?.library_id || '...'}</p>
          </div>
        </div>
      </header>

      <div className="tabs">
        <button className={`tab-btn ${view === 'books' ? 'active' : ''}`} onClick={() => setView('books')}>Browse Books</button>
        <button className={`tab-btn ${view === 'loans' ? 'active' : ''}`} onClick={() => setView('loans')}>My Loans</button>
        <button className={`tab-btn ${view === 'reservations' ? 'active' : ''}`} onClick={() => setView('reservations')}>Reservations</button>
      </div>

      {view === 'books' && (
        <div className="tab-content active">
          <div className="search-bar">
            <input 
              type="text" 
              placeholder="Search books..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="books-grid">
            {filteredBooks.map(book => (
              <div key={book.id} className="book-card">
                <div className="book-image">
                  {book.cover_image ? (
                    <img src={book.cover_image} alt={book.title} />
                  ) : (
                    <div className="placeholder-cover">
                      <span style={{ fontSize: '3rem' }}>📚</span>
                    </div>
                  )}
                </div>
                <div className="book-overlay">
                  <div className="book-info">
                    <div className="book-title" title={book.title}>{book.title}</div>
                    <div className="book-author">{book.author}</div>
                    <div className="book-meta">
                      <span className="chip">{book.category}</span>
                    </div>
                    <p className="book-about">{book.about || "No description available."}</p>
                    <button className="btn reserve-btn" onClick={(e) => { e.stopPropagation(); handleReserve(book.id); }}>
                      Reserve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {view === 'loans' && (
        <div className="tab-content active">
          <div className="status-grid">
            {loans.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', textAlign: 'center', gridColumn: '1/-1' }}>No active loans.</p>
            ) : (
              loans.map(loan => (
                <div key={loan.id} className="status-card">
                  <div className="card-image">
                    {loan.copy__book__cover_image ? (
                      <img src={loan.copy__book__cover_image} alt={loan.copy__book__title} />
                    ) : (
                      <div className="placeholder-image">📚</div>
                    )}
                    <span className={`status-badge status-${loan.status.toLowerCase()}`}>{loan.status}</span>
                  </div>
                  <div className="card-details">
                    <h4>{loan.copy__book__title}</h4>
                    <p className="card-date">Due: {formatDate(loan.due_date)}</p>
                    {loan.status === 'OVERDUE' && <p className="overdue-alert">Overdue!</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {view === 'reservations' && (
        <div className="tab-content active">
          <div className="status-grid">
            {reservations.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', textAlign: 'center', gridColumn: '1/-1' }}>No reservations.</p>
            ) : (
              reservations.map(res => (
                <div key={res.id} className="status-card">
                  <div className="card-image">
                    {res.book__cover_image ? (
                      <img src={res.book__cover_image} alt={res.book__title} />
                    ) : (
                      <div className="placeholder-image">📚</div>
                    )}
                    <span className={`status-badge status-${res.status.toLowerCase()}`}>{res.status}</span>
                  </div>
                  <div className="card-details">
                    <h4>{res.book__title}</h4>
                    <p className="card-date">Expires: {formatDate(res.expires_at)}</p>
                    {res.status === 'PENDING' && (
                      <button 
                        className="btn cancel-btn" 
                        onClick={() => handleCancelReservation(res.id)}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Book Details Modal */}
      {selectedBook && (
        <div className="modal-overlay" onClick={() => setSelectedBook(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedBook(null)}>×</button>
            {selectedBook.cover_image && (
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <img 
                  src={selectedBook.cover_image} 
                  alt={selectedBook.title} 
                  style={{ maxWidth: '200px', maxHeight: '300px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }} 
                />
              </div>
            )}
            <h2>{selectedBook.title}</h2>
            <div className="book-details">
                <p><strong>Author:</strong> {selectedBook.author}</p>
                <p><strong>ISBN:</strong> {selectedBook.isbn}</p>
                <p><strong>Category:</strong> {selectedBook.category}</p>
                <p><strong>Book ID:</strong> {selectedBook.id}</p>
                <hr style={{ margin: '1rem 0', borderColor: 'var(--border-color)' }} />
                <p><strong>Charges:</strong> Free to borrow.</p>
                <p><strong>Penalty:</strong> ₹10.00 per hour overdue.</p>
                <p><strong>Loan Period:</strong> 30 minutes.</p>
                <div style={{ marginTop: '2rem' }}>
                    <button className="btn" onClick={() => handleReserve(selectedBook.id)}>
                        Reserve This Book
                    </button>
                </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
