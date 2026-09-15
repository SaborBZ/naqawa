import os, sys, glob, shutil, argparse, subprocess, re, gc, torch
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import uvicorn, yt_dlp

XOR_KEY = 0x5A
HEADER_SIZE = 64

FFMPEG_BIN = shutil.which("ffmpeg")
if not FFMPEG_BIN:
    try:
        import imageio_ffmpeg
        FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FFMPEG_BIN = "ffmpeg"

DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_cache")
parser = argparse.ArgumentParser(description="Naqawa Local Engine")
parser.add_argument("--cache-dir", type=str, default=DEFAULT_CACHE_DIR, help="مسار حفظ الكاش المؤقت")
args, _ = parser.parse_known_args()

CACHE_DIR = os.path.abspath(args.cache_dir)
os.makedirs(CACHE_DIR, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

NOTICE_FILE = os.path.join(CACHE_DIR, "README_NOTICE.txt")
if not os.path.exists(NOTICE_FILE):
    with open(NOTICE_FILE, "w", encoding="utf-8") as f:
        f.write("""================================================================================
           تنبيه هام حول ملفات التخزين المؤقت (نقاوة - Naqawa)
           IMPORTANT NOTICE - Naqawa Temporary Cache Files
================================================================================

[ARABIC / العربية]
1. الغرض التقني:
هذا المجلد يحتوي على ملفات كاش مؤقتة بصيغة (.nq) ذات ترويسة تالفة برمجياً،
وهي مخصصة حصرياً لمحرك المزامنة الفوري داخل المتصفح أثناء مشاهدة يوتيوب.

2. إخلاء المسؤولية والاستخدام غير المصرح به:
- هذه الأداة لم تُصنع لتكون برنامجاً لتنزيل الصوتيات أو حفظها على القرص.
- لا يجوز شرعاً ولا أخلاقياً محاولة فك هذه الملفات أو استخراجها واستخدامها
  خارج إطار المشاهدة المباشرة المباحة على منصة يوتيوب.
- ترويسة هذه الملفات تالفة برمجياً ولا يمكن تشغيلها بواسطة برامج الوسائط
  التقليدية (مثل VLC أو Media Player)، ومحاولة التلاعب بها تتعارض مع الغرض
  الأخلاقي للمشروع.

المشروع مفتوح المصدر لخدمة النفع العام وتجنب المحتوى غير المناسب، والأمانة
مسؤولية فردية أمام الله تعالى.

--------------------------------------------------------------------------------

[ENGLISH / الإنجليزية]
1. Technical Purpose:
This directory contains temporary, header-scrambled cache files (.nq) generated
exclusively for the real-time in-browser synchronization engine while watching
YouTube videos.

2. Disclaimer & Unauthorized Use:
- This tool is strictly NOT designed, intended, or authorized to download, rip,
  or store audio files for offline use outside YouTube.
- Attempting to tamper with, reverse-engineer, or reconstruct these files for
  offline playback violates the ethical and technical purpose of this project.
- The binary headers of these files are deliberately corrupted; they cannot be
  opened or played by standard media players (such as VLC or Windows Media Player).

This project is open-source to provide a clean browsing experience. Personal
integrity and ethical use remain the sole responsibility of the user.
================================================================================
""")

print("="*60)
print(f"🔥 تم تشغيل محرك نقاوة المحلي | المعالجة عبر: [{DEVICE.upper()}]")
print(f"📁 مجلد الكاش المؤقت: {CACHE_DIR}")
print(f"🔒 نظام حماية الملفات: ترويسة تالفة برمجياً (.nq)")
print("="*60)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

task_status = {}

YTDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['tv_downgraded', 'tv', 'android', 'mweb'],
            'player_skip': ['webpage', 'configs']
        }
    }
}

