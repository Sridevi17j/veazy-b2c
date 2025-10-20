# Veazy B2C Database Architecture Knowledge

## 📊 Database Design Overview

This document contains the complete database architecture discussion and design decisions for the Veazy travel visa application system.

## 🏗️ Core Problem Statement

**Challenge:** Users (account holders) often need to apply for visas for multiple travelers (family members, colleagues, etc.). The system needs to separate:
- **WHO logs in and pays** (Account Holder)
- **WHO actually travels** (Travelers)
- **WHAT documents belong to whom** (Document Management)

## 📋 Database Collections Architecture

### 1. Users Collection (Account Holders)
**Purpose:** People who create accounts, log in, and manage applications

```python
class User(Document):
    # Basic account information
    first_name: Optional[str] = None           # "Amit"
    last_name: Optional[str] = None            # "Singh"
    email: Optional[EmailStr] = None           # "amit@email.com"
    phone: Optional[str] = None                # "+91-9884841894"
    preferred_name: Optional[str] = None       # "Amit" (nickname)
    
    # Authentication fields
    otp_code: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    otp_attempts: int = 0
    verified_at: Optional[datetime] = None
    session_token: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        collection = "users"
```

**Sample Data:**
```json
{
  "_id": "676f1111111111111111111111",
  "first_name": "Amit",
  "last_name": "Singh",
  "phone": "+91-9884841894",
  "email": "amit@email.com",
  "verified_at": "2024-12-16T09:00:00Z"
}
```

### 2. Travelers Collection (People Who Travel)
**Purpose:** Actual people who will be traveling (can be different from account holder)

```python
class Traveler(Document):
    # Link to account holder
    account_id: PydanticObjectId              # Links to User._id
    
    # Traveler personal details
    first_name: str                           # "Priya"
    last_name: str                            # "Singh"
    date_of_birth: Optional[date] = None      # "1992-05-15"
    nationality: Optional[str] = None         # "Indian"
    passport_number: Optional[str] = None     # "Z3456789"
    passport_expiry: Optional[date] = None    # "2032-03-09"
    
    # Relationship context
    relation_to_account_holder: str           # "self|spouse|child|parent|friend|other"
    
    # Travel preferences
    dietary_preferences: Optional[str] = None
    medical_conditions: Optional[str] = None
    
    # Metadata
    created_at: datetime
    is_active: bool = True                    # For soft delete
    
    class Settings:
        collection = "travelers"
```

**Sample Data:**
```json
{
  "_id": "676f2222222222222222222222",
  "account_id": "676f1111111111111111111111",
  "first_name": "Priya",
  "last_name": "Singh",
  "date_of_birth": "1992-05-15",
  "nationality": "Indian",
  "passport_number": "Z3456789",
  "passport_expiry": "2032-03-09",
  "relation_to_account_holder": "spouse"
}
```

### 3. Visa Applications Collection
**Purpose:** Links account holders with travelers for specific visa applications

```python
class VisaApplication(Document):
    # Links
    account_id: PydanticObjectId              # WHO is managing/paying
    traveler_id: PydanticObjectId             # WHO is traveling
    
    # Application details
    destination_country: str                  # "Thailand"
    purpose: str                              # "Tourism"
    travel_dates: dict = {
        "departure": "2024-12-15",
        "return": "2024-12-25"
    }
    
    # Application status
    status: str                               # "draft|submitted|approved|rejected"
    application_data: dict = {}               # All form data
    
    # Agent conversation
    thread_id: Optional[str] = None           # ChatInterface thread
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        collection = "visa_applications"
```

**Sample Data:**
```json
{
  "_id": "676f3333333333333333333333",
  "account_id": "676f1111111111111111111111",
  "traveler_id": "676f2222222222222222222222",
  "destination_country": "Thailand",
  "purpose": "Tourism",
  "travel_dates": {
    "departure": "2024-12-15",
    "return": "2024-12-25"
  },
  "status": "documents_pending",
  "thread_id": "thread_abc123"
}
```

### 4. Document Types Collection (Reference Data)
**Purpose:** Define what types of documents are required and their validation rules

