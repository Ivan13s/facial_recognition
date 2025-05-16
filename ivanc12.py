# Importa pachetele necesare
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import socket
from flask import Flask, Response, request
import warnings
import logging
import sys
import threading
print("START")
# Crează serverul Flask pentru streaming video
app = Flask(__name__)
warnings.filterwarnings("ignore", message="This is a development server.")
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Variabilă globală pentru controlul închiderii
should_exit = False

# Configurări inițiale
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5005))
server.listen(1)

conn, addr = server.accept()

SCOPES = ['https://mail.google.com/']
TOKEN_PATH = 'token.json'
credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('gmail', 'v1', credentials=credentials)


def trimite_email_cu_poza(img_name):
    try:
        if not os.path.exists(img_name):
            print(f"[EROARE] Fișierul {img_name} nu există!")
            return

        expeditor = "d003lab@gmail.com"
        destinatar = "d003lab@gmail.com"
        subiect = "Persoana necunoscuta in D101"
        text_email = "Poza atasata: "

        mesaj = MIMEMultipart()
        mesaj['to'] = destinatar
        mesaj['from'] = expeditor
        mesaj['subject'] = subiect
        mesaj.attach(MIMEText(text_email, 'plain'))

        with open(img_name, 'rb') as fisier:
            continut_poza = fisier.read()

        atasament = MIMEBase('image', 'jpeg')
        atasament.set_payload(continut_poza)
        encoders.encode_base64(atasament)
        atasament.add_header('Content-Disposition', f'attachment; filename={img_name}')
        mesaj.attach(atasament)

        mesaj_codificat = base64.urlsafe_b64encode(mesaj.as_bytes()).decode()

        mesaj_trimis = service.users().messages().send(userId="me", body={'raw': mesaj_codificat}).execute()
        print(f"[SUCCES] Email trimis cu ID: {mesaj_trimis['id']}")

    except Exception as error:
        print(f"[EROARE] A aparut o eroare la trimiterea emailului: {error}")


# Variabile globale pentru contorizare
people_count = 0
known_face_encodings = []
known_face_names = []
currentname = "unknown"
encodingsP = "encodings.pickle"
cascade = "haarcascade_frontalface_default.xml"

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# Incarcă encodarile și numele fetelor cunoscute
data_encodings = data["encodings"]
data_names = data["names"]
known_face_encodings.extend(data_encodings)
known_face_names.extend(data_names)

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

fps = FPS().start()
last_seen = {}


def log_intrare(nume):
    with open("log_persoane_cunoscute.txt", "a") as fisier_log:
        data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fisier_log.write(f"{data_ora} - {nume} a intrat in incapere\n")
        print(f"[LOG] INTRARE: {nume}")


def log_iesire(nume):
    with open("log_persoane_cunoscute.txt", "a") as fisier_log:
        data_ora = datetime.now() - timedelta(minutes=2)
        data_ora_completa = data_ora.strftime("%Y-%m-%d %H:%M:%S")
        fisier_log.write(f"{data_ora_completa} - {nume} a iesit din incapere\n")
        print(f"[LOG] IESIRE: {nume}")


def stop_flask():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        print("[EROARE] Nu pot opri serverul Flask - nu rulează în modul de dezvoltare?")
    else:
        func()
    print("[INFO] Serverul Flask s-a oprit!")


def cleanup_resources():
    print("[INFO] Se închid resursele...")
    conn.close()
    server.close()
    fps.stop()
    cv2.destroyAllWindows()
    vs.stop()
    print("[INFO] Toate resursele au fost închise!")


def gen_frames():
    global should_exit, people_count
    while not should_exit:
        conn.settimeout(1)
        try:
            data = conn.recv(1024).decode().strip()
            if data == "q":
                print("[INFO] Oprire cerută de client!")
                should_exit = True
                conn.close()
                server.close()
                os._exit(0)  # Oprire imediată a aplicației (kill instantaneu)
                threading.Thread(target=stop_flask).start()
                break
        except socket.timeout:
            pass

        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        for encoding in encodings:
            matches = face_recognition.compare_faces(known_face_encodings, encoding, tolerance=0.6)
            name = "Unknown"

            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = known_face_names[i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

                if name not in last_seen:
                    log_intrare(name)

                last_seen[name] = datetime.now()

            else:
                people_count += 1
                img_name = f"person_{people_count}.jpg"

                success = cv2.imwrite(img_name, frame)
                if not success:
                    print(f"[EROARE] Nu am putut salva imaginea {img_name}!")
                    continue

                print(f"[DETECTIE] Noua persoana detectata! Salvata ca {img_name}")
                known_face_encodings.append(encoding)
                known_face_names.append(name)

                trimite_email_cu_poza(img_name)

            names.append(name)

        current_time = datetime.now()
        for name in list(last_seen.keys()):
            if (current_time - last_seen[name]) > timedelta(minutes=2):
                log_iesire(name)
                del last_seen[name]

        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    print("[INFO] Serverul Flask a pornit!")
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        os._exit(0)  # Oprire imediată a aplicației (kill instantaneu)
