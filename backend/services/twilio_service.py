# services/twilio_service.py
import os
import secrets
from typing import Optional, Dict, List
from twilio.rest import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.verify_service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')
        
        if not all([self.account_sid, self.auth_token]):
            raise ValueError("Missing Twilio credentials in environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
        
        # Create Verify service if not provided
        if not self.verify_service_sid:
            self.verify_service_sid = self.create_verify_service()
    
    def create_verify_service(self) -> str:
        """Create a Twilio Verify service"""
        try:
            service = self.client.verify.v2.services.create(
                friendly_name="Veazy OTP Verification"
            )
            print(f"✅ Created Twilio Verify service: {service.sid}")
            print(f"⚠️  Add this to your .env file: TWILIO_VERIFY_SERVICE_SID={service.sid}")
            return service.sid
        except Exception as e:
            print(f"❌ Error creating Verify service: {e}")
            raise
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code - Not needed with Verify API"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    def send_otp(self, phone_number: str, otp_code: str = None) -> dict:
        """Send OTP using Twilio Verify API"""
        try:
            # Use Twilio Verify to send OTP (ignores otp_code parameter)
            verification = self.client.verify.v2.services(self.verify_service_sid).verifications.create(
                to=phone_number,
                channel='sms'
            )
            
            return {
                'success': True,
                'verification_sid': verification.sid,
                'status': verification.status,
                'phone_number': phone_number,
                'channel': verification.channel
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def verify_otp(self, phone_number: str, otp_code: str) -> dict:
        """Verify OTP using Twilio Verify API"""
        try:
            verification_check = self.client.verify.v2.services(self.verify_service_sid).verification_checks.create(
                to=phone_number,
                code=otp_code
            )
            
            return {
                'success': verification_check.status == 'approved',
                'status': verification_check.status,
                'phone_number': phone_number
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'phone_number': phone_number
            }
    
    def validate_local_phone(self, local_phone: str, country_code: str) -> bool:
        """Validate local phone number based on country code"""
        # Remove all non-digit characters
        cleaned = ''.join(c for c in local_phone if c.isdigit())
        
        # Basic validation - most countries have 7-11 digit local numbers
        if len(cleaned) < 7 or len(cleaned) > 11:
            return False
        
        # Country-specific validation (add more as needed)
        country_rules = {
            '+1': {'min': 10, 'max': 10},    # US - exactly 10 digits
            '+91': {'min': 10, 'max': 10},   # India - exactly 10 digits
            '+31': {'min': 9, 'max': 9},     # Netherlands - exactly 9 digits
            '+44': {'min': 10, 'max': 10},   # UK - 10 digits (without leading 0)
        }
        
        if country_code in country_rules:
            rules = country_rules[country_code]
            return rules['min'] <= len(cleaned) <= rules['max']
        
        # Default validation for other countries
        return 7 <= len(cleaned) <= 11
    
    def combine_phone_number(self, country_code: str, local_phone: str) -> str:
        """Combine country code and local phone into international format"""
        # Clean the local phone number (remove all non-digits)
        cleaned_local = ''.join(c for c in local_phone if c.isdigit())
        
        # Ensure country code starts with +
        if not country_code.startswith('+'):
            country_code = '+' + country_code
        
        return country_code + cleaned_local
    
    def get_supported_countries(self) -> List[Dict[str, str]]:
        """Get list of supported countries with their codes"""
        return [
            {'id': 'in', 'code': '+91', 'name': 'India', 'flag': '🇮🇳'},
            {'id': 'us', 'code': '+1', 'name': 'United States', 'flag': '🇺🇸'},
            {'id': 'nl', 'code': '+31', 'name': 'Netherlands', 'flag': '🇳🇱'},
            {'id': 'gb', 'code': '+44', 'name': 'United Kingdom', 'flag': '🇬🇧'},
        ]

# Create a singleton instance
twilio_service = TwilioService()