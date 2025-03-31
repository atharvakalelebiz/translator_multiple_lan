# crud.py
from sqlalchemy.orm import Session
from models import TranslationRequest
from language_tables import create_language_table

def create_translation_record(db: Session, original_text: str, translated_text: str, source_lang: str, target_lang: str):
    """
    Create or update a translation record in the database
    
    Args:
        db: Database session
        original_text: Text to be translated
        translated_text: Translated text
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        The created or updated translation record
    """
    # Step 1: Get or create the main translation request
    request = db.query(TranslationRequest).filter(
        TranslationRequest.original_text == original_text,
        TranslationRequest.source_lang == source_lang,
        TranslationRequest.target_lang == target_lang
    ).first()
    
    if not request:
        request = TranslationRequest(
            original_text=original_text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        db.add(request)
        db.commit()
        db.refresh(request)
    
    # Step 2: Create or update the language-specific translation
    LanguageTranslation = create_language_table(target_lang)
    
    translation = db.query(LanguageTranslation).filter(
        LanguageTranslation.request_id == request.id
    ).first()
    
    if not translation:
        translation = LanguageTranslation(
            request_id=request.id,
            translated_text=translated_text
        )
        db.add(translation)
    else:
        translation.translated_text = translated_text
    
    db.commit()
    db.refresh(translation)
    
    return translation


def get_translation_record(db: Session, original_text: str, source_lang: str, target_lang: str):
    """
    Retrieve a translation record if it exists
    
    Args:
        db: Database session
        original_text: Original text to find
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        The translation record if found, None otherwise
    """
    # Find the translation request
    request = db.query(TranslationRequest).filter(
        TranslationRequest.original_text == original_text,
        TranslationRequest.source_lang == source_lang,
        TranslationRequest.target_lang == target_lang
    ).first()
    
    if not request:
        return None
    
    # Get the appropriate language table and find the translation
    LanguageTranslation = create_language_table(target_lang)
    translation = db.query(LanguageTranslation).filter(
        LanguageTranslation.request_id == request.id
    ).first()
    
    return translation