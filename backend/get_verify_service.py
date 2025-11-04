#!/usr/bin/env python3
"""
Script to list all Twilio Verify services and their SIDs
"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def list_verify_services():
    """List all Twilio Verify services"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not all([account_sid, auth_token]):
        print("❌ Error: Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in .env file")
        return

    try:
        client = Client(account_sid, auth_token)

        print("\n📋 Fetching Twilio Verify Services...\n")

        services = client.verify.v2.services.list()

        if not services:
            print("⚠️  No Verify services found in your account")
            print("\n💡 You can create one by running your backend or using:")
            print("   python -c \"from services.twilio_service import twilio_service\"")
            return

        print(f"✅ Found {len(services)} Verify service(s):\n")

        for i, service in enumerate(services, 1):
            print(f"{i}. Service Name: {service.friendly_name}")
            print(f"   Service SID:  {service.sid}")
            print(f"   Status:       {service.status if hasattr(service, 'status') else 'N/A'}")
            print(f"   Created:      {service.date_created}")
            print()

        # Recommend the first one for .env
        if len(services) > 0:
            print("💡 Add this to your .env file:")
            print(f"   TWILIO_VERIFY_SERVICE_SID={services[0].sid}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_verify_services()
