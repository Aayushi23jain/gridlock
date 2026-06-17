"""Generate synthetic test images/videos for all violation types.

This script creates realistic synthetic violation data that can be used
to test the Gridlock 2.0 system and generate E-Challans.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from datetime import datetime
import json


class ViolationTestDataGenerator:
    """Generate synthetic test data for all violation types."""
    
    def __init__(self, output_dir="test_data/violation_samples"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.violation_types = [
            "Helmet Non-Compliance",
            "Seatbelt Non-Compliance", 
            "Triple Riding",
            "Wrong-Side Driving",
            "Stop-Line Violation",
            "Red-Light Violation",
            "Illegal Parking",
            "Overspeed"
        ]
    
    def create_base_scene(self, width=640, height=480):
        """Create base traffic scene with road and environment."""
        scene = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Sky
        scene[:100, :] = (135, 206, 235)  # Light blue sky
        
        # Road
        scene[150:400, :] = (100, 100, 100)  # Gray road
        
        # Road markings
        cv2.line(scene, (320, 150), (320, 400), (255, 255, 255), 2)  # Center line
        
        # Sidewalks
        scene[400:480, :] = (200, 200, 200)  # Gray sidewalks
        
        return scene
    
    def generate_helmet_violation(self):
        """Generate motorcycle rider without helmet."""
        scene = self.create_base_scene()
        
        # Road with traffic context
        cv2.rectangle(scene, (50, 200), (150, 350), (80, 80, 80), -1)  # Road background
        
        # Motorcycle body
        cv2.rectangle(scene, (200, 250), (350, 380), (200, 50, 50), -1)  # Red motorcycle
        cv2.rectangle(scene, (210, 240), (340, 250), (150, 150, 150), -1)  # Motorcycle seat
        
        # Rider body
        cv2.rectangle(scene, (230, 180), (320, 250), (50, 100, 200), -1)  # Blue jacket
        
        # Head without helmet (skin color)
        cv2.circle(scene, (275, 160), 25, (255, 200, 150), -1)  # Skin-toned head
        cv2.circle(scene, (275, 160), 25, (200, 150, 100), 2)  # Head outline
        
        # Hair (indicating no helmet)
        cv2.ellipse(scene, (275, 145), (20, 15), 0, 0, 360, (50, 30, 10), -1)
        
        # License plate area
        cv2.rectangle(scene, (330, 300), (350, 320), (255, 255, 0), -1)  # Yellow plate
        cv2.putText(scene, "MH12", (332, 312), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "helmet_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_seatbelt_violation(self):
        """Generate car driver without seatbelt."""
        scene = self.create_base_scene()
        
        # Car body
        cv2.rectangle(scene, (100, 200), (500, 350), (50, 100, 200), -1)  # Blue car
        
        # Windows
        cv2.rectangle(scene, (120, 210), (200, 280), (135, 206, 235), -1)  # Front window
        cv2.rectangle(scene, (400, 210), (480, 280), (135, 206, 235), -1)  # Rear window
        
        # Driver area (no seatbelt visible)
        cv2.circle(scene, (160, 245), 15, (255, 200, 150), -1)  # Driver head
        cv2.rectangle(scene, (145, 260), (175, 280), (200, 150, 100), -1)  # Driver body
        
        # Steering wheel
        cv2.circle(scene, (160, 275), 10, (50, 50, 50), 2)
        
        # License plate
        cv2.rectangle(scene, (480, 300), (520, 320), (255, 255, 0), -1)
        cv2.putText(scene, "DL01", (485, 312), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "seatbelt_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_triple_riding(self):
        """Generate motorcycle with 3 riders."""
        scene = self.create_base_scene()
        
        # Motorcycle body (larger for 3 riders)
        cv2.rectangle(scene, (150, 220), (450, 380), (200, 50, 50), -1)  # Red motorcycle
        
        # 3 riders
        # Rider 1 (front)
        cv2.circle(scene, (200, 200), 20, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (180, 220), (220, 250), (50, 100, 200), -1)  # Body
        
        # Rider 2 (middle)
        cv2.circle(scene, (280, 200), 20, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (260, 220), (300, 250), (100, 100, 50), -1)  # Body
        
        # Rider 3 (rear)
        cv2.circle(scene, (360, 200), 20, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (340, 220), (380, 250), (150, 50, 100), -1)  # Body
        
        # License plate
        cv2.rectangle(scene, (420, 320), (450, 340), (255, 255, 0), -1)
        cv2.putText(scene, "KA01", (425, 332), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "triple_riding.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_wrong_side_driving(self):
        """Generate vehicle driving on wrong side."""
        scene = self.create_base_scene()
        
        # Road with clear lane markings
        cv2.line(scene, (320, 150), (320, 400), (255, 255, 0), 5)  # Yellow center line
        cv2.line(scene, (160, 150), (160, 400), (255, 255, 255), 2)  # Left lane marker
        cv2.line(scene, (480, 150), (480, 400), (255, 255, 255), 2)  # Right lane marker
        
        # Car on wrong side (left side when should be right)
        cv2.rectangle(scene, (50, 250), (150, 320), (0, 100, 255), -1)  # Car on wrong side
        cv2.rectangle(scene, (60, 230), (80, 250), (200, 200, 200), -1)  # Windshield
        
        # Arrow indicators showing wrong direction
        cv2.arrowedLine(scene, (320, 300), (200, 300), (0, 255, 0), 3, tipLength=0.3)  # Correct direction
        cv2.arrowedLine(scene, (100, 300), (180, 300), (255, 0, 0), 3, tipLength=0.3)  # Wrong direction
        
        # License plate
        cv2.rectangle(scene, (120, 300), (150, 320), (255, 255, 0), -1)
        cv2.putText(scene, "TN07", (125, 312), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "wrong_side_driving.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_stop_line_violation(self):
        """Generate vehicle crossing stop line."""
        scene = self.create_base_scene()
        
        # Intersection with stop line
        cv2.line(scene, (100, 280), (540, 280), (255, 255, 255), 8)  # Stop line
        cv2.putText(scene, "STOP", (300, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Car crossing stop line
        cv2.rectangle(scene, (250, 260), (350, 330), (0, 100, 255), -1)  # Car crossing line
        cv2.rectangle(scene, (260, 240), (340, 260), (200, 200, 200), -1)  # Windshield
        
        # Stop line text emphasis
        cv2.putText(scene, "VIOLATION", (200, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # License plate
        cv2.rectangle(scene, (330, 310), (370, 330), (255, 255, 0), -1)
        cv2.putText(scene, "GJ01", (335, 322), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "stop_line_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_red_light_violation(self):
        """Generate vehicle at red light intersection."""
        scene = self.create_base_scene()
        
        # Traffic light pole
        cv2.rectangle(scene, (550, 50), (560, 200), (50, 50, 50), -1)  # Pole
        
        # Traffic light box
        cv2.rectangle(scene, (540, 60), (580, 140), (30, 30, 30), -1)  # Light box
        
        # Red light (active)
        cv2.circle(scene, (560, 80), 12, (0, 0, 255), -1)  # Red light
        cv2.circle(scene, (560, 80), 12, (255, 0, 0), -1)  # Inner red
        
        # Yellow light (inactive)
        cv2.circle(scene, (560, 100), 12, (50, 50, 50), -1)
        
        # Green light (inactive)
        cv2.circle(scene, (560, 120), 12, (50, 50, 50), -1)
        
        # Car at intersection during red light
        cv2.rectangle(scene, (200, 270), (350, 340), (0, 100, 255), -1)  # Car
        cv2.rectangle(scene, (210, 250), (340, 270), (200, 200, 200), -1)  # Windshield
        
        # Red light emphasis
        cv2.putText(scene, "RED LIGHT", (450, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # License plate
        cv2.rectangle(scene, (330, 320), (370, 340), (255, 255, 0), -1)
        cv2.putText(scene, "UP32", (335, 332), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "red_light_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_illegal_parking(self):
        """Generate vehicle parked in no-parking zone."""
        scene = self.create_base_scene()
        
        # Road with no-parking zone markings
        cv2.line(scene, (50, 380), (150, 380), (255, 255, 0), 3)  # No-parking line
        cv2.line(scene, (50, 380), (50, 420), (255, 255, 0), 3)  # Vertical line
        cv2.line(scene, (150, 380), (150, 420), (255, 255, 0), 3)  # Vertical line
        
        # No parking symbol
        cv2.circle(scene, (100, 400), 20, (255, 255, 0), 2)
        cv2.line(scene, (100, 385), (100, 415), (255, 255, 0), 3)
        
        # Car parked in no-parking zone
        cv2.rectangle(scene, (60, 360), (140, 420), (0, 100, 255), -1)  # Parked car
        cv2.rectangle(scene, (65, 345), (135, 360), (200, 200, 200), -1)  # Windshield
        
        # No parking text
        cv2.putText(scene, "NO PARKING", (55, 435), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 2)
        
        # License plate
        cv2.rectangle(scene, (120, 405), (140, 420), (255, 255, 0), -1)
        cv2.putText(scene, "RJ14", (122, 415), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
        
        output_path = os.path.join(self.output_dir, "illegal_parking.jpg")
        cv2.imwrite(output_path, scene)
        return output_path
    
    def generate_overspeed_video(self):
        """Generate video sequence showing speeding vehicle."""
        fps = 30
        duration_seconds = 3
        width, height = 640, 480
        
        # Create video writer
        output_path = os.path.join(self.output_dir, "overspeed_violation.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Generate frames with vehicle moving at increasing speed
        num_frames = fps * duration_seconds
        
        for frame_num in range(num_frames):
            frame = self.create_base_scene()
            
            # Speed reference markers (every 100 pixels)
            for x in range(100, 600, 100):
                cv2.line(frame, (x, 150), (x, 400), (255, 255, 0), 1)
                cv2.putText(frame, f"{x}px", (x-15, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
            
            # Speed text (simulated)
            speed = 40 + (frame_num / num_frames) * 40  # 40-80 km/h
            cv2.putText(frame, f"Speed: {int(speed)} km/h", (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if speed > 50:
                cv2.putText(frame, "OVERSPEED!", (450, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Car position (moving faster as frames progress)
            start_x = 50
            end_x = 550
            progress = frame_num / num_frames
            
            # Non-linear movement to simulate acceleration
            car_x = int(start_x + (end_x - start_x) * (progress ** 1.5))
            
            # Car
            cv2.rectangle(frame, (car_x, 280), (car_x + 100, 350), (0, 100, 255), -1)
            cv2.rectangle(frame, (car_x + 10, 260), (car_x + 90, 280), (200, 200, 200), -1)
            
            # Motion blur effect
            blur_length = int(speed / 10)
            if blur_length > 0:
                cv2.line(frame, (car_x - blur_length, 315), (car_x, 315), (200, 200, 255), blur_length)
            
            # License plate
            cv2.rectangle(frame, (car_x + 70, 340), (car_x + 100, 360), (255, 255, 0), -1)
            cv2.putText(frame, "HR26", (car_x + 72, 352), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            
            # Frame number
            cv2.putText(frame, f"Frame: {frame_num}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            out.write(frame)
        
        out.release()
        return output_path
    
    def generate_all_violations(self):
        """Generate test data for all violation types."""
        print("Generating Violation Test Data")
        print("=" * 50)
        
        generated_files = {}
        
        # Generate image-based violations
        print("\nGenerating image violations...")
        
        violations_map = {
            "Helmet Non-Compliance": self.generate_helmet_violation,
            "Seatbelt Non-Compliance": self.generate_seatbelt_violation,
            "Triple Riding": self.generate_triple_riding,
            "Wrong-Side Driving": self.generate_wrong_side_driving,
            "Stop-Line Violation": self.generate_stop_line_violation,
            "Red-Light Violation": self.generate_red_light_violation,
            "Illegal Parking": self.generate_illegal_parking,
        }
        
        for violation_name, generator_func in violations_map.items():
            try:
                print(f"  Generating: {violation_name}")
                output_path = generator_func()
                generated_files[violation_name] = output_path
                print(f"    ✓ Created: {output_path}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                generated_files[violation_name] = None
        
        # Generate video-based violation
        print("\nGenerating video violations...")
        print("  Generating: Overspeed")
        try:
            video_path = self.generate_overspeed_video()
            generated_files["Overspeed"] = video_path
            print(f"    ✓ Created: {video_path}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            generated_files["Overspeed"] = None
        
        # Generate metadata file
        print("\nGenerating metadata file...")
        metadata = {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_violations": len(generated_files),
            "violations": {}
        }
        
        for violation_name, path in generated_files.items():
            metadata["violations"][violation_name] = {
                "file_path": path,
                "file_type": "video" if violation_name == "Overspeed" else "image",
                "status": "generated" if path else "failed"
            }
        
        metadata_path = os.path.join(self.output_dir, "violation_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"    ✓ Created: {metadata_path}")
        
        # Summary
        print("\n" + "=" * 50)
        print("Generation Summary")
        print("=" * 50)
        successful = sum(1 for path in generated_files.values() if path)
        total = len(generated_files)
        
        print(f"Total violations: {total}")
        print(f"Successfully generated: {successful}")
        print(f"Failed: {total - successful}")
        print(f"\nOutput directory: {self.output_dir}")
        
        print("\nGenerated Files:")
        for violation_name, path in generated_files.items():
            status = "✓" if path else "✗"
            print(f"  {status} {violation_name}: {path}")
        
        print("\nUsage:")
        print("1. Use these images/videos in the Gridlock 2.0 system")
        print("2. Upload via Streamlit app or process with pipeline")
        print("3. Generate E-Challans for detected violations")
        print("\nExample:")
        print("  python app.py  # Then upload generated images")
        print("  # Or use programmatically:")
        print("  pipeline.run_pipeline('test_data/violation_samples/helmet_violation.jpg')")
        
        return generated_files


def main():
    """Main function to generate all violation test data."""
    generator = ViolationTestDataGenerator()
    generator.generate_all_violations()


if __name__ == "__main__":
    main()