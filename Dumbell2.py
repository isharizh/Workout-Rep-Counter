import cv2
import time
import pygame
import mediapipe as mp
import tkinter as tk

mpdraw = mp.solutions.drawing_utils
mppose = mp.solutions.pose
pose = mppose.Pose()  

# Custom label class with a border around the text
class TextBorderLabel(tk.Label):
    def __init__(self, master, text, font, fg, border_color, border_width, **kwargs):
        super().__init__(master, text=text, font=font, fg=border_color, **kwargs)
        self.config(relief=tk.SOLID, bd=border_width)

# Create a function to update the labels
def update_counts():
    global rcounter, lcounter
    left_label.config(text=f"Left Arm Count: {lcounter}")
    right_label.config(text=f"Right Arm Count: {rcounter}")
    root.after(1000, update_counts)  # Update every second

cap = cv2.VideoCapture(0)
#cap.set(3, 2080)
#cap.set(4, 2020)

rup = False
lup = False
rcounter = 0
lcounter = 0
start_time = None
exercise_duration = 30

pygame.mixer.init()
pygame.mixer.music.load(r"/Users/harizh/Pypro/GYM_Workout/Tevvez.mp3")

root = tk.Tk()
root.title("REP Counter")
root.geometry("1080x720")

frame = tk.Frame(root)
frame.pack()

heading_label = TextBorderLabel(frame, text="Bicep Curl Rep Counter", font=("Helvetica", 90), fg="skyblue", border_color="black", border_width=2)
heading_label.pack(pady=20)

left_label = tk.Label(frame, text=f"Left Count: {lcounter}", font=("Helvetica", 70), fg="red", pady=100)
right_label = tk.Label(frame, text=f"Right Count: {rcounter}", font=("Helvetica", 70), fg="orange", pady=10)
left_label.pack()
right_label.pack()

# Start updating the count labels
update_counts()

while True:
    success, img = cap.read()
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    bd = 13
    img = cv2.copyMakeBorder(img, bd, bd, bd, bd, cv2.BORDER_CONSTANT, value=(0,0,0))
    result = pose.process(imgrgb)

    if start_time is None:
        start_time = time.time()

    elapsed_time = time.time() - start_time
    remaining_time = max(exercise_duration - elapsed_time, 0)

    cv2.putText(img, f"Time left: {int(remaining_time)}s", (450, 700), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 5)
    cv2.putText(img, f"Time left: {int(remaining_time)}s", (450, 700), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)

    if elapsed_time >= exercise_duration:
        pygame.mixer.music.stop()
        break  # Exit the loop when the timer is up

    if result.pose_landmarks:
        mpdraw.draw_landmarks(img, result.pose_landmarks, mppose.POSE_CONNECTIONS)

        points = {}
        for id, lm in enumerate(result.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            points[id] = (cx, cy)

        cv2.circle(img, points[14], 15, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, points[16], 15, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, points[13], 15, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, points[15], 15, (0, 0, 255), cv2.FILLED)

        cv2.circle(img, points[14], 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, points[16], 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, points[13], 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, points[15], 10, (0, 255, 255), cv2.FILLED)

        if not rup and points[14][1] - 80 > points[16][1]:
            rup = True
            rcounter += 1

        elif points[14][1] < points[16][1]:
            rup = False

        if not lup and points[13][1] - 80 > points[15][1]:
            lup = True
            lcounter += 1

        elif points[13][1] < points[15][1]:
            lup = False

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    cv2.putText(img, "Right Arm: " + str(rcounter), (40, 75), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 10)
    cv2.putText(img, "Right Arm: " + str(rcounter), (40, 75), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 250, 0), 5)

    cv2.putText(img, "Left Arm: " + str(lcounter), (835, 75), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 10)
    cv2.putText(img, "Left Arm: " + str(lcounter), (835, 75), cv2.FONT_HERSHEY_DUPLEX, 2, (14, 94, 255), 5)

    cv2.imshow("Counter", img)
    cv2.waitKey(1)

root.mainloop()
