import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import courses, auth, teacher_courses, profile_teacher

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API routers
app.include_router(courses.router)
app.include_router(auth.router)
app.include_router(teacher_courses.router, prefix="/teacher_courses", tags=["Teacher Courses"])
app.include_router(profile_teacher.router, prefix="/profile", tags=["Profile"])

# Serve upload static files
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# Adjust path to your React dist folder
REACT_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
