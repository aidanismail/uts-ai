# app/routes.py

from flask import Blueprint, render_template, request
from scheduler import jalankan_simulasi

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    hasil_simulasi = jalankan_simulasi(jumlah_peserta_total=35)  # or any default number
    return render_template('index.html', hasil=hasil_simulasi)

@routes.route('/jadwal', methods=['POST'])
def jadwal():
    jumlah_peserta = int(request.form.get('jumlah_peserta'))
    hasil_simulasi = jalankan_simulasi(jumlah_peserta)
    return render_template('hasil.html', hasil=hasil_simulasi)
