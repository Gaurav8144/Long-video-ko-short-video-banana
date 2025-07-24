from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

app = FastAPI()

# Serve static HTML files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure folders exist
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/upload/")
async def upload_video(file: UploadFile, timer: int = Form(...)):
    # Save uploaded file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Load video using moviepy
    clip = VideoFileClip(file_location)
    duration = int(clip.duration)
    base_name = os.path.splitext(file.filename)[0]

    # Split and save clips
    for start in range(0, duration, timer * 60):
        end = min(start + timer * 60, duration)
        subclip = clip.subclip(start, end)
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_{start//60}-{end//60}.mp4")
        subclip.write_videofile(output_path, codec="libx264")

    return {"message": "Video split successfully!"}
