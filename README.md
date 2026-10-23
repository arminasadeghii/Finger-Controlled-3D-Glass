# 🥃 Finger-Controlled 3D Glass

A small computer vision and 3D graphics experiment that lets you control a virtual glass using nothing but your fingers and a webcam.

The idea is simple: move your hand to rotate a 3D glass, pinch your fingers to fill it, and tilt it to pour the liquid. What started as a random idea turned into a fun experiment combining real-time hand tracking, gesture recognition, and interactive 3D rendering.

No mouse or keyboard is needed for the main interactions — just your hand.

## ✨ Features

- 🖐️ **Real-Time Hand Tracking** — Detects hand landmarks using MediaPipe.
- 🔄 **Finger-Controlled Rotation** — Rotate the 3D glass by moving your index finger.
- 🤏 **Pinch-to-Fill Interaction** — Fill the glass by bringing your thumb and index finger together.
- 🥃 **Interactive Liquid Simulation** — Watch the liquid level change as you fill or pour.
- ↘️ **Gesture-Based Pouring** — Tilt the glass to pour liquid out.
- ✋ **Hand-Gesture Reset** — Open your hand to reset the glass.
- 🎥 **Live Webcam Feedback** — View the camera feed and detected hand landmarks in real time.
- 🎨 **Custom 3D Geometry** — A procedurally defined glass with adjustable dimensions and appearance.
- 🎛️ **Adjustable Responsiveness** — Fine-tune movement smoothing while the application is running.

## 🎮 Controls

| Input                        | Action                  |
| ---------------------------- | ----------------------- |
| Move your index finger       | Rotate the glass        |
| Pinch thumb and index finger | Fill the glass          |
| Tilt the glass               | Pour the liquid         |
| Open your hand               | Reset the glass         |
| `R`                          | Recenter the rotation   |
| `↑`                          | Increase responsiveness |
| `↓`                          | Increase smoothing      |
| `ESC`                        | Exit the application    |

## 🧠 How It Works

The project combines computer vision with real-time 3D rendering to translate hand movements into interactive actions.

### 1. Hand Tracking

The webcam captures video frames, and MediaPipe detects key landmarks on the hand. These landmarks provide the positions needed to interpret finger movements and gestures.

### 2. Glass Rotation

The application uses the index finger's position to estimate a rotation angle. That angle is mapped to the glass's orientation in the 3D scene.

Because hand tracking can produce small, unwanted movements, smoothing is applied to make rotation feel more stable and natural.

### 3. Pinch-to-Fill

The distance between the thumb and index finger is used to recognize a pinch gesture.

**Thumb + Index Finger → Pinch Detected → Fill the Glass**

### 4. Tilt-to-Pour

When the glass tilts beyond a certain angle, the pouring behavior begins. The liquid level decreases according to the tilt, creating a simple interactive pouring effect.

**Tilt the Glass → Pouring Starts → Liquid Level Decreases**

### 5. Gesture-Based Reset

Opening the hand triggers the reset behavior, bringing the glass back toward its initial state.

## 🛠️ Tech Stack

| Technology | Purpose                                          |
| ---------- | ------------------------------------------------ |
| Python     | Core application and interaction logic           |
| MediaPipe  | Hand landmark detection                          |
| OpenCV     | Webcam input and computer vision                 |
| PyOpenGL   | 3D rendering                                     |
| Pygame     | Application window, event handling, and controls |
| NumPy      | Numerical calculations and geometry operations   |

## 📁 Project Structure

```text
Finger-Controlled-3D-Glass/
├── main.py           # Main application and interaction loop
├── hand_tracker.py   # Hand tracking and gesture-related logic
├── cup_geometry.py   # Glass geometry and liquid representation
├── README.md         # Project documentation
└── requirements.txt  # Python dependencies
```

### Main Components

- **`main.py`** — Coordinates the webcam, rendering, keyboard input, glass rotation, and liquid interactions.
- **`hand_tracker.py`** — Detects hand landmarks and provides the information needed to interpret gestures and finger movement.
- **`cup_geometry.py`** — Defines the 3D glass geometry and manages the liquid representation.
- **`requirements.txt`** — Lists the Python packages needed to run the project.

## 🎨 Customization

The glass geometry and rendering parameters can be adjusted directly in the source code.

For example, the glass dimensions can be customized through its geometry configuration:

```python
cup = PentagonCup(
    height=2.0,
    outer_radius=1.0,
    wall_ratio=0.82,
    base_thickness=0.18
)
```

The appearance of the glass and liquid can also be adjusted through rendering parameters, including color and transparency.

You can experiment with different dimensions, visual styles, and smoothing settings to change how the glass looks and responds to your hand.

## 🔧 Tuning Hand Tracking

Hand movement can feel jittery because of small variations in landmark detection. Smoothing helps reduce this effect.

For example:

```python
IndexFingerRotationTracker(
    smoothing=0.35,
    max_hands=1,
    detection_conf=0.6,
    tracking_conf=0.6
)
```

The exact balance between responsiveness and smoothness depends on the environment and the desired interaction. Higher smoothing generally reduces jitter but can make movement feel less immediate.

## 💡 Why I Built This

I like taking random ideas that pop into my head and seeing whether I can actually build them.

This project started with a simple question: *What if I could control a 3D glass with my fingers?*

It became an opportunity to experiment with computer vision, gesture recognition, OpenGL, and real-time interaction — without needing to turn the idea into a serious product.

The goal wasn't to build a perfect physics simulator. It was to explore an idea, learn by building, and have fun with the process.

## 📄 License

This project was created for personal experimentation and learning. If you plan to reuse or distribute the code, check the repository's licensing terms or add an explicit open-source license.

## 👩‍💻 Author

**Armina Sadeghi**

[GitHub Profile](https://github.com/arminasadeghii)

*Built out of curiosity, one random idea at a time.*
