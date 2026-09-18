import cv2
import mediapipe as mp
import math
import numpy as np

from show_image import show_image

from constants import MIN_ZOOM, MAX_ZOOM, IMAGE_PATH

# загрузка изображения
image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Ошибка: не найден файл image.jpg")
    exit()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# камера
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Ошибка: камера не открылась")
    exit()

zoom = 1.0

# расстояние между точками
def distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )



# ==========================================
# ПОЛНОЭКРАННОЕ ОКНО
# ==========================================

cv2.namedWindow(
    "Image Zoom",
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    "Image Zoom",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ==========================================
# ОСНОВНОЙ ЦИКЛ
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Не удалось получить кадр")
        break

    # Зеркальное отображение камеры
    frame = cv2.flip(frame, 1)

    # BGR -> RGB
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(rgb)

    # если нашлись руки
    if result.multi_hand_landmarks:

        detected_hands = result.multi_hand_landmarks

        if len(detected_hands) == 2:

            hand1 = detected_hands[0]
            hand2 = detected_hands[1]

            palm1 = hand1.landmark[
                mp_hands.HandLandmark.WRIST
            ]

            palm2 = hand2.landmark[
                mp_hands.HandLandmark.WRIST
            ]

            hand_distance = distance(
                palm1,
                palm2
            )

            # Расстояние между руками
            # превращаем в zoom

            zoom = np.interp(
                hand_distance,
                [0.15, 0.8],
                [MIN_ZOOM, MAX_ZOOM]
            )

            mp_draw.draw_landmarks(
                frame,
                hand1,
                mp_hands.HAND_CONNECTIONS
            )

            mp_draw.draw_landmarks(
                frame,
                hand2,
                mp_hands.HAND_CONNECTIONS
            )

            cv2.putText(
                frame,
                "TWO HANDS",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        else:

            hand = detected_hands[0]

            landmarks = hand.landmark

            wrist = landmarks[
                mp_hands.HandLandmark.WRIST
            ]

            fingertips = [
                mp_hands.HandLandmark.THUMB_TIP,
                mp_hands.HandLandmark.INDEX_FINGER_TIP,
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                mp_hands.HandLandmark.RING_FINGER_TIP,
                mp_hands.HandLandmark.PINKY_TIP,
            ]

            avg_distance = sum(
                distance(
                    landmarks[finger],
                    wrist
                )
                for finger in fingertips
            ) / len(fingertips)

            if avg_distance < 0.35:

                zoom -= 0.02

            elif avg_distance > 0.55:

                zoom += 0.02

            zoom = max(
                MIN_ZOOM,
                min(MAX_ZOOM, zoom)
            )

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            cv2.putText(
                frame,
                "ONE HAND",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    # информация о зуме

    cv2.putText(
        frame,
        f"Zoom: {zoom:.2f}x",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # показываем картинку
    display = show_image(
        image,
        zoom
    )

    cv2.imshow(
        "Image Zoom",
        display
    )

    # Окно камеры
    cv2.imshow(
        "Camera",
        frame
    )

    # ESC -> выход
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
