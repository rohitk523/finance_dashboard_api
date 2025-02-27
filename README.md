# Indian Finance Dashboard - Backend

This is the backend API for the Indian Finance Dashboard application, built with FastAPI and PostgreSQL.

## Features

- User authentication with JWT
- Transaction management and categorization
- Investment portfolio tracking
- Indian tax calculation and filing assistance
- Document storage for tax receipts and forms
- AI-powered financial assistant and insights
- Support for Indian investment types (PPF, NPS, ELSS, etc.)
- GST integration
- UPI transaction categorization

## Tech Stack

- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Pydantic - Data validation
- JWT - Authentication
- Alembic - Database migrations
- Docker - Containerization

## Setup and Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/finance-dashboard-backend.git
   cd finance-dashboard-backend
   ```

2. Create a `.env` file based on the `.env.template` provided.

3. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

4. The API will be available at http://localhost:8000

5. To seed the database with sample data:
   ```
   docker-compose exec api python -m scripts.seed_db
   ```

### Option 2: Manual Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/finance-dashboard-backend.git
   cd finance-dashboard-backend
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a PostgreSQL database:
   ```
   createdb finance_dashboard
   ```

4. Set up your environment variables in a `.env` file based on the `.env.template`.

5. Run database migrations:
   ```
   alembic upgrade head
   ```

6. Start the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

7. Seed the database with sample data:
   ```
   python -m scripts.seed_db
   ```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key API Endpoints

### Authentication
- POST `/api/v1/auth/register` - Register a new user
- POST `/api/v1/auth/login` - Login and get access token
- POST `/api/v1/auth/verify/{token}` - Verify email
- GET `/api/v1/auth/profile` - Get user profile

### Transactions
- GET `/api/v1/transactions` - List transactions
- POST `/api/v1/transactions` - Create a transaction
- GET `/api/v1/transactions/categories` - List transaction categories

### Investments
- GET `/api/v1/investments` - List investments
- POST `/api/v1/investments` - Create an investment
- GET `/api/v1/investments/types` - List investment types
- GET `/api/v1/investments/insights` - Get investment insights

### Tax
- GET `/api/v1/tax/summary` - Get tax summary
- POST `/api/v1/tax/calculate` - Calculate tax liability
- GET `/api/v1/tax/saving-suggestions` - Get tax saving suggestions
- POST `/api/v1/tax/documents/upload` - Upload tax document

### AI Assistant
- POST `/api/v1/ai/assistant` - Query the AI assistant
- POST `/api/v1/ai/assistant/analyze-expenses` - Analyze expenses
- POST `/api/v1/ai/assistant/tax-advice` - Get tax advice
- POST `/api/v1/ai/assistant/investment-recommendations` - Get investment recommendations

## Development

### Running Tests

```
pytest
```

### Creating a New Migration

After changing models, create a new migration:

```
alembic revision --autogenerate -m "Description of changes"
```

Then apply the migration:

```
alembic upgrade head
```

## License

[MIT](LICENSE)