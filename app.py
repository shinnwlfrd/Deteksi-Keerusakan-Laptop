import streamlit as st
from datetime import datetime

# =============================================================================
# [1] KONFIGURASI HALAMAN & CSS
# =============================================================================
st.set_page_config(
    page_title="Sistem Pakar Diagnosa Laptop",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load Material Icons & Custom CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    
    <style>
        /* GLOBAL THEME OVERRIDES */
        .stApp {
            background-color: #101622;
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }
        
        /* REMOVE STREAMLIT DEFAULT PADDING */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 700px;
        }

        /* CUSTOM UTILITIES */
        .glass-card {
            background: rgba(25, 34, 51, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .hero-section {
            background: linear-gradient(rgba(16, 22, 34, 0.7), rgba(16, 22, 34, 0.9)), 
                        url("https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            border-radius: 1.5rem;
            padding: 2.5rem 1.5rem;
            text-align: center;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        /* PRIMARY BUTTON STYLING (Blue Pill) */
        div.stButton > button[kind="primary"] {
            width: 100%;
            background-color: #135bec;
            color: white;
            border: none;
            border-radius: 9999px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 0 20px rgba(19, 91, 236, 0.3);
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #2563eb;
            transform: scale(1.02);
            box-shadow: 0 0 30px rgba(19, 91, 236, 0.5);
            color: white;
        }

        /* SECONDARY BUTTON STYLING (For Back Button - Transparent) */
        div.stButton > button[kind="secondary"] {
            background-color: transparent;
            border: 1px solid rgba(255,255,255,0.1);
            color: #94a3b8;
            border-radius: 50%;
            width: 42px;
            height: 42px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: rgba(255,255,255,0.1);
            color: white;
            border-color: rgba(255,255,255,0.3);
        }

        /* CHECKBOX STYLING */
        .stCheckbox label {
            color: #e2e8f0;
            font-size: 0.95rem;
        }

        /* EXPANDER STYLING */
        .streamlit-expanderHeader {
            background-color: #1a2230;
            border-radius: 0.75rem;
            color: white;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .streamlit-expanderContent {
            background-color: #1a2230;
            border-bottom-left-radius: 0.75rem;
            border-bottom-right-radius: 0.75rem;
            border: 1px solid rgba(255,255,255,0.05);
            border-top: none;
        }

        /* CUSTOM TYPOGRAPHY */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.025em;
        }
        
        /* PROGRESS BAR CUSTOM */
        .custom-progress-bg {
            background-color: #1e293b !important;
            border-radius: 9999px !important; /* FIXED SPACE TYPO HERE */
            height: 0.75rem !important;
            width: 100% !important;
            overflow: hidden !important;
            display: block !important;
        }
        .custom-progress-fill {
            height: 100% !important;
            border-radius: 9999px !important;
            transition: width 1s ease-in-out !important;
            display: block !important;
        }
        
        /* Fix for Streamlit markdown rendering */
        .element-container div[data-testid="stMarkdownContainer"] .custom-progress-bg {
            background-color: #1e293b !important;
            height: 0.75rem !important;
        }

    </style>
""", unsafe_allow_html=True)

# =============================================================================
# [2] LOGIKA SISTEM PAKAR (DATABASE & RULES)
# =============================================================================
THRESHOLD_CF = 0.4

SYMPTOMS = {
    "G001": {"text": "Layar gelap/hitam total, namun indikator power menyala", "category": "Layar"},
    "G002": {"text": "Layar sering berkedip (flickering) saat engsel digerakkan", "category": "Layar"},
    "G003": {"text": "Terdapat retakan fisik atau cairan bocor di dalam layar", "category": "Layar"},
    "G004": {"text": "Muncul titik/pixel warna-warni yang statis (Dead/Stuck Pixel)", "category": "Layar"},
    "G005": {"text": "Layar sentuh merespon acak tanpa disentuh (Ghost Touch)", "category": "Layar"},
    "G006": {"text": "Gambar di layar sangat redup, hanya terlihat jika disenter", "category": "Layar"},
    "G007": {"text": "Tampilan layar pecah-pecah (artefak) atau ada kotak-kotak aneh", "category": "Layar"},
    "G008": {"text": "Warna layar dominan satu warna (misal: kemerahan/kebiruan)", "category": "Layar"},
    "G009": {"text": "Layar menjadi putih polos (White Screen of Death)", "category": "Layar"},
    "G010": {"text": "Ada garis vertikal/horizontal tipis yang permanen", "category": "Layar"},
    "G011": {"text": "Baterai drop drastis (misal 100% ke 20% dalam hitungan menit)", "category": "Power"},
    "G012": {"text": "Laptop mendeteksi charger tapi persentase tidak naik (Plugged in, not charging)", "category": "Power"},
    "G013": {"text": "Konektor charger harus ditekuk/digoyang agar daya masuk", "category": "Power"},
    "G014": {"text": "Casing area baterai/keyboard melengkung atau terangkat", "category": "Power"},
    "G015": {"text": "Laptop mati total seketika saat kabel charger dicabut", "category": "Power"},
    "G016": {"text": "Adaptor charger sangat panas hingga sulit disentuh", "category": "Power"},
    "G017": {"text": "Muncul percikan api kecil saat mencolok charger ke laptop", "category": "Power"},
    "G018": {"text": "Indikator lampu baterai berkedip merah/oranye terus menerus", "category": "Power"},
    "G019": {"text": "Laptop sering mati sendiri secara acak meski baterai penuh", "category": "Power"},
    "G020": {"text": "Beberapa tombol keyboard mati/tidak merespon sama sekali", "category": "Input"},
    "G021": {"text": "Muncul karakter berulang terus menerus seolah tombol tertindih", "category": "Input"},
    "G022": {"text": "Tombol keyboard terasa lengket atau tidak membal saat ditekan", "category": "Input"},
    "G023": {"text": "Touchpad sama sekali tidak merespon sentuhan", "category": "Input"},
    "G024": {"text": "Kursor mouse bergerak liar sendiri (drifting)", "category": "Input"},
    "G025": {"text": "Klik kiri/kanan pada touchpad tidak berfungsi", "category": "Input"},
    "G026": {"text": "Fingerprint reader panas atau tidak mendeteksi jari", "category": "Input"},
    "G027": {"text": "Tombol power sulit ditekan atau masuk ke dalam", "category": "Input"},
    "G028": {"text": "Suara speaker pecah/sember saat volume diatas 50%", "category": "Audio"},
    "G029": {"text": "Tidak ada suara sama sekali (tanda silang merah di ikon speaker)", "category": "Audio"},
    "G030": {"text": "Suara hanya keluar sebelah (kiri/kanan saja)", "category": "Audio"},
    "G031": {"text": "Headset tidak terdeteksi saat dicolok ke jack audio", "category": "Audio"},
    "G032": {"text": "Ada suara dengung (static noise) konstan dari speaker/headset", "category": "Audio"},
    "G033": {"text": "Webcam menampilkan layar hitam blank", "category": "Audio"},
    "G034": {"text": "Lampu indikator webcam menyala tapi tidak ada gambar", "category": "Audio"},
    "G035": {"text": "Mikrofon lawan bicara mendengar suara kita sangat kecil/kresek", "category": "Audio"},
    "G036": {"text": "Proses copy-paste file sangat lambat (speed drop ke 0 KB/s)", "category": "Storage"},
    "G037": {"text": "Terdengar bunyi 'tek-tek' atau gesekan logam dari dalam laptop", "category": "Storage"},
    "G038": {"text": "Muncul pesan 'Boot Device Not Found' atau 'No Media'", "category": "Storage"},
    "G039": {"text": "Drive partisi hilang (misal Drive D: tidak ada)", "category": "Storage"},
    "G040": {"text": "File sering corrupt atau tidak bisa dibuka tiba-tiba", "category": "Storage"},
    "G041": {"text": "Kapasitas SSD/HDD penuh padahal data sedikit", "category": "Storage"},
    "G042": {"text": "Proses booting Windows sangat lama (> 5 menit)", "category": "Storage"},
    "G043": {"text": "Sering muncul pesan 'Disk Usage 100%' di Task Manager", "category": "Storage"},
    "G044": {"text": "Wi-Fi tidak bisa diaktifkan (tombol on/off abu-abu)", "category": "Network"},
    "G045": {"text": "Daftar Wi-Fi kosong (tidak mendeteksi hotspot apapun)", "category": "Network"},
    "G046": {"text": "Sinyal Wi-Fi sangat lemah (1 bar) padahal dekat router", "category": "Network"},
    "G047": {"text": "Wi-Fi sering putus nyambung (disconnect) setiap beberapa menit", "category": "Network"},
    "G048": {"text": "Bluetooth device paired tapi tidak mau connect", "category": "Network"},
    "G049": {"text": "Port LAN tidak menyala lampunya saat kabel dipasang", "category": "Network"},
    "G050": {"text": "Internet 'No Internet Access' (Tanda seru kuning)", "category": "Network"},
    "G051": {"text": "Laptop mati mendadak saat menjalankan aplikasi berat (Game/Render)", "category": "Thermal"},
    "G052": {"text": "Bagian bawah laptop sangat panas hingga tidak nyaman dipangku", "category": "Thermal"},
    "G053": {"text": "Kipas laptop berbunyi kasar/berisik seperti benda tersangkut", "category": "Thermal"},
    "G054": {"text": "Kipas laptop tidak berputar sama sekali (hening total saat panas)", "category": "Thermal"},
    "G055": {"text": "Angin yang keluar dari ventilasi terasa lemah/tidak ada", "category": "Thermal"},
    "G056": {"text": "Laptop terasa lambat (throttling) saat suhu naik", "category": "Thermal"},
    "G057": {"text": "Sering muncul Blue Screen (BSOD) dengan kode error berbeda-beda", "category": "System"},
    "G058": {"text": "Laptop Freeze/Hang total, kursor tidak bisa gerak", "category": "System"},
    "G059": {"text": "Windows gagal update (Stuck di 'Getting Windows Ready')", "category": "System"},
    "G060": {"text": "Muncul banyak iklan Pop-up tidak senonoh/judi di desktop", "category": "System"},
    "G061": {"text": "Ekstensi file berubah aneh (misal .encrypted)", "category": "System"},
    "G062": {"text": "Aplikasi sering Force Close (Not Responding) sendiri", "category": "System"},
    "G063": {"text": "Jam dan Tanggal laptop selalu kembali ke tahun lama (Reset)", "category": "System"},
    "G064": {"text": "BIOS meminta password padahal tidak pernah disetting", "category": "System"},
    "G065": {"text": "Engsel laptop bunyi 'krek' saat dibuka/ditutup", "category": "Fisik"},
    "G066": {"text": "Casing laptop terbuka/menganga di area engsel", "category": "Fisik"},
    "G067": {"text": "USB Drive tidak terdeteksi di semua port USB", "category": "Fisik"},
    "G068": {"text": "Port USB longgar, flashdisk mudah goyang", "category": "Fisik"},
    "G069": {"text": "Port HDMI tidak menampilkan gambar ke proyektor/TV", "category": "Fisik"},
    "G070": {"text": "Keluar bau gosong/hangus dari ventilasi udara", "category": "Fisik"},
    "G071": {"text": "Tersetrum ringan (grounding) saat menyentuh bodi logam laptop", "category": "Fisik"},
    "G072": {"text": "Tombol trackpad keras/tidak bisa diklik", "category": "Fisik"},
    "G073": {"text": "Layar laptop tidak bisa menutup rapat", "category": "Fisik"},
    "G074": {"text": "Baut-baut casing bawah banyak yang hilang/lepas", "category": "Fisik"},
    "G075": {"text": "Slot SD Card tidak bisa membaca memori kamera", "category": "Fisik"},
}

CAUSES = {
    "C01": {"name": "Backlight Inverter Rusak/Putus", "category": "Layar", "prior_cf": 0.88, "level": "Sedang",
            "desc": "Inverter adalah komponen yang mengubah arus DC menjadi AC untuk menyalakan lampu latar. Jika rusak, layar tampak gelap gulita.",
            "sol": ["1. Sorot layar dengan senter HP. Jika terlihat bayangan gambar samar, masalah pada Backlight/Inverter.",
                    "2. Ganti modul Inverter atau ganti satu set panel layar (untuk laptop LED modern)."]},
    "C02": {"name": "Kabel Fleksibel Layar (LVDS) Bermasalah", "category": "Layar", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Kabel pita yang menghubungkan motherboard dengan layar terjepit di engsel atau mengalami keausan.",
            "sol": ["1. Posisikan layar pada sudut tertentu di mana gambar terlihat normal.",
                    "2. Bongkar bezel layar dan ganti kabel fleksibel (LVDS Cable)."]},
    "C03": {"name": "Panel LCD Pecah/Rusak Fisik", "category": "Layar", "prior_cf": 0.95, "level": "Tinggi",
            "desc": "Lapisan kristal cair di dalam panel layar mengalami keretakan akibat tekanan fisik atau benturan.",
            "sol": ["1. Sambungkan laptop ke monitor eksternal via HDMI untuk memastikan VGA aman.",
                    "2. Tidak bisa diservis. Solusi satu-satunya adalah penggantian Panel LCD/LED baru."]},
    "C04": {"name": "Dead Pixel / Stuck Pixel", "category": "Layar", "prior_cf": 0.90, "level": "Rendah",
            "desc": "Transistor sub-pixel pada layar mati atau terkunci pada warna tertentu.",
            "sol": ["1. Gunakan software 'Pixel Healer' atau video flashing warna-warni cepat selama 1-2 jam.",
                    "2. Ganti layar jika sangat mengganggu pandangan."]},
    "C05": {"name": "Driver Grafis (VGA) Corrupt", "category": "Layar", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Perangkat lunak pengendali kartu grafis mengalami konflik sistem atau file korup.",
            "sol": ["1. Gunakan DDU (Display Driver Uninstaller) untuk menghapus driver lama.",
                    "2. Download dan install driver VGA versi terbaru dari situs resmi."]},
    "C06": {"name": "GPU (VGA Card) Artifact/Rusak", "category": "Layar", "prior_cf": 0.92, "level": "Tinggi",
            "desc": "Chipset grafis (GPU) mengalami kerusakan fisik akibat panas berlebih yang ekstrem.",
            "sol": ["1. Lakukan proses 'Reballing' (solder ulang chipset GPU).",
                    "2. Jika Reballing gagal, ganti Motherboard satu set."]},
    "C07": {"name": "Digitizer Touchscreen Error", "category": "Layar", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Lapisan kaca sensor sentuh mengalami gangguan elektrostatis atau tekanan fisik.",
            "sol": ["1. Nonaktifkan fitur Touchscreen melalui Device Manager.",
                    "2. Ganti kaca Digitizer Touchscreen."]},
    "C08": {"name": "Baterai Drop/Aus (Soak)", "category": "Power", "prior_cf": 0.88, "level": "Sedang",
            "desc": "Kapasitas penyimpanan kimiawi di dalam sel baterai sudah menurun drastis karena siklus charge-discharge.",
            "sol": ["1. Lakukan kalibrasi baterai: Charge 100%, pakai sampai mati total, diamkan 2 jam, charge penuh lagi.",
                    "2. Jika Wear Level > 50%, ganti dengan baterai baru."]},
    "C09": {"name": "Baterai Kembung (Swollen Battery)", "category": "Power", "prior_cf": 0.95, "level": "Tinggi",
            "desc": "Terjadi penumpukan gas di dalam kemasan baterai. BAHAYA MELEDAK/TERBAKAR!",
            "sol": ["1. SEGERA LEPAS baterai dari laptop! Jangan coba menusuk atau menekannya.",
                    "2. Ganti baterai baru. Buang baterai lama di tempat limbah B3."]},
    "C10": {"name": "IC Power Motherboard Rusak", "category": "Power", "prior_cf": 0.90, "level": "Tinggi",
            "desc": "Kerusakan pada IC pengatur daya di motherboard. Listrik masuk tapi tidak didistribusikan.",
            "sol": ["1. Cek tegangan 19V pada jalur utama motherboard menggunakan Multitester.",
                    "2. Solder ulang atau ganti komponen IC yang terbakar/short."]},
    "C11": {"name": "DC Jack (Port Charger) Rusak", "category": "Power", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Soket tempat mencolok charger mengalami keretakan pada kaki solderan atau pin patah.",
            "sol": ["1. Goyangkan ujung charger pelan-pelan. Jika indikator nyala-mati, port bermasalah.",
                    "2. Bongkar laptop, ganti part DC Jack."]},
    "C12": {"name": "Adaptor Charger Rusak", "category": "Power", "prior_cf": 0.82, "level": "Sedang",
            "desc": "Unit adaptor tidak mampu mengeluarkan tegangan atau arus yang stabil.",
            "sol": ["1. Coba gunakan charger lain yang voltase dan tipe colokannya sama.",
                    "2. Beli adaptor charger baru. Disarankan Original."]},
    "C13": {"name": "Kabel Power Putus Dalam", "category": "Power", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Serabut tembaga di dalam kabel charger putus akibat kebiasaan menggulung kabel terlalu ketat.",
            "sol": ["1. Potong bagian kabel yang putus, lalu sambung ulang (solder dan isolasi).",
                    "2. Ganti kabel power AC atau ganti unit adaptor baru."]},
    "C14": {"name": "Fleksibel Keyboard Kotor/Korosi", "category": "Input", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Ujung kabel pita keyboard mengalami oksidasi atau tertutup debu halus.",
            "sol": ["1. Lepas keyboard, bersihkan ujung pin kabel fleksibel menggunakan penghapus pensil.",
                    "2. Pasang kembali dengan presisi dan kunci soketnya dengan rapat."]},
    "C15": {"name": "Switch Tombol Keyboard Rusak", "category": "Input", "prior_cf": 0.90, "level": "Sedang",
            "desc": "Mekanisme karet atau pengait plastik di bawah tombol patah atau aus.",
            "sol": ["1. Pindahkan mekanisme dari tombol yang jarang dipakai.",
                    "2. Ganti keyboard satu set."]},
    "C16": {"name": "Jalur Matrix Keyboard Short (Cairan)", "category": "Input", "prior_cf": 0.92, "level": "Sedang",
            "desc": "Terjadi korsleting pada lapisan sirkuit matriks keyboard akibat masuknya cairan.",
            "sol": ["1. Gunakan Keyboard USB Eksternal atau On-Screen Keyboard.",
                    "2. Keyboard yang kena cairan wajib ganti unit baru."]},
    "C17": {"name": "Driver Touchpad Konflik", "category": "Input", "prior_cf": 0.70, "level": "Rendah",
            "desc": "Driver touchpad bawaan Windows bentrok dengan driver produsen.",
            "sol": ["1. Cek tombol fungsi (Fn + F7/F9) untuk memastikan touchpad tidak dimatikan.",
                    "2. Uninstall driver touchpad di Device Manager, restart, lalu install driver terbaru."]},
    "C18": {"name": "Kabel Touchpad Lepas", "category": "Input", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Kabel fleksibel pipih yang menghubungkan modul touchpad ke motherboard terlepas.",
            "sol": ["1. Buka casing laptop, cari kabel touchpad di bawah baterai/palmrest.",
                    "2. Masukkan kembali kabel ke soket dan tekan penguncinya sampai bunyi 'klik'."]},
    "C19": {"name": "Sensor Fingerprint Rusak", "category": "Input", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Permukaan sensor pembaca sidik jari tergores, berminyak parah, atau kabel putus.",
            "sol": ["1. Bersihkan sensor dengan kain microfiber dan sedikit alkohol.",
                    "2. Hapus data sidik jari lama di Windows Hello, lalu daftarkan ulang."]},
    "C20": {"name": "Membran Speaker Robek", "category": "Audio", "prior_cf": 0.88, "level": "Rendah",
            "desc": "Daun membran speaker pecah atau sobek karena usia atau volume 100%.",
            "sol": ["1. Jangan setel volume diatas 70-80% untuk mengurangi distorsi.",
                    "2. Ganti sepasang speaker internal laptop."]},
    "C21": {"name": "Driver Audio Corrupt", "category": "Audio", "prior_cf": 0.80, "level": "Rendah",
            "desc": "File driver suara rusak atau hilang akibat update Windows yang gagal.",
            "sol": ["1. Klik kanan ikon speaker -> Troubleshoot Sound Problems.",
                    "2. Download driver Audio Realtek terbaru dari situs resmi laptop."]},
    "C22": {"name": "Port Jack Audio Rusak", "category": "Audio", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Plat logam kontak di dalam lubang jack 3.5mm bengkok atau patah.",
            "sol": ["1. Gunakan USB Sound Card External.",
                    "2. Ganti port audio (solder board) atau ganti Daughter Board Audio."]},
    "C23": {"name": "Kabel Webcam Putus", "category": "Video", "prior_cf": 0.82, "level": "Sedang",
            "desc": "Jalur kabel data untuk kamera yang melewati engsel laptop putus.",
            "sol": ["1. Gunakan Webcam USB eksternal.",
                    "2. Ganti kabel fleksibel kamera (biasanya satu paket dengan kabel LCD)."]},
    "C24": {"name": "Modul Mikrofon Rusak/Tertutup", "category": "Audio", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Lubang mikrofon di bezel layar tertutup debu atau modul mic internal mati.",
            "sol": ["1. Pastikan lubang kecil di dekat webcam tidak tertutup stiker/kotoran.",
                    "2. Cek Privacy Settings di Windows, pastikan akses Microphone diizinkan."]},
    "C25": {"name": "Harddisk (HDD) Bad Sector", "category": "Storage", "prior_cf": 0.90, "level": "Tinggi",
            "desc": "Piringan magnetik harddisk mengalami kerusakan fisik di sektor-sektor tertentu.",
            "sol": ["1. Segera BACKUP data penting ke tempat lain selagi bisa.",
                    "2. Ganti HDD lama dengan SSD untuk kecepatan 10x lipat."]},
    "C26": {"name": "Head Harddisk Macet (Mechanical Fail)", "category": "Storage", "prior_cf": 0.95, "level": "Tinggi",
            "desc": "Komponen jarum pembaca/penulis data (Head) menabrak piringan atau macet, bunyi 'klik-klik'.",
            "sol": ["1. Jangan dipaksakan menyala terus menerus karena akan memperparah kerusakan.",
                    "2. Harddisk sudah rusak total secara fisik. Wajib ganti baru."]},
    "C27": {"name": "SSD Health Critical / End of Life", "category": "Storage", "prior_cf": 0.88, "level": "Tinggi",
            "desc": "Chip memori Flash pada SSD sudah mencapai batas maksimum siklus tulis (TBW).",
            "sol": ["1. Cek kesehatan SSD menggunakan 'CrystalDiskInfo' atau 'Hard Disk Sentinel'.",
                    "2. Segera cloning sistem ke SSD baru sebelum SSD lama mati."]},
    "C28": {"name": "Bootloader Windows Rusak", "category": "Storage", "prior_cf": 0.85, "level": "Sedang",
            "desc": "File sistem yang bertugas memanggil OS saat start-up (BCD/MBR) hilang atau korup.",
            "sol": ["1. Booting menggunakan USB Installer Windows -> Repair your computer -> Startup Repair.",
                    "2. Buka Command Prompt di mode repair, ketik: 'bootrec /fixmbr' dan 'bootrec /rebuildbcd'."]},
    "C29": {"name": "Koneksi SATA/M.2 Kotor", "category": "Storage", "prior_cf": 0.70, "level": "Rendah",
            "desc": "Pin konektor pada harddisk/SSD atau slot di motherboard kotor oleh debu/oksidasi.",
            "sol": ["1. Cabut storage, bersihkan pin emasnya dengan penghapus, bersihkan slot dengan kuas.",
                    "2. Jika pakai kabel SATA, coba ganti kabelnya."]},
    "C30": {"name": "File System Corrupt", "category": "Storage", "prior_cf": 0.75, "level": "Sedang",
            "desc": "Struktur pengalamatan file berantakan karena laptop sering dimatikan paksa.",
            "sol": ["1. Buka CMD sebagai Admin, ketik 'chkdsk C: /f /r' lalu enter dan restart.",
                    "2. Jika error berlanjut, backup data lalu format ulang drive."]},
    "C31": {"name": "Wi-Fi Card (WLAN) Rusak", "category": "Network", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Modul hardware penerima sinyal Wi-Fi di motherboard mengalami kerusakan komponen.",
            "sol": ["1. Beli USB Wi-Fi Dongle (Plug and Play) sebagai solusi termurah.",
                    "2. Ganti card Wi-Fi internal (biasanya slot M.2 atau Mini PCIe)."]},
    "C32": {"name": "Kabel Antena Wi-Fi Lepas", "category": "Network", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Kabel antena (hitam/putih) yang menempel pada card Wi-Fi terlepas akibat guncangan.",
            "sol": ["1. Buka casing belakang laptop, cari card Wi-Fi.",
                    "2. Tekan kembali kepala kabel antena ke soket di card Wi-Fi sampai bunyi 'klik'."]},
    "C33": {"name": "Driver Network Adapter Error", "category": "Network", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Driver pengendali jaringan crash atau tidak kompatibel dengan update Windows.",
            "sol": ["1. Buka Settings -> Network & Internet -> Network Reset.",
                    "2. Download driver WLAN/LAN via HP lain, transfer via USB, lalu install."]},
    "C34": {"name": "Modul Bluetooth Rusak", "category": "Network", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Komponen Bluetooth (biasanya satu chip dengan Wi-Fi) mati.",
            "sol": ["1. Gunakan USB Bluetooth Dongle 5.0.",
                    "2. Pastikan Bluetooth Support Service berjalan di 'services.msc'."]},
    "C35": {"name": "Pasta Termal Kering", "category": "Thermal", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Pasta konduktor panas di atas prosesor sudah mengeras, panas tidak tersalurkan ke heatsink.",
            "sol": ["1. Bongkar sistem pendingin, bersihkan pasta lama dengan alkohol, oleskan pasta baru (Arctic MX-4).",
                    "2. Lakukan penggantian pasta termal setiap 1-2 tahun sekali."]},
    "C36": {"name": "Kipas Pendingin (Fan) Mati", "category": "Thermal", "prior_cf": 0.92, "level": "Tinggi",
            "desc": "Dinamo kipas putus atau macet total. Panas akan terperangkap dan menyebabkan laptop mati mendadak.",
            "sol": ["1. Coba bersihkan debu yang mengganjal kipas.",
                    "2. Jika dibersihkan tetap tidak muter, wajib ganti unit kipas baru."]},
    "C37": {"name": "Bearing Kipas Aus/Kotor", "category": "Thermal", "prior_cf": 0.80, "level": "Rendah",
            "desc": "Poros putaran kipas kering pelumasnya atau kemasukan debu kasar, bunyi bising/bergetar.",
            "sol": ["1. Buka kipas, beri 1 tetes minyak mesin jahit di porosnya.",
                    "2. Jika kipas model permanen (sealed), harus ganti baru."]},
    "C38": {"name": "Ventilasi Heatsink Tersumbat", "category": "Thermal", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Debu tebal membentuk 'karpet' di sirip-sirip heatsink, menghalangi angin panas keluar.",
            "sol": ["1. Gunakan kompresor angin atau kaleng compressed air untuk meniup debu keluar.",
                    "2. Gunakan kuas antistatik untuk membersihkan celah-celah ventilasi."]},
    "C39": {"name": "Baterai CMOS Habis", "category": "Motherboard", "prior_cf": 0.90, "level": "Rendah",
            "desc": "Baterai kancing (CR2032) di motherboard yang menjaga settingan BIOS dan Jam habis dayanya.",
            "sol": ["1. Buka casing, cari baterai bulat seperti uang koin, ganti dengan tipe CR2032 baru.",
                    "2. Setelah ganti, masuk BIOS dan atur ulang tanggal/jam."]},
    "C40": {"name": "Korsleting (Short Circuit) Motherboard", "category": "Motherboard", "prior_cf": 0.95, "level": "Tinggi",
            "desc": "Terjadi hubungan arus pendek antar jalur komponen. BAHAYA KEBAKARAN!",
            "sol": ["1. Jangan coba nyalakan laptop! Cabut charger dan baterai.",
                    "2. Bawa ke tempat servis spesialis motherboard untuk pelacakan jalur short."]},
    "C41": {"name": "RAM Rusak/Kotor", "category": "Motherboard", "prior_cf": 0.88, "level": "Tinggi",
            "desc": "Modul memori RAM mengalami error pada chip-nya atau pin konektornya kotor.",
            "sol": ["1. Lepas RAM, gosok pin emasnya dengan penghapus pensil putih, pasang lagi.",
                    "2. Coba ganti dengan RAM lain yang normal."]},
    "C42": {"name": "Slot RAM Bermasalah", "category": "Motherboard", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Kaki-kaki logam di dalam slot memori motherboard ada yang bengkok atau longgar.",
            "sol": ["1. Jika laptop punya 2 slot, pindahkan RAM ke slot satunya.",
                    "2. Jika semua slot error, perlu solder ulang kaki slot."]},
    "C43": {"name": "BIOS Corrupt", "category": "Motherboard", "prior_cf": 0.92, "level": "Tinggi",
            "desc": "Firmware dasar (BIOS) rusak, biasanya karena gagal update BIOS atau mati listrik saat flashing.",
            "sol": ["1. Lakukan Flash BIOS ulang menggunakan alat programmer (USB EPROM Programmer).",
                    "2. Coba reset BIOS dengan mencabut baterai CMOS selama 5 menit."]},
    "C44": {"name": "Infeksi Virus/Malware/Adware", "category": "Software", "prior_cf": 0.90, "level": "Sedang",
            "desc": "Sistem terinfeksi program jahat yang memakan resource CPU/RAM atau memunculkan iklan.",
            "sol": ["1. Jalankan Full Scan menggunakan Windows Defender atau Malwarebytes.",
                    "2. Hapus ekstensi browser yang mencurigakan."]},
    "C45": {"name": "Serangan Ransomware", "category": "Software", "prior_cf": 0.98, "level": "Tinggi",
            "desc": "Virus berbahaya yang mengenkripsi (mengunci) semua data pribadi dan meminta tebusan.",
            "sol": ["1. Matikan internet segera agar tidak menyebar ke jaringan.",
                    "2. Format habis harddisk dan install ulang Windows. Data yang terkunci sangat sulit kembali."]},
    "C46": {"name": "Registry Windows Error", "category": "Software", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Database konfigurasi sistem operasi berantakan karena sisa uninstalasi program.",
            "sol": ["1. Buka CMD Admin, ketik 'sfc /scannow' untuk memperbaiki file sistem.",
                    "2. Gunakan fitur 'Reset this PC' di settings Windows (Keep my files)."]},
    "C47": {"name": "Update Windows Bermasalah", "category": "Software", "prior_cf": 0.85, "level": "Sedang",
            "desc": "File update Windows korup atau tidak cocok dengan hardware, menyebabkan bootloop.",
            "sol": ["1. Masuk Safe Mode, hapus update terakhir via Control Panel -> View Installed Updates.",
                    "2. Pause update sementara waktu sampai Microsoft merilis patch perbaikan."]},
    "C48": {"name": "Bloatware Berlebihan", "category": "Software", "prior_cf": 0.75, "level": "Rendah",
            "desc": "Terlalu banyak aplikasi berjalan otomatis saat laptop dinyalakan (Startup), membebani RAM.",
            "sol": ["1. Buka Task Manager -> Tab Startup -> Disable aplikasi yang tidak perlu.",
                    "2. Hapus aplikasi bawaan pabrik yang tidak pernah dipakai."]},
    "C49": {"name": "Engsel (Hinge) Patah/Jebol", "category": "Fisik", "prior_cf": 0.98, "level": "Tinggi",
            "desc": "Dudukan baut kuningan di dalam casing plastik hancur, engsel besi tidak punya pegangan.",
            "sol": ["1. Servis casing dengan lem khusus campur bubuk penguat untuk membuat dudukan baru.",
                    "2. Ganti casing laptop (Top Case/Bottom Case) dengan yang baru/copotan."]},
    "C50": {"name": "Port USB Controller Rusak", "category": "Motherboard", "prior_cf": 0.85, "level": "Sedang",
            "desc": "Chipset yang mengatur lalu lintas data USB di motherboard mati atau short.",
            "sol": ["1. Gunakan USB Hub pada port yang masih menyala (jika ada).",
                    "2. Jika ada slot ExpressCard (laptop lama), pakai USB ExpressCard adapter."]},
}

RULES = [
    # LAYAR
    {"id": "R01", "symptoms": ["G006", "G001"], "cause": "C01", "cf": 0.85},
    {"id": "R02", "symptoms": ["G002", "G008", "G009"], "cause": "C02", "cf": 0.80},
    {"id": "R03", "symptoms": ["G003", "G007"], "cause": "C03", "cf": 0.95},
    {"id": "R04", "symptoms": ["G004"], "cause": "C04", "cf": 0.90},
    {"id": "R05", "symptoms": ["G007", "G058"], "cause": "C05", "cf": 0.70},
    {"id": "R06", "symptoms": ["G007", "G057", "G051"], "cause": "C06", "cf": 0.90},
    {"id": "R07", "symptoms": ["G005"], "cause": "C07", "cf": 0.85},
    {"id": "R08", "symptoms": ["G010"], "cause": "C03", "cf": 0.85},
    # POWER
    {"id": "R09", "symptoms": ["G011", "G019"], "cause": "C08", "cf": 0.85},
    {"id": "R10", "symptoms": ["G014", "G027"], "cause": "C09", "cf": 0.95},
    {"id": "R11", "symptoms": ["G012", "G015"], "cause": "C10", "cf": 0.88},
    {"id": "R12", "symptoms": ["G013", "G012"], "cause": "C11", "cf": 0.90},
    {"id": "R13", "symptoms": ["G016", "G012"], "cause": "C12", "cf": 0.80},
    {"id": "R14", "symptoms": ["G013", "G017"], "cause": "C13", "cf": 0.75},
    {"id": "R15", "symptoms": ["G018"], "cause": "C08", "cf": 0.80},
    # INPUT
    {"id": "R16", "symptoms": ["G020"], "cause": "C14", "cf": 0.70},
    {"id": "R17", "symptoms": ["G020", "G022"], "cause": "C15", "cf": 0.85},
    {"id": "R18", "symptoms": ["G021"], "cause": "C16", "cf": 0.90},
    {"id": "R19", "symptoms": ["G023", "G024"], "cause": "C17", "cf": 0.60},
    {"id": "R20", "symptoms": ["G023"], "cause": "C18", "cf": 0.80},
    {"id": "R21", "symptoms": ["G026"], "cause": "C19", "cf": 0.85},
    {"id": "R22", "symptoms": ["G025"], "cause": "C18", "cf": 0.75},
    # AUDIO/VIDEO
    {"id": "R23", "symptoms": ["G028", "G030"], "cause": "C20", "cf": 0.90},
    {"id": "R24", "symptoms": ["G029"], "cause": "C21", "cf": 0.80},
    {"id": "R25", "symptoms": ["G031", "G032"], "cause": "C22", "cf": 0.85},
    {"id": "R26", "symptoms": ["G033", "G034"], "cause": "C23", "cf": 0.85},
    {"id": "R27", "symptoms": ["G035"], "cause": "C24", "cf": 0.80},
    # STORAGE
    {"id": "R28", "symptoms": ["G036", "G042"], "cause": "C25", "cf": 0.75},
    {"id": "R29", "symptoms": ["G037", "G038"], "cause": "C26", "cf": 0.95},
    {"id": "R30", "symptoms": ["G057", "G038", "G040"], "cause": "C27", "cf": 0.85},
    {"id": "R31", "symptoms": ["G038"], "cause": "C28", "cf": 0.80},
    {"id": "R32", "symptoms": ["G038"], "cause": "C29", "cf": 0.65},
    {"id": "R33", "symptoms": ["G036", "G040"], "cause": "C30", "cf": 0.60},
    {"id": "R34", "symptoms": ["G043"], "cause": "C25", "cf": 0.70},
    # NETWORK
    {"id": "R35", "symptoms": ["G044", "G045"], "cause": "C31", "cf": 0.85},
    {"id": "R36", "symptoms": ["G046", "G047"], "cause": "C32", "cf": 0.80},
    {"id": "R37", "symptoms": ["G044", "G050"], "cause": "C33", "cf": 0.70},
    {"id": "R38", "symptoms": ["G048"], "cause": "C34", "cf": 0.80},
    {"id": "R39", "symptoms": ["G049"], "cause": "C33", "cf": 0.75},
    # THERMAL
    {"id": "R40", "symptoms": ["G051", "G052", "G056"], "cause": "C35", "cf": 0.80},
    {"id": "R41", "symptoms": ["G051", "G052", "G054"], "cause": "C36", "cf": 0.90},
    {"id": "R42", "symptoms": ["G053"], "cause": "C37", "cf": 0.85},
    {"id": "R43", "symptoms": ["G051", "G055"], "cause": "C38", "cf": 0.75},
    # MOBO & OS
    {"id": "R44", "symptoms": ["G063"], "cause": "C39", "cf": 0.95},
    {"id": "R45", "symptoms": ["G070", "G015"], "cause": "C40", "cf": 0.95},
    {"id": "R46", "symptoms": ["G057", "G058"], "cause": "C41", "cf": 0.85},
    {"id": "R47", "symptoms": ["G057"], "cause": "C42", "cf": 0.70},
    {"id": "R48", "symptoms": ["G001", "G015"], "cause": "C43", "cf": 0.80},
    {"id": "R49", "symptoms": ["G064"], "cause": "C43", "cf": 0.90},
    # SOFTWARE
    {"id": "R50", "symptoms": ["G060", "G056"], "cause": "C44", "cf": 0.85},
    {"id": "R51", "symptoms": ["G061"], "cause": "C45", "cf": 0.98},
    {"id": "R52", "symptoms": ["G062", "G057"], "cause": "C46", "cf": 0.75},
    {"id": "R53", "symptoms": ["G059"], "cause": "C47", "cf": 0.85},
    {"id": "R54", "symptoms": ["G056", "G042"], "cause": "C48", "cf": 0.70},
    # FISIK
    {"id": "R55", "symptoms": ["G065", "G066", "G073"], "cause": "C49", "cf": 0.98},
    {"id": "R56", "symptoms": ["G067", "G068"], "cause": "C50", "cf": 0.85},
    {"id": "R57", "symptoms": ["G071"], "cause": "C40", "cf": 0.60},
    {"id": "R58", "symptoms": ["G069"], "cause": "C05", "cf": 0.60},
    {"id": "R59", "symptoms": ["G072"], "cause": "C09", "cf": 0.80},
]

def combine_cf(cf1, cf2):
    return cf1 + cf2 * (1 - cf1)

def forward_chaining(user_symptoms):
    results = {}
    for rule in RULES:
        if all(sym in user_symptoms for sym in rule["symptoms"]):
            cause_id = rule["cause"]
            rule_cf = rule["cf"]
            prior_cf = CAUSES[cause_id]["prior_cf"]
            if cause_id not in results:
                results[cause_id] = combine_cf(prior_cf, rule_cf)
            else:
                results[cause_id] = combine_cf(results[cause_id], rule_cf)
    return results

def run_diagnosis(user_symptoms):
    results = forward_chaining(user_symptoms)
    valid = {k: v for k, v in results.items() if v >= 0}
    sorted_results = sorted(valid.items(), key=lambda x: x[1], reverse=True)[:3]
    if not sorted_results:
        return None, "low_confidence"
    return sorted_results, "success"

# Session State Init
if "page" not in st.session_state:
    st.session_state.page = "home"
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =============================================================================
# [3] UI COMPONENTS & PAGES
# =============================================================================

def ui_top_nav(title, back_action=None):
    """Component: Top Navigation Bar"""
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if back_action:
            if st.button("←", key="nav_back", type="secondary"):
                back_action()
    with col2:
        st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 1.1rem; padding-top: 5px;'>{title}</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='text-align: right; color: #94a3b8;'><span class='material-symbols-outlined'>account_circle</span></div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

def home_page():
    ui_top_nav("Dasbor")
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; background: rgba(19, 91, 236, 0.2); border-radius: 99px; border: 1px solid rgba(19, 91, 236, 0.3); margin-bottom: 1rem;">
            <span style="width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%;"></span>
            <span style="color: #60a5fa; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Sistem Online</span>
        </div>
        <h1 style="font-size: 2.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 0.5rem;">Analisis Kerusakan Laptop</h1>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0;">Sistem Pakar menggunakan metode Certainty Factor untuk mendiagnosa kerusakan perangkat keras.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats Grid
    st.markdown("<h3 style='font-size: 1.1rem; margin-top: 2rem; margin-bottom: 1rem;'>Modul Sistem</h3>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #135bec; margin-bottom: 0.5rem;">
                <span class="material-symbols-outlined">analytics</span>
                <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Akurasi</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 900;">98.4%</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #06b6d4; margin-bottom: 0.5rem;">
                <span class="material-symbols-outlined">history</span>
                <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">Diagnosa</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 900;">{len(st.session_state.history)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Info Card
    st.markdown("""
    <div class="glass-card" style="display: flex; gap: 1rem; align-items: center;">
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span class="material-symbols-outlined" style="color: #a855f7;">functions</span>
                <span style="font-weight: 700;">Certainty Factor</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">Memahami logika matematika di balik perhitungan probabilitas kerusakan.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Buttons (Primary)
    col_hist, col_kb = st.columns(2)
    with col_hist:
        if st.button("Mulai Diagnosa", type="primary", key="btn_start"):
            st.session_state.page = "symptoms"
            st.rerun()
    with col_kb:
        if st.button("Riwayat Diagnosa", type="primary", key="btn_hist"):
            st.session_state.page = "history"
            st.rerun()
        
        
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

def symptoms_page():
    def go_home():
        st.session_state.page = "home"
        st.rerun()
        
    ui_top_nav("Pilih Gejala", go_home)
    
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">Katalog Masalah</h2>
        <p style="color: #94a3b8; font-size: 0.9rem;">Kategorikan masalah untuk membantu AI menemukan titik kerusakan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected = []
    
    # Categorize
    categories = {}
    for code, data in SYMPTOMS.items():
        cat = data.get("category", "Lainnya")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((code, data))
        
    icon_map = {
        "Layar": ("laptop_mac", "#3b82f6"),
        "Power": ("battery_alert", "#ef4444"),
        "Input": ("keyboard", "#a855f7"),
        "Audio": ("volume_up", "#f59e0b"),
        "Storage": ("hard_drive", "#10b981"),
        "Network": ("wifi_off", "#06b6d4"),
        "Thermal": ("thermostat", "#f97316"),
        "System": ("memory", "#6366f1"),
        "Fisik": ("build", "#64748b")
    }

    # # Accordions
    # for cat, items in categories.items():
    #     icon, color = icon_map.get(cat, ("folder", "#94a3b8"))
        
    #     with st.expander(f"{cat} ({len(items)})"):
    #         st.markdown(f"""
    #         <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
    #             <div style="width: 2.5rem; height: 2.5rem; border-radius: 50%; background: {color}20; display: flex; align-items: center; justify-content: center; color: {color};">
    #                 <span class="material-symbols-outlined" style="font-size: 1.25rem;">{icon}</span>
    #             </div>
    #             <div style="font-weight: 600; font-size: 1rem;">Masalah {cat}</div>
    #         </div>
    #         """, unsafe_allow_html=True)
            
    #         for code, data in items:
    #             if st.checkbox(f"{data['text']}", key=code):
    #                 selected.append(code)

    # st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

    # 1. Inisialisasi layout kolom (3 kolom)
    cols = st.columns(3)

    # 2. Iterasi kategori dengan enumerate untuk mendapatkan index
    for i, (cat, items) in enumerate(categories.items()):
        
        # 3. Tentukan ikon dan warna
        icon, color = icon_map.get(cat, ("folder", "#94a3b8"))
        
        # 4. Pilih kolom berdasarkan urutan (0, 1, 2, 0, 1, 2, dst...)
        with cols[i % 3]:
            # Masukkan expander ke dalam kolom tersebut
            with st.expander(f"{cat} ({len(items)})"):
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                    <div style="width: 2.5rem; height: 2.5rem; border-radius: 50%; background: {color}20; display: flex; align-items: center; justify-content: center; color: {color};">
                        <span class="material-symbols-outlined" style="font-size: 1.25rem;">{icon}</span>
                    </div>
                    <div style="font-weight: 600; font-size: 1rem;">Masalah {cat}</div>
                </div>
                """, unsafe_allow_html=True)
                
                for code, data in items:
                    # Pastikan key checkbox unik
                    if st.checkbox(f"{data['text']}", key=code):
                        selected.append(code)

    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
    
    # Analyze Button
    if st.button("Analisa Kerusakan", type="primary", key="btn_analyze"):
        if not selected:
            st.error("Harap pilih minimal satu gejala.")
        else:
            results, status = run_diagnosis(selected)
            if status == "success" and results:
                st.session_state.last_result = {
                    "results": results,
                    "symptoms": selected,
                    "timestamp": datetime.now()
                }
                # Save History
                top = results[0]
                cause = CAUSES[top[0]]
                st.session_state.history.append({
                    "cause_name": cause["name"],
                    "confidence": top[1],
                    "symptoms_text": ", ".join(SYMPTOMS[s]["text"][:30] for s in selected[:3] if s in SYMPTOMS),
                    "timestamp": datetime.now(),
                    "level": cause["level"]
                })
                st.session_state.page = "results"
                st.rerun()
            else:
                st.warning("Tingkat keyakinan rendah atau kombinasi tidak dikenal.")

def results_page():
    def go_back():
        st.session_state.page = "symptoms"
        st.rerun()
        
    ui_top_nav("Laporan Diagnosa", go_back)

    if (not st.session_state.last_result or 
        "results" not in st.session_state.last_result or 
        not st.session_state.last_result["results"]):
        
        st.error("Gagal memuat hasil. Tidak ada diagnosa yang mencapai tingkat keyakinan yang memadai. Silakan ulangi.")
        
        if st.button("Kembali ke Pemilihan Gejala", type="primary", key="btn_return_fail"):
            st.session_state.page = "symptoms"
            st.rerun()
            
        return
        
    results = st.session_state.last_result["results"]
    
    # Top Result Logic
    top_cause_id, top_conf = results[0]
    top_cause = CAUSES[top_cause_id]
    top_percent = int(top_conf * 100)
    
    risk_color = "#135bec" 
    risk_bg = "rgba(19, 91, 236, 0.1)"
    risk_border = "rgba(19, 91, 236, 0.3)"
    risk_label = "TIDAK DIKETAHUI"
    
    # Determine Colors & Labels
    if top_cause["level"] == "Tinggi":
        risk_color = "#ef4444"
        risk_bg = "rgba(239, 68, 68, 0.1)"
        risk_border = "rgba(239, 68, 68, 0.3)"
        risk_label = "RISIKO KRITIS TERDETEKSI"
    elif top_cause["level"] == "Sedang":
        risk_color = "#f59e0b"
        risk_bg = "rgba(245, 158, 11, 0.1)"
        risk_border = "rgba(245, 158, 11, 0.3)"
        risk_label = "RISIKO MENENGAH"
    else:
        risk_color = "#10b981"
        risk_bg = "rgba(16, 185, 129, 0.1)"
        risk_border = "rgba(16, 185, 129, 0.3)"
        risk_label = "RISIKO RENDAH"

    # Risk Banner (Translated) - INDENTASI DIHAPUS
    st.markdown(f"""
<div class="glass-card" style="padding: 0; overflow: hidden; position: relative;">
<div style="position: absolute; top: 0; right: 0; width: 60%; height: 100%; background: radial-gradient(circle at top right, {risk_color}20, transparent 70%); pointer-events: none;"></div>
<div style="padding: 1.5rem; position: relative; z-index: 1;">
<div style="color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.25rem;">Penyebab Utama</div>
<h2 style="font-size: 1.75rem; font-weight: 800; margin-bottom: 1.5rem; line-height: 1.1;">{top_cause['name']}</h2>
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.5rem;">
<span style="color: #94a3b8; font-size: 0.85rem;">Tingkat Keyakinan</span>
<div style="display: flex; align-items: baseline; gap: 2px;">
<span style="font-size: 2rem; font-weight: 800; color: #135bec;">{top_percent}</span>
<span style="font-size: 1rem; font-weight: 600; color: #135bec;">%</span>
</div>
</div>
<div class="custom-progress-bg">
<div class="custom-progress-fill" style="width: {top_percent}%; background-color: #135bec; box-shadow: 0 0 15px rgba(19, 91, 236, 0.5);"></div>
</div>
<div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">{top_cause['desc']}</div>
</div>
</div>
</div>
    """, unsafe_allow_html=True)
    
    # Solutions (Translated)
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; margin-top: 2rem;'>Solusi Perbaikan</h3>", unsafe_allow_html=True)
    
    for sol in top_cause["sol"]:
        # INDENTASI DIHAPUS
        st.markdown(f"""
<div class="glass-card" style="padding: 1rem; display: flex; gap: 1rem; align-items: flex-start; background: rgba(25, 34, 51, 0.4);">
<div style="width: 2rem; height: 2rem; border-radius: 50%; background: rgba(19, 91, 236, 0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
<span class="material-symbols-outlined" style="font-size: 1.2rem; color: #60a5fa;">build_circle</span>
</div>
<div style="font-size: 0.9rem; color: #e2e8f0; line-height: 1.5;">{sol}</div>
</div>
        """, unsafe_allow_html=True)

    # Secondary Results (Translated)
    if len(results) > 1:
        st.markdown("<h3 style='font-size: 1rem; font-weight: 700; margin-top: 2rem; color: #94a3b8;'>Kemungkinan Lainnya</h3>", unsafe_allow_html=True)
        for i in range(1, len(results)):
            cid, conf = results[i]
            cause_data = CAUSES[cid]
            pct = int(conf * 100)
            # INDENTASI DIHAPUS
            st.markdown(f"""
<div style="background: rgba(255,255,255,0.03); border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.05);">
<div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
<span style="font-weight: 600; font-size: 0.95rem;">{cause_data['name']}</span>
<span style="font-weight: 700; color: #94a3b8;">{pct}%</span>
</div>
<div class="custom-progress-bg">
<div class="custom-progress-fill" style="width: {pct}%; background-color: #64748b;"></div>
</div>
</div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
    
    col_hist, col_new = st.columns(2)
    with col_hist:
        if st.button("Lihat Riwayat", type="secondary", key="btn_to_history"):
            st.session_stage.page = "history"
            st.rerun()
    with col_new:
        if st.button("Diagnosa Baru", type="primary", key="btn_new_diag"):
            st.session_state.page = "symptoms"
            st.rerun()

def history_page():
    def go_home():
        st.session_state.page = "home"
        st.rerun()
        
    ui_top_nav("Riwayat", go_home)
    
    # Filters (Visual only for now - Translated)
    st.markdown("""
    <div style="display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 1rem; margin-bottom: 0.5rem;">
        <span style="background: #135bec; color: white; padding: 0.4rem 1rem; border-radius: 99px; font-size: 0.85rem; font-weight: 600;">Semua</span>
        <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; padding: 0.4rem 1rem; border-radius: 99px; font-size: 0.85rem;">Kritis</span>
        <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; padding: 0.4rem 1rem; border-radius: 99px; font-size: 0.85rem;">Perangkat Lunak</span>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("Belum ada riwayat diagnosa.")
    else:
        for item in reversed(st.session_state.history):
            # Style config based on severity
            if item["level"] == "Tinggi":
                icon_bg = "rgba(239, 68, 68, 0.15)"
                icon_color = "#ef4444"
                icon_name = "error"
            elif item["level"] == "Sedang":
                icon_bg = "rgba(245, 158, 11, 0.15)"
                icon_color = "#f59e0b"
                icon_name = "warning"
            else:
                icon_bg = "rgba(16, 185, 129, 0.15)"
                icon_color = "#10b981"
                icon_name = "check_circle"

            dt_str = item["timestamp"].strftime('%d %b • %H:%M')
            pct = int(item["confidence"] * 100)
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; transition: transform 0.2s; cursor: pointer;">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                    <div style="display: flex; gap: 1rem; flex: 1;">
                        <div style="width: 3rem; height: 3rem; background: {icon_bg}; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <span class="material-symbols-outlined" style="color: {icon_color}; font-size: 1.5rem;">{icon_name}</span>
                        </div>
                        <div>
                            <div style="font-weight: 700; font-size: 1rem; color: white; margin-bottom: 0.2rem;">{item['cause_name']}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">{dt_str}</div>
                        </div>
                    </div>
                    <div style="background: {icon_bg}; color: {icon_color}; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700;">
                        {pct}%
                    </div>
                </div>
                <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 0.8rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%;">
                        {item['symptoms_text']}
                    </div>
                    <span class="material-symbols-outlined" style="color: #475569; font-size: 1.2rem;">chevron_right</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # Floating Action Button for New Diagnosis
    st.markdown("<div style='height: 4rem'></div>", unsafe_allow_html=True)
    if st.button("Diagnosa Baru", key="fab_new", type="primary"):
        st.session_state.page = "symptoms"
        st.rerun()

# =============================================================================
# [4] ROUTER (TIDAK BERUBAH)
# =============================================================================
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "symptoms":
    symptoms_page()
elif st.session_state.page == "results":
    results_page()
elif st.session_state.page == "history":
    history_page()
