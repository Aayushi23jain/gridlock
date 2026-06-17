"""Professional E-Challan generator with comprehensive traffic citation format."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import Any

from fpdf import FPDF


# Fine amounts for different violation types (in INR - can be customized)
VIOLATION_FINES = {
    "Helmet Non-Compliance": 1000,
    "Seatbelt Non-Compliance": 1000,
    "Triple Riding": 1000,
    "Wrong-Side Driving": 1500,
    "Stop-Line Violation": 500,
    "Red-Light Violation": 1000,
    "Illegal Parking": 500,
}

# Violation sections and legal references
VIOLATION_LEGAL_REFERENCES = {
    "Helmet Non-Compliance": "Section 194D, Motor Vehicles Act",
    "Seatbelt Non-Compliance": "Section 194B, Motor Vehicles Act", 
    "Triple Riding": "Section 194D, Motor Vehicles Act",
    "Wrong-Side Driving": "Section 184, Motor Vehicles Act",
    "Stop-Line Violation": "Section 177, Motor Vehicles Act",
    "Red-Light Violation": "Section 183, Motor Vehicles Act",
    "Illegal Parking": "Section 177, Motor Vehicles Act",
}

# Authority information
AUTHORITY_INFO = {
    "name": "City Traffic Enforcement Authority",
    "department": "Department of Transport",
    "jurisdiction": "Metropolitan City Region",
    "address": "Traffic Control Center, Main Road, City - 560001",
    "phone": "+91-1800-XXX-XXXX",
    "email": "traffic.enforcement@gov.in",
    "website": "www.citytraffic.gov.in",
}

# Camera locations (can be expanded or made dynamic)
CAMERA_LOCATIONS = {
    "default": {
        "intersection": "Main Street & 5th Avenue Intersection",
        "camera_id": "CAM-001",
        "gps_coordinates": "12.9716° N, 77.5946° E",
        "zone": "Central Business District",
    }
}


class ChallanPDF(FPDF):
    """Custom PDF class with header and footer for E-Challan."""

    def header(self):
        """Generate official header for each page."""
        # Main header with authority information
        self.set_fill_color(220, 53, 69)  # Red header background
        self.rect(0, 0, 210, 35, "F")
        
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 16)
        self.cell(0, 8, AUTHORITY_INFO["name"], ln=1, align="C")
        
        self.set_font("Arial", "", 10)
        self.cell(0, 5, AUTHORITY_INFO["department"], ln=1, align="C")
        self.cell(0, 5, f"Jurisdiction: {AUTHORITY_INFO['jurisdiction']}", ln=1, align="C")
        
        self.set_y(40)
        self.set_text_color(0, 0, 0)

    def footer(self):
        """Generate footer with page numbers and disclaimer."""
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"Page {self.page_no()}", ln=1, align="C")
        self.cell(0, 5, "This is an electronically generated citation.", ln=1, align="C")
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align="C")


class EChallanGenerator:
    """Generate comprehensive E-Challan documents with all required elements."""

    def __init__(self):
        self.authority = AUTHORITY_INFO

    def _generate_challan_id(self, plate: str) -> str:
        """Generate unique challan ID based on plate and timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        plate_part = plate.replace(" ", "")[:6].upper()
        random_part = str(uuid.uuid4())[:4].upper()
        return f"CTE/{plate_part}/{timestamp}/{random_part}"

    def _get_payment_deadline(self) -> tuple[str, str]:
        """Calculate payment deadline (30 days from violation)."""
        deadline = datetime.now() + timedelta(days=30)
        due_date = deadline.strftime("%d-%m-%Y")
        due_time = deadline.strftime("%H:%M")
        return due_date, due_time

    def _get_camera_location(self, camera_id: str = None) -> dict:
        """Get camera location information."""
        if camera_id and camera_id in CAMERA_LOCATIONS:
            return CAMERA_LOCATIONS[camera_id]
        return CAMERA_LOCATIONS["default"]

    def _add_official_seal(self, pdf: ChallanPDF, x: float, y: float):
        """Add simulated official seal."""
        pdf.set_draw_color(220, 53, 69)
        pdf.set_line_width(0.5)
        pdf.circle(x, y, 20)
        pdf.set_font("Arial", "B", 8)
        pdf.set_text_color(220, 53, 69)
        pdf.text(x - 15, y - 5, "OFFICIAL")
        pdf.text(x - 12, y + 2, "SEAL")
        pdf.set_text_color(0, 0, 0)

    def _add_qr_placeholder(self, pdf: ChallanPDF, x: float, y: float):
        """Add QR code placeholder for payment."""
        pdf.set_draw_color(0, 0, 0)
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(x, y, 30, 30, "FD")
        pdf.set_font("Arial", "", 6)
        pdf.set_text_color(80, 80, 80)
        pdf.text(x + 3, y + 12, "SCAN TO")
        pdf.text(x + 5, y + 18, "PAY")
        pdf.set_text_color(0, 0, 0)

    def generate_challan(
        self,
        violation_data: dict[str, Any],
        evidence_image_path: str = None,
        annotated_image_path: str = None,
        camera_id: str = None,
    ) -> str:
        """
        Generate comprehensive E-Challan PDF.
        
        Args:
            violation_data: Dictionary containing violation details
            evidence_image_path: Path to original evidence image
            annotated_image_path: Path to annotated evidence image
            camera_id: Camera identifier for location info
            
        Returns:
            Path to generated PDF file
        """
        pdf = ChallanPDF()
        pdf.add_page()
        
        # Generate unique challan ID
        challan_id = self._generate_challan_id(violation_data.get("license_plate", "UNKNOWN"))
        violation_type = violation_data.get("violation_type", "Unknown Violation")
        plate = violation_data.get("license_plate", "UNKNOWN")
        confidence = violation_data.get("confidence", 0.0)
        timestamp = violation_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        vehicle_class = violation_data.get("vehicle_class", "Unknown")
        fine_amount = VIOLATION_FINES.get(violation_type, 500)
        legal_ref = VIOLATION_LEGAL_REFERENCES.get(violation_type, "Motor Vehicles Act")
        
        # Get location information
        location_info = self._get_camera_location(camera_id)
        
        # Calculate payment deadline
        due_date, due_time = self._get_payment_deadline()

        # ========== SECTION 1: CHALLAN HEADER ==========
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(220, 53, 69)
        pdf.cell(0, 10, "ELECTRONIC TRAFFIC CITATION (E-CHALLAN)", ln=1, align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Challan No: {challan_id}", ln=1, align="L")
        pdf.ln(3)

        # ========== SECTION 2: VIOLATION DETAILS ==========
        pdf.set_fill_color(255, 240, 240)
        pdf.rect(10, pdf.get_y(), 190, 25, "F")
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(220, 53, 69)
        pdf.cell(0, 6, "VIOLATION DETAILS", ln=1, align="L")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"Violation Type: {violation_type}", ln=0)
        pdf.cell(95, 6, f"Legal Reference: {legal_ref}", ln=1)
        pdf.cell(95, 6, f"Confidence Score: {confidence * 100:.1f}%", ln=0)
        pdf.cell(95, 6, f"Vehicle Class: {vehicle_class}", ln=1)
        pdf.ln(4)

        # ========== SECTION 3: VEHICLE INFORMATION ==========
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, "VEHICLE INFORMATION", ln=1, align="L")
        pdf.set_font("Arial", "", 10)
        
        # Get current Y position for box drawing
        current_y = pdf.get_y()
        
        # Vehicle information box
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(10, current_y, 90, 35)
        
        pdf.set_xy(12, current_y + 3)
        pdf.cell(86, 6, f"License Plate: {plate}", ln=1)
        pdf.set_xy(12, pdf.get_y())
        pdf.cell(86, 6, f"Vehicle Type: {vehicle_class}", ln=1)
        pdf.set_xy(12, pdf.get_y())
        pdf.cell(86, 6, "Color: Not Detected", ln=1)
        pdf.set_xy(12, pdf.get_y())
        pdf.cell(86, 6, "Make/Model: Not Detected", ln=1)
        
        # Location information box - reset Y to match vehicle box
        pdf.set_y(current_y)
        pdf.rect(110, current_y, 90, 35)
        
        pdf.set_xy(112, current_y + 3)
        pdf.cell(86, 6, f"Camera ID: {location_info['camera_id']}", ln=1)
        pdf.set_xy(112, pdf.get_y())
        
        # Handle potentially long location names with multi_cell
        location_text = f"Location: {location_info['intersection']}"
        if len(location_text) > 35:
            pdf.multi_cell(86, 5, location_text)
        else:
            pdf.cell(86, 6, location_text, ln=1)
            pdf.set_xy(112, pdf.get_y())
        
        pdf.set_xy(112, pdf.get_y())
        # Handle potentially long GPS coordinates
        gps_text = f"GPS: {location_info['gps_coordinates']}"
        if len(gps_text) > 35:
            pdf.multi_cell(86, 5, gps_text)
        else:
            pdf.cell(86, 6, gps_text, ln=1)
            pdf.set_xy(112, pdf.get_y())
        
        pdf.set_xy(112, pdf.get_y())
        pdf.cell(86, 6, f"Zone: {location_info['zone']}", ln=1)
        
        pdf.set_y(current_y + 40)  # Move past the boxes

        # ========== SECTION 4: INCIDENT DETAILS ==========
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, "INCIDENT DETAILS", ln=1, align="L")
        pdf.set_font("Arial", "", 10)
        
        # Get current Y position for box drawing
        current_y = pdf.get_y()
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(10, current_y, 190, 20)
        
        pdf.set_xy(12, current_y + 3)
        pdf.cell(93, 6, f"Date & Time: {timestamp}", ln=0)
        pdf.cell(93, 6, f"Status: Unpaid", ln=1)
        
        pdf.set_y(current_y + 25)  # Move past the incident box

        # ========== SECTION 5: EVIDENCE IMAGES ==========
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, "EVIDENCE", ln=1, align="L")
        
        # Get current Y position for consistent layout
        current_y = pdf.get_y()
        
        # Add evidence images if available
        if evidence_image_path and os.path.exists(evidence_image_path):
            try:
                pdf.set_draw_color(200, 200, 200)
                pdf.rect(10, current_y, 90, 60)
                pdf.image(evidence_image_path, x=12, y=current_y + 2, w=86, h=56)
                pdf.set_font("Arial", "", 8)
                pdf.text(12, current_y + 65, "Original Image")
            except Exception:
                pdf.set_fill_color(240, 240, 240)
                pdf.rect(10, current_y, 90, 60, "F")
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.set_xy(12, current_y + 25)
                pdf.cell(86, 20, "Image not available", align="C")
                pdf.set_text_color(0, 0, 0)
        
        if annotated_image_path and os.path.exists(annotated_image_path):
            try:
                pdf.set_draw_color(200, 200, 200)
                pdf.rect(110, current_y, 90, 60)
                pdf.image(annotated_image_path, x=112, y=current_y + 2, w=86, h=56)
                pdf.set_font("Arial", "", 8)
                pdf.text(112, current_y + 65, "Annotated Evidence")
            except Exception:
                pdf.set_fill_color(240, 240, 240)
                pdf.rect(110, current_y, 90, 60, "F")
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.set_xy(112, current_y + 25)
                pdf.cell(86, 20, "Image not available", align="C")
                pdf.set_text_color(0, 0, 0)
        
        pdf.set_y(current_y + 70)  # Move past the evidence section

        # ========== SECTION 6: PAYMENT INFORMATION ==========
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, "PAYMENT INFORMATION", ln=1, align="L")
        
        # Get current Y position for consistent layout
        current_y = pdf.get_y()
        pdf.set_fill_color(255, 245, 230)
        pdf.rect(10, current_y, 190, 25, "F")
        
        pdf.set_xy(12, current_y + 3)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(220, 53, 69)
        pdf.cell(95, 8, f"Fine Amount: INR {fine_amount}", ln=0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"Due Date: {due_date} by {due_time}", ln=1)
        
        pdf.set_xy(12, current_y + 13)
        pdf.set_font("Arial", "", 9)
        pdf.cell(95, 5, "Payment Methods: Online, UPI, Bank Transfer", ln=0)
        pdf.cell(95, 5, "Late Fee: INR 100 after due date", ln=1)
        
        # Add QR code placeholder
        self._add_qr_placeholder(pdf, 170, current_y)
        
        pdf.set_y(current_y + 30)  # Move past the payment section

        # ========== SECTION 7: LEGAL DISCLAIMER ==========
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "LEGAL DISCLAIMER & RIGHTS", ln=1, align="L")
        
        pdf.set_font("Arial", "", 8)
        pdf.set_text_color(80, 80, 80)
        disclaimer_text = (
            "This citation is electronically generated and has the same legal validity as a manually issued citation. "
            "You have the right to contest this citation within 15 days by appearing at the Traffic Tribunal Office. "
            "Failure to pay or contest may result in additional penalties and legal action. "
            "For queries, contact the Traffic Enforcement Authority."
        )
        pdf.multi_cell(0, 4, disclaimer_text)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

        # ========== SECTION 8: CONTACT INFORMATION ==========
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "CONTACT INFORMATION", ln=1, align="L")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 4, f"Address: {self.authority['address']}", ln=1)
        pdf.cell(0, 4, f"Phone: {self.authority['phone']}", ln=1)
        pdf.cell(0, 4, f"Email: {self.authority['email']}", ln=1)
        pdf.cell(0, 4, f"Website: {self.authority['website']}", ln=1)
        pdf.ln(4)

        # ========== SECTION 9: OFFICIAL SIGNATURE & SEAL ==========
        pdf.set_font("Arial", "B", 10)
        pdf.cell(120, 6, "", ln=0)
        pdf.cell(0, 6, "AUTHORISED SIGNATURE", ln=1)
        
        pdf.set_font("Arial", "I", 8)
        pdf.cell(120, 4, "", ln=0)
        pdf.cell(0, 4, "Traffic Enforcement Officer", ln=1)
        
        # Get current Y position for seal placement
        current_y = pdf.get_y()
        # Add official seal
        self._add_official_seal(pdf, 175, current_y - 5)
        
        pdf.ln(3)
        pdf.set_font("Arial", "", 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 4, "This document is computer-generated and requires no physical signature.", ln=1, align="C")
        pdf.set_text_color(0, 0, 0)

        # Generate output filename
        output_filename = f"E-Challan_{plate}_{challan_id.split('/')[-1]}.pdf"
        pdf.output(output_filename)
        
        return output_filename


def generate_challan_for_violation(
    violation_data: dict[str, Any],
    evidence_image_path: str = None,
    annotated_image_path: str = None,
    camera_id: str = None,
) -> str:
    """
    Convenience function to generate E-Challan for a violation.
    
    Args:
        violation_data: Dictionary containing violation details from the pipeline
        evidence_image_path: Path to original evidence image
        annotated_image_path: Path to annotated evidence image  
        camera_id: Camera identifier for location info
        
    Returns:
        Path to generated PDF file
    """
    generator = EChallanGenerator()
    return generator.generate_challan(
        violation_data=violation_data,
        evidence_image_path=evidence_image_path,
        annotated_image_path=annotated_image_path,
        camera_id=camera_id,
    )