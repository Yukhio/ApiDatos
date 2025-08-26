from flask import Flask, jsonify, render_template, url_for, abort
from uuid import uuid4


app = Flask(__name__)


# Seed one contact (you can add more later). The key is a UUID string used in the URL.
CONTACTS = {}


def seed_contact():
    uid = str(uuid4()) # generate once at boot; store in DB in real use
    CONTACTS[uid] = {
    "uuid": uid,
    "avatar": url_for("static", filename="img/perfiles/Yukhio.jpg"),
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


BOOT_UUID = None


@app.before_first_request
def _bootstrap():
    global BOOT_UUID
    if not CONTACTS:
        BOOT_UUID = seed_contact()


# 1) JSON API -> /api/v1/card/<uuid>
@app.get("/api/v1/card/<uid>")
def api_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    return jsonify(card)


# 2) Frontend page (for QR) -> /<uuid>
@app.get("/<uid>")
def front_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    return render_template("card.html", c=card)


# 3) Helper route to see the demo UUID quickly: /
@app.get("/")
def root():
    # Redirect-like landing showing the demo UUID and link
    return render_template("welcome.html", demo_uuid=BOOT_UUID)


if __name__ == "__main__":
    # Debug server; for prod use gunicorn/uwsgi and a reverse proxy
    app.run(host="0.0.0.0", port=5000, debug=True)