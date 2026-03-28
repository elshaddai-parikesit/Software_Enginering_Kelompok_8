from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'kelompok8_mykost_key'

DB_FILE = 'users.json'

def get_all_users():
    if not os.path.exists(DB_FILE):
        default_data = {"admin": {"password": "123", "full_name": "Administrator", "username": "admin", "role": "Pencari Kost"}}
        with open(DB_FILE, 'w') as f: json.dump(default_data, f, indent=4)
        return default_data
    with open(DB_FILE, 'r') as f:
        try: return json.load(f)
        except: return {}

current_login = None

AGEN_DB = [
    {"id": 1, "nama": "Budi Santoso", "rating": "4.8", "spesialis": "Bekasi Barat", "wa": "62812345678"},
    {"id": 2, "nama": "Siti Aminah", "rating": "4.9", "spesialis": "Bekasi Timur", "wa": "62812345679"},
    {"id": 3, "nama": "Andi Wijaya", "rating": "4.7", "spesialis": "Rawalumbu", "wa": "62812345670"}
]

@app.route('/')
def index():
    current_users = get_all_users()
    user_data = current_users.get(current_login) if current_login else None
    
    # 1. Data Promo (Bisa digeser/scroll horizontal)
    promo_data = [
        {"id": p, "nama": f"Promo Kost MyKost {p}", "img": f"https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&sig={p}"} 
        for p in range(1, 6)
    ]

    # 2. Data Kost (Dibuat banyak untuk simulasi 6 kolom)
    nama_list = ["Arditya Tembalang", "Aurea SCBD", "Mandira Pluit", "Moza Hill Pakis", "Galaxy Suite", "Mawar Rawalumbu"]
    lokasi_list = ["Pedalangan, Banyumanik", "Senayan, Kebayoran Baru", "Pluit, Penjaringan", "Tirtomoyo, Pakis", "Bekasi Selatan", "Bekasi Timur"]
    jarak_list = ["793 m dari Politeknik Negeri Semarang", "923 m dari Stasiun MRT Istora Mandiri", "4.1 km dari Stasiun Angke", "1.0 km dari Universitas BINUS", "500 m dari Mall Grand Galaxy", "2 km dari Tol Bekasi Timur"]
    
    kost_data = []
    for i in range(1, 19): # 18 Data agar bisa 6 per baris x 3 baris
        idx = i % 6
        kost_data.append({
            "id": i,
            "nama": f"MyKost {nama_list[idx]} {i}",
            "lokasi": lokasi_list[idx],
            "jarak": jarak_list[idx],
            "harga": "{:,.0f}".format(1718000 + (i * 50000)).replace(',', '.'),
            "img": f"https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&sig={i}"
        })

    # 3. Data Testimoni (10 data, 5 kolom x 2 baris)
    testimoni_data = [
        {"nama": f"Penyewa {t}", "peran": "Mahasiswa", "teks": f"Kos ini sangat nyaman dan strategis! Fasilitas lengkap. (Testimoni {t})"} 
        for t in range(1, 11)
    ]

    return render_template('index.html', user=user_data, promo=promo_data, kosts=kost_data, testimoni=testimoni_data)

# --- PERBAIKAN FITUR REGISTRASI ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        users = get_all_users()
        if username in users:
            flash("Username sudah digunakan! Coba yang lain.", "danger")
            return redirect(url_for('register'))
            
        users[username] = {"password": password, "full_name": full_name, "role": "Pencari Kost"}
        with open(DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
            
        flash("Registrasi berhasil! Silakan login.", "success")
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/auth', methods=['POST'])
def auth():
    global current_login
    current_users = get_all_users()
    username = request.form.get('username')
    password = request.form.get('password')
    if username in current_users and current_users[username]['password'] == password:
        current_login = username
        return redirect(url_for('index'))
    flash("Username/Password salah!", "danger")
    return redirect(url_for('index'))

@app.route('/pembayaran/<int:kost_id>/<int:agen_id>')
def pembayaran(kost_id, agen_id):
    if not current_login: return redirect(url_for('index'))
    harga_fix = "{:,.0f}".format(1718000 + (kost_id * 50000)).replace(',', '.')
    agen_data = next((a for a in AGEN_DB if a['id'] == agen_id), None)
    return render_template('pembayaran.html', kost_id=kost_id, agen=agen_data, harga=harga_fix, user=get_all_users()[current_login])

@app.route('/logout')
def logout():
    global current_login
    current_login = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)