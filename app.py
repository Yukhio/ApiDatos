from flask import Flask, jsonify, render_template, abort, request
from uuid import uuid4

app = Flask(__name__)

CONTACTS = {}
BOOT_UUID = None

def seed_contact():
    uid = str(uuid4())
    # No usar url_for aquí (no hay request activo)
    avatar_path = app.static_url_path + "/img/perfiles/Yukhio.jpg"  # => "/static/img/perfiles/Yukhio.jpg"
    CONTACTS[uid] = {
        "uuid": uid,
        "avatar": avatar_path,  # ruta relativa
        "firstName": "JESÚS",
        "lastName": "ORTIZ ESTEVEZ",
        "title": "CO",
        "org": "COLLEGE",
        "phoneWork": "+52 314 000 0000",
        "phoneMobile": "+52 314 123 4567",
        "email": "pruebamail@gmail.com",
        "website": "https://alfapcsmax.com/",
        "street": "Calle 5 de Diciembre #5",
        "city": "Manzanillo",
        "state": "Colima",
        "zip": "28239",
        "country": "México",
    }
    return uid

# Siembra al arrancar
if not CONTACTS:
    BOOT_UUID = seed_contact()

@app.get("/api/v1/card/<uid>")
def api_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    # Construir URL absoluta para el JSON (ya hay request activo)
    data = dict(card)
    data["avatar"] = request.url_root.rstrip("/") + card["avatar"]
    return jsonify(data)

@app.get("/<uid>")
def front_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    # En la plantilla usa {{ url_for('static', filename='img/perfiles/Yukhio.jpg') }}
    # o directamente c.avatar si ya es relativo
    return render_template("card.html", c=card)

@app.get("/")
def root():
    return render_template("welcome.html", demo_uuid=BOOT_UUID)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
