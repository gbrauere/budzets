from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime

# Izveido Flask aplikāciju
app = Flask(__name__)

# CSV fails, kur glabās datus
fails = "dati.csv"
dati = []

# Funkcijas datu apstrādei
def ieladet_datus():
    """Ielādē datus no CSV faila."""
    try:
        with open(fails, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Pārvērš summas uz float un saglabā datumu, ja tas ir pieejams
            return [
                {
                    "tips": r["tips"],
                    "summa": float(r["summa"]),
                    "apraksts": r["apraksts"],
                    "datums": r.get("datums", "")
                } for r in reader
            ]
    except FileNotFoundError:
        return [] # Ja fails neeksistē, atgriež tukšu sarakstu

def saglabat_datus():
    """Saglabā datus CSV failā."""
    with open(fails, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["tips", "summa", "apraksts", "datums"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader() # Ieraksta kolonnu virsrakstus
        for ier in dati:
            writer.writerow({
                "tips": ier["tips"],
                "summa": ier["summa"],
                "apraksts": ier["apraksts"],
                "datums": ier["datums"]
            })

# Ielādē CSV datus sākumā
dati = ieladet_datus()

# Flask maršruti (routes)
@app.route('/')
def index():
    """Rāda sākumlapu ar ierakstiem un bilanci."""
    tips_filter = request.args.get("tips_filter", "")

    # Filtrē ierakstus pēc tipa, ja nepieciešams
    if tips_filter:
        dati_filtr = [ier for ier in dati if ier["tips"] == tips_filter]
    else:
        dati_filtr = dati

    # Aprēķina ienākumus un izdevumus
    ienakumi = sum(ier["summa"] for ier in dati_filtr if ier["tips"] == "Ienākums")
    izdevumi = sum(ier["summa"] for ier in dati_filtr if ier["tips"] == "Izdevums")
    bilance = ienakumi - izdevumi

    # Padod datus HTML templātam
    return render_template(
        "index.html",
        dati=dati_filtr,
        ienakumi=ienakumi,
        izdevumi=izdevumi,
        bilance=bilance,
        tips_filter=tips_filter
    )

# Pievieno ierakstu
@app.route('/pievienot', methods=['POST'])
def pievienot():
    """Pievieno ienākumu vai izdevumu ar validāciju un datumu."""
    tips = request.form['tips']
    apraksts = request.form['apraksts']
    summa_text = request.form['summa']

    # pārbauda, vai apraksts nav tukšs
    if not apraksts.strip():
        return "Kļūda: apraksts nedrīkst būt tukšs!", 400

    # pārvērš tekstu uz skaitli, ja tas nav iespējams, atgriež kļūdu
    try:
        summa = float(summa_text)
    except ValueError:
        return "Kļūda: summa nav skaitlis!", 400

    datums = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Pievieno jaunu ierakstu datu sarakstam
    dati.append({
        "tips": tips,
        "summa": summa,
        "apraksts": apraksts,
        "datums": datums
    })

    # Saglabā datus CSV un atgriež uz sākumlapu
    saglabat_datus()
    return redirect('/')

# Dzēst ierakstu
@app.route('/dzest/<int:index>')
def dzest(index):
    """Dzēš ierakstu pēc indeksa."""
    if 0 <= index < len(dati):
        dati.pop(index) # Noņem ierakstu
        saglabat_datus() # Atjauno CSV failu
    return redirect('/')

# bilances kopsavilkuma lapa
@app.route('/bilance')
def bilance_lapa():
    """Rāda kopsavilkuma bilanci."""
    ienakumi = sum(ier["summa"] for ier in dati if ier["tips"] == "Ienākums")
    izdevumi = sum(ier["summa"] for ier in dati if ier["tips"] == "Izdevums")
    bilance = ienakumi - izdevumi
    return render_template("bilance.html", ienakumi=ienakumi, izdevumi=izdevumi, bilance=bilance)

# Palaist Flask serveri
if __name__ == "__main__":
    app.run(debug=True)