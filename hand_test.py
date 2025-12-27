import cv2
import mediapipe as mp
import pyttsx3

# 1. Initialize Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0) # Full volume

# 2. Initialize MediaPipe "Eyes"
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# 3. Start Camera
cap = cv2.VideoCapture(0)
last_spoken = ""

print("System Ready! Show your hand to the camera. Press 'q' to quit.")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Prepare Image
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    current_sign = ""

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Draw dots and lines
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

            # --- FINGER LOGIC MAP ---
            # 1 = Finger is UP, 0 = Finger is DOWN
            lms = hand_lms.landmark
            
            # Index (ID 8), Middle (ID 12), Ring (ID 16), Pinky (ID 20)
            f1 = 1 if lms[8].y < lms[6].y else 0
            f2 = 1 if lms[12].y < lms[10].y else 0
            f3 = 1 if lms[16].y < lms[14].y else 0
            f4 = 1 if lms[20].y < lms[18].y else 0
            
            # Thumb (ID 4) - Check if it's extended outward
            thumb = 1 if lms[4].x > lms[3].x else 0

            # --- SIGN DICTIONARY ---
            # Pattern: [Thumb, Index, Middle, Ring, Pinky]
            if [thumb, f1, f2, f3, f4] == [0, 1, 1, 0, 0]:
                current_sign = "Victory"
            elif [thumb, f1, f2, f3, f4] == [1, 1, 1, 1, 1]:
                current_sign = "Hello"
            elif [thumb, f1, f2, f3, f4] == [1, 0, 0, 0, 1]:
                current_sign = "I Love You"
            elif [thumb, f1, f2, f3, f4] == [1, 0, 0, 0, 0]:
                current_sign = "Good Job"
            elif [thumb, f1, f2, f3, f4] == [0, 1, 0, 0, 0]:
                current_sign = "Point"
            elif [thumb, f1, f2, f3, f4] == [0, 0, 0, 0, 0]:
                current_sign = "Fist"

            # 4. Speak the sign (only once per detection)
            if current_sign != "" and current_sign != last_spoken:
                engine.say(current_sign)
                engine.runAndWait()
                last_spoken = current_sign
            elif current_sign == "":
                last_spoken = ""

    # Show result on screen
    cv2.putText(img, current_sign, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    cv2.imshow("Sign Language Bridge", img)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()