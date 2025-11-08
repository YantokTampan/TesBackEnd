from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import time
import random
import os

# Inisialisasi Flask dan SocketIO
app = Flask(__name__)
# CORS (Cross-Origin Resource Sharing) penting agar 
# browser mengizinkan koneksi dari HTML ke server ini
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

# Daftar semua slot parkir Anda
SEMUA_SLOT = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]

# --- SOLUSI 1: BUAT "MEMORI" SERVER ---
# Inisialisasi memori dengan semua slot kosong saat server pertama kali menyala
status_parkir_saat_ini = {slot: 'kosong' for slot in SEMUA_SLOT}


# Fungsi ini akan berjalan di background untuk simulasi
def simulasi_parkir():
    """
    PERBAIKAN: Mengirim data BATCH (semua slot) setiap 1 detik
    agar cocok dengan app.js
    """
    print("Simulasi parkir (Mode Batch) dimulai...")
    
    # Gunakan 'global' untuk memberitahu bahwa kita ingin mengubah variabel 'memori'
    global status_parkir_saat_ini
    
    while True:
        # 1. Buat satu objek (dictionary) untuk menampung status batch baru
        batch_data_baru = {}
        
        # 2. Isi objek tersebut dengan status acak untuk setiap slot
        for slot in SEMUA_SLOT:
            status_terpilih = random.choice(['penuh', 'kosong'])
            batch_data_baru[slot] = status_terpilih
            
        # --- SOLUSI 2: UPDATE "MEMORI" SERVER ---
        # 3. Simpan status baru ini ke "memori" server
        status_parkir_saat_ini = batch_data_baru
        
        # 4. Mengirim (emit) SELURUH BATCH data dari memori ke SEMUA klien
        #    Menggunakan 'status_parkir_batch' agar cocok dengan app.js
        socketio.emit('status_parkir_batch', status_parkir_saat_ini)
        print(f"Mengirim update batch: {len(status_parkir_saat_ini)} slot")
        
        # 5. Tunggu 1 detik (sesuai permintaan Anda sebelumnya)
        socketio.sleep(1)


# Event handler ketika website (front-end) terhubung
@socketio.on('connect')
def handle_connect():
    print('Sebuah website telah terhubung!')
    
    # --- SOLUSI 3: KIRIM DATA DARI "MEMORI" ---
    # Saat klien baru terhubung (atau refresh), kirim status
    # yang tersimpan di 'status_parkir_saat_ini', BUKAN data "semua kosong".
    # 'emit' di sini HANYA akan mengirim ke klien yang BARU terhubung.
    socketio.emit('status_parkir_batch', status_parkir_saat_ini)
    print(f"Mengirim status dari memori: {len(status_parkir_saat_ini)} slot terkirim ke klien baru.")


# Event handler ketika website terputus
@socketio.on('disconnect')
def handle_disconnect():
    print('Koneksi website terputus.')

# ... (sisa komentar Anda) ...


# Bagian ini sudah benar untuk deployment
if __name__ == '__main__':
    # 1. Dapatkan Port dari variabel lingkungan Render
    #    Jika tidak ada (saat di lokal), gunakan 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Menjalankan server di port {port}")
    
    # 2. Mulai thread background untuk simulasi
    socketio.start_background_task(target=simulasi_parkir)
    
    # 3. Jalankan server
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=port, 
                 debug=False,
                 allow_unsafe_werkzeug=True)
