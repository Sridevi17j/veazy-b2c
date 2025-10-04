# models/form_template.py
from pydantic import BaseModel
from typing import List, Optional

class FormFieldTemplate(BaseModel):
    field: str
    type: str  # "text", "date", "select", "number"
    required: bool = True
    validation: Optional[str] = None

class FormTemplate(BaseModel):
    country_code: str
    visa_type: str
    visa_code: str
    form_fields: List[FormFieldTemplate]
    version: str = "1.0"
