import cv2
import mediapipe as mp
import math
import numpy as np

# ==========================================
# НАСТРОЙКИ
# ==========================================

IMAGE_PATH = "image.jpg"

MIN_ZOOM = 0.5
MAX_ZOOM = 2.5

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


# ==========================================
# ЗАГРУЗКА ИЗОБРАЖЕНИЯ
# ==========================================

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Ошибка: не найден файл image.jpg")
    exit()


# ==========================================
# MEDIAPIPE
# ==========================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


# ==========================================
# КАМЕРА
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Ошибка: камера не открылась")
    exit()


zoom = 1.0


# ==========================================
# РАССТОЯНИЕ МЕЖДУ ТОЧКАМИ
# ==========================================

def distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


# ==========================================
# ПОКАЗ ИЗОБРАЖЕНИЯ
# ==========================================

def show_image(image, zoom):

    image_height, image_width = image.shape[:2]

    # Базовый масштаб:
    # картинка полностью помещается на экран
    base_scale = min(
        SCREEN_WIDTH / image_width,
        SCREEN_HEIGHT / image_height
    )

    # Добавляем пользовательский zoom
    scale = base_scale * zoom

    new_width = int(image_width * scale)
    new_height = int(image_height * scale)

    scaled = cv2.resize(
        image,
        (new_width, new_height)
    )

    # Белый фон экрана
    display = np.ones(
        (SCREEN_HEIGHT, SCREEN_WIDTH, 3),
        dtype=np.uint8
    ) * 255

    h, w = scaled.shape[:2]

    # ======================================
    # КАРТИНКА МЕНЬШЕ ЭКРАНА
    # ======================================

    if w <= SCREEN_WIDTH and h <= SCREEN_HEIGHT:

        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2

        display[
            y:y + h,
            x:x + w
        ] = scaled

    # ======================================
    # КАРТИНКА БОЛЬШЕ ЭКРАНА
    # ======================================

    else:

        # Берём центральную часть
        x = max(0, (w - SCREEN_WIDTH) // 2)
        y = max(0, (h - SCREEN_HEIGHT) // 2)

        crop = scaled[
            y:y + SCREEN_HEIGHT,
            x:x + SCREEN_WIDTH
        ]

        display[
            :crop.shape[0],
            :crop.shape[1]
        ] = crop

    return display


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

    # ======================================
    # ЕСЛИ НАШЛИ РУКИ
    # ======================================

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

    # ======================================
    # ИНФОРМАЦИЯ О ZOOM
    # ======================================

    cv2.putText(
        frame,
        f"Zoom: {zoom:.2f}x",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # ======================================
    # ПОКАЗЫВАЕМ КАРТИНКУ
    # ======================================

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
