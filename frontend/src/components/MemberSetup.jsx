import axios from 'axios';

function MemberSetup({ user, onMemberCreated, showToast }) {
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const libraryId = formData.get('library_id');

    try {
      const res = await axios.post('/api/members/', {
        user_id: user.id,
        library_id: libraryId
      });
      onMemberCreated(res.data);
      showToast('Member profile created successfully');
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed to create profile', 'error');
    }
  };

  return (
    <div className="container" id="auth-container">
      <div className="auth-box">
        <h2>Complete Profile</h2>
        <p style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
          Please set your Library ID to continue.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Library ID</label>
            <input type="text" name="library_id" placeholder="e.g. LIB-001" required />
          </div>
          <button type="submit" className="btn">Create Profile</button>
        </form>
      </div>
    </div>
  );
}

export default MemberSetup;
