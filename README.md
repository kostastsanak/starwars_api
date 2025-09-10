# Star Wars API

A Django REST API that provides Star Wars data (characters, films, starships) with voting functionality, integrated with SWAPI.

## Features

- **Characters, Films & Starships**: Browse, search, filter, and paginate Star Wars data
- **Voting System**: Vote for favorite characters, films, and starships with statistics
- **SWAPI Integration**: Populate data from the Star Wars API
- **Comprehensive API Documentation**: Swagger/OpenAPI interface
- **Full Test Coverage**: 80%+ test coverage with mocked external calls
- **Environment Variables**: Secure configuration management

## Quick Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd starwars_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration:**
```bash
# Copy the example .env file
cp .env.example .env  # or create a new .env file

# Edit .env with your settings:
# - Change SECRET_KEY to a new secure key
# - Update database credentials
# - Set DEBUG=False for production
```

**Example .env file:**
```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=starwars_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

3. **Database setup:**
```bash
# Create PostgreSQL database 'starwars_db'
createdb starwars_db ( or manually just create a database the name is an example it depends how you add it later on, on your .env)

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

4. **Populate data:**
```bash
python manage.py runserver
# POST to http://127.0.0.1:8000/api/swapi/populate_all/
# Or use Django command:
python manage.py populate_swapi_data
```

## Running the Application

```bash
python manage.py runserver
```

**API Documentation:** http://127.0.0.1:8000/api/docs/  
**Admin Interface:** http://127.0.0.1:8000/admin/

## API Endpoints

### Core Endpoints
- `GET /api/characters/` - List characters (with filters, search, pagination)
- `GET /api/characters/{id}/` - Character details
- `GET /api/characters/search/?q=name` - Search characters
- `GET /api/films/` - List films
- `GET /api/films/search/?q=title` - Search films
- `GET /api/starships/` - List starships
- `GET /api/starships/search/?q=name` - Search starships

### Voting Endpoints
- `POST /api/votes/` - Cast a vote
- `GET /api/votes/` - List votes
- `GET /api/votes/stats/` - Voting statistics with percentages

### Data Management
- `POST /api/swapi/populate_all/` - Populate from SWAPI
- `GET /api/swapi/sync_status/` - Check sync status

## Running Tests

### Basic Testing
```bash
# Run all tests
python manage.py test --settings=starwars_api.test_settings

# Run specific app tests
python manage.py test core.tests --settings=starwars_api.test_settings
python manage.py test voting.tests --settings=starwars_api.test_settings
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test --settings=starwars_api.test_settings

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
open htmlcov/index.html  # View in browser
```

### Expected Results
- **42+ tests** covering all major functionality
- **85%+ code coverage** (exceeds 80% requirement)
- **All external API calls mocked** for reliable testing

## Project Structure

```
starwars_api/
├── .env                    # Environment variables (create from template)
├── core/                   # Star Wars data (Characters, Films, Starships)
├── voting/                 # Voting functionality  
├── starwars_api/          # Django project settings
├── .coveragerc            # Coverage configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Environment Variables

The application uses environment variables for secure configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Django secret key | **Required** |
| `DB_NAME` | Database name | **Required** |
| `DB_USER` | Database username | **Required** |
| `DB_PASSWORD` | Database password | **Required** |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |

## Key Technologies

- **Django 4.2+** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Production database
- **drf-spectacular** - API documentation
- **django-filter** - Advanced filtering
- **Coverage.py** - Test coverage analysis
- **python-decouple** - Environment variable management

## Security Features

- **Environment Variables**: Sensitive data stored securely
- **Input Validation**: Comprehensive serializer validation
- **CORS Configuration**: Controlled cross-origin access
- **SQL Injection Protection**: Django ORM provides protection

## For Production

### Required Changes:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Recommended Additions:
- Set up proper logging
- Configure static file serving
- Use environment variables for all secrets
- Set up SSL/HTTPS
- Configure rate limiting
- Add authentication if needed

## Testing Architecture

- **Model Tests**: Database models and relationships
- **ViewSet Tests**: API endpoints with all HTTP methods
- **Service Tests**: SWAPI integration with mocked external calls
- **Integration Tests**: End-to-end API functionality
- **Coverage**: Excludes migrations, settings, and test files

## Assignment Requirements ✅

- [x] **Environment Setup**: Python 3.x, Django, PostgreSQL, virtual environment
- [x] **API Endpoints**: CRUD operations with pagination, search, filtering
- [x] **Database Models**: Characters, Films, Starships with relationships
- [x] **External API Integration**: SWAPI data fetching with error handling
- [x] **Error Handling**: Proper HTTP status codes and error messages
- [x] **Unit Testing**: 80%+ coverage with mocked external calls
- [x] **Documentation**: Comprehensive Swagger/OpenAPI documentation
- [x] **Security**: Environment variables and secure configuration
