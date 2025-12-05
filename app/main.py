from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import profile, auth, test, question  # Added test & question

app = FastAPI(
    title="Profile & Test API",
    description="""
    ## Complete API for Profiles & Tests
    
    ### 🔐 Authentication
    - Register & Login
    - JWT Token based auth
    
    ### 👤 Profiles
    - User & Institution profiles
    
    ### 📝 Tests
    - Create, Update, Delete tests
    - MCQ Questions (4 options)
    - Theory Questions (long answer)
    - Coding Questions (with test cases)
    
    ### Made with ❤️ using FastAPI + Supabase
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(test.router, prefix="/api/v1")          # NEW
app.include_router(question.router, prefix="/api/v1")      # NEW


@app.get("/")
def root():
    return {
        "message": "Welcome to Profile & Test API!",
        "version": "3.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "profiles": "/api/v1/profiles",
            "tests": "/api/v1/tests",
            "questions": "/api/v1/questions"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running!"}