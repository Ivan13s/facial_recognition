# Importa pachetele necesare
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import socket 
import os
import pprint
print("DISPLAY =",os.environ.get('DISPLAY'))
env_var=os.environ
os.environ['DISPLAY']= ':0'
pprint.pprint(dict(env_var),width=1)
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("0.0.0.0",5005))
server.listen(2)

conn, addr=server.accept()
# Configuratii initiale
SCOPES = ['https://mail.google.com/']
TOKEN_PATH = 'token.json'
credentials = Credentials.from_authorized_user_file('token.json', SCOPES)

# Creeaza serviciul Gmail
service = build('gmail', 'v1', credentials=credentials)

def trimite_email_cu_poza(img_name):
    expeditor = "d003lab@gmail.com"
    destinatar = "d003lab@gmail.com"
    subiect = "Persoana necunoscuta in D101"
    text_email = "Poza atasata: "

    mesaj = MIMEMultipart()
    mesaj['to'] = destinatar
    mesaj['from'] = expeditor
    mesaj['subject'] = subiect
    mesaj.attach(MIMEText(text_email, 'plain'))

    cale_pozei = f"/home/ivan/opencv/build/facial_recognition/{img_name}"
    nume_pozei = f"{img_name}"

    with open(cale_pozei, 'rb') as fisier:
        continut_poza = fisier.read()

    atasament = MIMEBase('image', 'jpeg')
    atasament.set_payload(continut_poza)
    encoders.encode_base64(atasament)
    atasament.add_header('Content-Disposition', f'attachment; filename={nume_pozei}')
    mesaj.attach(atasament)

    mesaj_codificat = base64.urlsafe_b64encode(mesaj.as_bytes()).decode()

    try:
        mesaj_trimis = service.users().messages().send(userId="me", body={'raw': mesaj_codificat}).execute()
        print(f"Email trimis cu succes! ID mesaj: {mesaj_trimis['id']}")
    except Exception as error:
        print(f"A aparut o eroare: {error}")

# Variabile globale pentru contorizare
people_count = 0
known_face_encodings = []
known_face_names = []  # Lista pentru numele fetelor cunoscute

# Initializeaza 'currentname' pentru a detecta o persoana noua
currentname = "unknown"
encodingsP = "encodings.pickle"
cascade = "haarcascade_frontalface_default.xml"

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# Incarca encodarile și numele fetelor cunoscute
data_encodings = data["encodings"]
data_names = data["names"]
known_face_encodings.extend(data_encodings)
known_face_names.extend(data_names)

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
print("ceva1")
time.sleep(2.0)

fps = FPS().start()
print("ceva")
# Dictionar pentru ultima detectare a fiecarei persoane cunoscute
last_seen = {}

def log_intrare(nume):
    with open("log_persoane_cunoscute.txt", "a") as fisier_log:
        data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fisier_log.write(f"{data_ora} - {nume} a intrat in incapere\n")
        print("INTRARE",last_seen)
def log_iesire(nume):
    with open("log_persoane_cunoscute.txt", "a") as fisier_log:
        data_ora = datetime.now()-timedelta(minutes=2)
        data_ora_completa=data_ora.strftime("%Y-%m-%d %H:%M:%S")
        fisier_log.write(f"{data_ora_completa} - {nume} a iesit din incapere\n")
        print("IESIRE",last_seen)

while True:
    conn.settimeout(1)
    print("timeout")
    try:
        print("try1")
        data=conn.recv(1024).decode().strip()
        print("try2")
        print("data",data)
        if data=="q":
            print("OPRIRE!")
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
    print("TOtul ok")
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
           
            # Inregistrare intrare daca e prima detectare
            if name not in last_seen:
                log_intrare(name)

            # Actualizare ultima detectare
            last_seen[name] = datetime.now()

        else:
            known_face_encodings.append(encoding)
            known_face_names.append(name)
            people_count += 1
            print(f"Noua persoana detectata! Total persoane: {people_count}")

            img_name = f"person_{people_count}.jpg"
            cv2.imwrite(img_name, frame)
            trimite_email_cu_poza(img_name)

        names.append(name)

    # Verifica persoanele care au iesit
    current_time = datetime.now()
    for name in list(last_seen.keys()):
        if (current_time - last_seen[name]) > timedelta(minutes=2):
            log_iesire(name)
            del last_seen[name]

    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    print("MERGE")

    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
conn.close()
server.close()
fps.stop()
print(f"[INFO] elapsed time: {fps.elapsed():.2f}")
print(f"[INFO] approx. FPS: {fps.fps():.2f}")
print(f"Numarul total de persoane detectate: {people_count}")

cv2.destroyAllWindows()
vs.stop()
