from sqlalchemy import Column,Integer,String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
Base = declarative_base()

class TranslationRequest(Base):
    __tablename__ = "translation_requests"
    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    __table_args__ = (
        UniqueConstraint('original_text', 'source_lang', 'target_lang', name='uix_translation_request'),
    )

class LanguageTranslationBase:
    """Base class for language-specific translation tables"""
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("translation_requests.id", ondelete="CASCADE"), nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Use declared_attr for the relationship
    @declared_attr
    def request(cls):
        return relationship("TranslationRequest")

def create_tables(engine):
    Base.metadata.create_all(bind=engine)

