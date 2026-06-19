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
            "Illegal Parking"
        ]
        
        # Indian state codes for realistic number plates
        self.state_codes = ["MH", "DL", "KA", "TN", "GJ", "UP", "RJ", "WB", "HR", "PB"]
    
    def generate_number_plate(self, state_code=None):
        """Generate a realistic Indian number plate."""
        if state_code is None:
            state_code = np.random.choice(self.state_codes)
        
        district = f"{np.random.randint(1, 100):02d}"
        series = "".join(np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 2))
        number = f"{np.random.randint(1000, 9999)}"
        
        return f"{state_code}{district}{series}{number}"
    
    def create_base_scene(self, width=1280, height=720):
        """Create base traffic scene with road and environment."""
        scene = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Sky
        scene[:200, :] = (135, 206, 235)  # Light blue sky
        
        # Road
        scene[250:600, :] = (100, 100, 100)  # Gray road
        
        # Road markings
        cv2.line(scene, (640, 250), (640, 600), (255, 255, 255), 4)  # Center line
        
        # Sidewalks
        scene[600:720, :] = (200, 200, 200)  # Gray sidewalks
        
        return scene
    
    def generate_helmet_violation(self):
        """Generate motorcycle rider without helmet."""
        scene = self.create_base_scene()
        
        # Road with traffic context (scaled)
        cv2.rectangle(scene, (100, 400), (300, 700), (80, 80, 80), -1)  # Road background
        
        # Motorcycle body (scaled)
        cv2.rectangle(scene, (400, 500), (700, 760), (200, 50, 50), -1)  # Red motorcycle
        cv2.rectangle(scene, (420, 480), (680, 500), (150, 150, 150), -1)  # Motorcycle seat
        
        # Rider body (scaled)
        cv2.rectangle(scene, (460, 360), (640, 500), (50, 100, 200), -1)  # Blue jacket
        
        # Head without helmet (skin color)
        cv2.circle(scene, (550, 320), 50, (255, 200, 150), -1)  # Skin-toned head
        cv2.circle(scene, (550, 320), 50, (200, 150, 100), 4)  # Head outline
        
        # Hair (indicating no helmet)
        cv2.ellipse(scene, (550, 290), (40, 30), 0, 0, 360, (50, 30, 10), -1)
        
        # License plate area with full number (larger)
        number_plate = self.generate_number_plate("MH")
        cv2.rectangle(scene, (620, 600), (780, 640), (255, 255, 0), -1)  # Yellow plate
        cv2.putText(scene, number_plate, (630, 625), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "helmet_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_seatbelt_violation(self):
        """Generate car driver without seatbelt."""
        scene = self.create_base_scene()
        
        # Car body (scaled)
        cv2.rectangle(scene, (200, 400), (1000, 700), (50, 100, 200), -1)  # Blue car
        
        # Windows (scaled)
        cv2.rectangle(scene, (240, 420), (400, 560), (135, 206, 235), -1)  # Front window
        cv2.rectangle(scene, (800, 420), (960, 560), (135, 206, 235), -1)  # Rear window
        
        # Driver area (no seatbelt visible) (scaled)
        cv2.circle(scene, (320, 490), 30, (255, 200, 150), -1)  # Driver head
        cv2.rectangle(scene, (290, 520), (350, 560), (200, 150, 100), -1)  # Driver body
        
        # Steering wheel (scaled)
        cv2.circle(scene, (320, 550), 20, (50, 50, 50), 4)
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("DL")
        cv2.rectangle(scene, (940, 600), (1060, 640), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (950, 625), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "seatbelt_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_triple_riding(self):
        """Generate motorcycle with 3 riders."""
        scene = self.create_base_scene()
        
        # Motorcycle body (larger for 3 riders) (scaled)
        cv2.rectangle(scene, (300, 440), (900, 760), (200, 50, 50), -1)  # Red motorcycle
        
        # 3 riders (scaled)
        # Rider 1 (front)
        cv2.circle(scene, (400, 400), 40, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (360, 440), (440, 500), (50, 100, 200), -1)  # Body
        
        # Rider 2 (middle)
        cv2.circle(scene, (560, 400), 40, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (520, 440), (600, 500), (100, 100, 50), -1)  # Body
        
        # Rider 3 (rear)
        cv2.circle(scene, (720, 400), 40, (255, 200, 150), -1)  # Head
        cv2.rectangle(scene, (680, 440), (760, 500), (150, 50, 100), -1)  # Body
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("KA")
        cv2.rectangle(scene, (820, 640), (920, 680), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (830, 665), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "triple_riding.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_wrong_side_driving(self):
        """Generate vehicle driving on wrong side."""
        scene = self.create_base_scene()
        
        # Road with clear lane markings (scaled)
        cv2.line(scene, (640, 250), (640, 600), (255, 255, 0), 10)  # Yellow center line
        cv2.line(scene, (320, 250), (320, 600), (255, 255, 255), 4)  # Left lane marker
        cv2.line(scene, (960, 250), (960, 600), (255, 255, 255), 4)  # Right lane marker
        
        # Car on wrong side (left side when should be right) (scaled)
        cv2.rectangle(scene, (100, 500), (300, 640), (0, 100, 255), -1)  # Car on wrong side
        cv2.rectangle(scene, (120, 460), (160, 500), (200, 200, 200), -1)  # Windshield
        
        # Arrow indicators showing wrong direction (scaled)
        cv2.arrowedLine(scene, (640, 600), (400, 600), (0, 255, 0), 6, tipLength=0.3)  # Correct direction
        cv2.arrowedLine(scene, (200, 600), (360, 600), (255, 0, 0), 6, tipLength=0.3)  # Wrong direction
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("TN")
        cv2.rectangle(scene, (220, 600), (320, 640), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (230, 625), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "wrong_side_driving.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_stop_line_violation(self):
        """Generate vehicle crossing stop line."""
        scene = self.create_base_scene()
        
        # Intersection with stop line (scaled)
        cv2.line(scene, (200, 560), (1080, 560), (255, 255, 255), 16)  # Stop line
        cv2.putText(scene, "STOP", (600, 540), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 4)
        
        # Car crossing stop line (scaled)
        cv2.rectangle(scene, (500, 520), (700, 660), (0, 100, 255), -1)  # Car crossing line
        cv2.rectangle(scene, (520, 480), (680, 520), (200, 200, 200), -1)  # Windshield
        
        # Stop line text emphasis (scaled)
        cv2.putText(scene, "VIOLATION", (400, 720), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 255), 4)
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("GJ")
        cv2.rectangle(scene, (640, 620), (760, 660), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (650, 645), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "stop_line_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_red_light_violation(self):
        """Generate vehicle at red light intersection."""
        scene = self.create_base_scene()
        
        # Traffic light pole (scaled)
        cv2.rectangle(scene, (1100, 100), (1120, 400), (50, 50, 50), -1)  # Pole
        
        # Traffic light box (scaled)
        cv2.rectangle(scene, (1080, 120), (1160, 280), (30, 30, 30), -1)  # Light box
        
        # Red light (active) (scaled)
        cv2.circle(scene, (1120, 160), 24, (0, 0, 255), -1)  # Red light
        cv2.circle(scene, (1120, 160), 24, (255, 0, 0), -1)  # Inner red
        
        # Yellow light (inactive) (scaled)
        cv2.circle(scene, (1120, 200), 24, (50, 50, 50), -1)
        
        # Green light (inactive) (scaled)
        cv2.circle(scene, (1120, 240), 24, (50, 50, 50), -1)
        
        # Car at intersection during red light (scaled)
        cv2.rectangle(scene, (400, 540), (700, 680), (0, 100, 255), -1)  # Car
        cv2.rectangle(scene, (420, 500), (680, 540), (200, 200, 200), -1)  # Windshield
        
        # Red light emphasis (scaled)
        cv2.putText(scene, "RED LIGHT", (900, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 4)
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("UP")
        cv2.rectangle(scene, (640, 640), (760, 680), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (650, 665), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "red_light_violation.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    def generate_illegal_parking(self):
        """Generate vehicle parked in no-parking zone."""
        scene = self.create_base_scene()
        
        # Road with no-parking zone markings (scaled)
        cv2.line(scene, (100, 760), (300, 760), (255, 255, 0), 6)  # No-parking line
        cv2.line(scene, (100, 760), (100, 840), (255, 255, 0), 6)  # Vertical line
        cv2.line(scene, (300, 760), (300, 840), (255, 255, 0), 6)  # Vertical line
        
        # No parking symbol (scaled)
        cv2.circle(scene, (200, 800), 40, (255, 255, 0), 4)
        cv2.line(scene, (200, 770), (200, 830), (255, 255, 0), 6)
        
        # Car parked in no-parking zone (scaled)
        cv2.rectangle(scene, (120, 720), (280, 840), (0, 100, 255), -1)  # Parked car
        cv2.rectangle(scene, (130, 690), (270, 720), (200, 200, 200), -1)  # Windshield
        
        # No parking text (scaled)
        cv2.putText(scene, "NO PARKING", (110, 870), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 4)
        
        # License plate with full number (larger)
        number_plate = self.generate_number_plate("RJ")
        cv2.rectangle(scene, (230, 810), (290, 840), (255, 255, 0), -1)
        cv2.putText(scene, number_plate, (236, 830), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        output_path = os.path.join(self.output_dir, "illegal_parking.jpg")
        cv2.imwrite(output_path, scene)
        return output_path, number_plate
    
    
    
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
                output_path, number_plate = generator_func()
                generated_files[violation_name] = {
                    "file_path": output_path,
                    "number_plate": number_plate
                }
                print(f"    [OK] Created: {output_path}")
                print(f"    [OK] Number Plate: {number_plate}")
            except Exception as e:
                print(f"    [ERROR] Error: {e}")
                generated_files[violation_name] = {
                    "file_path": None,
                    "number_plate": None
                }
        
        # Generate metadata file
        print("\nGenerating metadata file...")
        metadata = {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_violations": len(generated_files),
            "violations": {}
        }
        
        for violation_name, data in generated_files.items():
            metadata["violations"][violation_name] = {
                "file_path": data["file_path"],
                "number_plate": data["number_plate"],
                "file_type": "image",
                "status": "generated" if data["file_path"] else "failed"
            }
        
        metadata_path = os.path.join(self.output_dir, "violation_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"    [OK] Created: {metadata_path}")
        
        # Summary
        print("\n" + "=" * 50)
        print("Generation Summary")
        print("=" * 50)
        successful = sum(1 for data in generated_files.values() if data["file_path"])
        total = len(generated_files)
        
        print(f"Total violations: {total}")
        print(f"Successfully generated: {successful}")
        print(f"Failed: {total - successful}")
        print(f"\nOutput directory: {self.output_dir}")
        
        print("\nGenerated Files:")
        for violation_name, data in generated_files.items():
            status = "[OK]" if data["file_path"] else "[FAIL]"
            print(f"  {status} {violation_name}: {data['file_path']}")
            if data["number_plate"]:
                print(f"      Number Plate: {data['number_plate']}")
        
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