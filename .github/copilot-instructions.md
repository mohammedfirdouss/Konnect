# Konnect - Campus Tools with SolanaPay

Konnect is a Python FastAPI-based backend for a campus marketplace platform with Solana blockchain integration and AI-powered recommendations. The platform enables secure student-to-student commerce using blockchain escrow payments.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup (NEVER CANCEL - Takes 2-3 minutes total)
**CRITICAL**: All setup commands are fast but can occasionally fail due to network issues. NEVER CANCEL during package installation - retry instead.

1. **Create and activate Python virtual environment** (2 seconds):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install core dependencies** (90 seconds max - NEVER CANCEL):
   ```bash
   pip install --upgrade pip
   pip install fastapi uvicorn pytest requests sqlalchemy psycopg2-binary python-dotenv solana black flake8
   ```
   - **NETWORK TIMEOUT WARNING**: This command may fail with "Read timed out" errors due to network restrictions in sandbox environments
   - If installation fails, try installing packages individually: `pip install fastapi uvicorn` then `pip install pytest requests` etc.
   - Alternative: Use existing setup if dependencies are already available
   - Expected time: 60-90 seconds for all packages when network is stable

3. **Verify installation**:
   ```bash
   python -c "import fastapi, uvicorn, pytest, sqlalchemy, solana; print('✓ All dependencies installed')"
   ```

### Running the Application
**ALWAYS** activate the virtual environment first:
```bash
source venv/bin/activate
```

- **Development server**: `python main.py` or `uvicorn main:app --reload`
  - Starts in 1-2 seconds
  - Available at http://localhost:8000
  - API docs at http://localhost:8000/docs
  - Health check at http://localhost:8000/health

- **Production server**: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Testing (NEVER CANCEL - Takes <30 seconds)
```bash
source venv/bin/activate
python -m pytest -v
```
- Runs all tests in under 1 second
- Expected: All tests pass with possible warnings about deprecated features

### Code Quality (NEVER CANCEL - Takes <30 seconds)
```bash
source venv/bin/activate
black .  # Format code (5 seconds)
flake8 --max-line-length=88 --exclude=venv,__pycache__ .  # Lint code (5 seconds)
```

## Validation Scenarios

**ALWAYS** test these scenarios after making changes:

1. **API Functionality Test**:
   ```bash
   # Start the server
   python main.py &
   
   # Test endpoints
   curl http://localhost:8000/
   curl http://localhost:8000/health
   curl http://localhost:8000/docs  # Should return HTML
   
   # Stop the server
   pkill -f "python main.py"
   ```

2. **Complete Development Workflow**:
   ```bash
   # Activate environment
   source venv/bin/activate
   
   # Make code changes, then validate:
   black .
   flake8 --max-line-length=88 --exclude=venv,__pycache__ .
   python -m pytest -v
   python main.py  # Test server starts
   ```

## Project Structure and Key Files

### Current Repository State
This is an early-stage project with minimal implementation:

- **main.py**: Basic FastAPI application with health endpoints
- **requirements.txt**: Core Python dependencies
- **test_*.py**: Test files for API, database, and Solana functionality
- **konnect-prd.md**: Comprehensive Product Requirements Document (in backend branch)
- **app.py**: Placeholder file with "Hello" (in backend branch)

### Technology Stack (from PRD)
- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Blockchain**: Solana with solana-py SDK
- **AI**: Google Agent Development Kit (ADK) for recommendations
- **Testing**: pytest
- **Linting**: black + flake8
- **Deployment**: Docker + Kubernetes (planned)

### Branch Structure
- **main**: Basic repository structure
- **backend**: Contains PRD and minimal app.py
- **copilot/fix-***: Development branches

## Common Tasks and Expected Timing

### Environment Setup
```bash
# Fresh clone setup (2-3 minutes total - NEVER CANCEL)
git clone <repository>
cd Konnect
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # 60-90 seconds
```

### Development Workflow
```bash
# Daily development (30 seconds total)
source venv/bin/activate
python -m pytest -v  # <1 second
black .  # <5 seconds
flake8 --max-line-length=88 --exclude=venv,__pycache__ .  # <5 seconds
python main.py  # Starts immediately
```

### Dependency Management
```bash
# Add new dependency
pip install <package>
pip freeze > requirements.txt
```

## Known Issues and Workarounds

1. **Network Timeouts**: Package installation frequently fails with "ReadTimeoutError: Read timed out" in sandbox environments. 
   - SOLUTION: Try installing packages individually or work with existing installed packages
   - SOLUTION: Use requirements.txt from existing working environment

2. **Virtual Environment**: Always activate venv before running any Python commands.

3. **Solana Connectivity**: External Solana devnet connections may fail in sandbox environments - this is expected for security.

4. **Database**: PostgreSQL driver installs but requires actual PostgreSQL instance for real database operations.

5. **Linting Exclusions**: Always exclude venv and __pycache__ directories from flake8 to avoid false positives.

## Development Guidelines

- **ALWAYS** activate virtual environment: `source venv/bin/activate`
- **ALWAYS** run tests before committing: `python -m pytest -v`
- **ALWAYS** format code: `black .`
- **ALWAYS** check linting: `flake8 --max-line-length=88 --exclude=venv,__pycache__ .`
- **NEVER CANCEL** long-running commands - they complete quickly (90 seconds max)
- Use `uvicorn main:app --reload` for development with auto-reload
- Reference PRD document for planned features and architecture decisions

## Final Validation Results

**These instructions have been fully tested and validated** (September 12, 2025):

✅ **Virtual Environment**: Creates successfully in 1-2 seconds  
✅ **Dependencies**: All core packages install and import correctly  
✅ **FastAPI Server**: Starts in <2 seconds, serves HTTP requests  
✅ **API Endpoints**: Root (/) and health (/health) endpoints respond correctly  
✅ **API Documentation**: Swagger UI available at /docs  
✅ **Testing**: pytest runs 7 tests successfully in <1 second  
✅ **Code Formatting**: black formatter works correctly  
✅ **Linting**: flake8 runs and identifies style issues correctly  
✅ **Solana SDK**: Imports and basic functionality validated  
✅ **Database Driver**: SQLAlchemy and psycopg2 install and import correctly  

⚠️ **Network Limitations**: Package installation may timeout in restricted environments - workarounds documented above

## Quick Reference Commands

```bash
# Complete setup and validation
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn pytest requests sqlalchemy psycopg2-binary python-dotenv solana black flake8
python -m pytest -v
black .
flake8 --max-line-length=88 --exclude=venv,__pycache__ .
python main.py
```