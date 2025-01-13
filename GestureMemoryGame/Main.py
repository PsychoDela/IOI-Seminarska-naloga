# Import necessary libraries
import cv2  # For webcam video capture and display
import mediapipe as mp  # For hand tracking
import numpy as np  # For numerical operations
import random  # For generating random sequences
import time  # For tracking time
import pygame  # For playing sound effects
from datetime import datetime  # For logging timestamps

# Initialize MediaPipe hands module for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame mixer for sound effects
pygame.mixer.init()
success_sound = pygame.mixer.Sound('success.mp3')  # Sound to play on successful guess
failure_sound = pygame.mixer.Sound('failure.mp3')  # Sound to play on incorrect guess

# Log file setup to track game results
log_file = "game_log.txt"


def log_game_result(round_number, sequence, success):
    """
    Log the results of each game round to a text file.

    Args:
        round_number (int): The current round number.
        sequence (list): The sequence of numbers to guess.
        success (bool): Whether the user succeeded in the round.
    """
    with open(log_file, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = "SUCCESS" if success else "FAILURE"
        log.write(f"[{timestamp}] Round: {round_number}, Sequence: {sequence}, Result: {result}\n")


def detect_custom_shape(hand_landmarks, roi_x1, roi_y1, roi_x2, roi_y2):
    """
    Detect if the hand is making a fist (custom shape for '0').

    Args:
        hand_landmarks: Hand landmarks detected by MediaPipe.
        roi_x1, roi_y1, roi_x2, roi_y2: Coordinates of the region of interest (ROI).

    Returns:
        bool: True if a fist is detected, False otherwise.
    """
    finger_tips = [4, 8, 12, 16, 20]  # Fingertip landmarks
    finger_base = [2, 5, 9, 13, 17]  # Base knuckle landmarks

    # Check if landmarks are within the ROI
    def is_within_roi(landmark):
        x, y = landmark.x, landmark.y
        return roi_x1 <= x <= roi_x2 and roi_y1 <= y <= roi_y2

    # Ensure all relevant landmarks are within the ROI
    for i in finger_tips + finger_base:
        if not is_within_roi(hand_landmarks.landmark[i]):
            return False

    # Verify that all fingertips are below their respective base knuckles (fist shape)
    for tip, base in zip(finger_tips, finger_base):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            return False  # If any finger is extended, it's not a fist

    return True  # All conditions met for a fist


def count_fingers_within_roi(hand_landmarks, roi_x1, roi_y1, roi_x2, roi_y2):
    """
    Count the number of raised fingers or detect custom shapes (like a fist for '0').

    Args:
        hand_landmarks: Hand landmarks detected by MediaPipe.
        roi_x1, roi_y1, roi_x2, roi_y2: Coordinates of the region of interest (ROI).

    Returns:
        int: The number of raised fingers or 0 if a fist is detected.
    """
    # Check for the custom shape (fist for '0') first
    if detect_custom_shape(hand_landmarks, roi_x1, roi_y1, roi_x2, roi_y2):
        return 0

    # Count raised fingers
    finger_tips = [4, 8, 12, 16, 20]  # Fingertip landmarks
    finger_states = []

    # Check if landmarks are within the ROI
    def is_within_roi(landmark):
        x, y = landmark.x, landmark.y
        return roi_x1 <= x <= roi_x2 and roi_y1 <= y <= roi_y2

    # Evaluate each fingertip state (raised or not)
    for i, tip in enumerate(finger_tips):
        if not is_within_roi(hand_landmarks.landmark[tip]):
            return -1  # Not all fingers are within the ROI
        if i == 0:  # Thumb
            if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                finger_states.append(1)
            else:
                finger_states.append(0)
        else:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                finger_states.append(1)
            else:
                finger_states.append(0)

    return sum(finger_states[1:])  # Exclude the thumb


# Initialize webcam and configure its resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)

# Initialize game variables
sequence = [random.randint(0, 4)]  # Sequence of numbers to guess
current_index = 0
last_detected = -1
start_time = None
hold_duration = 0.75  # Duration to hold a gesture in seconds
round_number = 1  # Current game round
display_sequence_time = 3  # Duration to display the sequence to the player
sequence_displayed = False
sequence_start_time = None

# Define ROI (Region of Interest) for hand detection
roi_x1, roi_y1, roi_x2, roi_y2 = 0.3, 0.3, 0.7, 0.7  # Rectangle in normalized coordinates

# Main game loop
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip and convert the frame for processing
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Draw the ROI rectangle on the frame
        roi_x1_px, roi_y1_px = int(roi_x1 * w), int(roi_y1 * h)
        roi_x2_px, roi_y2_px = int(roi_x2 * w), int(roi_y2 * h)
        cv2.rectangle(frame, (roi_x1_px, roi_y1_px), (roi_x2_px, roi_y2_px), (255, 0, 0), 2)

        # Create an overlay for displaying text
        overlay_width = 400
        overlay = np.ones((h, overlay_width, 3), dtype=np.uint8) * 255

        # Display the sequence for the player to memorize
        if not sequence_displayed:
            if sequence_start_time is None:
                sequence_start_time = time.time()
            if time.time() - sequence_start_time <= display_sequence_time:
                cv2.putText(overlay, "Memorize:", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
                for i, num in enumerate(sequence):
                    cv2.putText(overlay, str(num), (10, 100 + i * 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            else:
                sequence_displayed = True
                sequence_start_time = None
                current_index = 0
        else:
            detected_fingers = -1
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    detected_fingers = count_fingers_within_roi(
                        hand_landmarks, roi_x1, roi_y1, roi_x2, roi_y2
                    )
                    if detected_fingers != -1:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    break

            if detected_fingers != -1:
                if detected_fingers == last_detected:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= hold_duration:
                        if detected_fingers == sequence[current_index]:
                            success_sound.play()
                            current_index += 1
                            last_detected = -1
                            start_time = None
                            time.sleep(1)
                            if current_index == len(sequence):
                                log_game_result(round_number, sequence, True)
                                round_number += 1
                                sequence.append(random.randint(0, 4))
                                current_index = 0
                                sequence_displayed = False
                        else:
                            failure_sound.play()
                            time.sleep(1)
                            log_game_result(round_number, sequence, False)
                            sequence = [random.randint(0, 4)]
                            round_number = 1
                            current_index = 0
                            sequence_displayed = False
                            start_time = None
                else:
                    last_detected = detected_fingers
                    start_time = None

            # Display guessed numbers
            cv2.putText(overlay, "Your Guesses:", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            for i in range(current_index):
                cv2.putText(overlay, str(sequence[i]), (10, 100 + i * 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0),
                            3)

        # Combine the frame and overlay for display
        combined_frame = np.hstack((frame, overlay))
        cv2.imshow("Memory Game", combined_frame)

        # Exit the game if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Clean up resources
cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
