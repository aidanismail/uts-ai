# app/fuzzy_logic.py

def fuzzifikasi(rasio):
    μ = {
        "Underutilized Berat": 1 if rasio < 3 else max(0, (4 - rasio) / 1),
        "Underutilized Ringan": 0,
        "Optimal": 0,
        "Overload Ringan": 0,
        "Overload Berat": 0,
    }

    if 3 <= rasio <= 4:
        μ["Underutilized Ringan"] = (rasio - 3) / 1
    elif 4 < rasio <= 5:
        μ["Underutilized Ringan"] = (5 - rasio) / 1

    if 5 <= rasio <= 10:
        μ["Optimal"] = (rasio - 5) / 5
    elif 10 < rasio <= 15:
        μ["Optimal"] = (15 - rasio) / 5

    if 15 <= rasio <= 18:
        μ["Overload Ringan"] = (rasio - 15) / 3
    elif 18 < rasio <= 20:
        μ["Overload Ringan"] = (20 - rasio) / 2

    if 20 < rasio <= 25:
        μ["Overload Berat"] = (rasio - 20) / 5
    elif rasio > 25:
        μ["Overload Berat"] = 1

    return μ

# Konversi fuzzy output ke nilai crisp
output_rules = {
    "Underutilized Berat": 1,
    "Underutilized Ringan": 0.5,
    "Optimal": 0,
    "Overload Ringan": 1,
    "Overload Berat": 2
}

def inferensi(μ):
    return {label: μ[label] * output_rules[label] for label in μ}

def defuzzifikasi(hasil_inferensi):
    total_numerator = sum(hasil_inferensi.values())
    total_denominator = sum(μ for μ in hasil_inferensi.values() if μ > 0)

    if total_denominator == 0:
        return 0
    else:
        return round(total_numerator / total_denominator, 2)

def fuzzy_relokasi(rasio):
    μ = fuzzifikasi(rasio)
    hasil = inferensi(μ)
    return defuzzifikasi(hasil)
