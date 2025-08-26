from flask import Flask, jsonify, render_template, abort, request, Response, url_for
from uuid import uuid4
import re

app = Flask(__name__)

CONTACTS = {}
BOOT_UUID = None

def seed_contact():
    uid = str(uuid4())
    # Evitamos usar url_for fuera de contexto; usamos la ruta pública /static
    avatar_path = app.static_url_path + "/img/perfiles/Yukhio.png"
    CONTACTS[uid] = {
        "uuid": uid,
        "avatar": avatar_path,  # relativo; luego lo volvemos absoluto cuando haga falta
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

def tel_compact(t: str) -> str:
    """Compacta el teléfono (quita espacios, guiones, paréntesis)."""
    if not t:
        return ""
    return re.sub(r"[^\d+]", "", t)

@app.get("/api/v1/card/<uid>")
def api_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    # Construir URL absoluta para el avatar
    data = dict(card)
    data["avatar"] = request.url_root.rstrip("/") + card["avatar"]
    return jsonify(data)

@app.get("/<uid>")
def front_card(uid):
    card = CONTACTS.get(uid)
    if not card:
        abort(404)
    return render_template("card.html", c=card)

@app.get("/")
def root():
    return render_template("welcome.html", demo_uuid=BOOT_UUID)

# ========= vCard (.vcf) =========
@app.get("/contact/<uid>/card.vcf")
def vcard(uid):
    c = CONTACTS.get(uid)
    if not c:
        abort(404)

    # Hacemos absoluta la URL del avatar para la vCard
    avatar_abs = request.url_root.rstrip("/") + c["avatar"]

    vcf = f"""BEGIN:VCARD
    VERSION:3.0
    N:{c['lastName']};{c['firstName']};;;
    FN:{c['firstName']} {c['lastName']}
    ORG:{c['org']}
    TITLE:{c['title']}
    TEL;TYPE=WORK,VOICE:{tel_compact(c.get('phoneWork',''))}
    TEL;TYPE=CELL,VOICE:{tel_compact(c.get('phoneMobile',''))}
    EMAIL;TYPE=INTERNET:{c['email']}
    URL:{c['website']}
    ADR;TYPE=WORK:;;{c['street']};{c['city']};{c['state']};{c['zip']};{c['country']}
    PHOTO;VALUE=URI:{avatar_abs}
    END:VCARD
    """
    filename = f"{c['firstName']}-{c['lastName']}.vcf".replace(" ", "_")
    return Response(
        vcf,
        mimetype="text/vcard; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

if __name__ == "__main__":
    # host/port a tu gusto
    app.run(host="0.0.0.0", port=5000, debug=True)
