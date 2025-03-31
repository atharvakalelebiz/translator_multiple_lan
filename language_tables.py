from models import Base, LanguageTranslationBase
from database import engine
from sqlalchemy import inspect

def create_language_table(target_lang):
    table_name = f"{target_lang.lower()}_translations"
    
    # Create a new class for this language
    class_name = f"{target_lang.capitalize()}Translation"
    translation_class = type(
        class_name,
        (Base, LanguageTranslationBase),
        {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True}
        }
    )
    
    # Create the actual table in the database if it doesn't exist
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        translation_class.__table__.create(bind=engine)
    
    return translation_class