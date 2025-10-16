# api/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

from database.models.user import User
from services.twilio_service import twilio_service
from services.jwt_service import jwt_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)

# Request/Response Models
class SendOTPRequest(BaseModel):
    country_code: str = Field(..., description="Country code with + prefix", example="+91")
    local_phone: str = Field(..., description="Local phone number without country code", example="9884841894")

class VerifyOTPRequest(BaseModel):
    country_code: str = Field(..., description="Country code with + prefix", example="+91")
    local_phone: str = Field(..., description="Local phone number without country code", example="9884841894")
    otp_code: str = Field(..., description="6-digit OTP code", example="123456")

class CompleteRegistrationRequest(BaseModel):
    country_code: str = Field(..., description="Country code with + prefix", example="+91")
    local_phone: str = Field(..., description="Local phone number without country code", example="9884841894")
    otp_code: str = Field(..., description="6-digit OTP code", example="123456")
    first_name: str = Field(..., description="User's first name", example="Amit")
    last_name: str = Field(..., description="User's last name", example="Singh")
    email: str = Field(..., description="User's email address", example="amit@example.com")
    preferred_name: Optional[str] = Field(None, description="User's preferred name/nickname", example="Amit")

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    phone_number: Optional[str] = None

class CountryCodeResponse(BaseModel):
    code: str
    name: str
    flag: str

# Rate limiting helper
async def check_rate_limit(phone_number: str) -> bool:
    """Check if user can request OTP (rate limiting)"""
    user = await User.find_one(User.phone == phone_number)
    if not user:
        return True
    
    # Allow new OTP request after 1 minute
    if user.updated_at:
        time_diff = datetime.utcnow() - user.updated_at
        return time_diff.total_seconds() > 60
    
    return True

# Dependency for authenticated routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = jwt_service.verify_token(credentials.credentials)
    if not result['success']:
        raise HTTPException(status_code=401, detail=result['error'])
    
    user_id = result['data']['user_id']
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.get("/countries", response_model=list[CountryCodeResponse])
async def get_supported_countries():
    """Get list of supported countries with their codes"""
    return twilio_service.get_supported_countries()

