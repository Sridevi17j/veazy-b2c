# Workflow Tools Dynamic Analysis

**Created:** 2025-01-04
**Purpose:** Document what is currently dynamic vs hardcoded in workflow tools, and what needs to change for 100% dynamic workflow execution.

---

## Current Architecture

**Single Agent System:**
- One main Visa Assistant Agent (React Agent)
- Multiple tools organized into:
  - Simple tools (greetings, general_enquiry, base_info_collector, database_visa_lookup)
  - Wrapper tools (start_detailed_application_process, workflow_executor_tool)
  - Workflow tools (in `intelligent_workflow_agent.py`)

**Workflow Tools:**
1. `initialize_workflow_session` - Creates workflow session
2. `load_workflow_dynamically` - Loads JSON workflow
3. `execute_current_stage` - Gets stage requirements
4. `collect_data_item` - Collects user data
5. `process_document_extraction` - Processes extracted docs
6. `validate_stage_completion` - Checks if stage done
7. `advance_to_next_stage` - Moves to next stage
8. `generate_automation_js_file` - Generates final JS
9. `get_workflow_status` - Returns current status

---

## ✅ What IS Fully Dynamic

### 1. Stage Sequence & Progression

```python
# In execute_current_stage, advance_to_next_stage
stages = workflow_json.get("collection_sequence", [])
current_stage = stages[session["current_stage_index"]]
```

**Works for:**
- Vietnam has 5 stages → Tools work with 5 stages
- Thailand has 8 stages → Tools work with 8 stages
- Stage order follows JSON exactly

### 2. Stage Titles & Descriptions

```python
stage_title = current_stage.get("stage_title", "")
stage_description = current_stage.get("description", "")
```

**Works for:**
- Reads titles directly from JSON
- No hardcoding of stage names
- Different countries can have different stage names

### 3. Field Collection

```python
# In collect_data_item
fields = current_stage.get("fields", {})
for field_name, field_config in fields.items():
    # Collects ANY field defined in JSON
```

**Works for:**
- If JSON says collect "mother_maiden_name", tool collects it
- If JSON says collect "pet_name", tool collects it
- Completely dynamic field names
- No limit on number of fields

### 4. Required vs Optional Fields

```python
if field_config.get("required", True):
    # Mark as required
```

**Works for:**
- Reads from JSON whether field is required
- Validation based on JSON rules
- Can mix required and optional fields

---

## ⚠️ What Needs Specific JSON Structure

The tools expect the JSON to have this structure:

```json
{
  "collection_sequence": [
    {
      "stage": "stage_1_documents",
      "stage_title": "Document Upload",
      "description": "Upload required documents",
      "required_documents": [
        {
          "name": "passport_bio_page",
          "description": "Passport bio page",
          "extracts": ["passport_number", "surname", "given_name"]
        }
      ],
      "fields": {
        "email": {
          "field_type": "email",
          "required": true,
          "validation": "email_format"
        }
      }
    }
  ]
}
```

**Required Keys:**
- `collection_sequence` → Tools look for this key
- `stage`, `stage_title` → Tools read these
- `required_documents`, `fields` → Tools distinguish document vs data stages

**If you change these structure keys, you MUST update the tools.**

---

## ❌ What Is NOT Fully Dynamic (Needs Code Changes)

### 1. Document Type Extraction Logic

**Location:** `document_processing_tool` and `process_document_extraction`

**Current Implementation:**
```python
# Currently hardcoded document types
if doc_type in ["passport_bio_page", "passport"]:
    extracted_data = await _extract_passport_with_gpt4_vision(file_path)
    # Knows to extract: passport_number, surname, given_name, etc.

elif doc_type in ["passport_photo", "photo"]:
    # Validates photo format
```

**Issue:**
If you add a NEW document type like `"birth_certificate"` in JSON, the tool doesn't know how to extract it.

**Solution Needed:**
Make extraction prompt-based and driven by JSON:

```python
# Dynamic extraction based on JSON definition
document_definition = stage_config["required_documents"].find(d => d["name"] == doc_type)
extraction_fields = document_definition.get("extracts", [])
extraction_instructions = document_definition.get("extraction_instructions", "")

# Tell GPT-4 Vision what to extract
prompt = f"""
Extract the following fields from this document:
{', '.join(extraction_fields)}

Additional instructions: {extraction_instructions}

Return as JSON.
"""

extracted_data = await _extract_with_gpt4_vision(file_path, prompt)
```

**JSON Structure Needed:**
```json
{
  "required_documents": [
    {
      "name": "birth_certificate",
      "description": "Official birth certificate",
      "document_type": "pdf",
      "extracts": ["full_name", "date_of_birth", "place_of_birth", "parents_names"],
      "extraction_instructions": "Look for official stamps and registration numbers",
      "validation_rules": {
        "must_contain_text": ["birth", "certificate"],
        "must_have_stamp": true
      }
    }
  ]
}
```

