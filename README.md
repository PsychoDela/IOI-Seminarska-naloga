# Hand Gesture Memory Game 🎮🤲

This project is a hand-gesture-based memory game implemented using Python, OpenCV, MediaPipe, and Pygame. The game challenges players to memorize and replicate a sequence of numbers using hand gestures, with each number represented by the count of fingers shown.

## Table of Contents
1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Game Rules](#game-rules)

---

## Features

- Detects hand gestures using [MediaPipe](https://google.github.io/mediapipe/).
- Recognizes a "fist" as `0` and raised fingers for numbers `1` to `4`.
- Visualizes a region of interest (ROI) for gesture detection.
- Logs game results (success or failure) to a text file with timestamps.
- Plays success and failure sounds for better interactivity.

---

## How It Works

1. A random sequence of numbers (0-4) is generated.
2. The player memorizes the sequence displayed on the screen.
3. The player performs the sequence of gestures (fist = `0`, raised fingers = `1-4`).
4. Success or failure is determined based on the gestures made.

---

## Requirements

- Python 3.7+
- Webcam
- Libraries:
  - OpenCV
  - MediaPipe
  - Pygame
  - NumPy

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/PsychoDela/IOI-Seminarska-naloga.git
   cd IOI-Seminarska-naloga
   ```

2. **Set Up a Virtual Environment (Optional)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install opencv-python mediapipe numpy pygame
   ```

---

## Usage

1. **Run the Game**:
   ```bash
   python Main.py
   ```

2. **Controls**:
   - Press `Q` to quit the game.

3. **Gameplay**:
   - Observe the number sequence displayed on the screen.
   - Perform the corresponding hand gestures within the blue rectangular ROI.
   - Hold each gesture for at least 0.75 seconds.
   - Complete the sequence to progress to the next round.

---

## Game Rules

- **Hand Gestures**:
  - `0`: Fist (all fingers closed).
  - `1`: One finger raised.
  - `2`: Two fingers raised.
  - `3`: Three fingers raised.
  - `4`: Four fingers raised.

- **Region of Interest (ROI)**:
  - Ensure your hand is within the blue rectangle on the screen for gestures to be detected.

- **Winning the Round**:
  - Successfully replicate the sequence of gestures in the correct order.

- **Losing the Round**:
  - An incorrect gesture resets the game to the first round.

---

Enjoy the game! If you encounter any issues, feel free to open an issue or reach out. 😊
