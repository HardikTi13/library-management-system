import { useState, useEffect } from 'react';
import axios from 'axios';

function LibrarianPanel({ showToast, refreshBooks }) {
  const [activeTab, setActiveTab] = useState('add-book');
  const [reservations, setReservations] = useState([]);
  const [loans, setLoans] = useState([]);

  // Fetch all reservations and loans when component mounts or tab changes
  useEffect(() => {
    if (activeTab === 'reservations') {
      fetchReservations();
    } else if (activeTab === 'loans') {
      fetchLoans();
    }
  }, [activeTab]);

  const fetchReservations = async () => {
    try {
      const res = await axios.get('/api/reservations/list/');
      setReservations(res.data);
    } catch (err) {
      showToast('Failed to fetch reservations', 'error');
    }
  };

  const fetchLoans = async () => {
    try {
      const res = await axios.get('/api/loans/');
      setLoans(res.data);
    } catch (err) {
      showToast('Failed to fetch loans', 'error');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  const handleAddBook = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      await axios.post('/api/books/', data);
      showToast('Book added successfully');
      e.target.reset();
      refreshBooks();
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to add book', 'error');
    }
  };

  const handleAddCopy = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      // No barcode needed, backend generates it
      await axios.post(`/api/books/${data.book_id}/copies/`, {});
      showToast('Copy added successfully');
      e.target.reset();
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to add copy', 'error');
    }
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      await axios.post('/api/loans/checkout/', data);
      showToast('Book checked out successfully');
      e.target.reset();
    } catch (err) {
      showToast(err.response?.data?.error || 'Checkout failed', 'error');
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
      const res = await axios.post('/api/loans/return/', data);
      if (res.data.penalty) {
        showToast(`Returned with penalty: $${res.data.penalty.amount}`, 'warning');
      } else {
        showToast('Book returned successfully');
      }
      e.target.reset();
    } catch (err) {
      showToast(err.response?.data?.error || 'Return failed', 'error');
    }
  };

  const handleCancelReservation = async (reservationId) => {
    try {
      await axios.post(`/api/reservations/${reservationId}/cancel/`);
      showToast('Reservation cancelled successfully');
      fetchReservations(); // Refresh the list
    } catch (err) {
      showToast(err.response?.data?.error || 'Cancellation failed', 'error');
    }
  };

  return (
    <div className="librarian-panel">
      <div className="tabs">
        <button className={`tab-btn ${activeTab === 'add-book' ? 'active' : ''}`} onClick={() => setActiveTab('add-book')}>Add Book</button>
        <button className={`tab-btn ${activeTab === 'add-copy' ? 'active' : ''}`} onClick={() => setActiveTab('add-copy')}>Add Copy</button>
        <button className={`tab-btn ${activeTab === 'checkout' ? 'active' : ''}`} onClick={() => setActiveTab('checkout')}>Checkout</button>
        <button className={`tab-btn ${activeTab === 'return' ? 'active' : ''}`} onClick={() => setActiveTab('return')}>Return</button>
        <button className={`tab-btn ${activeTab === 'loans' ? 'active' : ''}`} onClick={() => setActiveTab('loans')}>All Loans</button>
        <button className={`tab-btn ${activeTab === 'reservations' ? 'active' : ''}`} onClick={() => setActiveTab('reservations')}>All Reservations</button>
      </div>

      <div className="tab-content active">
        {activeTab === 'add-book' && (
          <form onSubmit={handleAddBook} className="admin-form">
            <div className="form-group"><label>Title</label><input name="title" required /></div>
            <div className="form-group"><label>Author</label><input name="author" required /></div>
            <div className="form-group"><label>ISBN</label><input name="isbn" required /></div>
            <div className="form-group"><label>Category</label><input name="category" required /></div>
            <button type="submit" className="btn">Add Book</button>
          </form>
        )}

        {activeTab === 'add-copy' && (
          <form onSubmit={handleAddCopy} className="admin-form">
            <div className="form-group"><label>Book ID</label><input name="book_id" type="number" required /></div>
            <button type="submit" className="btn">Add Copy (Auto-ID)</button>
          </form>
        )}

        {activeTab === 'checkout' && (
          <form onSubmit={handleCheckout} className="admin-form">
            <div className="form-group"><label>Library ID</label><input name="library_id" required placeholder="Member ID" /></div>
            <div className="form-group"><label>Book ID</label><input name="book_id" type="number" required placeholder="Book ID" /></div>
            <button type="submit" className="btn">Checkout Book</button>
          </form>
        )}

        {activeTab === 'return' && (
          <form onSubmit={handleReturn} className="admin-form">
            <div className="form-group"><label>Library ID</label><input name="library_id" required placeholder="Member ID" /></div>
            <div className="form-group"><label>Book ID</label><input name="book_id" type="number" required placeholder="Book ID" /></div>
            <button type="submit" className="btn">Return Book</button>
          </form>
        )}

        {activeTab === 'loans' && (
          <div className="loans-list">
            <h3 style={{ marginBottom: '1rem' }}>All Loans</h3>
            {loans.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>No loans found.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Book Title</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Due Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Return Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loans.map(loan => (
                      <tr key={loan.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.75rem' }}>{loan.copy__book__title}</td>
                        <td style={{ padding: '0.75rem' }}>{formatDate(loan.due_date)}</td>
                        <td style={{ padding: '0.75rem' }}>{formatDate(loan.return_date)}</td>
                        <td style={{ padding: '0.75rem' }}>
                          <span className={`status-badge status-${loan.status.toLowerCase()}`}>{loan.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'reservations' && (
          <div className="reservations-list">
            <h3 style={{ marginBottom: '1rem' }}>All Reservations</h3>
            {reservations.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>No reservations found.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Book ID</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Book Title</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Library ID</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Reserved At</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Expires At</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reservations.map(res => (
                      <tr key={res.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.75rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>{res.book__id}</td>
                        <td style={{ padding: '0.75rem' }}>{res.book__title}</td>
                        <td style={{ padding: '0.75rem', fontFamily: 'monospace', fontSize: '0.9rem' }}>{res.member__library_id}</td>
                        <td style={{ padding: '0.75rem' }}>{formatDate(res.reserved_at)}</td>
                        <td style={{ padding: '0.75rem' }}>{formatDate(res.expires_at)}</td>
                        <td style={{ padding: '0.75rem' }}>
                          <span className={`status-badge status-${res.status.toLowerCase()}`}>{res.status}</span>
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          {res.status === 'PENDING' && (
                            <button 
                              className="btn" 
                              style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', background: 'var(--danger)' }}
                              onClick={() => handleCancelReservation(res.id)}
                            >
                              Cancel
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default LibrarianPanel;
