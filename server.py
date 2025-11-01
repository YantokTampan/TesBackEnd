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
    UNTUK SEMUA SLOT sekaligus setiap 3 detik.
    """
    print("Simulasi parkir (Mode Batch) dimulai...")
    while True:
        # 1. Buat satu objek (dictionary) untuk menampung semua status
        batch_data = {}
        
        # 2. Isi objek tersebut dengan status acak untuk setiap slot
        for slot in SEMUA_SLOT:
            status_terpilih = random.choice(['penuh', 'kosong'])
            batch_data[slot] = status_terpilih
            
        # 3. Mengirim (emit) SELURUH BATCH data dalam satu kali kirim
        #    Kita bisa tetap pakai event 'status_parkir' atau ganti nama
        #    (Mari kita ganti nama agar jelas)
        socketio.emit('status_parkir_batch', batch_data)
        print(f"Mengirim update batch: {len(batch_data)} slot")
        
        # 4. Tunggu 3 detik sebelum mengirim batch berikutnya
        socketio.sleep(3)


# Event handler ketika website (front-end) terhubung
@socketio.on('connect')
def handle_connect():
    print('Sebuah website telah terhubung!')
    
    # Kirim status awal (semua kosong) dalam format BATCH
    batch_data_awal = {}
    for slot in SEMUA_SLOT:
        batch_data_awal[slot] = 'kosong'
        
    socketio.emit('status_parkir_batch', batch_data_awal)
    print("Mengirim status batch awal (semua kosong).")

# Event handler ketika website terputus
@socketio.on('disconnect')
def handle_disconnect():
    print('Koneksi website terputus.')

# ... (sisa komentar Anda) ...


if __name__ == '__main__':
    print("Menjalankan server di http://localhost:5000")
    
    # Mulai thread background untuk simulasi
    socketio.start_background_task(target=simulasi_parkir)
    
    # Jalankan server
    # 'allow_unsafe_werkzeug=True' diperlukan untuk versi Flask/SocketIO terbaru
    socketio.run(app, port=5000, debug=True, allow_unsafe_werkzeug=True)