---

### 2. JS File Generation Logic

**Location:** `generate_automation_js_file`

**Current Implementation:**
```python
# Might have hardcoded mappings like:
js_code += f'document.querySelector("#passport").value = "{passport_number}";'
js_code += f'document.querySelector("#fullName").value = "{full_name}";'
```

**Issue:**
Different country websites have different selectors. The tool needs to know how to map collected data to website form fields.

**Solution Needed:**
Include target website mapping in JSON:

```json
{
  "automation_config": {
    "target_url": "https://evisa.xuatnhapcanh.gov.vn",
    "form_type": "multi_step",
    "steps": [
      {
        "step_number": 1,
        "url_path": "/step1",
        "field_mappings": {
          "passport_number": {
            "selector": "#passportNumber",
            "input_type": "text",
            "wait_for_element": true
          },
          "full_name": {
            "selector": "#fullName",
            "input_type": "text"
          },
          "date_of_birth": {
            "selector": "#dob",
            "input_type": "date",
            "format": "DD/MM/YYYY"
          }
        },
        "submit_button": {
          "selector": "#btnNext",
          "wait_after_click": 2000
        }
      }
    ]
  }
}
```

**Implementation:**
```python
# In generate_automation_js_file
automation_config = workflow_json.get("automation_config", {})
target_url = automation_config.get("target_url")
steps = automation_config.get("steps", [])

js_code = f"// Auto-generated for {target_url}\n"
js_code += f"window.location.href = '{target_url}';\n\n"

for step in steps:
    js_code += f"// Step {step['step_number']}\n"
    for field_name, field_config in step['field_mappings'].items():
        selector = field_config['selector']
        value = collected_data.get(field_name, '')

        if field_config.get('wait_for_element'):
            js_code += f"await waitForElement('{selector}');\n"

        js_code += f"document.querySelector('{selector}').value = '{value}';\n"

    submit_selector = step['submit_button']['selector']
    js_code += f"document.querySelector('{submit_selector}').click();\n"
```

---

### 3. Field Type Validation

**Location:** `collect_data_item`

**Current Implementation:**
```python
# Might need specific validation for field types
if field_type == "email":
    # Validate email format
elif field_type == "date":
    # Validate date format
elif field_type == "phone":
    # Validate phone format
```

**Issue:**
If JSON defines a new field type like `"iban"` (international bank account), tool doesn't know how to validate it.

**Solution Needed:**
Make validation configurable in JSON:

```json
{
  "fields": {
    "bank_account": {
      "field_type": "text",
      "required": true,
      "validation": {
        "type": "regex",
        "pattern": "^[A-Z]{2}[0-9]{2}[A-Z0-9]+$",
        "error_message": "Invalid IBAN format. Must start with 2 letters, 2 digits, followed by alphanumeric characters."
      }
    },
    "age": {
      "field_type": "number",
      "required": true,
      "validation": {
        "type": "range",
        "min": 18,
        "max": 100,
        "error_message": "Age must be between 18 and 100"
      }
    },
    "passport_expiry": {
      "field_type": "date",
      "required": true,
      "validation": {
        "type": "date_range",
        "min": "today",
        "min_offset_months": 6,
        "error_message": "Passport must be valid for at least 6 months"
      }
    }
  }
}
```

**Implementation:**
```python
# In collect_data_item
def validate_field(field_value, field_config):
    validation = field_config.get("validation", {})
    validation_type = validation.get("type")

    if validation_type == "regex":
        import re
        pattern = validation.get("pattern")
        if not re.match(pattern, field_value):
            return False, validation.get("error_message")

    elif validation_type == "range":
        value = float(field_value)
        min_val = validation.get("min")
        max_val = validation.get("max")
        if value < min_val or value > max_val:
            return False, validation.get("error_message")

    elif validation_type == "date_range":
        # Parse date and check range
        pass

    return True, None
```

---

## Example: Adding Thailand Workflow

### What Works Automatically:

**Vietnam JSON:**
```json
{
  "collection_sequence": [
    { "stage": "stage_1_documents", "stage_title": "Documents" },
    { "stage": "stage_2_personal_info", "stage_title": "Personal Information" },
    { "stage": "stage_3_travel_info", "stage_title": "Travel Information" }
  ]
}
```

**Thailand JSON:**
```json
{
  "collection_sequence": [
    { "stage": "stage_1_identity_verification", "stage_title": "Identity Verification" },
    { "stage": "stage_2_accommodation", "stage_title": "Accommodation Details" },
    { "stage": "stage_3_financial_proof", "stage_title": "Financial Proof" },
    { "stage": "stage_4_travel_insurance", "stage_title": "Travel Insurance" },
    { "stage": "stage_5_documents", "stage_title": "Supporting Documents" }
  ]
}
```

