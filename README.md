# 🤖 Bx-Website-Optimization-Latest 🚨 Protection Security Bypass

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-4.15%2B-green.svg)](https://selenium-python.readthedocs.io/)

Bot otomatis untuk mengirim komentar dengan backlink ke berbagai platform website menggunakan sistem template yang cerdas dan adaptive dengan machine learning capabilities. Serta memiliki kemampuan untuk melewati Protection Security pada website.

<img src="/backlink.jpg" width="600" alt="Bx-Website-Optimization-Latest">

## ✨ Fitur Utama

- 🎯 **Multi-Template Support** - WordPress, Wix, Forum, dan template custom
- 🧠 **Smart Auto-Detection** - Mengenali platform website secara otomatis
- 📚 **Machine Learning** - Belajar dari setiap attempt untuk meningkatkan success rate
- 💾 **Advanced Caching** - Menyimpan pattern yang berhasil untuk optimasi
- 🚫 **Popup Handler** - Menangani popup Google OAuth dan cookie consent
- 📊 **Detailed Reporting** - Laporan lengkap hasil eksekusi
- 🔄 **Auto-Retry** - Retry otomatis jika terjadi kegagalan
- 🔄 **Resume Feature** - Melanjutkan dari URL yang belum diproses
- 💻 **Command Line Interface** - Kontrol penuh via terminal
- 🔗 **Smart Link Processing** - Format link otomatis sesuai platform

## ✨ Latest Updates (v2.0.0) 🚨 Protection Security Bypass 🚨

- ✅ reCAPTCHA v2 Bypass
- ✅ Secureimg Bypass
- ✅ Honeypot Field Bypass
- ✅ Borlabs cookie Bypass

- ✅ Fix templates selector
- ✅ Fix error post

- ✅ Templates clean

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/Dzbackdor/Bx-Website-Optimization-Latest.git
cd Bx-Website-Optimization-Latest
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Chrome Browser
Pastikan Google Chrome terinstall di sistem Anda. Bot akan otomatis mendeteksi versi Chrome dan download ChromeDriver yang sesuai.

## ⚙️ Konfigurasi Wajib

### 1. **Konfigurasi API Key** 

```bash
📁 templates/                   
   ├── 📁 Wordpress/               
       ├── 📄 api_config.py        # ⚠️ Konfigurasi API Key
       ├── 📄 secureimg_solver.py  # ⚠️ Konfigurasi API Key 
```


### 2. **config.yaml** 
```yaml
# Data komentar default - WAJIB GANTI
comment_data:
  name: "John Doe"                     # ⚠️ GANTI dengan nama Anda
  email: "john.doe@example.com"        # ⚠️ GANTI dengan email Anda
  website: "https://yourwebsite.com"   # ⚠️ GANTI dengan website Anda
  comment_file: "komen.txt"

# Pengaturan aplikasi
app:
  name: "Backlink"
  version: "2.0.0"
  delay_between_comments: 5    # Jeda antar komentar (detik)
  max_retries: 3              # Maksimal retry per URL
  timeout: 30                 # Timeout request
  page_load_timeout: 30       # Timeout load halaman
  element_wait_timeout: 15    # Timeout tunggu element


# Cache settings
cache:
  enabled: true
  file: "cache/template_cache.json"
  element_cache_file: "cache/element_cache.json"
  ttl: 3600
  element_ttl: 0              # 0 = permanent cache

# Logging
logging:
  disabled: false             # true = matikan file logging
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  file: "bot.log"
```

### 3. **list.txt** - Daftar URL Target (WAJIB)
```
https://example1.com/blog/post1
https://example2.com/article/sample
https://wordpress-site.com/news/latest
https://wix-site.com/blog/update
```

### 4. **komen.txt** - Template Komentar dengan Keyword Links (WAJIB)
```
Artikel yang sangat menarik! {Kunjungi juga|https://yourwebsite.com}
Terima kasih atas informasinya. {Lihat juga|https://yourwebsite.com}
Perspektif yang bagus. {Info lebih lanjut|https://yourwebsite.com}
Postingan yang bermanfaat. {Cek juga|https://yourwebsite.com}
Sangat membantu! {Baca selengkapnya|https://yourwebsite.com}
Konten berkualitas. {Klik di sini|https://yourwebsite.com}
```

**Format Keyword Links:** `{anchor_text|url}`
- `{Kunjungi juga|https://yourwebsite.com}` → Akan diproses menjadi link sesuai platform
- WordPress: `<a href="https://yourwebsite.com">Kunjungi juga</a>`
- Forum: `[url=https://yourwebsite.com]Kunjungi juga[/url]`
- Plain text: `Kunjungi juga (https://yourwebsite.com)`

### 4. **akun.txt** - Database Akun
```
user1@gmail.com
password123
user2@yahoo.com
mypassword456
user3@hotmail.com
secretpass789
```

⚠️ **Penting:**
- Gunakan akun yang valid dan aktif
- Pastikan password benar
- Email harus sesuai dengan akun


## 🎯 Cara Penggunaan

### Mode Dasar
```bash
# Jalankan dengan tampilan browser (default dengan GUI dan list.txt) 
python main.py

# Mode background (headless)
python main.py --headless
```

### Mode Advanced
```bash
# Test satu URL saja
python main.py test https://example.com/blog/post

# Gunakan file URL custom dengan mode GUI dan resume
python main.py list custom_url.txt

# Gunakan file custom dengan mode HEADLESS dan resume
python main.py --headless list custom_url.txt

# Kombinasi lengkap
python main.py --headless --no-resume list custom_url.txt
```

### Resume Feature
```bash
# Default: Otomatis skip URL yang sudah berhasil
python main.py

# Matikan resume (proses semua URL dari awal)
python main.py --no-resume
```

## 📋 Command Line Options

```bash
python main.py -h
[OPTIONS] [COMMAND] [FILE]

✅ Argumen yang dapat digunakan
Usage:
  python main.py                                           # Mode GUI default, Menggunakan list.txt
  python main.py list <file>                               # Gunakan file URL custom dengan filter
  python main.py test <url>                                # Test satu URL saja
  python main.py --headless                                # Mode background tanpa tampilan browser
  python main.py --gui                                     # Mode GUI (ada tampilan browser)
  python main.py --no-resume                               # Load semua URLs tanpa filter

Contoh:
  python main.py list urls.txt                             # Filter URLs yang sudah diproses
  python main.py --no-resume list urls.txt                 # Load semua URLs dari awal
  python main.py --headless list urls.txt                  # Background mode dengan filter
  python main.py test https://example.com/blog/post        # Test satu URL

Options:
  --headless    Jalankan browser di background (tanpa tampilan)
  --gui         Mode GUI (mengaktifkan tampilan browser)
  --no-resume   Load semua URLs dari awal (tidak filter yang sudah diproses)

Resume Feature:
  🔄 Default: Filter URLs yang sudah berhasil diproses
  🚫 --no-resume: Load semua URLs tanpa melihat riwayat
```

## 🔗 Sistem Keyword Links

Bot mendukung **smart link processing** yang otomatis menyesuaikan format link sesuai platform:

### Format Input (komen.txt):
```
{anchor_text|url}
```

### Output Berdasarkan Platform:

#### WordPress (HTML):
```html
<a href="https://yourwebsite.com" target="_blank">Kunjungi juga</a>
```

#### Forum (BBCode):
```bbcode
[url=https://yourwebsite.com]Kunjungi juga[/url]
```

#### Plain Text:
```
Kunjungi juga (https://yourwebsite.com)
```

#### Wix (Custom Processing):
- Bot akan menggunakan rich text editor Wix
- Otomatis membuat link dengan formatting yang sesuai

## 🧠 Sistem Pembelajaran (Machine Learning)

Bot menggunakan **advanced machine learning** untuk meningkatkan performa:

### Learning Features:
- 📊 **Success Rate Tracking** - Melacak tingkat keberhasilan per domain
- 🎯 **Pattern Recognition** - Mengenali pattern URL, text, dan alert yang sukses
- 💾 **Domain-Specific Learning** - Menyimpan konfigurasi optimal per domain
- 🔄 **Adaptive Selectors** - Menyesuaikan selector berdasarkan pengalaman
- 📈 **Performance Optimization** - Otomatis optimasi berdasarkan historical data

### Cache System:
```
cache/
├── template_cache.json          # Template compatibility cache
├── element_cache.json           # Element selector cache
├── success_learning_data.json   # Learning history & patterns
└── domain_success_patterns.json # Domain-specific success patterns
```

## 🎨 Template yang Didukung

### 1. **WordPress** (Auto-Detection)
- ✅ Deteksi otomatis berdasarkan `wp-content`, `wp-includes`
- ✅ Support comment form standard WordPress
- ✅ Smart selector detection untuk theme custom
- ✅ Auto-learning domain baru
- ✅ HTML link formatting

### 2. **Wix** (Auto-Detection)
- ✅ Deteksi berdasarkan `static.wixstatic.com`, `wix-site`
- ✅ Advanced popup handling (Google OAuth, Cookie consent)
- ✅ Support rich text editor Wix
- ✅ Browser cleanup setelah setiap URL
- ✅ Custom link processing untuk editor Wix

### 3. **Auto-Detection System**
- 🤖 Sistem otomatis mengenali platform website
- 🧠 Tidak perlu konfigurasi manual domain
- 📚 Learning dari setiap attempt
- 🎯 Adaptive template selection
- 🔗 Smart link format detection

## 📊 Hasil Eksekusi

Setiap run menghasilkan folder timestamped di `results/`:

```
results/20240115_143022/
├── success_20240115_143022.txt      # URL yang berhasil
├── failed_20240115_143022.txt       # URL yang gagal  
├── no_template_20240115_143022.txt  # URL tanpa template
└── summary_20240115_143022.txt      # Ringkasan eksekusi dengan statistik
```

### Resume System
- 🔄 **Otomatis skip** URL yang sudah berhasil diproses
- 📊 **Progress tracking** dengan statistik lengkap
- 🎯 **Smart continuation** dari URL terakhir yang gagal

## 🔧 Troubleshooting

### Element Tidak Ditemukan
- ✅ Bot otomatis mencoba selector alternatif
- ✅ Learning system menyimpan selector yang berhasil
- ✅ Cache mempercepat detection di run berikutnya
- ✅ Smart detection mengadaptasi website baru

### Keyword Links Tidak Bekerja
- ✅ Pastikan format `{text|url}` benar
- ✅ Bot otomatis detect platform dan format link
- ✅ Cek log untuk melihat format yang digunakan
- ✅ Template Wix menggunakan custom processing

### Popup Mengganggu
- ✅ Wix template include popup handler otomatis
- ✅ Google OAuth popup ditangani otomatis
- ✅ Cookie consent banner di-dismiss otomatis
- ✅ Browser cleanup setelah setiap URL (Wix)

### Chrome Driver Issues
- ✅ Bot otomatis detect versi Chrome
- ✅ Download ChromeDriver yang sesuai
- ✅ Fallback ke konfigurasi minimal jika error
- ✅ Support Chrome 130+ dan versi lama

### Login Issues
- ✅ Pastikan format `email:password` di akun.txt
- ✅ Gunakan akun yang valid dan aktif
- ✅ Cek apakah website memerlukan 2FA
- ✅ Bot akan skip login jika tidak diperlukan

## 🔒 Keamanan & Privacy


### Best Practices
- ✅ Gunakan akun terpisah untuk bot
- ✅ Jangan gunakan akun utama/pribadi
- ✅ Backup file akun.txt secara terpisah
- ✅ Gunakan password yang kuat


## 💡 Tips & Best Practices

### Optimasi Performa
```yaml
# config.yaml untuk production
app:
  delay_between_comments: 3  # Lebih cepat tapi tetap aman
  
cache:
  element_ttl: 0           # Permanent cache untuk speed
  
```

### Komentar Berkualitas
```
# komen.txt - Variasi yang natural
Artikel yang sangat informatif! {Baca juga|https://yourwebsite.com}
Terima kasih sudah berbagi. {Lihat tips lainnya|https://yourwebsite.com}
Perspektif yang menarik. {Kunjungi blog kami|https://yourwebsite.com}
Sangat membantu! {Info lebih lengkap|https://yourwebsite.com}
Konten berkualitas tinggi. {Cek artikel serupa|https://yourwebsite.com}
```

### URL Management
```
# list.txt - Organisasi yang baik
# WordPress Sites
https://wordpress-site1.com/blog/post1
https://wordpress-site2.com/article/sample

# Wix Sites  
https://wix-site1.com/blog/update
https://wix-site2.com/news/latest

# Forum Sites
https://forum-site1.com/thread/discussion
```

## 🚀 Advanced Features

### Smart Detection Capabilities
- 🧠 **Auto-Learning** - Bot belajar dari setiap website
- 🎯 **Pattern Recognition** - Mengenali success patterns
- 📊 **Success Rate Optimization** - Meningkatkan tingkat keberhasilan
- 🔄 **Adaptive Behavior** - Menyesuaikan strategi per domain

### Multi-Format Link Support
- 📝 **HTML** - `<a href="url">text</a>` untuk WordPress
- 🏷️ **BBCode** - `[url=link]text[/url]` untuk Forum
- 📋 **Markdown** - `[text](url)` untuk platform Markdown
- 🔗 **Plain Text** - `text (url)` untuk platform sederhana
- ⚡ **Custom** - Processing khusus untuk Wix dan platform unik

### Browser Optimization
- 🔧 **Auto Chrome Detection** - Deteksi versi Chrome otomatis
- 🚀 **Performance Tuning** - Optimasi speed dan resource
- 🛡️ **Anti-Detection** - Bypass bot detection systems
- 🧹 **Smart Cleanup** - Browser cleanup per template

## ⚠️ Disclaimer & Etika

### Penggunaan yang Bertanggung Jawab
- 🎓 **Tool ini untuk tujuan edukasi dan testing**
- ⚖️ **Pastikan mematuhi Terms of Service website target**
- 🤝 **Gunakan dengan bijak dan bertanggung jawab**
- 🚫 **Jangan spam atau abuse sistem**
- 👤 **Akun yang digunakan adalah tanggung jawab user**
- ⏰ **Respect website dengan delay yang wajar**
- 💬 **Buat komentar yang berkualitas dan relevan**

### Legal Notice
- ⚖️ Developer tidak bertanggung jawab atas penyalahgunaan tool
- 🔒 User bertanggung jawab penuh atas aktivitas yang dilakukan
- 📋 Pastikan mematuhi hukum dan regulasi yang berlaku
- 🌐 Respect website owners dan community guidelines


## 🙏 Acknowledgments

- [Selenium](https://selenium.dev/) - Web automation framework
- [Undetected ChromeDriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Anti-detection Chrome driver
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [PyYAML](https://pyyaml.org/) - YAML configuration handling
- [Colorama](https://pypi.org/project/colorama/) - Terminal color output

---



**Made with ❤️ by Dzone**
