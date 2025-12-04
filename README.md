# Library Checkout System

A full-stack library management system with Django backend and React frontend, focusing on circulation (loans, returns, reservations).

## Tech Stack

- **Backend**: Django 4.2, PostgreSQL/SQLite, Django REST Framework
- **Frontend**: React, Vite, Axios
- **Deployment**: Render (Backend), Vercel (Frontend)

## Quick Start (Development)

### Backend Setup

1. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a librarian account**
   ```bash
   python create_librarian.py
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Backend will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

Frontend will be available at `http://localhost:5173`

## Environment Variables

### Backend (.env)

Create a `.env` file in the root directory (see `.env.example`):

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:port/database  # Optional, uses SQLite if not set
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)

Create a `.env` file in the `frontend` directory (see `frontend/.env.example`):

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Production Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for detailed deployment instructions for:
- Backend deployment on Render with PostgreSQL
- Frontend deployment on Vercel
- Environment configuration
- Troubleshooting guide

## Features

- **User Management**: Member and Librarian roles
- **Book Management**: Add, view, and manage books and copies
- **Circulation**: Check out and return books
- **Reservations**: Reserve books when unavailable
- **Penalties**: Automatic penalty calculation for overdue books
- **Real-time Updates**: Dynamic dashboard for members and librarians

## Project Structure

```
Library/
├── circulation/          # Django app for library operations
├── library_checkout/     # Django project settings
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── App.jsx      # Main app component
│   └── dist/           # Build output
├── requirements.txt     # Python dependencies
├── Procfile            # Render deployment config
├── runtime.txt         # Python version
└── DEPLOYMENT.md       # Deployment guide
```

## API Endpoints

- `GET /api/books/` - List all books
- `POST /api/books/` - Create a book (Librarian only)
- `GET /api/loans/` - List loans
- `POST /api/loans/checkout/` - Check out a book
- `POST /api/loans/return/` - Return a book
- `GET /api/reservations/list/` - List reservations
- `POST /api/reservations/create/` - Create a reservation

## Testing

Run backend tests:
```bash
python manage.py test
```

Run verification script:
```bash
python verify_library.py
```

## License

MIT License
