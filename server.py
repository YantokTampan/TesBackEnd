from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import random

# Inisialisasi Flask dan SocketIO
app = Flask(__name__)
# CORS (Cross-Origin Resource Sharing) penting agar 
# browser mengizinkan koneksi dari HTML ke server ini
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

# Daftar semua slot parkir Anda
SEMUA_SLOT = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# Fungsi ini akan berjalan di background untuk simulasi
def simulasi_parkir():
    """
    Simulasi ini mengirimkan update status parkir
    secara acak setiap 3 detik.
    """
    print("Simulasi parkir dimulai...")
    while True:
        # Pilih slot acak
        slot_terpilih = random.choice(SEMUA_SLOT)
        
        # Pilih status acak
        status_terpilih = random.choice(['penuh', 'kosong'])
        
        # Buat data untuk dikirim
        data = {
            'slotId': slot_terpilih,
            'status': status_terpilih
        }
        
        # Mengirim (emit) data ke semua website yang terhubung
        # 'status_parkir' adalah nama event yang didengarkan oleh app.js
        socketio.emit('status_parkir', data)
        print(f"Mengirim update: {data}")
        
        # Tunggu 3 detik sebelum mengirim update berikutnya
        socketio.sleep(3)


# Event handler ketika website (front-end) terhubung
@socketio.on('connect')
def handle_connect():
    print('Sebuah website telah terhubung!')
    
    # Kirim status awal (semua kosong) saat baru terhubung
    for slot in SEMUA_SLOT:
        socketio.emit('status_parkir', {'slotId': slot, 'status': 'kosong'})

# Event handler ketika website terputus
@socketio.on('disconnect')
def handle_disconnect():
    print('Koneksi website terputus.')

# --- DI SINI ANDA INTEGRASIKAN LOGIKA YOLO ANDA ---
#
# Nanti, daripada menggunakan 'simulasi_parkir',
# program YOLO Anda akan memanggil fungsi seperti ini:
#
# def update_status_dari_yolo(slot_id, status):
#     data = {'slotId': slot_id, 'status': status}
#     socketio.emit('status_parkir', data)
#     print(f"YOLO update: {data}")
#
# ----------------------------------------------------


if __name__ == '__main__':
    print("Menjalankan server di http://localhost:5000")
    
    # Mulai thread background untuk simulasi
    socketio.start_background_task(target=simulasi_parkir)
    
    # Jalankan server
    # 'allow_unsafe_werkzeug=True' diperlukan untuk versi Flask/SocketIO terbaru
    socketio.run(app, port=5000, debug=True, allow_unsafe_werkzeug=True)