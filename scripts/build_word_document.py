import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client

def set_cell_background(cell, fill_hex):
    """Sets the background color of a table cell using hex string (e.g. '1E3A8A')."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Sets cell padding in twentieths of a point (dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    """
    Set cell borders:
    kwargs can contain top, bottom, left, right with dict(val='single', sz='4', color='CBD5E1', space='0')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'<w:{edge} {nsdecls("w")} w:val="{edge_data.get("val", "single")}" ' \
                  f'w:sz="{edge_data.get("sz", "4")}" w:space="0" ' \
                  f'w:color="{edge_data.get("color", "CBD5E1")}"/>'
            tcBorders.append(parse_xml(tag))
        else:
            tag = f'<w:{edge} {nsdecls("w")} w:val="none"/>'
            tcBorders.append(parse_xml(tag))
    tcPr.append(tcBorders)

def create_document():
    doc = Document()

    # 1. Page Setup (A4, 2.5 cm margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.98)
    section.bottom_margin = Inches(0.98)
    section.left_margin = Inches(0.98)
    section.right_margin = Inches(0.98)

    # Header & Footer setup
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("Dokumen Rekayasa Kebutuhan Perangkat Lunak | ProdiPath")
    hrun.font.name = "Calibri"
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = RGBColor(148, 163, 184)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Program Studi S1 Informatika — Universitas Teknokrat Indonesia")
    frun.font.name = "Calibri"
    frun.font.size = Pt(8.5)
    frun.font.color.rgb = RGBColor(148, 163, 184)

    # ------------------ COVER PAGE ------------------
    cover_inst = doc.add_paragraph()
    cover_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_inst.paragraph_format.space_before = Pt(20)
    cover_inst.paragraph_format.space_after = Pt(4)
    run_inst = cover_inst.add_run("UNIVERSITAS TEKNOKRAT INDONESIA\nFAKULTAS TEKNIK DAN ILMU KOMPUTER\nPROGRAM STUDI S1 INFORMATIKA")
    run_inst.font.name = "Calibri"
    run_inst.font.size = Pt(13)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(30, 58, 138)

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(28)
    run_line = p_line.add_run("—" * 38)
    run_line.font.color.rgb = RGBColor(59, 130, 246)
    run_line.font.bold = True

    cover_title = doc.add_paragraph()
    cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_title.paragraph_format.space_after = Pt(10)
    run_title = cover_title.add_run("DOKUMEN PRODUCT BACKLOG &\nUSE CASE DIAGRAM")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    cover_sub = doc.add_paragraph()
    cover_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_sub.paragraph_format.space_after = Pt(36)
    run_sub = cover_sub.add_run("PROYEK PENGEMBANGAN SISTEM REKOMENDASI PROGRAM STUDI KULIAH (PRODIPATH)\nBERBASIS MACHINE LEARNING UNTUK SISWA KELAS XII")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(37, 99, 235)

    # Box Informasi Tim
    info_table = doc.add_table(rows=6, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False

    labels = [
        ("Mata Kuliah", "Proyek Perangkat Lunak (PPL) / Metodologi Penelitian"),
        ("Kelas / Semester", "IF 24 DX / Semester Ganjil 2026"),
        ("Nama Tim / Kelompok", "Kelompok ProdiPath"),
        ("Mitra Proyek", "SMA Muhammadiyah 2 Bandar Lampung"),
        ("Dosen Pengampu", "Tim Dosen Pengampu Mata Kuliah PPL"),
        ("Anggota Kelompok", "1. Yudistyo Herlambang (NPM: 24312120) — Ketua / Developer\n"
                              "2. Maelani Putri (NPM: 24312189) — Anggota / Requirements & UI/UX\n"
                              "3. Siti Diana (NPM: 24312118) — Anggota / QA & Data Analyst")
    ]

    for i, (k, v) in enumerate(labels):
        row = info_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 100, 100, 140, 140)
        set_cell_margins(c1, 100, 100, 140, 140)
        
        border_cfg = dict(val='single', sz='4', color='CBD5E1')
        set_cell_border(c0, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
        set_cell_border(c1, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(30, 41, 59)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    cover_foot = doc.add_paragraph()
    cover_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_foot.paragraph_format.space_before = Pt(50)
    run_foot = cover_foot.add_run("BANDAR LAMPUNG\nOKTOBER 2026")
    run_foot.font.name = "Calibri"
    run_foot.font.size = Pt(10.5)
    run_foot.font.bold = True
    run_foot.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # ------------------ HELPER FUNCTIONS FOR SECTIONS ------------------
    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(37, 99, 235)
        return h

    def add_body_paragraph(text, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    # ------------------ BAB I: PENDAHULUAN & PROFIL PROYEK ------------------
    add_heading_1("BAB I. PENDAHULUAN & GAMBARAN UMUM PROYEK")
    
    add_heading_2("1.1 Latar Belakang Masalah")
    add_body_paragraph(
        "Menentukan pilihan program studi di perguruan tinggi merupakan salah satu keputusan paling krusial bagi siswa kelas XII "
        "tingkat Sekolah Menengah Atas (SMA). Berdasarkan observasi awal, banyak siswa mengalami dilema dan kebingungan dalam "
        "menghubungkan antara capaian nilai rapor akademik dengan minat kejuruan, keterampilan praktis, serta kemampuan analitis yang dimilikinya. "
        "Informasi penjurusan sering kali tersaji secara terpisah, manual, dan belum ada alat bantu digital yang mampu memadukan profil siswa secara objektif."
    )
    add_body_paragraph(
        "ProdiPath hadir sebagai platform aplikasi web interaktif yang memanfaatkan algoritma Machine Learning (Decision Tree Classifier) "
        "untuk memberikan rekomendasi program studi secara terukur, objektif, dan transparan bagi siswa kelas XII. Sistem ini "
        "dirancang untuk menjadi bahan eksplorasi awal dan referensi diskusi terarah antara siswa, guru Bimbingan Konseling (BK), dan orang tua."
    )

    add_heading_2("1.2 Profil Mitra dan Sasaran Pengguna")
    add_body_paragraph(
        "Mitra utama penerapan proyek ini adalah SMA Muhammadiyah 2 Bandar Lampung. Sasaran pengguna terbagi menjadi dua kategori utama:"
    )
    add_bullet("Siswa aktif kelas XII (lintas jurusan IPA, IPS, dan Bahasa) yang memerlukan eksplorasi awal program studi perguruan tinggi secara mandiri tanpa perlu repot login akun.", "1. Pengguna Utama (Siswa): ")
    add_bullet("Guru Bimbingan Konseling (BK) dan Tim IT/Tata Usaha Sekolah yang bertindak sebagai administrator sistem untuk mengelola data siswa, meninjau distribusi pilihan, dan mengimpor dataset referensi pelatihan model.", "2. Pengguna Pengelola (Administrator): ")

    add_heading_2("1.3 Ruang Lingkup dan Arsitektur Sistem")
    add_body_paragraph(
        "Sistem dibangun dengan arsitektur modern berbasis Client-Server (REST API):"
    )
    add_bullet("Menggunakan React, Vite, dan Tailwind CSS yang responsif, modern, dan interaktif.", "Frontend Web: ")
    add_bullet("Menggunakan FastAPI (Python) yang menyajikan endpoint prediksi AI, autentikasi berbasis JWT, dan manajemen data siswa.", "Backend API: ")
    add_bullet("Model Decision Tree Classifier (scikit-learn) yang dilatih menggunakan dataset profil akademik dan peminatan rujukan.", "Machine Learning Engine: ")
    add_bullet("MySQL (metopen_db) untuk penyimpanan data kuesioner siswa, akun pengelola, dan riwayat rekomendasi.", "Database: ")

    # ------------------ BAB II: PRODUCT BACKLOG ------------------
    add_heading_1("BAB II. PRODUCT BACKLOG PROYEK PRODIPATH")
    add_body_paragraph(
        "Sesuai dengan kerangka kerja Agile Scrum yang dibahas pada Pertemuan ke-3, Product Backlog merupakan daftar terurut dan terprioritaskan "
        "dari seluruh kebutuhan fungsional perangkat lunak. Setiap Product Backlog Item (PBI) dinyatakan dalam bentuk User Story baku "
        "('Sebagai [Peran], Saya ingin [Fitur], Agar [Manfaat]'), dilengkapi Kriteria Penerimaan (Acceptance Criteria / Definition of Done), "
        "prioritas MoSCoW (Must Have, Should Have, Could Have), estimasi bobot Story Points (deret Fibonacci), serta alokasi target Sprint."
    )

    # Tabel Product Backlog
    backlog_data = [
        ("PBI-01", "AUTH", "Sebagai Administrator, saya ingin login menggunakan username dan password terenkripsi, agar saya dapat mengakses panel manajemen sistem secara aman.",
         "1. Form login memvalidasi kelengkapan input.\n2. Password diverifikasi dengan bcrypt hash.\n3. Diterbitkan token JWT yang tersimpan di sesi browser.\n4. Muncul notifikasi kesalahan jika kredensial salah.",
         "Must Have", "5", "Sprint 1"),
        
        ("PBI-02", "AUTH", "Sebagai Administrator, saya ingin melakukan logout dari sistem, agar sesi akses saya berakhir dan data sistem tetap terlindungi.",
         "1. Menekan tombol Logout menghapus token JWT dari local/session storage.\n2. Pengguna dialihkan otomatis ke halaman login.\n3. Rute halaman admin tidak dapat diakses kembali tanpa login ulang.",
         "Must Have", "2", "Sprint 1"),

        ("PBI-03", "STUDENT", "Sebagai Siswa, saya ingin melihat halaman informasi pengantar ProdiPath, agar saya memahami alur kerja dan batas rekomendasi sistem.",
         "1. Menampilkan hero section yang ramah dan informatif.\n2. Menjelaskan kriteria yang dinilai (nilai rapor, minat, analitis).\n3. Menyediakan tombol CTA langsung menuju form kuesioner tanpa perlu login.",
         "Should Have", "3", "Sprint 1"),

        ("PBI-04", "STUDENT", "Sebagai Siswa, saya ingin menginputkan identitas dasar (NISN 10 digit, nama lengkap, dan peminatan SMA IPA/IPS/Bahasa), agar data profil saya teridentifikasi.",
         "1. NISN divalidasi tepat 10 digit numerik.\n2. Pilihan jurusan SMA berupa dropdown (IPA, IPS, Bahasa).\n3. Nama lengkap tidak boleh kosong dan divalidasi format teks.",
         "Must Have", "3", "Sprint 1"),

        ("PBI-05", "STUDENT", "Sebagai Siswa, saya ingin memasukkan nilai rapor 4 mapel utama (Matematika, Sains, Sosial, Bahasa) skala 0-100, agar sistem dapat mengukur potensi akademik saya.",
         "1. Input angka divalidasi batas rentang 0 hingga 100.\n2. Terdapat validasi tipe data (tidak boleh huruf/negatif).\n3. Notifikasi visual jika input berada di luar batas yang ditentukan.",
         "Must Have", "3", "Sprint 1"),

        ("PBI-06", "STUDENT", "Sebagai Siswa, saya ingin menilai minat bidang (Teknologi, Seni, Komunikasi) dan kemampuan analitis mandiri skala Likert 1-5, agar potensi non-akademik saya terpetakan.",
         "1. Pilihan radio button / rating interaktif skala 1 sampai 5.\n2. Terdapat label keterangan (1: Sangat Rendah s.d. 5: Sangat Tinggi).\n3. Seluruh penilaian minat wajib dipilih sebelum submit.",
         "Must Have", "3", "Sprint 1"),

        ("PBI-07", "STUDENT", "Sebagai Siswa, saya ingin memberikan persetujuan penyimpanan data (consent checkbox), agar data saya digunakan secara transparan dan sesuai etika privasi.",
         "1. Terdapat checkbox persetujuan dengan klausul perlindungan privasi data.\n2. Tombol submit rekomendasi terkunci (disabled) jika checkbox belum dicentang.\n3. Status persetujuan dicatat ke database.",
         "Must Have", "2", "Sprint 1"),

        ("PBI-08", "AI-REC", "Sebagai Siswa, saya ingin menerima satu rekomendasi jurusan kuliah terbaik dari model Decision Tree, agar saya mendapat saran terarah untuk studi lanjut.",
         "1. Backend memanggil model Decision Tree Classifier terlatih.\n2. Menghasilkan label rekomendasi jurusan yang paling sesuai profil.\n3. Hasil prediksi ditampilkan dalam card hasil yang interaktif dan jelas.",
         "Must Have", "8", "Sprint 1"),

        ("PBI-09", "AI-REC", "Sebagai Siswa, saya ingin membaca detail penjelasan jurusan, peluang karir, dan disclaimer etika rekomendasi, agar saya memahami bahwa hasil adalah rujukan awal.",
         "1. Card rekomendasi memuat deskripsi program studi dan prospek karir.\n2. Ditampilkan badge disclaimer eksplisit bahwa keputusan akhir ada pada siswa/guru BK.\n3. Terdapat opsi saran alternatif program studi terkait.",
         "Should Have", "5", "Sprint 2"),

        ("PBI-10", "AI-REC", "Sebagai Sistem, saya ingin menyimpan hasil kuesioner dan rekomendasi siswa ke database dengan sumber 'kuesioner_web', agar riwayat data tersimpan rapi.",
         "1. Data tersimpan pada tabel questionnaire_data dengan flag sumber_data='kuesioner_web'.\n2. Jika NISN sudah ada, sistem memperbarui (update) data profil terkini.\n3. Timestamp created_at tercatat otomatis.",
         "Must Have", "3", "Sprint 2"),

        ("PBI-11", "DASH", "Sebagai Administrator, saya ingin melihat dashboard ringkasan statistik (total siswa, sebaran jurusan SMA, dan rekomendasi teratas), agar saya dapat memantau tren siswa.",
         "1. Kartu metrik total siswa, total data latih, dan rekomendasi dominan.\n2. Visualisasi grafik interaktif Chart.js (Bar chart & Doughnut chart).\n3. Data diperbarui real-time saat dashboard dibuka.",
         "Must Have", "5", "Sprint 2"),

        ("PBI-12", "STU-MGT", "Sebagai Administrator, saya ingin melihat daftar lengkap data siswa beserta fitur pencarian (berdasarkan NISN/Nama) dan filter jurusan SMA, agar data mudah ditelusuri.",
         "1. Tabel responsif memuat NISN, nama, jurusan SMA, nilai, minat, dan hasil jurusan.\n2. Kotak pencarian responsif menyaring data secara real-time.\n3. Filter dropdown berdasarkan jurusan SMA (IPA, IPS, Bahasa).",
         "Must Have", "5", "Sprint 2"),

        ("PBI-13", "STU-MGT", "Sebagai Administrator, saya ingin menghapus data kuesioner siswa tertentu jika terjadi kesalahan input, agar data tetap bersih dan relevan.",
         "1. Tombol aksi hapus pada setiap baris data siswa.\n2. Modal konfirmasi keamanan sebelum penghapusan dieksekusi.\n3. Data terhapus permanen dari database dan tabel me-refresh otomatis.",
         "Should Have", "3", "Sprint 2"),

        ("PBI-14", "DATASET", "Sebagai Administrator, saya ingin mengimpor dataset referensi baru berupa file CSV, agar model machine learning dapat diperbarui dengan data rujukan terkini.",
         "1. Form unggah berkas CSV khusus admin.\n2. Validasi struktur kolom (nisn, nilai, minat, rekomendasi_jurusan).\n3. Validasi rentang nilai (0-100) dan minat (1-5) sebelum proses simpan.",
         "Should Have", "5", "Sprint 3"),

        ("PBI-15", "DATASET", "Sebagai Tim Pengembang, saya ingin memiliki skrip training otomatis untuk melatih ulang model Decision Tree dan mengevaluasi akurasinya, agar kualitas model terjaga.",
         "1. Skrip train.py mengekstrak dataset CSV dan melakukan label encoding.\n2. Memisahkan data train dan holdout test.\n3. Menyimpan bobot model ke model_jurusan.pkl dan encoder ke label_encoder.pkl.",
         "Could Have", "5", "Sprint 3"),
    ]

    add_heading_2("2.1 Tabel Rinci Product Backlog Item (PBI)")
    
    table_pb = doc.add_table(rows=len(backlog_data) + 1, cols=7)
    table_pb.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_pb.autofit = False

    headers_pb = ["ID", "Modul", "User Story", "Kriteria Penerimaan (Acceptance Criteria)", "Prioritas", "Poin", "Sprint"]
    col_widths_pb = [Inches(0.65), Inches(0.75), Inches(2.2), Inches(2.1), Inches(0.8), Inches(0.5), Inches(0.65)]

    # Header Row
    hdr_row = table_pb.rows[0]
    for j, h_text in enumerate(headers_pb):
        cell = hdr_row.cells[j]
        cell.width = col_widths_pb[j]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 100, 100, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for i, row_data in enumerate(backlog_data):
        row = table_pb.rows[i + 1]
        bg_col = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.width = col_widths_pb[j]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, 80, 80, 90, 90)
            border_cfg = dict(val='single', sz='4', color='CBD5E1')
            set_cell_border(cell, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            
            # Text alignment
            if j in (0, 1, 4, 5, 6):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.2)
            
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 58, 138)
            elif j == 4:
                r.font.bold = True
                if val == "Must Have":
                    r.font.color.rgb = RGBColor(185, 28, 28)
                elif val == "Should Have":
                    r.font.color.rgb = RGBColor(217, 119, 6)
                else:
                    r.font.color.rgb = RGBColor(16, 185, 129)
            elif j == 5:
                r.font.bold = True
            else:
                r.font.color.rgb = RGBColor(51, 65, 85)

    add_body_paragraph("", space_after=4)

    # Rekapitulasi Rencana Sprint
    add_heading_2("2.2 Rekapitulasi Rencana Sprint dan Alokasi Beban Kerja")
    add_body_paragraph(
        "Berdasarkan hasil estimasi Story Points menggunakan deret Fibonacci, total bobot Product Backlog adalah 58 Story Points. "
        "Beban kerja dibagi secara bertahap ke dalam 3 Sprint iteratif:"
    )

    sprint_table = doc.add_table(rows=4, cols=5)
    sprint_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sprint_table.autofit = False

    sprint_headers = ["Sprint", "Fokus Utama Pengembangan", "Daftar Item PBI", "Total Poin", "Persentase"]
    sprint_widths = [Inches(0.9), Inches(2.6), Inches(1.8), Inches(1.0), Inches(1.0)]

    for j, h_text in enumerate(sprint_headers):
        cell = sprint_table.rows[0].cells[j]
        cell.width = sprint_widths[j]
        set_cell_background(cell, "2563EB")
        set_cell_margins(cell, 90, 90, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    sprint_rows = [
        ("Sprint 1", "Fondasi Sistem: Autentikasi Pengelola, Form Input Siswa, Validasi, dan Engine Prediksi Inti.",
         "PBI-01, PBI-02, PBI-03, PBI-04, PBI-05, PBI-06, PBI-07, PBI-08", "29 Poin", "50.0 %"),
        ("Sprint 2", "Antarmuka Hasil & Pengelolaan: Card Rekomendasi, Detail Prospek Karir, Penyimpanan Web, Dashboard Ringkasan, dan Manajemen Data Siswa.",
         "PBI-09, PBI-10, PBI-11, PBI-12, PBI-13", "21 Poin", "36.2 %"),
        ("Sprint 3", "Penyempurnaan Dataset: Fitur Import CSV Dataset Latih, Validasi Header/Rentang, dan Skrip Pelatihan Otomatis.",
         "PBI-14, PBI-15", "8 Poin", "13.8 %"),
    ]

    for i, s_row in enumerate(sprint_rows):
        row = sprint_table.rows[i + 1]
        bg_col = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(s_row):
            cell = row.cells[j]
            cell.width = sprint_widths[j]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, 80, 80, 90, 90)
            border_cfg = dict(val='single', sz='4', color='CBD5E1')
            set_cell_border(cell, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if j in (0, 2, 3, 4):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(51, 65, 85)
            if j in (0, 3):
                r.font.bold = True

    doc.add_page_break()

    # ------------------ BAB III: USE CASE DIAGRAM ------------------
    add_heading_1("BAB III. USE CASE DIAGRAM SISTEM REKOMENDASI PRODIPATH")
    add_body_paragraph(
        "Use Case Diagram menggambarkan interaksi fungsional antara aktor pengguna dengan sistem perangkat lunak ProdiPath. "
        "Diagram ini mendokumentasikan batasan sistem (system boundary), aktor luar yang terlibat, serta relasi dependensi "
        "seperti asosiasi langsung (association), pemanggilan wajib («include»), dan penambahan perilaku bersyarat («extend»)."
    )

    add_heading_2("3.1 Diagram Use Case")
    add_body_paragraph("Gambar berikut menyajikan Diagram Use Case Sistem Rekomendasi Program Studi Kuliah (ProdiPath):")

    # Insert Diagram Image
    diagram_path = r"d:\projek metopen\usecase_diagram.png"
    if os.path.exists(diagram_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(diagram_path, width=Inches(6.4))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run("Gambar 3.1 Use Case Diagram Sistem Rekomendasi Program Studi (ProdiPath)")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(100, 116, 139)

    add_heading_2("3.2 Deskripsi Aktor Sistem")
    add_body_paragraph(
        "Terdapat dua aktor utama yang berinteraksi dengan sistem perangkat lunak ProdiPath:"
    )
    add_bullet(
        "Siswa kelas XII SMA Muhammadiyah 2 Bandar Lampung sebagai pengguna publik akhir. Siswa dapat mengakses beranda, mengisi form profil diri (NISN, nilai rapor, minat, kemampuan analitis), menyetujui penyimpanan data, dan memperoleh rekomendasi jurusan AI tanpa perlu melakukan login akun.",
        "1. Siswa (Kelas XII): "
    )
    add_bullet(
        "Pihak Guru Bimbingan Konseling (BK) atau Tenaga Administrasi Sekolah yang memiliki hak akses kredensial resmi. Bertanggung jawab mengelola data isian siswa, memantau tren distribusi pilihan studi pada dashboard analitik, dan melakukan impor dataset referensi CSV untuk memperbarui data latih model.",
        "2. Administrator / Guru BK: "
    )

    add_heading_2("3.3 Daftar dan Klasifikasi Use Case")
    add_body_paragraph("Rincian use case yang didefinisikan pada sistem dirangkum dalam tabel berikut:")

    uc_summary = [
        ("UC-01", "Melihat Informasi Sistem & Panduan Studi", "Siswa", "Utama", "Menampilkan beranda pengantar, panduan pengisian profil, dan tujuan rekomendasi."),
        ("UC-02", "Mengisi Profil Akademik, Minat & Bakat", "Siswa", "Utama", "Menginput NISN, nama, jurusan SMA, nilai 4 mapel (0-100), dan minat 1-5."),
        ("UC-03", "Menyetujui Persetujuan Penyimpanan Data", "Siswa", "Utama", "Memberikan persetujuan (consent) penyimpanan data kuesioner ke sistem."),
        ("UC-04", "Mendapatkan Rekomendasi Jurusan (AI)", "Siswa", "Utama", "Memproses profil ke model Decision Tree dan menampilkan rekomendasi program studi."),
        ("UC-05", "Validasi Kelengkapan & Format Nilai Siswa", "Sistem", "«include»", "Memeriksa validitas NISN 10 digit, nilai 0-100, dan minat 1-5 sebelum rekomendasi dihitung."),
        ("UC-06", "Melihat Detail Penjelasan & Alternatif Jurusan", "Siswa", "«extend»", "Menampilkan prospek karir, penjabaran jurusan, dan alternatif bidang studi terkait."),
        ("UC-07", "Login Administrator (Kredensial Akun)", "Administrator", "Utama", "Autentikasi akun admin dengan username dan verifikasi password hash."),
        ("UC-08", "Melihat Dashboard Statistik & Distribusi Dataset", "Administrator", "Utama", "Menampilkan visualisasi grafik sebaran jurusan rekomendasi dan data siswa."),
        ("UC-09", "Mengelola Data Siswa (Cari, Tinjau, Hapus)", "Administrator", "Utama", "Menampilkan tabel data kuesioner web, pencarian nama/NISN, dan hapus entri."),
        ("UC-10", "Mengimpor Dataset CSV & Validasi Rentang", "Administrator", "Utama", "Mengunggah file CSV data latih baru dengan validasi struktur dan rentang nilai."),
        ("UC-11", "Logout Sesi Pengelola", "Administrator", "Utama", "Menghapus token JWT aktif dan mengakhiri sesi pengelolaan sistem."),
        ("UC-12", "Verifikasi Sesi Login & Autentikasi JWT", "Sistem", "«include»", "Memeriksa validitas bearer token JWT pada setiap permintaan API terproteksi.")
    ]

    table_ucs = doc.add_table(rows=len(uc_summary) + 1, cols=5)
    table_ucs.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_ucs.autofit = False

    ucs_headers = ["Kode", "Nama Use Case", "Aktor", "Kategori", "Deskripsi Fungsional Singkat"]
    ucs_widths = [Inches(0.7), Inches(2.3), Inches(1.1), Inches(0.9), Inches(2.2)]

    for j, h_text in enumerate(ucs_headers):
        cell = table_ucs.rows[0].cells[j]
        cell.width = ucs_widths[j]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 90, 90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for i, row_data in enumerate(uc_summary):
        row = table_ucs.rows[i + 1]
        bg_col = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.width = ucs_widths[j]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, 70, 70, 80, 80)
            border_cfg = dict(val='single', sz='4', color='CBD5E1')
            set_cell_border(cell, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if j in (0, 2, 3):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.2)
            r.font.color.rgb = RGBColor(51, 65, 85)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 58, 138)

    add_body_paragraph("", space_after=4)

    add_heading_2("3.4 Penjelasan Relasi Use Case («include» & «extend»)")
    add_bullet(
        "Relasi «include» menandakan use case sumber mutlak memerlukan use case tujuan agar dapat terselesaikan secara utuh. Pada sistem ProdiPath: "
        "(a) UC-02 (Mengisi Profil Siswa) meng-include UC-05 (Validasi Kelengkapan Nilai) karena data profil wajib divalidasi integritasnya sebelum sistem memproses rekomendasi; "
        "(b) UC-08, UC-09, dan UC-10 meng-include UC-12 (Verifikasi Sesi Login & Token JWT) karena endpoint panel administrator secara ketat memverifikasi token otorisasi sebelum mengizinkan pertukaran data.",
        "Relasi «include» (Penyertaan Wajib): "
    )
    add_bullet(
        "Relasi «extend» menandakan use case tambahan yang memperluas fungsionalitas use case dasar pada kondisi tertentu. Pada sistem ProdiPath, "
        "UC-06 (Melihat Detail Penjelasan & Alternatif Jurusan) meng-extend UC-04 (Mendapatkan Rekomendasi Jurusan) di mana setelah hasil rekomendasi utama keluar, "
        "siswa dapat memilih untuk mengeksplorasi deskripsi prospek karir dan program studi alternatif yang bersesuaian dengan profil minatnya.",
        "Relasi «extend» (Perluasan Bersyarat): "
    )

    doc.add_page_break()

    # ------------------ BAB IV: SPESIFIKASI DAN SKENARIO USE CASE ------------------
    add_heading_1("BAB IV. SPESIFIKASI DAN SKENARIO USE CASE (USE CASE SPECIFICATIONS)")
    add_body_paragraph(
        "Bagian ini mendokumentasikan spesifikasi rinci dan skenario alur kejadian (event flow) untuk setiap use case, mencakup prakondisi, "
        "pascakondisi, skenario normal (happy path), dan skenario alternatif/eksepsi kegagalan sistem."
    )

    use_case_specs = [
        {
            "id": "UC-01",
            "name": "Melihat Informasi Sistem & Panduan Studi",
            "actor": "Siswa (Kelas XII)",
            "desc": "Siswa membuka halaman awal website ProdiPath untuk memahami tujuan sistem dan panduan pengisian.",
            "pre": "Perangkat siswa terhubung dengan jaringan internet dan server web ProdiPath aktif.",
            "post": "Siswa memahami alur kuesioner dan siap mengisi formulir profil diri.",
            "normal": [
                "1. Siswa mengakses URL website ProdiPath melalui peramban web.",
                "2. Sistem menampilkan halaman Beranda (Hero Section, penjelasan kriteria, dan disclaimer model).",
                "3. Siswa membaca ringkasan alur rekomendasi dan petunjuk pengisian.",
                "4. Siswa mengklik tombol 'Mulai Rekomendasi' untuk menuju formulir kuesioner profil."
            ],
            "alt": [
                "2a. Server backend tidak merespons: Sistem menampilkan pesan peringatan status offline dan menyarankan refresh halaman."
            ]
        },
        {
            "id": "UC-02",
            "name": "Mengisi Profil Akademik, Minat & Bakat",
            "actor": "Siswa (Kelas XII)",
            "desc": "Siswa mengisikan data identitas, jurusan SMA, nilai rapor, dan preferensi minat pada formulir kuesioner.",
            "pre": "Siswa berada pada halaman formulir rekomendasi (/prediksi).",
            "post": "Data profil siswa terisi lengkap dan siap dikirim untuk divalidasi (UC-05).",
            "normal": [
                "1. Siswa memasukkan NISN (10 digit numerik) dan Nama Lengkap.",
                "2. Siswa memilih jurusan asal SMA (IPA, IPS, atau Bahasa) melalui dropdown.",
                "3. Siswa menginputkan nilai rapor Matematika, Sains, Sosial, dan Bahasa (skala 0-100).",
                "4. Siswa memilih rating minat Teknologi, Seni, Komunikasi, dan kemampuan Analitis (skala 1-5).",
                "5. Sistem menyertakan «include» UC-05 untuk memvalidasi kelengkapan dan format data."
            ],
            "alt": [
                "4a. Nilai rapor bernilai negatif atau melebihi 100: Form menampilkan border merah dan pesan 'Nilai harus 0-100'.",
                "4b. NISN kurang atau lebih dari 10 digit: Form menampilkan peringatan 'NISN harus 10 digit angka'."
            ]
        },
        {
            "id": "UC-03",
            "name": "Menyetujui Persetujuan Penyimpanan Data (Consent)",
            "actor": "Siswa (Kelas XII)",
            "desc": "Siswa memberikan konfirmasi etis dan persetujuan bahwa data profilnya disimpan untuk kebutuhan analisis sekolah.",
            "pre": "Siswa telah mengisi seluruh atribut formulir kuesioner.",
            "post": "Status persetujuan bernilai True dan tombol submit rekomendasi menjadi aktif.",
            "normal": [
                "1. Siswa membaca klausul persetujuan privasi data pada bagian akhir formulir.",
                "2. Siswa mencentang checkbox 'Saya menyetujui data profil ini disimpan untuk bahan evaluasi rekomendasi'.",
                "3. Sistem mengaktifkan tombol 'Dapatkan Rekomendasi Program Studi'."
            ],
            "alt": [
                "2a. Checkbox belum dicentang: Tombol submit tetap disabled dan muncul tooltip 'Persetujuan wajib dicentang sebelum melanjutkan'."
            ]
        },
        {
            "id": "UC-04",
            "name": "Mendapatkan Rekomendasi Jurusan (Decision Tree AI)",
            "actor": "Siswa (Kelas XII)",
            "desc": "Sistem mengirimkan profil siswa ke backend, mengeksekusi model klasifikasi, dan menyajikan rekomendasi.",
            "pre": "Formulir terisi valid (UC-05 terpenuhi) dan persetujuan data dicentang (UC-03 terpenuhi).",
            "post": "Rekomendasi jurusan ditampilkan di layar dan data tersimpan ke tabel questionnaire_data.",
            "normal": [
                "1. Siswa menekan tombol 'Dapatkan Rekomendasi Program Studi'.",
                "2. Frontend mengirimkan payload JSON profil siswa ke endpoint POST /api/predict/.",
                "3. Backend mengonversi fitur kategori jurusan SMA dan mengeksekusi Decision Tree model.",
                "4. Backend menyimpan data isian dan hasil prediksi ke MySQL dengan sumber 'kuesioner_web'.",
                "5. Sistem menampilkan Card Rekomendasi Jurusan yang memuat nama prodi dan kecocokan profil.",
                "6. Siswa dapat memperluas informasi melalui «extend» UC-06 untuk melihat detail penjelasan."
            ],
            "alt": [
                "3a. Model AI belum dilatih atau file model_jurusan.pkl korup: Backend merespons status error 500 dan frontend menampilkan saran hubungi admin.",
                "4a. NISN siswa telah ada sebelumnya: Sistem melakukan UPDATE pada rekaman data NISN yang bersangkutan."
            ]
        },
        {
            "id": "UC-05",
            "name": "Validasi Kelengkapan & Format Nilai Siswa («include»)",
            "actor": "Sistem (ProdiPath Engine)",
            "desc": "Memeriksa integritas seluruh isian sebelum diproses lebih lanjut oleh engine klasifikasi.",
            "pre": "Siswa melakukan interaksi pengisian form dan menekan tombol rekomendasi.",
            "post": "Data diverifikasi valid (siap dikirim ke server) atau ditolak dengan pesan kesalahan visual.",
            "normal": [
                "1. Sistem memverifikasi NISN hanya memuat angka dan berjumlah 10 karakter.",
                "2. Sistem memverifikasi nilai Matematika, Sains, Sosial, dan Bahasa bertipe integer dan 0 <= nilai <= 100.",
                "3. Sistem memverifikasi minat Teknologi, Seni, Komunikasi, dan Analitis bertipe integer 1 <= nilai <= 5.",
                "4. Sistem menerbitkan status lolos validasi ke form pemanggil."
            ],
            "alt": [
                "1a. Terdapat field kosong: Sistem menyorot input terkait dan menampilkan notifikasi 'Kolom ini wajib diisi'."
            ]
        },
        {
            "id": "UC-06",
            "name": "Melihat Detail Penjelasan & Alternatif Jurusan («extend»)",
            "actor": "Siswa (Kelas XII)",
            "desc": "Siswa membuka tab atau modal informasi pendukung untuk memperdalam wawasan program studi hasil rekomendasi.",
            "pre": "Siswa telah berhasil menerima rekomendasi jurusan utama pada UC-04.",
            "post": "Siswa mendapatkan wawasan komprehensif mengenai prospek karir dan alternatif jurusan terkait.",
            "normal": [
                "1. Pada card hasil rekomendasi, siswa mengklik tombol 'Pelajari Jurusan Ini & Alternatif'.",
                "2. Sistem menampilkan penjelasan bidang keilmuan yang dipelajari dan relevansi nilai raportnya.",
                "3. Sistem menyajikan daftar prospek karir potensial di dunia industri.",
                "4. Sistem menampilkan opsi 2 jurusan alternatif serumpun sebagai bahan pembanding.",
                "5. Siswa membaca catatan pengingat untuk tetap mendiskusikan hasil bersama Guru BK dan orang tua."
            ],
            "alt": [
                "1a. Siswa tidak mengklik tombol detail: Alur selesai pada tampilan rekomendasi utama tanpa kendala."
            ]
        },
        {
            "id": "UC-07",
            "name": "Login Administrator (Kredensial Akun)",
            "actor": "Administrator / Guru BK",
            "desc": "Proses otentikasi pengelola untuk memperoleh akses ke halaman dashboard dan data siswa.",
            "pre": "Administrator membuka halaman login (/login) dan memiliki akun terdaftar.",
            "post": "Administrator berhasil masuk ke dashboard dan token JWT disimpan pada browser.",
            "normal": [
                "1. Administrator membuka halaman login.",
                "2. Administrator memasukkan username dan password.",
                "3. Administrator menekan tombol 'Masuk sebagai Pengelola'.",
                "4. Backend memverifikasi username dan mencocokkan password_hash (bcrypt).",
                "5. Backend menghasilkan JWT access token.",
                "6. Frontend menyimpan token dan mengarahkan admin ke halaman Dashboard (/dashboard)."
            ],
            "alt": [
                "4a. Username tidak ditemukan atau password salah: Sistem menampilkan pesan 'Username atau password salah'.",
                "4b. Role akun bukan admin: Sistem menolak akses dan mengarahkan ke halaman prediksi publik."
            ]
        },
        {
            "id": "UC-08",
            "name": "Melihat Dashboard Statistik & Distribusi Dataset",
            "actor": "Administrator / Guru BK",
            "desc": "Menyajikan ringkasan visual analitis data siswa dan dataset latih rujukan.",
            "pre": "Administrator telah terautentikasi dan sesi valid («include» UC-12).",
            "post": "Grafik statistik dan metrik data tampil secara akurat di layar dashboard.",
            "normal": [
                "1. Administrator memilih menu 'Dashboard' pada navigasi samping.",
                "2. Sistem menyertakan «include» UC-12 untuk memverifikasi bearer token JWT.",
                "3. Backend menghitung total siswa, total dataset latih, dan sebaran jurusan melalui endpoint GET /api/dashboard/summary.",
                "4. Sistem me-render kartu metrik ringkasan data.",
                "5. Sistem menampilkan grafik Chart.js distribusi jurusan rekomendasi dan sebaran jurusan SMA."
            ],
            "alt": [
                "2a. Token kadaluarsa: Sistem menampilkan sesi berakhir dan mengarahkan admin ke halaman login."
            ]
        },
        {
            "id": "UC-09",
            "name": "Mengelola Data Siswa (Pencarian, Tinjau, Hapus)",
            "actor": "Administrator / Guru BK",
            "desc": "Pengelolaan data kuesioner siswa yang tersimpan di sistem, termasuk pencarian dan pembersihan data uji.",
            "pre": "Administrator telah login dan sesi valid («include» UC-12).",
            "post": "Data siswa tertampil, dapat difilter, dan entri terpilih dapat dihapus bila diperlukan.",
            "normal": [
                "1. Administrator memilih menu 'Data Siswa' (/mahasiswa).",
                "2. Sistem menyertakan «include» UC-12 untuk validasi otorisasi token.",
                "3. Backend mengambil daftar siswa sumber 'kuesioner_web' via GET /api/students/.",
                "4. Administrator dapat mengetikkan nama/NISN pada kolom pencarian untuk menyaring data seketika.",
                "5. Administrator dapat mengklik tombol 'Hapus' pada baris siswa tertentu.",
                "6. Sistem menampilkan dialog konfirmasi penghapusan.",
                "7. Administrator mengonfirmasi, backend mengeksekusi DELETE /api/students/{nisn}, dan tabel me-refresh."
            ],
            "alt": [
                "7a. Penghapusan dibatalkan: Sistem menutup dialog konfirmasi tanpa mengubah database."
            ]
        },
        {
            "id": "UC-10",
            "name": "Mengimpor Dataset CSV & Validasi Format Data",
            "actor": "Administrator / Guru BK",
            "desc": "Mengunggah berkas CSV dataset eksternal untuk melengkapi data latih rekomendasi.",
            "pre": "Administrator berada di halaman Import Data (/import) dengan token valid («include» UC-12).",
            "post": "Baris data valid tersimpan ke database dengan tag sumber_data='dataset'.",
            "normal": [
                "1. Administrator memilih menu 'Import Dataset'.",
                "2. Administrator mengunggah berkas format CSV melalui tombol file picker / drag-and-drop.",
                "3. Sistem memverifikasi kesesuaian header kolom (nisn, nama, nilai, minat, rekomendasi_jurusan).",
                "4. Sistem memverifikasi rentang nilai setiap baris (0-100 dan 1-5).",
                "5. Administrator menekan tombol 'Proses Import ke Database'.",
                "6. Backend memproses data via POST /api/dataset/import dan menampilkan pesan jumlah baris berhasil."
            ],
            "alt": [
                "3a. Header CSV tidak sesuai template: Sistem menolak file dan menampilkan daftar kolom yang wajib ada.",
                "4a. Terdapat baris dengan nilai di luar rentang: Sistem menampilkan baris error dan membatalkan impor."
            ]
        },
        {
            "id": "UC-11",
            "name": "Logout Sesi Pengelola",
            "actor": "Administrator / Guru BK",
            "desc": "Mengakhiri sesi akses manajemen administrator secara aman.",
            "pre": "Administrator sedang dalam kondisi login di sistem.",
            "post": "Token sesi terhapus dan sistem kembali ke halaman login.",
            "normal": [
                "1. Administrator mengklik tombol 'Keluar' pada menu profil / sidebar.",
                "2. Sistem menghapus token otentikasi JWT dari local storage browser.",
                "3. Sistem mereset state otentikasi pada context aplikasi.",
                "4. Sistem mengarahkan browser ke halaman /login."
            ],
            "alt": [
                "1a. Koneksi internet terputus saat klik logout: Pembersihan sisi klien tetap dieksekusi demi keamanan."
            ]
        },
        {
            "id": "UC-12",
            "name": "Verifikasi Sesi Login & Autentikasi JWT («include»)",
            "actor": "Sistem (Auth Security Middleware)",
            "desc": "Memeriksa keabsahan token JWT pada setiap transaksi permintaan rute dan data terproteksi.",
            "pre": "Pengguna melakukan aksi yang membutuhkan hak akses Administrator.",
            "post": "Permintaan diteruskan jika token valid, atau diblokir dengan kode HTTP 401 Unauthorized.",
            "normal": [
                "1. Frontend melampirkan Authorization: Bearer <token> pada header permintaan HTTP.",
                "2. Backend memverifikasi tanda tangan digital JWT menggunakan secret key server.",
                "3. Backend memastikan token belum melewati masa berlaku (expiration time).",
                "4. Backend mengonfirmasi role pengguna bernilai 'admin'.",
                "5. Permintaan diizinkan untuk diproses oleh controller endpoint."
            ],
            "alt": [
                "2a. Token hilang, cacat, atau kedaluwarsa: Backend mengembalikan status 401 Unauthorized, frontend menghapus sesi dan me-redirect ke halaman login."
            ]
        }
    ]

    for spec in use_case_specs:
        add_heading_2(f"4.{use_case_specs.index(spec)+1} Spesifikasi {spec['id']}: {spec['name']}")
        
        spec_table = doc.add_table(rows=8, cols=2)
        spec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        spec_table.autofit = False

        spec_rows_data = [
            ("Kode & Nama Use Case", f"{spec['id']} — {spec['name']}"),
            ("Aktor yang Terlibat", spec['actor']),
            ("Deskripsi Singkat", spec['desc']),
            ("Kondisi Awal (Pre-condition)", spec['pre']),
            ("Kondisi Akhir (Post-condition)", spec['post']),
            ("Alur Kejadian Utama (Normal Flow)", "\n".join(spec['normal'])),
            ("Alur Alternatif / Eksepsi (Alternative Flow)", "\n".join(spec['alt'])),
            ("Aturan Bisnis & Validasi Terkait", "Sesuai Standar Data Akademik SMA & Kebijakan Etika Privasi Data Siswa")
        ]

        for i, (k, v) in enumerate(spec_rows_data):
            row = spec_table.rows[i]
            c0, c1 = row.cells[0], row.cells[1]
            c0.width = Inches(2.1)
            c1.width = Inches(4.4)
            
            set_cell_background(c0, "F1F5F9")
            set_cell_background(c1, "FFFFFF" if i % 2 == 0 else "F8FAFC")
            set_cell_margins(c0, 60, 60, 80, 80)
            set_cell_margins(c1, 60, 60, 80, 80)
            
            border_cfg = dict(val='single', sz='4', color='CBD5E1')
            set_cell_border(c0, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
            set_cell_border(c1, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)

            p0 = c0.paragraphs[0]
            p0.paragraph_format.space_after = Pt(0)
            r0 = p0.add_run(k)
            r0.font.name = "Calibri"
            r0.font.size = Pt(8.5)
            r0.font.bold = True
            r0.font.color.rgb = RGBColor(30, 41, 59)

            p1 = c1.paragraphs[0]
            p1.paragraph_format.space_after = Pt(0)
            p1.paragraph_format.line_spacing = 1.05
            r1 = p1.add_run(v)
            r1.font.name = "Calibri"
            r1.font.size = Pt(8.5)
            r1.font.color.rgb = RGBColor(51, 65, 85)

        add_body_paragraph("", space_after=4)

    doc.add_page_break()

    # ------------------ BAB V: MATRIKS KETERTELUSURAN ------------------
    add_heading_1("BAB V. MATRIKS KETERTELUSURAN (REQUIREMENTS TRACEABILITY MATRIX)")
    add_body_paragraph(
        "Matriks Ketertelusuran (Requirements Traceability Matrix) membuktikan bahwa setiap Product Backlog Item (PBI) "
        "yang didefinisikan pada tahap perencanaan kebutuhan telah memiliki representasi yang jelas pada Use Case Diagram "
        "dan skenario sistem, serta tidak ada kebutuhan fungsional yang terlewatkan."
    )

    trace_data = [
        ("PBI-01", "Login Pengelola menggunakan username dan password", "UC-07", "Login Administrator (Kredensial Akun)"),
        ("PBI-02", "Logout dari sistem untuk mengakhiri sesi akses", "UC-11", "Logout Sesi Pengelola"),
        ("PBI-03", "Melihat halaman informasi pengantar dan panduan", "UC-01", "Melihat Informasi Sistem & Panduan Studi"),
        ("PBI-04", "Input identitas dasar (NISN, Nama, Peminatan SMA)", "UC-02, UC-05", "Mengisi Profil Siswa & Validasi Kelengkapan"),
        ("PBI-05", "Input nilai rapor 4 mapel utama skala 0-100", "UC-02, UC-05", "Mengisi Profil Siswa & Validasi Rentang Nilai"),
        ("PBI-06", "Penilaian minat bidang dan analitis skala 1-5", "UC-02, UC-05", "Mengisi Profil Siswa & Validasi Skala Minat"),
        ("PBI-07", "Persetujuan penyimpanan data (consent checkbox)", "UC-03", "Menyetujui Persetujuan Penyimpanan Data"),
        ("PBI-08", "Menerima rekomendasi prodi dari model Decision Tree", "UC-04", "Mendapatkan Rekomendasi Jurusan (AI)"),
        ("PBI-09", "Melihat detail prodi, prospek karir, dan disclaimer", "UC-06", "Melihat Detail Penjelasan & Alternatif Jurusan"),
        ("PBI-10", "Penyimpanan hasil kuesioner web ke database MySQL", "UC-04", "Mendapatkan Rekomendasi Jurusan (AI)"),
        ("PBI-11", "Melihat dashboard analitik dan grafik distribusi", "UC-08, UC-12", "Melihat Dashboard & Verifikasi Sesi JWT"),
        ("PBI-12", "Melihat daftar siswa, pencarian, dan filter jurusan", "UC-09, UC-12", "Mengelola Data Siswa & Verifikasi Sesi JWT"),
        ("PBI-13", "Menghapus data kuesioner siswa dengan konfirmasi", "UC-09, UC-12", "Mengelola Data Siswa & Verifikasi Sesi JWT"),
        ("PBI-14", "Import dataset referensi CSV dan validasi rentang", "UC-10, UC-12", "Mengimpor Dataset CSV & Verifikasi Sesi JWT"),
        ("PBI-15", "Skrip pelatihan ulang model Decision Tree offline", "Modul ML", "ml/train.py & Pembaruan Model Klasifikasi"),
    ]

    table_trace = doc.add_table(rows=len(trace_data) + 1, cols=4)
    table_trace.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_trace.autofit = False

    tr_headers = ["Kode PBI", "Deskripsi Kebutuhan Product Backlog", "Kode UC", "Nama Use Case / Komponen Terkait"]
    tr_widths = [Inches(1.0), Inches(2.7), Inches(1.0), Inches(2.3)]

    for j, h_text in enumerate(tr_headers):
        cell = table_trace.rows[0].cells[j]
        cell.width = tr_widths[j]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 90, 90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for i, row_data in enumerate(trace_data):
        row = table_trace.rows[i + 1]
        bg_col = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.width = tr_widths[j]
            set_cell_background(cell, bg_col)
            set_cell_margins(cell, 70, 70, 80, 80)
            border_cfg = dict(val='single', sz='4', color='CBD5E1')
            set_cell_border(cell, top=border_cfg, bottom=border_cfg, left=border_cfg, right=border_cfg)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if j in (0, 2):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.2)
            r.font.color.rgb = RGBColor(51, 65, 85)
            if j in (0, 2):
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 58, 138)

    add_body_paragraph("", space_after=4)

    # ------------------ BAB VI: PENUTUP ------------------
    add_heading_1("BAB VI. PENUTUP & KESIMPULAN")
    add_body_paragraph(
        "Penyusunan dokumen Product Backlog dan Use Case Diagram ini menjadi landasan rekayasa perangkat lunak yang kokoh "
        "bagi proyek pengembangan sistem rekomendasi program studi ProdiPath. Melalui perumusan 15 Product Backlog Items "
        "yang terstruktur rapi ke dalam 3 tahapan Sprint, tim pengembang dapat memastikan setiap fungsionalitas dibangun "
        "secara terukur dan selaras dengan kebutuhan mitra di SMA Muhammadiyah 2 Bandar Lampung."
    )
    add_body_paragraph(
        "Diagram Use Case dan spesifikasi formal yang dirancang telah mencakup interaksi dua aktor (Siswa dan Administrator) "
        "beserta relasi ketergantungan «include» untuk validasi keamanan dan «extend» untuk pendalaman wawasan studi siswa. "
        "Dengan dokumentasi ini, proyek siap melanjutkan ke tahapan implementasi sprint berikutnya serta pengujian fungsional sistem."
    )

    return doc

