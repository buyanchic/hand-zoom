# ✋ Hand Zoom

Управление масштабом изображения с помощью жестов руки через веб-камеру.

Проект использует компьютерное зрение для распознавания положения рук и позволяет увеличивать или уменьшать изображение без использования мыши или клавиатуры.

## ✨ Возможности

- 🖐 Управление масштабом одной рукой
- ✊ Сжатая ладонь уменьшает изображение
- 🖐 Разжатая ладонь увеличивает изображение
- 🤲 Управление двумя руками
- ↔️ Расстояние между руками определяет масштаб
- 🖼 Изображение сохраняет пропорции
- 🖥 Полноэкранный режим
- 📷 Распознавание рук в реальном времени

## 🎥 Demo


## 🛠 Tech Stack

- Python 3.12
- OpenCV
- MediaPipe
- NumPy

## 📁 Project Structure

```text
hand_zoom/
├── main.py
├── constants.py
├── show_image.py
├── image.jpg
├── demo.gif
├── requirements.txt
└── README.md
````

## 🚀 Installation

Клонируйте репозиторий:

```bash
git clone https://github.com/YOUR_USERNAME/hand_zoom.git
cd hand_zoom
```

Создайте виртуальное окружение:

```bash
python3 -m venv venv
```

Активируйте его:

```bash
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

## ▶️ Run

Запустите приложение:

```bash
python main.py
```

После запуска разрешите приложению доступ к веб-камере.

Для выхода нажмите:

```text
Esc
```

## 🖐 Gesture Control

### One hand

| Gesture      | Action   |
| ------------ | -------- |
| ✊ Fist       | Zoom out |
| 🖐 Open hand | Zoom in  |

### Two hands

| Gesture                | Action   |
| ---------------------- | -------- |
| 🤲 Hands closer        | Zoom out |
| 🤲 Hands farther apart | Zoom in  |

## 🧠 How it works

Проект получает видеопоток с камеры с помощью OpenCV.

MediaPipe Hands определяет ключевые точки руки, после чего приложение вычисляет расстояние между определёнными точками.

Для одной руки используется среднее расстояние от кончиков пальцев до запястья:

```text
fingertips → wrist
```

Для двух рук используется расстояние между запястьями:

```text
wrist ←────────→ wrist
```

Полученное значение преобразуется в коэффициент масштабирования изображения.

```text
hand position
      ↓
MediaPipe
      ↓
landmarks
      ↓
distance calculation
      ↓
zoom value
      ↓
image scaling
```

## 🧩 Architecture

Логика проекта разделена на отдельные модули:

```text
main.py
   │
   ├── camera
   ├── MediaPipe
   └── gesture detection
          │
          ↓
    zoom calculation
          │
          ↓
   show_image.py
          │
          ↓
      full-screen
```

Конфигурационные значения вынесены в `constants.py`, а логика отображения и масштабирования изображения находится в `show_image.py`.

Это позволяет разделить ответственность между модулями и упростить дальнейшее развитие проекта.

## 🔮 Possible Improvements

* [ ] Плавное сглаживание масштаба
* [ ] Управление перемещением изображения
* [ ] Жест для сброса масштаба
* [ ] Поддержка нескольких изображений
* [ ] Настройка чувствительности жестов
* [ ] Переключение изображений жестами

## 📄 License

This project is created for educational and experimental purposes.