```python
class DocumentType(Document):
    code: str                                 # "passport|photo|bank_statement|employment_letter"
    name: str                                 # "Passport"
    description: str                          # "Valid passport with at least 6 months validity"
    
    # Requirements
    required_for_countries: List[str]         # ["thailand", "singapore", "uae"]
    required_for_purposes: List[str]          # ["tourism", "business", "transit"]
    file_formats: List[str]                   # ["pdf", "jpg", "png"]
    max_file_size_mb: int                     # 10
    
    # OCR extraction fields
    extractable_fields: List[str]             # ["passport_number", "expiry_date", "nationality"]
    
    class Settings:
        collection = "document_types"
```

### 5. Traveler Documents Collection (Uploaded Files)
**Purpose:** Store actual uploaded documents with OCR data and validation status

```python
class TravelerDocument(Document):
    # Links
    account_id: PydanticObjectId              # WHO uploaded (account holder)
    traveler_id: PydanticObjectId             # WHO it belongs to (traveler)
    application_id: Optional[PydanticObjectId] = None  # WHICH application
    document_type_code: str                   # WHAT type (passport/photo/etc)
    
    # File information
    original_filename: str                    # "priya_passport_scan.pdf"
    file_path: str                            # "/uploads/2024/12/16/priya_676f1234.pdf"
    file_size_bytes: int                      # 2048576
    file_format: str                          # "pdf"
    content_hash: str                         # "sha256hash" (duplicate detection)
    
    # Upload metadata
    uploaded_at: datetime
    uploaded_by_user_id: PydanticObjectId    # Could be different from account_id
    
    # Document validation
    validation_status: str                    # "pending|valid|invalid|expired"
    validation_errors: List[str]              # ["passport_expired", "poor_image_quality"]
    validation_date: Optional[datetime] = None
    
    # OCR extraction results
    extracted_data: Dict[str, Any] = {}       # {"passport_number": "Z3456789", "expiry_date": "2032-03-09"}
    extraction_confidence: Dict[str, float] = {}  # {"passport_number": 0.98, "expiry_date": 0.96}
    extraction_date: Optional[datetime] = None
    
    # Document verification (human review)
    is_verified: bool = False                 # Manual verification by admin
    verified_by: Optional[str] = None         # Admin user ID
    verified_at: Optional[datetime] = None
    
    # Lifecycle
    is_active: bool = True                    # For soft delete
    expires_at: Optional[datetime] = None     # Document expiry (e.g., passport expiry)
    
    class Settings:
        collection = "traveler_documents"
```

**Complete Sample Document Record:**
```json
{
  "_id": "676f1234567890abcdef1234",
  "account_id": "676f1111111111111111111111",
  "traveler_id": "676f2222222222222222222222",
  "application_id": "676f3333333333333333333333",
  "document_type_code": "passport",
  "original_filename": "priya_passport_scan.pdf",
  "file_path": "/uploads/2024/12/16/priya_676f1234567890abcdef1234.pdf",
  "file_size_bytes": 2048576,
  "file_format": "pdf",
  "content_hash": "sha256:abc123def456...",
  "uploaded_at": "2024-12-16T10:30:00Z",
  "uploaded_by_user_id": "676f1111111111111111111111",
  "validation_status": "valid",
  "validation_errors": [],
  "validation_date": "2024-12-16T10:35:00Z",
  "extracted_data": {
    "passport_number": "Z3456789",
    "given_names": "PRIYA",
    "surname": "SINGH",
    "nationality": "IND",
    "date_of_birth": "1992-05-15",
    "issue_date": "2022-03-10",
    "expiry_date": "2032-03-09",
    "place_of_birth": "MUMBAI",
    "gender": "F"
  },
  "extraction_confidence": {
    "passport_number": 0.98,
    "given_names": 0.95,
    "surname": 0.97,
    "nationality": 0.99,
    "date_of_birth": 0.92,
    "expiry_date": 0.96
  },
  "extraction_date": "2024-12-16T10:32:00Z",
  "is_verified": true,
  "verified_by": "admin_user_id_12345",
  "verified_at": "2024-12-16T11:00:00Z",
  "is_active": true,
  "expires_at": "2032-03-09T00:00:00Z"
}
```

## 📊 Data Relationships