@router.post("/send-otp", response_model=AuthResponse)
async def send_otp(request: SendOTPRequest):
    """Send OTP to user's phone number"""
    try:
        # Validate input
        if not twilio_service.validate_local_phone(request.local_phone, request.country_code):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid phone number format for country code {request.country_code}"
            )
        
        # Combine phone number
        full_phone = twilio_service.combine_phone_number(request.country_code, request.local_phone)
        
        # Check rate limiting
        if not await check_rate_limit(full_phone):
            raise HTTPException(
                status_code=429, 
                detail="Please wait 1 minute before requesting another OTP"
            )
        
        # Find or create user (but don't store OTP code - Twilio Verify handles it)
        user = await User.find_one(User.phone == full_phone)
        if not user:
            user = User(
                phone=full_phone,
                otp_attempts=0
            )
        else:
            user.otp_attempts = 0
            user.updated_at = datetime.utcnow()
        
        await user.save()
        
        # Send OTP via Twilio Verify (no need to generate OTP ourselves)
        sms_result = twilio_service.send_otp(full_phone)
        
        if not sms_result['success']:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send OTP: {sms_result['error']}"
            )
        
        return AuthResponse(
            success=True,
            message=f"OTP sent to {request.country_code} {request.local_phone}",
            phone_number=full_phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, response: Response):
    """Verify OTP and authenticate user"""
    try:
        # Combine phone number
        full_phone = twilio_service.combine_phone_number(request.country_code, request.local_phone)
        
        # Find user
        user = await User.find_one(User.phone == full_phone)
        if not user:
            raise HTTPException(status_code=400, detail="No verification request found for this phone number")
        
        # Check attempts
        max_attempts = int(os.getenv('OTP_MAX_ATTEMPTS', 3))
        if user.otp_attempts >= max_attempts:
            raise HTTPException(status_code=400, detail="Maximum OTP attempts exceeded")
        
        # Verify OTP using Twilio Verify
        verify_result = twilio_service.verify_otp(full_phone, request.otp_code)
        
        if not verify_result['success']:
            user.otp_attempts += 1
            await user.save()
            
            error_message = "Invalid OTP code"
            if 'error' in verify_result:
                error_message = str(verify_result['error'])
            
            raise HTTPException(
                status_code=400, 
                detail=f"{error_message}. {max_attempts - user.otp_attempts} attempts remaining"
            )
        
        # OTP is valid - mark user as verified
        user.otp_attempts = 0
        user.verified_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Generate JWT token
        token = jwt_service.generate_token(str(user.id), user.phone)
        user.session_token = token
        
        await user.save()
        
        # Set httpOnly cookie
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return AuthResponse(
            success=True,
            message="OTP verified successfully",
            user_id=str(user.id),
            phone_number=user.phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/session", response_model=AuthResponse)
async def check_session(current_user: User = Depends(get_current_user)):
    """Check if user has valid session"""
    return AuthResponse(
        success=True,
        message="Valid session",
        user_id=str(current_user.id),
        phone_number=current_user.phone
    )

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    """Logout user by clearing session"""
    # Clear session token in database
    current_user.session_token = None
    await current_user.save()
    
    # Clear cookie
    response.delete_cookie("auth_token")
    
    return {"success": True, "message": "Logged out successfully"}

@router.post("/complete-registration", response_model=AuthResponse)
async def complete_registration(request: CompleteRegistrationRequest, response: Response):
    """Complete user registration with phone verification and profile information"""
    try:
        # Validate input
        if not request.country_code.startswith('+'):
            raise HTTPException(status_code=400, detail="Country code must start with +")
        
        if not request.otp_code or len(request.otp_code) != 6:
            raise HTTPException(status_code=400, detail="OTP must be 6 digits")
        
        if not request.first_name.strip() or not request.last_name.strip():
            raise HTTPException(status_code=400, detail="First name and last name are required")
        
        if not request.email.strip():
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Format phone number
        full_phone = twilio_service.combine_phone_number(request.country_code, request.local_phone)
        
        # Verify OTP with Twilio
        verify_result = twilio_service.verify_otp(full_phone, request.otp_code)
        
        if not verify_result['success']:
            raise HTTPException(
                status_code=400, 
                detail=f"OTP verification failed: {verify_result['error']}"
            )
        
        # Check if user already exists
        existing_user = await User.find_one(User.phone == full_phone)
        if existing_user and existing_user.verified_at:
            raise HTTPException(
                status_code=400, 
                detail="User already registered with this phone number"
            )
        
        # Check if email is already taken
        email_user = await User.find_one(User.email == request.email.lower().strip())
        if email_user and email_user.verified_at:
            raise HTTPException(
                status_code=400, 
                detail="Email address is already registered"
            )
        
        # Create or update user with complete profile
        if existing_user:
            user = existing_user
        else:
            user = User()
        
        # Set all user fields
        user.phone = full_phone
        user.first_name = request.first_name.strip()
        user.last_name = request.last_name.strip()
        user.email = request.email.lower().strip()
        user.preferred_name = request.preferred_name.strip() if request.preferred_name else None
        
        # Mark as verified
        user.verified_at = datetime.utcnow()
        user.otp_attempts = 0
        user.updated_at = datetime.utcnow()
        
        # Generate JWT token
        token = jwt_service.generate_token(str(user.id), user.phone)
        user.session_token = token
        
        # Save user to database
        await user.save()
        
        # Set httpOnly cookie
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return AuthResponse(
            success=True,
            message=f"Registration completed successfully! Welcome, {user.first_name}!",
            user_id=str(user.id),
            phone_number=user.phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")