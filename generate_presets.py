import cv2
import numpy as np

def create_traffic_test_image():
    # Create a 1080p Dark/Rainy Asphalt Background (Simulation for challenges)
    img = np.ones((1080, 1920, 3), dtype=np.uint8) * 30
    
    # Draw Road Lanes (Yellow center line, White stop lines)
    cv2.line(img, (0, 700), (1920, 700), (0, 255, 255), 8) # Double Yellow Line
    cv2.line(img, (800, 700), (800, 1080), (255, 255, 255), 10) # Zebra/Stop Line Boundary
    
    # Mock Vehicle 1: Simulated SUV (Red Bounding Area placeholder)
    # Bounding box coordinates for testing: [x1, y1, x2, y2] -> [200, 400, 600, 800]
    cv2.rectangle(img, (200, 400), (600, 800), (50, 50, 200), -1) 
    cv2.rectangle(img, (200, 400), (600, 800), (0, 0, 255), 4) # Edge
    
    # Mock License Plate 1 on SUV
    cv2.rectangle(img, (350, 720), (520, 770), (255, 255, 255), -1)
    cv2.putText(img, "DL3CAM1234", (360, 755), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

    # Mock Vehicle 2: Triple Riding / No Helmet Motorcyclist (Blue Area placeholder)
    # Coordinates: [1000, 450, 1300, 900]
    cv2.rectangle(img, (1000, 450), (1300, 900), (200, 100, 50), -1)
    cv2.rectangle(img, (1000, 450), (1300, 900), (255, 165, 0), 4)
    
    # Mock License Plate 2 on Motorcycle
    cv2.rectangle(img, (1100, 820), (1250, 860), (255, 255, 255), -1)
    cv2.putText(img, "MH12AB9999", (1110, 850), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Add Simulated Low Light/Rain Noise Overlays (Motion blur challenge simulation)
    noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
    img = cv2.addWeighted(img, 0.9, noise, 0.1, 0)
    
    # Add UI Overlay Text to show it's a test file
    cv2.putText(img, "SIMULATED ENFORCEMENT CAMERA: NODE-04", (50, 80), 
                cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)
    
    # Save the file to your workspace
    output_path = "test_traffic_scene.jpg"
    cv2.imwrite(output_path, img)
    print(f"✅ Success! Test image generated dynamically at: {output_path}")

if __name__ == "__main__":
    create_traffic_test_image()