### Complete Data Flow Example:
```
User (Amit - Account Holder)
├── Traveler 1 (Amit - Self)
│   ├── TravelerDocument 1 (Passport)
│   ├── TravelerDocument 2 (Photo)
│   └── TravelerDocument 3 (Bank Statement)
├── Traveler 2 (Priya - Spouse)
│   ├── TravelerDocument 4 (Passport)
│   ├── TravelerDocument 5 (Photo)
│   └── TravelerDocument 6 (Employment Letter)
├── Traveler 3 (Rohan - Child, 12 years)
│   ├── TravelerDocument 7 (Passport)
│   ├── TravelerDocument 8 (Photo)
│   └── TravelerDocument 9 (Birth Certificate)
└── VisaApplication (Thailand Tourism - Family Trip)
    ├── Links to: All 3 travelers
    └── Required Documents: All 9 documents above
```

## 🔄 Common Database Queries

### 1. Get All Travelers for an Account
```python
travelers = await Traveler.find(
    Traveler.account_id == user.id,
    Traveler.is_active == True
).to_list()
```

### 2. Get All Documents for a Traveler
```python
traveler_docs = await TravelerDocument.find(
    TravelerDocument.traveler_id == traveler.id,
    TravelerDocument.is_active == True
).to_list()
```

### 3. Check Missing Documents for Application
```python
# Get required document types for Thailand tourism
required_doc_types = ["passport", "photo", "bank_statement", "flight_booking"]

# Get uploaded document types for traveler
uploaded_docs = await TravelerDocument.find(
    TravelerDocument.traveler_id == traveler.id,
    TravelerDocument.application_id == application.id
).to_list()
uploaded_types = [doc.document_type_code for doc in uploaded_docs]

# Find missing documents
missing_types = set(required_doc_types) - set(uploaded_types)
```

### 4. Get Documents Needing Validation
```python
pending_docs = await TravelerDocument.find(
    TravelerDocument.validation_status == "pending"
).to_list()
```

### 5. Agent Context Query
```python
# Get complete context for agent
user = await User.get(user_id)
traveler = await Traveler.get(traveler_id)
application = await VisaApplication.get(application_id)
documents = await TravelerDocument.find(
    TravelerDocument.traveler_id == traveler.id,
    TravelerDocument.application_id == application.id
).to_list()

# Build agent context
context = {
    "account_holder": user.first_name,
    "traveler_name": traveler.first_name,
    "relation": traveler.relation_to_account_holder,
    "destination": application.destination_country,
    "purpose": application.purpose,
    "documents_uploaded": len(documents),
    "documents_validated": len([d for d in documents if d.validation_status == "valid"]),
    "missing_documents": missing_types
}
```

## 🎯 Agent Intelligence Benefits

With this database structure, the AI agent can provide highly contextual responses:

**Example Agent Response:**
```
"Hi Amit! I see you're applying for Thailand tourism visas for your family.

Progress Summary:
✅ Amit (Self): Passport ✓, Photo ✓, Bank Statement ✓
✅ Priya (Spouse): Passport ✓, Photo ✓, Employment Letter ✓
❌ Rohan (Child): Passport ✓, Photo ❌, Birth Certificate ❌

Next Steps:
1. Upload Rohan's passport-size photo
2. Upload Rohan's birth certificate (for child visa requirements)

Would you like me to guide you through the photo requirements for children?"
```

## 🔗 Key Design Principles

1. **Separation of Concerns:** Account management vs. Travel details vs. Document storage
2. **Flexibility:** One account can manage multiple travelers and applications
3. **Traceability:** Complete audit trail of who uploaded what, when
4. **Validation:** Multi-stage document validation (automated + manual)
5. **OCR Integration:** Automatic data extraction to reduce manual entry
6. **Agent Intelligence:** Rich context for AI-powered assistance
7. **Scalability:** Support for family applications, group travel, corporate accounts

## 📝 Migration Strategy

1. Keep existing `User` model for account holders
2. Create `Traveler` collection and add "self" travelers for existing users
3. Add `TravelerDocument` collection for document management
4. Update `VisaApplication` to link account holders with travelers
5. Migrate existing applications to new structure

This architecture provides a robust foundation for visa application management with full family/group support and intelligent document handling.