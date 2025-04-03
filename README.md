# KostTicket

KostTicket adalah platform pelaporan masalah terkait kost yang memungkinkan penghuni kost untuk melaporkan masalah dan pemilik/admin kost untuk mengelola tiket pelaporan tersebut.

![KostTicket Dashboard](https://placeholder-for-screenshot.png)

## Fitur Utama

### Untuk Pengguna (Penghuni Kost)
- **Autentikasi Pengguna**: Pendaftaran dan login yang aman
- **Pelaporan Masalah**: Membuat tiket pelaporan masalah dengan judul dan deskripsi
- **Pelacakan Status**: Melihat status tiket (terbuka, sedang diproses, selesai)
- **Komentar**: Menambahkan komentar pada tiket yang belum selesai
- **Notifikasi Real-time**: Menerima notifikasi saat status tiket berubah
- **Notifikasi Email**: Menerima email saat ada pembaruan pada tiket

### Untuk Admin (Pemilik/Pengelola Kost)
- **Dashboard Admin**: Tampilan khusus untuk mengelola semua tiket
- **Manajemen Tiket**: Melihat, memfilter, dan mengubah status tiket
- **Statistik**: Melihat jumlah tiket berdasarkan status
- **Notifikasi Real-time**: Menerima notifikasi saat tiket baru dibuat atau komentar ditambahkan
- **Task Queue**: Sistem antrian tugas untuk memproses notifikasi, email, dan tugas lainnya secara asinkron
- **Auto-assignment**: Penugasan tiket secara otomatis ke admin

## Teknologi yang Digunakan

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (default Django)
- **Real-time Communication**: Django Channels dan WebSocket
- **Task Queue**: Sistem antrian tugas kustom untuk pemrosesan asinkron
- **Email**: Django Email Backend
- **ASGI Server**: Daphne

## Instalasi

### Prasyarat
- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- virtualenv (disarankan)

### Langkah-langkah Instalasi

1. **Clone repositori**
   ```bash
   git clone https://github.com/yourusername/kostiket.git
   cd kostiket
   ```

2. **Buat dan aktifkan virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Untuk Linux/Mac
   # ATAU
   .venv\Scripts\activate  # Untuk Windows
   ```

3. **Instal dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan migrasi database**
   ```bash
   python manage.py migrate
   ```

5. **Buat superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Buat file run_server.sh (jika belum ada)**
   ```bash
   echo '#!/bin/bash
   python manage.py runserver 0.0.0.0:8000 &
   daphne -p 8001 core.asgi:application
   ' > run_server.sh
   chmod +x run_server.sh
   ```

## Menjalankan Aplikasi

1. **Jalankan server**
   ```bash
   ./run_server.sh
   ```

2. **Akses aplikasi**
   - Buka browser dan kunjungi: http://127.0.0.1:8000
   - Django development server berjalan di port 8000 (untuk static files dan HTTP)
   - Daphne ASGI server berjalan di port 8001 (untuk WebSocket)
   - Task processor berjalan di background (untuk memproses tugas dari antrian)

3. **Monitoring Task Queue**
   - Admin dapat melihat status task queue di dashboard admin
   - Tugas yang menunggu akan ditampilkan dengan status dan waktu pembuatan
   - Tugas akan diproses secara otomatis oleh task processor
## Cara Penggunaan

### Untuk Pengguna (Penghuni Kost)

1. **Pendaftaran dan Login**
   - Kunjungi halaman pendaftaran dan buat akun baru
   - Login dengan username dan password yang telah dibuat

2. **Membuat Tiket Baru**
   - Dari dashboard, klik tombol "Buat Tiket"
   - Isi formulir dengan judul dan deskripsi masalah
   - Klik "Simpan" untuk membuat tiket

3. **Melihat Tiket**
   - Semua tiket yang Anda buat akan muncul di dashboard
   - Klik pada tiket untuk melihat detail dan status terkini

4. **Menambahkan Komentar**
   - Di halaman detail tiket, tambahkan komentar jika diperlukan
   - Komentar tidak dapat ditambahkan pada tiket yang sudah selesai

### Untuk Admin (Pemilik/Pengelola Kost)

1. **Login sebagai Admin**
   - Login dengan akun admin yang telah dibuat
   - Anda akan otomatis diarahkan ke dashboard admin

2. **Melihat dan Mengelola Tiket**
   - Dashboard admin menampilkan semua tiket dengan statistik
   - Gunakan filter untuk melihat tiket berdasarkan status
   - Klik pada tiket untuk melihat detail

3. **Mengubah Status Tiket**
   - Di halaman detail tiket, gunakan dropdown untuk mengubah status
   - Status dapat diubah menjadi: Terbuka, Sedang Diproses, atau Selesai
   - Perubahan status akan memicu tugas di task queue untuk mengirim notifikasi

4. **Mengelola Notifikasi**
   - Notifikasi akan muncul di dashboard admin
   - Badge di navbar menunjukkan jumlah notifikasi yang belum dibaca

5. **Memantau Task Queue**
   - Dashboard admin menampilkan daftar tugas yang sedang menunggu di antrian
   - Tugas-tugas ini termasuk pengiriman notifikasi, email, dan pemrosesan tiket
   - Task processor akan menjalankan tugas-tugas ini secara otomatis di background
   - Tugas yang dijadwalkan akan dijalankan pada waktu yang ditentukan

## Struktur Proyek

```
kostiket/
├── accounts/              # Aplikasi untuk manajemen pengguna
├── core/                  # Konfigurasi utama Django
├── static/                # File statis (CSS, JS)
│   ├── css/
│   └── js/
├── templates/             # Template HTML
│   ├── accounts/          # Template untuk autentikasi dan dashboard pengguna
│   ├── base/              # Template dasar yang digunakan oleh semua halaman
│   ├── emails/            # Template untuk email notifikasi
│   └── tickets/           # Template untuk manajemen tiket
├── tickets/               # Aplikasi untuk manajemen tiket
│   ├── management/        # Management commands
│   │   └── commands/      # Custom Django commands
│   │       └── process_tasks.py  # Command untuk memproses task queue
│   ├── models.py          # Model data (Ticket, Comment, Notification, Task)
│   ├── views.py           # View untuk menangani request
│   ├── task_manager.py    # Manager untuk task queue
│   └── ...                # File lainnya
├── manage.py              # Script manajemen Django
├── run_server.sh          # Script untuk menjalankan server dan task processor
└── README.md              # Dokumentasi proyek
```

## Kontribusi

Jika Anda ingin berkontribusi pada proyek ini, silakan fork repositori, buat branch fitur, dan kirim pull request.

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
