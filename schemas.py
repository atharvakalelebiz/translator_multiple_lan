from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text : str
    source_lang : str
    target_lang : str

class TranslationResponse(BaseModel):
    original_text : str
    translated_text : str  # Changed to match your model
    
    class Config:
        from_attributes = True  # Add this to work with SQLAlchemy

