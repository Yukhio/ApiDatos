from flask import Flask, jsonify, render_template, abort, request, Response, url_for
from uuid import uuid4
import re
from datetime import datetime
import base64, os

app = Flask(__name__)

CONTACTS = {}
BOOT_UUID = None

def seed_contact():
    uid = "datos"
    avatar_path = app.static_url_path + "/img/perfiles/persona.jpg"
    CONTACTS[uid] = {
        "uuid": uid,
        "avatar": avatar_path,
        "firstName": "JESÚS",
        "lastName": "ORTIZ ESTEVEZ",
        "title": "Coordinador de estrategia e innovación",
        # "org": "COLLEGE",
        "phoneWork": "+52 314 116 2950",
        "phoneMobile": "+52 314 123 4567",
        "email": "joestevez@icollege.com.mx",
        "website": "https://icollege.com.mx/",
        "street": "Calle 5 de Diciembre #5",
        "city": "Manzanillo",
        "state": "Colima",
        "zip": "28239",
        "country": "México",
    }
    return uid

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
    return render_template("welcome.html", demo_uuid="datos")

@app.get("/contact/<uid>/card.vcf")
def vcard(uid):
    c = CONTACTS.get(uid)
    if not c:
        abort(404)

    img_fs_path = os.path.join(app.root_path, c["avatar"].lstrip("/"))
    photo_line = ""
    try:
        with open(img_fs_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
            # vCard 3.0: PHOTO;TYPE=JPEG;ENCODING=b:<base64>
            photo_line = f"PHOTO;TYPE=JPEG;ENCODING=b:{b64}"
    except Exception:
        avatar_abs = request.url_root.rstrip("/") + c["avatar"]
        photo_line = f"PHOTO;VALUE=URI:{avatar_abs}"

    uid_line = f"UID:{c['uuid']}"
    rev_line = f"REV:{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}"

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{c['lastName']};{c['firstName']};;;",
        f"FN:{c['firstName']} {c['lastName']}",
        # NO incluir ORG ni TITLE
        f"TEL;TYPE=WORK,VOICE:{tel_compact(c.get('phoneWork',''))}",
        # NO incluir CELULAR
        f"EMAIL;TYPE=INTERNET:{c['email']}",
        f"URL:{c['website']}",
        f"ADR;TYPE=WORK:;;{c['street']};{c['city']};{c['state']};{c['zip']};{c['country']}",
        photo_line,
        uid_line,
        rev_line,
        "END:VCARD",
    ]
    vcf = "\r\n".join(lines) + "\r\n"

    filename = f"{c['firstName']}-{c['lastName']}.vcf".replace(" ", "_")
    return Response(
        vcf,
        mimetype="text/vcard; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
