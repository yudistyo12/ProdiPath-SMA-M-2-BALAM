import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

# Set figure size and resolution for crisp academic paper quality
fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Background color
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Draw Actor Function
def draw_actor(ax, x, y, name, role_desc):
    # Head
    head = Circle((x, y + 3.4), 1.25, fill=True, facecolor='#E0E7FF', edgecolor='#1E3A8A', lw=2.2, zorder=6)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 2.15, y - 0.7], color='#1E3A8A', lw=2.6, zorder=6)
    # Arms
    ax.plot([x - 2.2, x + 2.2], [y + 1.2, y + 1.2], color='#1E3A8A', lw=2.6, zorder=6)
    # Legs
    ax.plot([x, x - 1.8], [y - 0.7, y - 3.5], color='#1E3A8A', lw=2.6, zorder=6)
    ax.plot([x, x + 1.8], [y - 0.7, y - 3.5], color='#1E3A8A', lw=2.6, zorder=6)
    # Label Box
    ax.text(x, y - 5.0, name, ha='center', va='top', fontsize=10.5, fontweight='bold', color='#0F172A',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#94A3B8', lw=1.2))
    ax.text(x, y - 7.3, role_desc, ha='center', va='top', fontsize=8.2, color='#475569', style='italic')

# System Boundary Box
system_box = FancyBboxPatch((15, 5), 70, 90, boxstyle="round,pad=0.8,rounding_size=1.6",
                            facecolor='#FAFAFA', edgecolor='#334155', lw=2.4, zorder=1)
ax.add_patch(system_box)

# System Header
title_box = FancyBboxPatch((20, 89), 60, 4.8, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor='#1E40AF', edgecolor='#1D4ED8', lw=1.5, zorder=2)
ax.add_patch(title_box)
ax.text(50, 91.4, "Sistem Rekomendasi Program Studi Kuliah (ProdiPath)",
        ha='center', va='center', fontsize=13, fontweight='bold', color='#FFFFFF', zorder=3)

# Draw Use Case Helper Function (Ellipse-like pill)
def draw_usecase(ax, x, y, width, height, text, ucid, color_type='siswa'):
    if color_type == 'siswa':
        fcolor = '#EFF6FF'
        ecolor = '#2563EB'
        tcolor = '#1E3A8A'
    elif color_type == 'admin':
        fcolor = '#FAF5FF'
        ecolor = '#7C3AED'
        tcolor = '#4C1D95'
    else: # include / extend / shared
        fcolor = '#F8FAFC'
        ecolor = '#0284C7' if color_type == 'include' else ('#D97706' if color_type == 'extend' else '#475569')
        tcolor = '#0F172A'
        
    pill = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.4,rounding_size=2.0",
                          facecolor=fcolor, edgecolor=ecolor, lw=1.8, zorder=3)
    ax.add_patch(pill)
    
    full_text = f"«{ucid}»\n{text}"
    ax.text(x, y, full_text, ha='center', va='center', fontsize=8.3, fontweight='bold',
            color=tcolor, zorder=4, multialignment='center', linespacing=1.2)

# Coordinates for 3-column Layout:
# Col 1 (Siswa Primary): X = 28
# Col 2 (Shared / Sub-usecase): X = 50
# Col 3 (Admin Primary): X = 72

usecases = {
    # Siswa Column
    'UC01': {'x': 28, 'y': 80, 'w': 21, 'h': 5.2, 't': 'Melihat Informasi Sistem\n& Panduan Studi', 'id': 'UC-01', 'type': 'siswa'},
    'UC02': {'x': 28, 'y': 64, 'w': 21, 'h': 5.6, 't': 'Mengisi Profil Akademik,\nMinat & Bakat', 'id': 'UC-02', 'type': 'siswa'},
    'UC03': {'x': 28, 'y': 48, 'w': 21, 'h': 5.4, 't': 'Menyetujui Persetujuan\nPenyimpanan Data', 'id': 'UC-03', 'type': 'siswa'},
    'UC04': {'x': 28, 'y': 32, 'w': 21, 'h': 5.6, 't': 'Mendapatkan Rekomendasi\nJurusan (Decision Tree)', 'id': 'UC-04', 'type': 'siswa'},

    # Middle Column: Include & Extend
    'UC05': {'x': 50, 'y': 64, 'w': 20, 'h': 5.4, 't': 'Validasi Kelengkapan\n& Format Nilai Siswa', 'id': 'UC-05', 'type': 'include'},
    'UC06': {'x': 50, 'y': 32, 'w': 20, 'h': 5.4, 't': 'Melihat Detail Penjelasan\n& Alternatif Jurusan', 'id': 'UC-06', 'type': 'extend'},
    'UC12': {'x': 50, 'y': 16, 'w': 20, 'h': 5.4, 't': 'Verifikasi Sesi Login\n& Autentikasi JWT', 'id': 'UC-12', 'type': 'include'},

    # Admin Column
    'UC07': {'x': 72, 'y': 80, 'w': 21, 'h': 5.2, 't': 'Login Administrator\n(Kredensial Akun)', 'id': 'UC-07', 'type': 'admin'},
    'UC08': {'x': 72, 'y': 66, 'w': 21, 'h': 5.4, 't': 'Melihat Dashboard Statistik\n& Distribusi Dataset', 'id': 'UC-08', 'type': 'admin'},
    'UC09': {'x': 72, 'y': 52, 'w': 21, 'h': 5.4, 't': 'Mengelola Data Siswa\n(Pencarian, Tinjau, Hapus)', 'id': 'UC-09', 'type': 'admin'},
    'UC10': {'x': 72, 'y': 38, 'w': 21, 'h': 5.4, 't': 'Mengimpor Dataset CSV\n& Validasi Rentang Nilai', 'id': 'UC-10', 'type': 'admin'},
    'UC11': {'x': 72, 'y': 24, 'w': 21, 'h': 5.0, 't': 'Logout Sesi Pengelola\n(Hapus Token Sesi)', 'id': 'UC-11', 'type': 'admin'},
}

