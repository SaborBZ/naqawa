import os, sys, glob, shutil, argparse, subprocess, torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn, yt_dlp

# تحديد مسار FFmpeg تلقائياً
FFMPEG_BIN = shutil.which("ffmpeg")
if not FFMPEG_BIN:
    try:
        import imageio_ffmpeg
        FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FFMPEG_BIN = "ffmpeg"

DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_cache")
parser = argparse.ArgumentParser(description="Naqawa Local Engine")
parser.add_argument("--cache-dir", type=str, default=DEFAULT_CACHE_DIR, help="مسار حفظ الصوت")
args, _ = parser.parse_known_args()

CACHE_DIR = os.path.abspath(args.cache_dir)
os.makedirs(CACHE_DIR, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("="*60)
print(f"🔥 تم تشغيل محرك نقاوة المحلي | المعالجة عبر: [{DEVICE.upper()}]")
print(f"📁 مجلد الحفظ: {CACHE_DIR}")
print(f"🎬 مسار FFmpeg: {FFMPEG_BIN}")
print("="*60)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YTDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios', 'mweb'],
            'player_skip': ['webpage', 'configs']
        }
    }
}

@app.get("/")
def health():
    return {"status": "online", "mode": "local", "device": DEVICE, "cache_dir": CACHE_DIR}

@app.get("/process")
@app.post("/process")
async def process_video(url: str):
    print(f"\n🚀 [طلب محلي]: {url}")
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id")
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"خطأ يوتيوب: {str(e)}"})

    cached_file = os.path.join(CACHE_DIR, f"{video_id}.mp3")
    if os.path.exists(cached_file):
        print(f"⚡ [الكاش] المقطع {video_id} معالج مسبقاً! إرسال فوري...")
        return {"status": "ready", "video_id": video_id}

    work_dir = os.path.join(os.path.dirname(CACHE_DIR), f"temp_{video_id}")
    os.makedirs(work_dir, exist_ok=True)
    try:
        raw_tmpl = os.path.join(work_dir, "raw.%(ext)s")
        download_opts = {**YTDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': raw_tmpl}
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])

        raw_file = glob.glob(os.path.join(work_dir, "raw.*"))[0]
        input_wav = os.path.join(work_dir, "input.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", raw_file, "-vn", "-ar", "44100", "-ac", "2", input_wav], check=True)

        cmd = [sys.executable, "-m", "demucs.separate", "--two-stems", "vocals", "-d", DEVICE, "-n", "htdemucs", "-o", work_dir, input_wav]
        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0 and DEVICE == "cuda":
            print("⚠️ تحويل تلقائي للمعالج CPU...")
            cmd_cpu = [sys.executable, "-m", "demucs.separate", "--two-stems", "vocals", "-d", "cpu", "-n", "htdemucs", "-o", work_dir, input_wav]
            res = subprocess.run(cmd_cpu, capture_output=True, text=True)

        if res.returncode != 0:
            raise Exception(f"خطأ Demucs: {res.stderr[:200]}")

        vocals_list = glob.glob(os.path.join(work_dir, "**", "vocals.wav"), recursive=True)
        if not vocals_list:
            raise Exception("تعذر العثور على ملف vocals.wav الناتج")
        vocals_path = vocals_list[0]

        subprocess.run([FFMPEG_BIN, "-y", "-i", vocals_path, "-b:a", "192k", cached_file], check=True)
        shutil.rmtree(work_dir, ignore_errors=True)
        print(f"✅ تمت المعالجة بنجاح: {video_id}")
        return {"status": "ready", "video_id": video_id}
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/audio/{video_id}")
async def stream(video_id: str):
    file_path = os.path.join(CACHE_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
