# Development Guidelines

## Project Structure

```
split-wise-ruben/
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── auth/        # JWT authentication
│   │   ├── core/        # Configuration
│   │   ├── database/    # SQLAlchemy setup
│   │   ├── models/      # Database models
│   │   ├── routers/     # API endpoints
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── uploads/         # Receipt file storage
│   └── requirements.txt
│
└── frontend/            # React Native CLI
    ├── src/
    │   ├── components/  # Reusable components
    │   ├── navigation/  # React Navigation setup
    │   ├── screens/     # Screen components
    │   ├── services/    # API client
    │   ├── store/       # Zustand state
    │   ├── types/       # TypeScript types
    │   └── utils/       # Utility functions
    └── package.json
```

## Commands

### Backend
```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run server
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
cd backend && pytest

# Run linter
cd backend && ruff check .
```

### Frontend
```bash
# Install dependencies
cd frontend && npm install

# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android

# Run lint
npm run lint
```

## Code Style

- Backend: Follow PEP 8, use type hints, Pydantic for validation
- Frontend: TypeScript strict mode, functional components with hooks

## Database

- MySQL with SQLAlchemy ORM
- Run migrations with Alembic: `alembic upgrade head`
