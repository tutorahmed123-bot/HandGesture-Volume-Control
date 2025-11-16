import cv2
import mediapipe as mp
import numpy as np
import time
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class DynamicHandVolumeControl:
    def __init__(self):
        print("ðŸŽ¯ Dynamic Hand Volume Control - Hand Openness = Volume Level")

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Volume control
        self.setup_volume_control()

        # Smoothing
        self.volume_smoothing = 0.2
        self.current_volume_percent = 50

    def setup_volume_control(self):
        """Setup volume control"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = interface.QueryInterface(IAudioEndpointVolume)
            self.vol_range = self.volume.GetVolumeRange()
            self.min_vol = self.vol_range[0]
            self.max_vol = self.vol_range[1]
            print(f"âœ… Volume control ready! Range: {self.min_vol:.1f} to {self.max_vol:.1f} dB")
            return True
        except Exception as e:
            print(f"âŒ Volume control failed: {e}")
            print("Volume display will work, but system volume won't change")
            self.volume = None
            return False

    def calculate_hand_openness(self, landmarks):
        """Calculate how open the hand is (0% to 100%)"""
        # Key points for measuring hand openness
        wrist = landmarks[0]
        middle_tip = landmarks[12]
        middle_base = landmarks[9]

        # Calculate distance from wrist to middle finger tip (hand length)
        hand_length = self.calculate_distance(wrist, middle_tip)

        # Calculate distance from wrist to middle finger base (palm size)
        palm_size = self.calculate_distance(wrist, middle_base)

        # Calculate finger spread
        thumb_tip = landmarks[4]
        pinky_tip = landmarks[20]
        hand_width = self.calculate_distance(thumb_tip, pinky_tip)

        # Normalize openness (combination of finger spread and extension)
        if hand_length > 0 and palm_size > 0:
            # Factor 1: Finger extension (how far fingers are from palm)
            extension_ratio = hand_length / palm_size

            # Factor 2: Finger spread (how wide the hand is)
            spread_ratio = hand_width / hand_length

            # Combine factors for overall openness
            openness = (extension_ratio * 0.6 + spread_ratio * 0.4)

            # Convert to percentage (clamped between 0% and 100%)
            openness_percent = max(0, min(100, int(openness * 100)))

            return openness_percent

        return 50  # Default middle value

    def calculate_finger_openness(self, landmarks):
        """Alternative method using individual finger angles"""
        tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        mcp_joints = [2, 5, 9, 13, 17]  # metacarpophalangeal joints

        total_angle = 0
        valid_fingers = 0

        for tip_id, mcp_id in zip(tips, mcp_joints):
            # For thumb, use different reference points
            if tip_id == 4:  # thumb
                wrist = landmarks[0]
                angle = self.calculate_angle(landmarks[tip_id], landmarks[mcp_id], wrist)
            else:
                wrist = landmarks[0]
                angle = self.calculate_angle(landmarks[tip_id], landmarks[mcp_id], wrist)

            if angle > 0:
                total_angle += angle
                valid_fingers += 1

        if valid_fingers > 0:
            avg_angle = total_angle / valid_fingers
            # Convert angle to percentage (adjust these values based on testing)
            openness = max(0, min(100, int((avg_angle / 180) * 100)))
            return openness

        return 50

    def calculate_simple_openness(self, landmarks):
        """Simple method using finger tip distances from palm center"""
        # Palm center (average of palm base points)
        palm_points = [0, 1, 5, 9, 13, 17]  # wrist and MCP joints
        palm_x = sum(landmarks[i].x for i in palm_points) / len(palm_points)
        palm_y = sum(landmarks[i].y for i in palm_points) / len(palm_points)

        # Finger tips
        tip_points = [4, 8, 12, 16, 20]

        total_distance = 0
        for tip_id in tip_points:
            distance = np.sqrt(
                (landmarks[tip_id].x - palm_x) ** 2 +
                (landmarks[tip_id].y - palm_y) ** 2
            )
            total_distance += distance

        avg_distance = total_distance / len(tip_points)

        # Normalize to 0-100% (you may need to adjust these values)
        min_dist = 0.05  # closed hand
        max_dist = 0.25  # fully open hand

        openness = (avg_distance - min_dist) / (max_dist - min_dist)
        openness_percent = max(0, min(100, int(openness * 100)))

        return openness_percent

    def calculate_distance(self, point1, point2):
        """Calculate distance between two landmarks"""
        return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        # Create vectors
        ba = [a.x - b.x, a.y - b.y]
        bc = [c.x - b.x, c.y - b.y]

        # Calculate angle
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        mag_ba = np.sqrt(ba[0] ** 2 + ba[1] ** 2)
        mag_bc = np.sqrt(bc[0] ** 2 + bc[1] ** 2)

        if mag_ba > 0 and mag_bc > 0:
            cosine_angle = dot_product / (mag_ba * mag_bc)
            cosine_angle = max(-1, min(1, cosine_angle))  # Clamp to avoid numerical errors
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)

        return 0

    def set_volume_from_openness(self, openness_percent):
        """Set volume based on hand openness"""
        if self.volume is None:
            return

        # Smooth the volume changes
        self.current_volume_percent = (
                self.volume_smoothing * openness_percent +
                (1 - self.volume_smoothing) * self.current_volume_percent
        )

        # Convert percentage to dB volume
        target_vol = self.min_vol + (self.current_volume_percent / 100.0) * (self.max_vol - self.min_vol)

        # Set volume
        self.volume.SetMasterVolumeLevel(target_vol, None)

    def draw_dynamic_interface(self, frame, openness_percent, landmarks):
        """Draw enhanced interface with hand visualization"""
        height, width = frame.shape[:2]

        # Main volume bar
        bar_width = 300
        bar_height = 30
        bar_x = (width - bar_width) // 2
        bar_y = height - 100

        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)

        # Fill with color gradient
        fill_width = int(bar_width * openness_percent / 100)

        # Color changes from red to green
        if openness_percent < 30:
            color = (0, 0, 255)  # Red
        elif openness_percent < 70:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 255, 0)  # Green

        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), color, -1)

        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        # Volume text
        text = f"Volume: {int(self.current_volume_percent)}% (Openness: {openness_percent}%)"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Draw openness indicator on hand
        if landmarks:
            # Use palm center for indicator
            palm_points = [0, 1, 5, 9, 13, 17]
            palm_x = int(sum(landmarks[i].x for i in palm_points) / len(palm_points) * width)
            palm_y = int(sum(landmarks[i].y for i in palm_points) / len(palm_points) * height)

            # Draw circle that changes size with openness
            circle_radius = int(10 + (openness_percent / 100) * 20)
            cv2.circle(frame, (palm_x, palm_y), circle_radius, color, 2)
            cv2.putText(frame, f"{openness_percent}%", (palm_x - 15, palm_y - circle_radius - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Information display
        info_lines = [
            "DYNAMIC VOLUME CONTROL",
            f"Hand Openness: {openness_percent}%",
            f"Volume Level: {int(self.current_volume_percent)}%",
            "",
            "INSTRUCTIONS:",
            "â€¢ Open hand wide â†’ High volume",
            "â€¢ Close hand â†’ Low volume",
            "â€¢ Continuous control!",
            "",
            "Press 'Q' to quit"
        ]

        for i, line in enumerate(info_lines):
            y_pos = 30 + i * 22
            if "DYNAMIC" in line:
                color = (0, 255, 255)  # Yellow
                thickness = 2
            elif "INSTRUCTIONS" in line:
                color = (255, 255, 0)  # Cyan
                thickness = 1
            elif "%" in line:
                color = (0, 255, 0) if openness_percent > 50 else (0, 0, 255)
                thickness = 1
            else:
                color = (255, 255, 255)
                thickness = 1

            cv2.putText(frame, line, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

        return frame

    def run(self):
        """Main application loop"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("âŒ Error: Could not open camera")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("=" * 70)
        print("ðŸŽ¯ DYNAMIC HAND VOLUME CONTROL")
        print("=" * 70)
        print("INSTRUCTIONS:")
        print("â€¢ Open your hand wide â†’ Volume increases")
        print("â€¢ Close your hand â†’ Volume decreases")
        print("â€¢ Continuous control - no need for gestures!")
        print("â€¢ Volume follows your hand openness in real-time")
        print("=" * 70)
        print("Starting in 3 seconds...")
        time.sleep(3)

        while True:
            success, img = cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe
            results = self.hands.process(img_rgb)

            openness_percent = 50  # Default middle value
            landmarks = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # Get landmarks
                    landmarks = hand_landmarks.landmark

                    # Calculate hand openness using simple method (most reliable)
                    openness_percent = self.calculate_simple_openness(landmarks)

                    # Set volume based on openness
                    self.set_volume_from_openness(openness_percent)

            # Draw interface
            img = self.draw_dynamic_interface(img, openness_percent, landmarks)

            # Display
            cv2.imshow("Dynamic Hand Volume Control", img)

            # Exit on 'Q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Dynamic volume control stopped.")


if __name__ == "__main__":
    controller = DynamicHandVolumeControl()
    controller.run()