if __name__ == "__main__":
    print("Membangun dokumen Word (DOCX)...")
    doc = create_document()
    
    # Save target file paths
    # 1. in d:\projek metopen
    docx_file1 = os.path.abspath(r"d:\projek metopen\usecase_namakelompok.docx")
    docx_file2 = os.path.abspath(r"d:\projek metopen\usecase_prodipath.docx")
    doc.save(docx_file1)
    doc.save(docx_file2)
    print(f"File Word berhasil disimpan:\n  - {docx_file1}\n  - {docx_file2}")

    # Convert to PDF using Microsoft Word COM Automation
    print("Mengonversi dokumen Word ke PDF menggunakan Microsoft Word...")
    pdf_file1 = os.path.abspath(r"d:\projek metopen\usecase_namakelompok.pdf")
    pdf_file2 = os.path.abspath(r"d:\projek metopen\usecase_prodipath.pdf")
    
    # Also save to user Downloads folder for convenience
    pdf_downloads = os.path.abspath(r"C:\Users\acer\Downloads\usecase_namakelompok.pdf")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    
    try:
        wb = word.Documents.Open(docx_file1)
        wb.SaveAs(pdf_file1, FileFormat=17) # 17 = wdFormatPDF
        wb.SaveAs(pdf_file2, FileFormat=17)
        wb.SaveAs(pdf_downloads, FileFormat=17)
        wb.Close()
        print(f"File PDF berhasil dibuat:\n  - {pdf_file1}\n  - {pdf_file2}\n  - {pdf_downloads}")
    except Exception as e:
        print("Terjadi kesalahan saat konversi PDF:", e)
    finally:
        word.Quit()
    
    print("Selesai seluruh proses pembuatan dokumen!")
