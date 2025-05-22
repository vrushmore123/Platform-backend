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

# Mount React static assets (usually in dist/assets or dist/static depending on your setup)
app.mount("/react_static", StaticFiles(directory=os.path.join(REACT_DIST_DIR, "assets")), name="react_static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    api_prefixes = ("api", "teacher_courses", "profile", "auth", "courses")
    if any(full_path.startswith(prefix) for prefix in api_prefixes):
        return {"detail": "Not Found"}

    index_path = os.path.join(REACT_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "React dist not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