def extract_video_id(url: str):
    """استخراج المعرف فورياً بدون إرسال طلبات للشبكة"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})',
        r'shorts\/([0-9A-Za-z_-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def scramble_and_save(raw_mp3_path: str, target_nq_path: str):
    with open(raw_mp3_path, "rb") as f_in:
        data = bytearray(f_in.read())
    limit = min(len(data), HEADER_SIZE)
    for i in range(limit):
        data[i] ^= XOR_KEY
    with open(target_nq_path, "wb") as f_out:
        f_out.write(data)

def read_unscrambled_chunk(file_path: str, start: int, length: int) -> bytes:
    with open(file_path, "rb") as f:
        f.seek(start)
        chunk = bytearray(f.read(length))
    if start < HEADER_SIZE:
        overlap = min(len(chunk), HEADER_SIZE - start)
        for i in range(overlap):
            chunk[i] ^= XOR_KEY
    return bytes(chunk)

def background_processor(video_id: str, url: str):
    cached_file = os.path.join(CACHE_DIR, f"{video_id}.nq")
    work_dir = os.path.join(os.path.dirname(CACHE_DIR), f"temp_{video_id}")
    os.makedirs(work_dir, exist_ok=True)
    raw_tmpl = os.path.join(work_dir, "raw.%(ext)s")

    try:
        task_status[video_id] = {"status": "processing", "stage": "⬇️ سحب الصوت من يوتيوب..."}
        download_opts = {**YTDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': raw_tmpl}
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])

        downloaded = glob.glob(os.path.join(work_dir, "raw.*"))
        if not downloaded:
            raise Exception("فشل تنزيل ملف الصوت من يوتيوب")
        raw_file = downloaded[0]

        task_status[video_id] = {"status": "processing", "stage": "🎛️ تحويل الترددات إلى WAV..."}
        input_wav = os.path.join(work_dir, "input.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", raw_file, "-vn", "-ar", "44100", "-ac", "2", input_wav], check=True)

        task_status[video_id] = {"status": "processing", "stage": "🧠 فصل الموسيقى بنموذج Demucs v4..."}
        cmd = [sys.executable, "-m", "demucs.separate", "--two-stems", "vocals", "-d", DEVICE, "-n", "htdemucs", "--segment", "7", "-o", work_dir, input_wav]
        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0 and DEVICE == "cuda":
            task_status[video_id] = {"status": "processing", "stage": "⚠️ تحويل تلقائي للمعالجة عبر CPU..."}
            cmd_cpu = [sys.executable, "-m", "demucs.separate", "--two-stems", "vocals", "-d", "cpu", "-n", "htdemucs", "--segment", "7", "-o", work_dir, input_wav]
            res = subprocess.run(cmd_cpu, capture_output=True, text=True)

        if res.returncode != 0:
            err_msg = res.stderr[-300:] if res.stderr else res.stdout[-300:]
            raise Exception(f"خطأ Demucs: {err_msg.strip()}")

        vocals_list = glob.glob(os.path.join(work_dir, "**", "vocals.wav"), recursive=True)
        if not vocals_list:
            raise Exception("تعذر العثور على مسار الصوت الناتج")
        vocals_path = vocals_list[0]

        task_status[video_id] = {"status": "processing", "stage": "🔒 إتلاف الترويسة وتجهيز الكاش..."}
        temp_mp3 = os.path.join(work_dir, "clean.mp3")
        subprocess.run([FFMPEG_BIN, "-y", "-i", vocals_path, "-b:a", "192k", temp_mp3], check=True)

        scramble_and_save(temp_mp3, cached_file)
        task_status[video_id] = {"status": "ready"}
        print(f"✅ تمت معالجة المقطع بنجاح: {video_id}")

    except Exception as e:
        print(f"❌ خطأ معالجة محلي: {e}")
        task_status[video_id] = {"status": "error", "detail": str(e)}
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

@app.get("/")
def health():
    return {"status": "online", "mode": "local", "device": DEVICE, "cache_dir": CACHE_DIR}

@app.get("/process")
@app.post("/process")
def process_video(url: str, background_tasks: BackgroundTasks):
    video_id = extract_video_id(url)
    if not video_id:
        return JSONResponse(status_code=400, content={"detail": "رابط الفيديو غير صالح"})

    # فحص الكاش الفوري دون انتظار إنترنت
    cached_file = os.path.join(CACHE_DIR, f"{video_id}.nq")
    if os.path.exists(cached_file):
        return {"status": "ready", "video_id": video_id}

    if video_id in task_status and task_status[video_id]["status"] == "processing":
        return {"status": "processing", "video_id": video_id}

    task_status[video_id] = {"status": "processing", "stage": "بدء جدولة المعالجة المحلية..."}
    background_tasks.add_task(background_processor, video_id, url)
    return {"status": "processing", "video_id": video_id}

@app.get("/status/{video_id}")
def status(video_id: str):
    cached_file = os.path.join(CACHE_DIR, f"{video_id}.nq")
    if os.path.exists(cached_file):
        return {"status": "ready", "video_id": video_id}

    if video_id in task_status:
        return task_status[video_id]

    return JSONResponse(status_code=404, content={"status": "error", "detail": "المقطع غير مسجل"})

@app.get("/audio/{video_id}")
def stream(video_id: str, request: Request):
    file_path = os.path.join(CACHE_DIR, f"{video_id}.nq")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")

    if range_header:
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            content_length = end - start + 1

            chunk_data = read_unscrambled_chunk(file_path, start, content_length)
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": "audio/mpeg",
            }
            return Response(chunk_data, status_code=206, headers=headers)

    data = read_unscrambled_chunk(file_path, 0, file_size)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": "audio/mpeg",
    }
    return Response(data, status_code=200, headers=headers)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
