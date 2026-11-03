# 🥃 Finger-Controlled 3D Glass

A small computer vision and 3D graphics experiment that lets you control a virtual glass using nothing but your fingers and a webcam.

Move your hand to rotate a 3D glass, pinch your fingers to fill it, and tilt it to pour the liquid. No mouse or keyboard is needed for the main interactions, just your hand.


## ✨ Features

- 🖐️ **Real-Time Hand Tracking:** Detects hand landmarks using MediaPipe.
- 🔄 **Finger-Controlled Rotation:** Rotate the 3D glass by moving your index finger.
- 🤏 **Pinch-to-Fill:** Fill the glass by bringing your thumb and index finger together.
- 🥃 **Interactive Liquid Simulation:** Watch the liquid level change as you fill or pour.
- ↘️ **Gesture-Based Pouring:** Tilt the glass to pour liquid out.
- ✋ **Hand-Gesture Reset:** Open your hand to reset the glass.
- 🎥 **Live Webcam Feedback:** View the camera feed and detected hand landmarks in real time.
- 🎨 **Custom 3D Geometry:** A procedurally defined glass with adjustable dimensions and appearance.
- 🎛️ **Adjustable Responsiveness:** Fine-tune movement smoothing while the app is running.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/arminasadeghii/Finger-Controlled-3D-Glass.git
cd Finger-Controlled-3D-Glass

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

**Requirements:** Python 3.x (see note below), a working webcam, and a graphics driver with OpenGL support.

> ✏️ Replace "3.x" with the Python version you tested on (for example, 3.10), and pin package versions in `requirements.txt` (run `pip freeze` in your working environment). MediaPipe's API changes between releases, so pinned versions prevent surprises.

## 🎮 Controls

| Input                        | Action                  |
|------------------------------|-------------------------|
| Move your index finger       | Rotate the glass        |
| Pinch thumb and index finger | Fill the glass          |
| Tilt the glass               | Pour the liquid         |
| Open your hand               | Reset the glass         |
| `R`                          | Recenter the rotation   |
| `↑`                          | Increase responsiveness |
| `↓`                          | Increase smoothing      |
| `ESC`                        | Exit the application    |

## 🧠 How It Works

### 1. Hand Tracking

The webcam captures video frames, and MediaPipe detects key landmarks on the hand. These landmarks provide the positions needed to interpret finger movements and gestures.

### 2. Glass Rotation

The index finger's position is used to estimate a rotation angle, which is mapped to the glass's orientation in the 3D scene. Smoothing is applied to reduce the small, unwanted movements that hand tracking produces.

### 3. Pinch-to-Fill

The distance between the thumb and index finger is used to recognize a pinch.

**Thumb + Index Finger → Pinch Detected → Fill the Glass**

### 4. Tilt-to-Pour

When the glass tilts beyond a certain angle, pouring begins and the liquid level decreases according to the tilt.

**Tilt the Glass → Pouring Starts → Liquid Level Decreases**

### 5. Gesture-Based Reset

Opening the hand brings the glass back toward its initial state.

## 🛠️ Tech Stack

| Technology | Purpose                                          |
|------------|--------------------------------------------------|
| Python     | Core application and interaction logic           |
| MediaPipe  | Hand landmark detection                          |
| OpenCV     | Webcam input and computer vision                 |
| PyOpenGL   | 3D rendering                                     |
| Pygame     | Application window, event handling, and controls |
| NumPy      | Numerical calculations and geometry operations   |

## 📁 Project Structure

```
Finger-Controlled-3D-Glass/
├── main.py            # Main application and interaction loop
├── hand_tracker.py    # Hand tracking and gesture logic
├── cup_geometry.py    # Glass geometry and liquid representation
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
├── .gitignore
└── assets/
    └── demo.gif       # Demo recording
```

## 🎨 Customization

The glass geometry and rendering parameters can be adjusted in the source code. For example:

```python
cup = PentagonCup(
    height=2.0,
    outer_radius=1.0,
    wall_ratio=0.82,
    base_thickness=0.18
)
```

Color and transparency of the glass and liquid can also be changed through the rendering parameters.

## 🔧 Tuning Hand Tracking

Hand movement can feel jittery because of small variations in landmark detection. Smoothing reduces this:

```python
IndexFingerRotationTracker(
    smoothing=0.35,
    max_hands=1,
    detection_conf=0.6,
    tracking_conf=0.6
)
```

Higher smoothing reduces jitter but makes movement feel less immediate. The best balance depends on your lighting and setup.

## 🛟 Troubleshooting

**The webcam does not open**
- Close other apps that might be using the camera.
- Check that your operating system has granted camera permission to Python or your terminal.

**Hand tracking is jittery or loses your hand**
- Improve the lighting and keep your hand fully in frame.
- Press `↓` to increase smoothing.

**The 3D window fails to open**
- Update your graphics drivers and make sure OpenGL is supported on your machine.

## 💡 Why I Built This

I like taking random ideas that pop into my head and seeing whether I can actually build them. This project started with a simple question: *What if I could control a 3D glass with my fingers?*

It became a chance to experiment with computer vision, gesture recognition, OpenGL, and real-time interaction, without turning the idea into a serious product. The goal wasn't a perfect physics simulator. It was to explore an idea, learn by building, and have fun.

## 📄 License

This project is released under the [MIT License](LICENSE).

## 👩‍💻 Author

**Armina Sadeghi** — [GitHub](https://github.com/arminasadeghii)

*Built out of curiosity, one random idea at a time.*
