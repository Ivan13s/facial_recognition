import cv2
import os
import sys
print("DISPLAY =",os.environ.get('DISPLAY'))
env_var=os.environ
os.environ['DISPLAY']= ':0'
#name = sys.stdin.readline().strip()
name=input().strip()
if not name:
	print("Error")
	sys.exit(1)
cam = cv2.VideoCapture(0)

cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
cv2.resizeWindow("press space to take a photo", 500, 300)


folder_path=os.path.join("dataset",name)
if not os.path.exists(folder_path):
	os.makedirs(folder_path)
	print(f"Folder '{folder_path}' creat.")
img_counter = 0
while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("press space to take a photo", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = f"{folder_path}/{name}_{img_counter}.jpg"
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1


cam.release()

cv2.destroyAllWindows()
