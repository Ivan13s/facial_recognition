#! /usr/bin/python

# import the necessary packages
from imutils import paths
import face_recognition
# import argparse
import pickle
import cv2
import os
import socket 

print("Trebuie pornit serverul")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5005))
server.listen(1)
conn, addr = server.accept()
stop=False
start_server=False
while True:
    if stop:
        break
    conn.settimeout(1)
    print("timeout")
    try:
        print("try1")
        data1=conn.recv(1024).decode().strip()
        if data1=="b":
            start_server=True
            
        print("try2")
        print("data", data1)
        
        if data1 == "q":
            start_server=False
            print("OPRIRE! PROGRAM SI SERVER")
            break
        if stop:
            break

        if data1 == "t" and start_server==True:
            # our images are located in the dataset folder
            print("[INFO] start processing faces...")
            imagePaths = list(paths.list_images("dataset"))
            print("imagePaths",imagePaths)
            # initialize the list of known encodings and known names
            knownEncodings = []
            knownNames = []
    
            # loop over the image paths
            for (i, imagePath) in enumerate(imagePaths):

                # extract the person name from the image path
                print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
                print("PROCESING 1")
                conn.settimeout(1)
                try:
                    data2=conn.recv(1024).decode().strip()
                    print("DATA 2 PART1",data2)
                    if data2 == "q":
                        stop=True
                        print("OPRIRE ANTRENAMENT!!")
                        break
                except socket.timeout:
                    pass
                name = imagePath.split(os.path.sep)[-2]

                # load the input image and convert it from BGR (OpenCV ordering) to RGB
                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # detect the (x, y)-coordinates of the bounding boxes
                boxes = face_recognition.face_locations(rgb, model="hog")

                # compute the facial embedding for the face
                encodings = face_recognition.face_encodings(rgb, boxes)
                print("PROCESING 2")
                # loop over the encodings
                for encoding in encodings:
                    # add each encoding + name to our set of known names and encodings
                    knownEncodings.append(encoding)
                    knownNames.append(name)

            # dump the facial encodings + names to disk
            print("[INFO] serializing encodings...")
            data = {"encodings": knownEncodings, "names": knownNames}
            with open("encodings.pickle", "wb") as f:
                f.write(pickle.dumps(data))

    except socket.timeout:
        pass
conn.close()
server.close()