# Draw All Use Cases
for k, uc in usecases.items():
    draw_usecase(ax, uc['x'], uc['y'], uc['w'], uc['h'], uc['t'], uc['id'], uc['type'])

# Draw Actors
draw_actor(ax, 7.5, 56, "Siswa (Kelas XII)", "Pengguna Publik SMA M2")
draw_actor(ax, 92.5, 56, "Administrator", "Guru BK / Pengelola Sistem")

# Association Lines: Siswa to Siswa Use Cases
siswa_pt = (9.5, 57)
for ucid in ['UC01', 'UC02', 'UC03', 'UC04']:
    uc = usecases[ucid]
    ax.annotate("", xy=(uc['x'] - uc['w']/2, uc['y']), xytext=siswa_pt,
                arrowprops=dict(arrowstyle="-", color="#2563EB", lw=1.8, shrinkA=6, shrinkB=2))

# Association Lines: Admin to Admin Use Cases
admin_pt = (90.5, 57)
for ucid in ['UC07', 'UC08', 'UC09', 'UC10', 'UC11']:
    uc = usecases[ucid]
    ax.annotate("", xy=(uc['x'] + uc['w']/2, uc['y']), xytext=admin_pt,
                arrowprops=dict(arrowstyle="-", color="#7C3AED", lw=1.8, shrinkA=6, shrinkB=2))

# INCLUDE: UC-02 -> UC-05 (Mengisi Profil -> Validasi Input)
ax.annotate("", xy=(usecases['UC05']['x'] - usecases['UC05']['w']/2, usecases['UC05']['y']),
            xytext=(usecases['UC02']['x'] + usecases['UC02']['w']/2, usecases['UC02']['y']),
            arrowprops=dict(arrowstyle="->", linestyle="dashed", color="#0284C7", lw=1.8,
                            shrinkA=2, shrinkB=3, mutation_scale=14))
ax.text(39, 65.5, "«include»", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0284C7',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#0284C7', lw=0.8))

# EXTEND: UC-06 -> UC-04 (Detail Rekomendasi extends Mendapatkan Rekomendasi)
ax.annotate("", xy=(usecases['UC04']['x'] + usecases['UC04']['w']/2, usecases['UC04']['y']),
            xytext=(usecases['UC06']['x'] - usecases['UC06']['w']/2, usecases['UC06']['y']),
            arrowprops=dict(arrowstyle="->", linestyle="dashed", color="#D97706", lw=1.8,
                            shrinkA=2, shrinkB=3, mutation_scale=14))
ax.text(39, 33.5, "«extend»", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#D97706',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#D97706', lw=0.8))

# INCLUDE: UC-08, UC-09, UC-10 -> UC-12 (Verifikasi JWT)
# Clean curved arrows down to UC-12 from left of admin use cases
for ucid, rad_val, y_tgt in [('UC08', -0.16, 17.5), ('UC09', -0.12, 16.0), ('UC10', -0.08, 14.5)]:
    uc_adm = usecases[ucid]
    ax.annotate("", xy=(usecases['UC12']['x'] + usecases['UC12']['w']/2, y_tgt),
                xytext=(uc_adm['x'] - uc_adm['w']/2, uc_adm['y']),
                arrowprops=dict(arrowstyle="->", linestyle="dashed", color="#0284C7", lw=1.3,
                                shrinkA=2, shrinkB=3, mutation_scale=12,
                                connectionstyle=f"arc3,rad={rad_val}"))
ax.text(60.5, 29.5, "«include»", ha='center', va='center', fontsize=7.8, fontweight='bold', color='#0284C7',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#0284C7', lw=0.8))

# Legend at bottom
leg_y = 7.5
ax.text(18, leg_y, "Keterangan Legend:", fontsize=9, fontweight='bold', color='#1E293B')

# Siswa
ax.add_patch(FancyBboxPatch((32, leg_y - 1.0), 12, 2.0, boxstyle="round,pad=0.2", facecolor='#EFF6FF', edgecolor='#2563EB', lw=1.3))
ax.text(38, leg_y, "Use Case Siswa", fontsize=8, color='#1E3A8A', ha='center', va='center', fontweight='bold')

# Admin
ax.add_patch(FancyBboxPatch((46, leg_y - 1.0), 12, 2.0, boxstyle="round,pad=0.2", facecolor='#FAF5FF', edgecolor='#7C3AED', lw=1.3))
ax.text(52, leg_y, "Use Case Admin", fontsize=8, color='#4C1D95', ha='center', va='center', fontweight='bold')

# Include
ax.add_patch(FancyBboxPatch((60, leg_y - 1.0), 10.5, 2.0, boxstyle="round,pad=0.2", facecolor='#F8FAFC', edgecolor='#0284C7', lw=1.3))
ax.text(65.25, leg_y, "«include»", fontsize=8, color='#0284C7', ha='center', va='center', fontweight='bold')

# Extend
ax.add_patch(FancyBboxPatch((72, leg_y - 1.0), 10.5, 2.0, boxstyle="round,pad=0.2", facecolor='#F8FAFC', edgecolor='#D97706', lw=1.3))
ax.text(77.25, leg_y, "«extend»", fontsize=8, color='#D97706', ha='center', va='center', fontweight='bold')

plt.tight_layout()
output_path = r"d:\projek metopen\usecase_diagram.png"
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"Diagram saved successfully to: {output_path}")
