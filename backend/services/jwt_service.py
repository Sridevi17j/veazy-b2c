# services/jwt_service.py
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class JWTService:
    def __init__(self):
        self.secret = os.getenv('JWT_SECRET')
        self.algorithm = 'HS256'
        self.expiry_days = 7  # Token valid for 7 days
        
        if not self.secret:
            raise ValueError("JWT_SECRET not found in environment variables")
    
    def generate_token(self, user_id: str, phone_number: str) -> str:
        """Generate JWT token for authenticated user"""
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'phone_number': phone_number,
            'iat': now,
            'exp': now + timedelta(days=self.expiry_days),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return {
                'success': True,
                'data': payload
            }
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid token'
            }
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """Extract user_id from token"""
        result = self.verify_token(token)
        if result['success']:
            return result['data'].get('user_id')
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising exception"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            exp = datetime.fromtimestamp(payload['exp'])
            return datetime.utcnow() > exp
        except:
            return True

# Create a singleton instance
jwt_service = JWTService()