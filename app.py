from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'kelompok8_mykost_key'

# --- DATABASE SIMULASI ---
# Data user untuk login
users_db = {
    "admin": {"password": "123", "full_name": "Administrator", "username": "admin", "role": "Pencari Kost"}
}
current_login = None

# Data Agen Simulasi (Gunakan ID yang konsisten)
agen_db = [
    {"id": 1, "nama": "Budi Santoso", "rating": "4.8", "spesialis": "Bekasi Barat", "foto": "https://i.pravatar.cc/150?u=1"},
    {"id": 2, "nama": "Siti Aminah", "rating": "4.9", "spesialis": "Bekasi Timur", "foto": "https://i.pravatar.cc/150?u=2"},
    {"id": 3, "nama": "Andi Wijaya", "rating": "4.7", "spesialis": "Rawalumbu", "foto": "https://i.pravatar.cc/150?u=3"}
]

@app.route('/')
def index():
    user_data = users_db.get(current_login) if current_login else None
    return render_template('index.html', user=user_data)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        users_db[username] = {
            "password": request.form.get('password'),
            "full_name": request.form.get('full_name'),
            "username": username,
            "role": "Pencari Kost"
        }
        flash("Registrasi Berhasil!", "success")
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/auth', methods=['POST'])
def auth():
    global current_login
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users_db and users_db[username]['password'] == password:
        current_login = username
        return redirect(url_for('preferences_page'))
    flash("Username atau Password salah!", "danger")
    return redirect(url_for('index'))

@app.route('/preferences')
def preferences_page():
    if not current_login: return redirect(url_for('index'))
    return render_template('preferences.html', user=users_db[current_login])

@app.route('/search-kost', methods=['POST'])
def search_kost():
    if not current_login: return redirect(url_for('index'))
    lokasi = request.form.get('lokasi', 'Bekasi')
    
    # PENTING: Menambahkan 'id': i agar kost.id di HTML tidak kosong
    data_pilihan = [
        {
            "id": i, 
            "nama": f"Kost Exclusive {i}", 
            "alamat": f"Jl. Raya Bekasi No.{i}", 
            "harga": "1.500.000", 
            "image": f"https://images.unsplash.com/photo-1522771739844-649f6d1752a2?w=500&sig={i}"
        } for i in range(1, 11)
    ]
    return render_template('search_success.html', lokasi=lokasi, kost_data=data_pilihan, user=users_db[current_login])

# --- RUTE PILIH AGEN (ID Kost ditangkap di sini) ---
@app.route('/pilih-agen/<int:kost_id>')
def pilih_agen(kost_id):
    if not current_login: return redirect(url_for('index'))
    # Menampilkan daftar agen yang tersedia
    return render_template('pilih_agen.html', 
                           agen_list=agen_db, 
                           kost_id=kost_id, 
                           user=users_db[current_login])

# --- RUTE PEMBAYARAN (Membawa ID Kost dan ID Agen) ---
@app.route('/pembayaran/<int:kost_id>/<int:agen_id>')
def pembayaran(kost_id, agen_id):
    if not current_login: return redirect(url_for('index'))
    
    # Cari data agen berdasarkan ID
    agen = next((a for a in agen_db if a['id'] == agen_id), None)
    if not agen:
        flash("Agen tidak ditemukan!", "warning")
        return redirect(url_for('preferences_page'))
        
    return render_template('pembayaran.html', 
                           kost_id=kost_id, 
                           agen=agen, 
                           harga="1.500.000", 
                           user=users_db[current_login])

# --- RUTE PROSES BAYAR & STRUK SPOTIFY ---
@app.route('/proses-bayar', methods=['POST'])
def proses_bayar():
    if not current_login: return redirect(url_for('index'))
    
    metode = request.form.get('metode_pembayaran', 'Transfer Bank')
    
    # Data simulasi untuk Struk ala Spotify
    struk_data = {
        "no_transaksi": "MYKST-REC-202603",
        "tanggal": "26 Maret 2026",
        "total": "1.500.000",
        "metode": metode,
        "nama_user": users_db[current_login]['full_name']
    }
    return render_template('struk.html', struk=struk_data, user=users_db[current_login])

@app.route('/progress')
def progress():
    if not current_login: return redirect(url_for('index'))
    steps = [
        {"title": "Pembayaran Berhasil", "status": "done", "desc": "Dana aman di sistem MyKost."},
        {"title": "Konfirmasi Agen", "status": "active", "desc": "Agen sedang menuju lokasi kost."},
        {"title": "Serah Terima Kunci", "status": "waiting", "desc": "Penyerahan kunci dan tanda tangan kontrak."},
        {"title": "Selesai", "status": "waiting", "desc": "Selamat menempati kost baru!"}
    ]
    return render_template('progress.html', steps=steps, user=users_db[current_login])

@app.route('/logout')
def logout():
    global current_login
    current_login = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Pastikan port sesuai dengan yang Anda akses di browser (8000)
    app.run(debug=True, port=8000)