**✅ Works Automatically:**
- Tools automatically adapt to 5 stages instead of 3
- Different stage names work fine
- Different field names collected dynamically
- Stage progression follows Thai workflow order

### What Needs Code Changes:

**❌ Needs Updates:**
- If Thailand requires `"driving_license"` document (new type) → Update document extraction logic
- If Thailand website has different form selectors → Update JS generation with Thai website config
- If Thailand has unique validation rules (e.g., Thai ID card format) → Update validation logic

---

## Current State Summary Table

| Feature | Dynamic? | Notes |
|---------|----------|-------|
| Stage sequence | ✅ Yes | Reads from JSON, any number of stages |
| Stage titles | ✅ Yes | Reads from JSON, any stage names |
| Field names | ✅ Yes | Collects any field defined in JSON |
| Required/optional fields | ✅ Yes | Reads from JSON config |
| Field descriptions | ✅ Yes | Uses JSON descriptions |
| Document types | ⚠️ Partial | Known types (passport, photo) work. New types need code changes |
| Document extraction | ❌ No | Hardcoded per document type (passport extraction logic hardcoded) |
| Extraction fields | ⚠️ Partial | JSON defines what to extract, but extraction logic is hardcoded |
| JS generation | ❌ No | Website-specific code needed, selectors hardcoded |
| Field validation | ⚠️ Partial | Basic types (email, date) work. Custom validation needs code |
| Multi-traveler support | ✅ Yes | Can handle any number of travelers |
| Stage progression logic | ✅ Yes | Completely driven by JSON sequence |

---

## To Make It 100% Dynamic - Action Items

### Priority 1: Critical for Multi-Country Support

1. **JSON-Driven Document Extraction**
   - Location: `agent/tools/document_processing.py`
   - Change: Read extraction fields and instructions from JSON
   - Build GPT-4 Vision prompt dynamically from JSON config
   - No hardcoded document types

2. **JSON-Driven JS Generation**
   - Location: `agent/agents/intelligent_workflow_agent.py` → `generate_automation_js_file`
   - Change: Include `automation_config` section in workflow JSON
   - Define target URL, selectors, and field mappings in JSON
   - Generate JS code from template + JSON mappings

3. **JSON-Driven Validation Rules**
   - Location: `agent/agents/intelligent_workflow_agent.py` → `collect_data_item`
   - Change: Define validation rules in JSON (regex, range, custom)
   - Apply validations from JSON config dynamically
   - Support custom validation functions

### Priority 2: Enhanced Features

4. **Conditional Stage Logic**
   - Allow JSON to define conditional stages (if country X, show stage Y)
   - Support branching workflows based on user answers

5. **Multi-Language Support**
   - Add language field to JSON for stage titles and descriptions
   - Support multiple languages per workflow

6. **Advanced Document Validation**
   - OCR quality checks
   - Document authenticity verification
   - Expiry date validation

### Priority 3: Nice to Have

7. **Visual Workflow Editor**
   - UI to create/edit workflow JSON files
   - Drag-and-drop stage builder

8. **Workflow Version Control**
   - Track changes to workflow JSON files
   - Rollback to previous versions if needed

9. **A/B Testing Support**
   - Test different workflow variations
   - Analytics on completion rates per stage

---

## Implementation Checklist (Future Work)

When ready to make fully dynamic:

### Phase 1: Document Extraction (Week 1)
- [ ] Add `extraction_instructions` field to JSON document definitions
- [ ] Create generic `_extract_document_with_gpt4_vision()` function
- [ ] Build prompt dynamically from JSON config
- [ ] Test with passport, photo, birth certificate, bank statements
- [ ] Remove hardcoded document type checks

### Phase 2: Field Validation (Week 2)
- [ ] Add `validation` object to JSON field definitions
- [ ] Implement regex validation
- [ ] Implement range validation
- [ ] Implement date validation with offsets
- [ ] Implement custom validation functions
- [ ] Add clear error messages from JSON

### Phase 3: JS Generation (Week 3)
- [ ] Add `automation_config` section to workflow JSON
- [ ] Define field mappings for each country website
- [ ] Create JS generation template engine
- [ ] Test with Vietnam evisa website
- [ ] Test with Thailand evisa website
- [ ] Add support for multi-step forms
- [ ] Add support for file uploads in automation

### Phase 4: Testing (Week 4)
- [ ] Create test workflows for 3+ countries
- [ ] Test edge cases (missing fields, invalid data)
- [ ] Performance testing with large documents
- [ ] User acceptance testing
- [ ] Deploy to staging

---

## Notes

- Keep backward compatibility during migration
- Document any breaking changes to JSON structure
- Version the workflow JSON schema (v1, v2, etc.)
- Create migration scripts if JSON structure changes significantly

---

**Last Updated:** 2025-01-04
**Next Review:** When adding new country workflow
