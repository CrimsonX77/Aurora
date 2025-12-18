"""
Aurora Archive - Fake Payment Module
Simulates payment processing for tier upgrades/downgrades

Python 3.10+
Dependencies: PyQt6
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QMessageBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/payment_module.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaymentDialog(QDialog):
    """
    Fake payment processing dialog
    Simulates credit/debit card payments for tier upgrades
    """
    
    payment_successful = pyqtSignal(dict)  # Emits payment details on success
    
    # Tier pricing
    TIER_PRICES = {
        "Kids": 5.00,
        "Standard": 10.00,
        "Premium": 15.00
    }
    
    def __init__(self, member_data: Dict, target_tier: str, parent=None):
        super().__init__(parent)
        self.member_data = member_data
        self.target_tier = target_tier
        self.current_tier = member_data.get('subscription', {}).get('tier', 'Standard')
        
        self.setup_ui()
        
        logger.info(f"Payment dialog opened: {self.current_tier} -> {self.target_tier}")
    
    def setup_ui(self):
        self.setWindowTitle("Aurora Archive - Payment Processing")
        self.setFixedSize(500, 600)
        
        # Dark theme matching Archive Sanctum
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #dc2626;
            }
            QLabel {
                color: #fca5a5;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                background-color: rgba(220, 38, 38, 0.1);
                border: 2px solid #7f1d1d;
                border-radius: 6px;
                padding: 8px;
                color: #fca5a5;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #dc2626;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7f1d1d, stop:1 #991b1b);
                color: white;
                border: 2px solid #dc2626;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #991b1b, stop:1 #b91c1c);
                border: 2px solid #ef4444;
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 0.3);
                color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(220, 38, 38, 0.3);
            }
            QFrame {
                border: 2px solid #7f1d1d;
                border-radius: 8px;
                background-color: rgba(127, 29, 29, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Payment summary
        summary = self.create_summary()
        layout.addWidget(summary)
        
        # Payment form
        form = self.create_payment_form()
        layout.addWidget(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.pay_btn = QPushButton(f"💳 Process Payment - ${self.calculate_amount():.2f}")
        self.pay_btn.clicked.connect(self.process_payment)
        button_layout.addWidget(self.pay_btn)
        
        layout.addLayout(button_layout)
    
    def create_header(self):
        """Create header section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("🏛️ Tier Upgrade Payment")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #dc2626;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Simulated Payment Processing")
        subtitle.setStyleSheet("font-size: 14px; color: #fbbf24; font-style: italic;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        return frame
    
    def create_summary(self):
        """Create payment summary"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        summary_title = QLabel("📋 Payment Summary")
        summary_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #dc2626;")
        layout.addWidget(summary_title)
        
        # Member info
        member_name = self.member_data.get('member_profile', {}).get('name', 'Unknown')
        member_label = QLabel(f"Member: {member_name}")
        layout.addWidget(member_label)
        
        # Tier change
        tier_label = QLabel(f"Upgrade: {self.current_tier} → {self.target_tier}")
        tier_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #fbbf24;")
        layout.addWidget(tier_label)
        
        # Price
        price = self.TIER_PRICES.get(self.target_tier, 10.00)
        price_label = QLabel(f"Monthly Price: ${price:.2f}")
        layout.addWidget(price_label)
        
        # Prorated amount
        amount = self.calculate_amount()
        amount_label = QLabel(f"Amount Due Today: ${amount:.2f}")
        amount_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        layout.addWidget(amount_label)
        
        # Note
        note = QLabel("Note: Upgrade takes effect immediately. Downgrade after 1 month.")
        note.setStyleSheet("font-size: 11px; color: #9ca3af; font-style: italic;")
        layout.addWidget(note)
        
        return frame
    
    def create_payment_form(self):
        """Create payment form"""
        frame = QFrame()
        layout = QGridLayout(frame)
        layout.setSpacing(15)
        
        row = 0
        
        # Payment type
        layout.addWidget(QLabel("Payment Method:"), row, 0)
        self.payment_type = QComboBox()
        self.payment_type.addItems(["Credit Card", "Debit Card", "Bank Transfer"])
        layout.addWidget(self.payment_type, row, 1)
        row += 1
        
        # Card number
        layout.addWidget(QLabel("Card Number:"), row, 0)
        self.card_number = QLineEdit()
        self.card_number.setPlaceholderText("4532-1111-2222-3333")
        self.card_number.setMaxLength(19)
        layout.addWidget(self.card_number, row, 1)
        row += 1
        
        # Card name
        layout.addWidget(QLabel("Cardholder Name:"), row, 0)
        self.card_name = QLineEdit()
        self.card_name.setPlaceholderText("John Doe")
        layout.addWidget(self.card_name, row, 1)
        row += 1
        
        # Expiry
        layout.addWidget(QLabel("Expiry Date:"), row, 0)
        self.card_expiry = QLineEdit()
        self.card_expiry.setPlaceholderText("MM/YY")
        self.card_expiry.setMaxLength(5)
        layout.addWidget(self.card_expiry, row, 1)
        row += 1
        
        # CVV
        layout.addWidget(QLabel("CVV:"), row, 0)
        self.card_cvv = QLineEdit()
        self.card_cvv.setPlaceholderText("123")
        self.card_cvv.setMaxLength(4)
        self.card_cvv.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.card_cvv, row, 1)
        row += 1
        
        # Security notice
        security_label = QLabel("🔒 This is a simulated payment. No real charges will be made.")
        security_label.setStyleSheet("font-size: 11px; color: #10b981; font-style: italic;")
        security_label.setWordWrap(True)
        layout.addWidget(security_label, row, 0, 1, 2)
        
        return frame
    
    def calculate_amount(self) -> float:
        """Calculate prorated upgrade amount"""
        # For simulation, just return the tier price
        # In production, would calculate prorated amount based on billing cycle
        return self.TIER_PRICES.get(self.target_tier, 10.00)
    
    def process_payment(self):
        """Process the fake payment"""
        try:
            # Validate inputs
            if not self.card_number.text():
                QMessageBox.warning(self, "Validation Error", "Please enter card number")
                return
            
            if not self.card_name.text():
                QMessageBox.warning(self, "Validation Error", "Please enter cardholder name")
                return
            
            if not self.card_expiry.text():
                QMessageBox.warning(self, "Validation Error", "Please enter expiry date")
                return
            
            if not self.card_cvv.text():
                QMessageBox.warning(self, "Validation Error", "Please enter CVV")
                return
            
            # Simulate processing
            payment_details = {
                "success": True,
                "transaction_id": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": self.calculate_amount(),
                "payment_type": self.payment_type.currentText(),
                "card_last_four": self.card_number.text()[-4:] if len(self.card_number.text()) >= 4 else "****",
                "timestamp": datetime.now().isoformat(),
                "member_id": self.member_data.get('member_id'),
                "tier_change": f"{self.current_tier} -> {self.target_tier}",
                "downgrade_date": (datetime.now() + timedelta(days=30)).isoformat(),  # Auto-downgrade after 1 month
                "new_tier": self.target_tier
            }
            
            logger.info(f"Payment processed: {payment_details['transaction_id']}")
            
            # Show success message
            QMessageBox.information(
                self,
                "Payment Successful",
                f"✅ Payment of ${payment_details['amount']:.2f} processed successfully!\n\n"
                f"Transaction ID: {payment_details['transaction_id']}\n"
                f"New Tier: {self.target_tier}\n\n"
                f"Your account has been upgraded."
            )
            
            # Emit signal and close
            self.payment_successful.emit(payment_details)
            self.accept()
            
        except Exception as e:
            logger.error(f"Payment processing error: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Payment Failed",
                f"❌ Payment processing failed:\n{str(e)}\n\nPlease try again."
            )


# Convenience function
def process_tier_upgrade(member_data: Dict, target_tier: str, parent=None) -> Optional[Dict]:
    """
    Show payment dialog and process tier upgrade
    
    Returns:
        Payment details if successful, None if cancelled
    """
    dialog = PaymentDialog(member_data, target_tier, parent)
    
    payment_result = None
    
    def on_payment_success(details):
        nonlocal payment_result
        payment_result = details
    
    dialog.payment_successful.connect(on_payment_success)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return payment_result
    
    return None


# Test
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test data
    test_member = {
        "member_id": "m_test123",
        "member_profile": {
            "name": "Test User"
        },
        "subscription": {
            "tier": "Standard"
        }
    }
    
    result = process_tier_upgrade(test_member, "Premium")
    
    if result:
        print("Payment successful!")
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Amount: ${result['amount']:.2f}")
    else:
        print("Payment cancelled")
