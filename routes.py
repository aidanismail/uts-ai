# app/routes.py

from flask import Blueprint, render_template, request
from scheduler import jalankan_simulasi

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/jadwal', methods=['POST'])
def jadwal():
    jumlah_peserta = int(request.form.get('jumlah_peserta'))
    hasil_simulasi = jalankan_simulasi(jumlah_peserta)
    return render_template('hasil.html', hasil=hasil_simulasi)
