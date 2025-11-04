#!/usr/bin/env python3
"""
Script to create a Twilio Verify service and get the Service SID
"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def create_verify_service():
    """Create a new Twilio Verify service"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not all([account_sid, auth_token]):
        print("❌ Error: Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in .env file")
        return

    try:
        client = Client(account_sid, auth_token)

        print("\n🔄 Creating Twilio Verify Service...\n")

        # Create the verify service
        service = client.verify.v2.services.create(
            friendly_name="Veazy OTP Verification"
        )

        print("✅ Successfully created Twilio Verify service!")
        print(f"\n📝 Service Details:")
        print(f"   Name:        {service.friendly_name}")
        print(f"   Service SID: {service.sid}")
        print(f"   Created:     {service.date_created}")

        print(f"\n💡 Add this to your backend/.env file:")
        print(f"   TWILIO_VERIFY_SERVICE_SID={service.sid}")

        print(f"\n✨ Your Verify Service SID is: {service.sid}\n")

    except Exception as e:
        print(f"❌ Error creating Verify service: {e}")
        print("\n💡 Possible reasons:")
        print("   - Invalid Twilio credentials")
        print("   - Insufficient permissions")
        print("   - Network connection issue")

if __name__ == "__main__":
    create_verify_service()
