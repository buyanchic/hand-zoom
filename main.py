
import cv2
import mediapipe as mp
import math
import numpy as np

# ==========================================
# НАСТРОЙКИ
# ==========================================

IMAGE_PATH = "image.jpg"

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

MIN_ZOOM = 0.5
MAX_ZOOM = 2.5


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


# ==========================================
# ТЕКУЩИЙ ZOOM
# ==========================================

zoom = 1.0


# ==========================================
# ФУНКЦИЯ РАССТОЯНИЯ
# ==========================================

def distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


# ==========================================
# ОТОБРАЖЕНИЕ ИЗОБРАЖЕНИЯ
# ==========================================

def show_image(image, zoom):

    new_width = int(image.shape[1] * zoom)
    new_height = int(image.shape[0] * zoom)

    scaled = cv2.resize(
        image,
        (new_width, new_height)
    )

    # Белый фон
    display = np.ones(
        (WINDOW_HEIGHT, WINDOW_WIDTH, 3),
        dtype=np.uint8
    ) * 255

    h, w = scaled.shape[:2]

    # Центр изображения
    x = (WINDOW_WIDTH - w) // 2
    y = (WINDOW_HEIGHT - h) // 2

    # Если изображение меньше окна
    if w <= WINDOW_WIDTH and h <= WINDOW_HEIGHT:

        display[
            y:y + h,
            x:x + w
        ] = scaled

    else:

        # Центрированный crop
        crop_x = max(0, (w - WINDOW_WIDTH) // 2)
        crop_y = max(0, (h - WINDOW_HEIGHT) // 2)

        crop = scaled[
            crop_y:crop_y + WINDOW_HEIGHT,
            crop_x:crop_x + WINDOW_WIDTH
        ]

        display[
            :crop.shape[0],
            :crop.shape[1]
        ] = crop

    return display


# ==========================================
# ОСНОВНОЙ ЦИКЛ
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Не удалось получить кадр")
        break

    # Зеркальное отображение
    frame = cv2.flip(frame, 1)

    # BGR -> RGB
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Распознаём руки
    result = hands.process(rgb)

    # ======================================
    # ЕСЛИ ЕСТЬ РУКИ
    # ======================================

    if result.multi_hand_landmarks:

        detected_hands = result.multi_hand_landmarks

        # ==================================
        # ДВЕ РУКИ
        # ==================================

        if len(detected_hands) == 2:

            hand1 = detected_hands[0]
            hand2 = detected_hands[1]

            landmarks1 = hand1.landmark
            landmarks2 = hand2.landmark

            # Центры ладоней
            palm1 = landmarks1[
                mp_hands.HandLandmark.WRIST
            ]

            palm2 = landmarks2[
                mp_hands.HandLandmark.WRIST
            ]

            # Расстояние между ладонями
            hand_distance = distance(
                palm1,
                palm2
            )

            # Преобразуем расстояние рук
            # в zoom

            zoom = np.interp(
                hand_distance,
                [0.15, 0.8],
                [MIN_ZOOM, MAX_ZOOM]
            )

            # Рисуем обе руки
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

            # Показываем режим
            cv2.putText(
                frame,
                "TWO HANDS",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Distance: {hand_distance:.2f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # ==================================
        # ОДНА РУКА
        # ==================================

        else:

            hand = detected_hands[0]

            landmarks = hand.landmark

            wrist = landmarks[
                mp_hands.HandLandmark.WRIST
            ]

            # Кончики пальцев
            fingertips = [
                mp_hands.HandLandmark.THUMB_TIP,
                mp_hands.HandLandmark.INDEX_FINGER_TIP,
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                mp_hands.HandLandmark.RING_FINGER_TIP,
                mp_hands.HandLandmark.PINKY_TIP,
            ]

            # Среднее расстояние
            # от пальцев до запястья

            avg_distance = sum(
                distance(
                    landmarks[finger],
                    wrist
                )
                for finger in fingertips
            ) / len(fingertips)

            # Кулак
            if avg_distance < 0.35:

                zoom -= 0.02

            # Открытая ладонь
            elif avg_distance > 0.55:

                zoom += 0.02

            # Ограничиваем zoom
            zoom = max(
                MIN_ZOOM,
                min(MAX_ZOOM, zoom)
            )

            # Рисуем руку
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            # Показываем режим
            cv2.putText(
                frame,
                "ONE HAND",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Hand: {avg_distance:.2f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # ======================================
    # ZOOM НА ЭКРАНЕ
    # ======================================

    cv2.putText(
        frame,
        f"Zoom: {zoom:.2f}x",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # ======================================
    # ПОКАЗЫВАЕМ ИЗОБРАЖЕНИЕ
    # ======================================

    display = show_image(
        image,
        zoom
    )

    cv2.imshow(
        "Camera",
        frame
    )

    cv2.imshow(
        "Image Zoom",
        display
    )

    # ESC = выход
    if cv2.waitKey(1) & 0xFF == 27:
        break


# ==========================================
# ЗАВЕРШЕНИЕ
# ==========================================

cap.release()
hands.close()
cv2.destroyAllWindows()
