import cv2
import numpy as np

from constants import SCREEN_HEIGHT, SCREEN_WIDTH

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
