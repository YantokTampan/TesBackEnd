from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import random
import os  # <-- PERBAIKAN 1: Import 'os' untuk deployment

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
    PERBAIKAN 2: Mengembalikan simulasi ke mode SATU PER SATU
    agar cocok dengan app.js yang Anda unggah.
    """
    print("Simulasi parkir (Mode Satu per Satu) dimulai...")
    while True:
        # 1. Pilih slot acak
        slot_terpilih = random.choice(SEMUA_SLOT)
        
        # 2. Pilih status acak
        status_terpilih = random.choice(['penuh', 'kosong'])
        
        # 3. Buat data untuk dikirim
        data = {
            'slotId': slot_terpilih,
            'status': status_terpilih
        }
        
        # 4. Mengirim (emit) data SATUAN
        # Menggunakan 'status_parkir' agar cocok dengan app.js
        socketio.emit('status_parkir', data)
        print(f"Mengirim update: {data}")
        
        # 5. Tunggu 1 detik (sesuai file asli Anda)
        socketio.sleep(1)


# Event handler ketika website (front-end) terhubung
@socketio.on('connect')
def handle_connect():
    print('Sebuah website telah terhubung!')
    
    # PERBAIKAN 2: Kirim status awal (semua kosong) SATU PER SATU
    # agar cocok dengan app.js
    batch_data_awal = {}
    for slot in SEMUA_SLOT:
        socketio.emit('status_parkir', {'slotId': slot, 'status': 'kosong'})
        
    print("Mengirim status batch awal (semua kosong).")

# Event handler ketika website terputus
@socketio.on('disconnect')
def handle_disconnect():
    print('Koneksi website terputus.')

# ... (sisa komentar Anda) ...


# PERBAIKAN 1: Bagian ini diubah total untuk DEPLOYMENT
if __name__ == '__main__':
    # 1. Dapatkan Port dari variabel lingkungan Render
    #    Jika tidak ada (saat di lokal), gunakan 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Menjalankan server di port {port}")
    
    # 2. Mulai thread background untuk simulasi
    socketio.start_background_task(target=simulasi_parkir)
    
    # 3. Jalankan server di 0.0.0.0 (penting!), matikan debug, 
    #    dan gunakan port dari Render
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=port, 
                 debug=False,
                 allow_unsafe_werkzeug=True)



