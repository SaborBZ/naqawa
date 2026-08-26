<div align="center">

# 🎧 نقاوة | Naqawa
### AI Music & Vocal Remover for YouTube

<p align="center">
  <a href="#-english"><b>English</b></a> •
  <a href="#-العربية"><b>العربية</b></a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![AI Model: Demucs v4](https://img.shields.io/badge/AI_Model-Demucs_v4-gold.svg)](https://github.com/facebookresearch/demucs)
[![Platform: Chromium](https://img.shields.io/badge/Platform-Chrome%20%7C%20Edge%20%7C%20Brave-orange.svg)]()
[![Website: Live](https://img.shields.io/badge/Website-Live_Docs-00a86b.svg)](https://saborbz.github.io/naqawa/)

</div>

---

<a name="-english"></a>
## English

> **A 100% free and open-source browser extension to isolate music and instruments from YouTube videos using AI, with video-audio synchronization.**

### ✨ Key Features
- ⚡ **Synchronization (Drift Guard):** Matches video and audio timing even when seeking, scrubbing, or changing playback speed.
- 🧠 **AI-Powered (Demucs v4):** Isolates musical instruments with good accuracy while keeping human vocals clear.
- ☁️ **Cloud Processing Support:** Provides code that enables fast processing using free Google Colab GPUs (Tesla T4 GPU).
- 💻 **Local Processing:** Run directly on your machine using your **CPU** or **NVIDIA GPU (CUDA)** without uploading any data.

### 🚀 3-Step Quick Installation (Chrome / Edge / Brave):

1. **Download Extension:** Download the [`naqawa.zip`](https://github.com/saborbz/naqawa/raw/main/naqawa.zip) archive and extract it anywhere on your computer.
2. **Open Extensions Manager:** In your browser, navigate to `chrome://extensions` (or `edge://extensions`).
3. **Load Unpacked:** Enable **Developer mode** in the top corner, click **Load unpacked**, and select the extracted folder.

### ⚠️ Known Issues & Limitations

- ⏱️ **Slight Audio-Video Sync Delay:** A minor delay in audio/video synchronization may occur when seeking or fast-forwarding the video.
- 🎵 **Residual Music Artifacts:** Some background musical tones/artifacts may still be audible, as AI vocal separation is not 100% perfect.
- 🔄 **Audio Overlap on Video Change:** Switching to another YouTube video after using the extension might continue playing audio from the previous video unless you refresh the page.
- ☁️ **Cloud Processing Errors:** Potential issues or bugs may occur when using the cloud separation option, specifically within the Google Colab code.
- 💻 **Untested on Windows:** The local processing/extraction option has not been tested on Windows OS yet.

### 📖 Official Website & Interactive Guide:
Visit the official website to explore interactive setup commands and full guides:  
👉 **[https://naqawa.open-source-project.workers.dev/](https://naqawa.open-source-project.workers.dev/)**

---

<a name="-العربية"></a>
<div dir="rtl">

## العربية

> **إضافة متصفح مفتوحة المصدر ومجانية 100% لعزل الموسيقى والآلات عن مقاطع اليوتيوب بالذكاء الاصطناعي مع مزامنة الصوت والصورة.**

</div>

### ✨ المميزات الرئيسية
- ⚡ **المزامنة (Drift Guard):** تطابق بين الفيديو و الصوت حتى عند التقديم وتغيير سرعات التشغيل.
- 🧠 **الذكاء اصطناعي (Demucs v4):** عزل الآلات الموسيقية بدقة جيدة مع الحفاظ على نقاء الصوت البشري.
- ☁️ **دعم التشغيل السحابي:** توفير كود برمجي يسمح بمعالجة سريعة عبر كروت شاشة Google Colab مجاناً (Tesla T4 GPU).
- 💻 **تشغيل محلي بخصوصية مطلقة:** تشغيل مباشر على حاسوبك عبر المعالج (**CPU**) أو كرت الشاشة (**NVIDIA CUDA GPU**) دون رفع أي بيانات.

### 🚀 طريقة التثبيت في 3 خطوات (Chrome / Edge / Brave):

1. **حمّل الإضافة:** قم بتحميل ملف [`naqawa.zip`](https://github.com/saborbz/naqawa/raw/main/naqawa.zip) وفك الضغط عنه في أي مجلد على جهازك.
2. **افتح إدارة الإضافات:** في متصفحك، توجه إلى الرابط `chrome://extensions` (أو `edge://extensions`).
3. **فعّل وضع المطور:** فعّل **وضع المطور (Developer mode)** من الزاوية العلوية، ثم اضغط على زر **تحميل حزمة غير مضغوطة (Load unpacked)** واختر مجلد الإضافة.

### ⚠️ المشاكل المعروفة والعيوب الحالية
- ⏱️ **تأخير بسيط في المزامنة:** قد يحدث تأخير بسيط في مزامنة الصوت والصورة عند تقديم الفيديو.
- 🎵 **بقايا نغمات موسيقية:** احتمال سماع بعض البقايا الموسيقية نظراً لأن الذكاء الاصطناعي لا يعزل الموسيقى بنسبة 100%.
- 🔄 **تداخل صوت الفيديو السابق:** عند الانتقال لفيديو آخر بعد استخدام الإضافة قد يستمر صوت الفيديو السابق إلا إذا قمت بإعادة تحميل الصفحة.
- ☁️ **أخطاء في التشغيل السحابي:** وجود بعض المشاكل غير المستقرة في خيار المعالجة السحابية، تحديدا في كود Google Colab.
- 💻 **غير مُجرّب على ويندوز:** خيار المعالجة المحلية لم يتم اختباره بعد على أنظمة Windows.

### 📖الموقع الرسمي والشرح التفاعلي:
تفضل بزيارة الموقع الرسمي للاطلاع على الشرح التفاعلي وأوامر التثبيت:  
👉 **[https://naqawa.open-source-project.workers.dev/](https://naqawa.open-source-project.workers.dev/)**

</div>
