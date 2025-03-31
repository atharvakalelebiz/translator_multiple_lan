# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from openai import OpenAI
import os
from dotenv import load_dotenv
from database import get_db, engine
from schemas import TranslationRequest, TranslationResponse
import models
import crud
from language_tables import create_language_table

# Create all basic tables
models.create_tables(engine)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
   api_key=os.getenv("OPENAI_API_KEY"),
   base_url="https://beta.sree.shop/v1",
)

# Create FastAPI application
app = FastAPI(
   title="Multilingual Translation API",
   description="API for translating text between multiple languages with language-specific database storage",
   version="1.0.0"
)

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest, db: Session = Depends(get_db)):
   """
   Translate text from one language to another.
   
   If a translation already exists in the database, it will be returned.
   Otherwise, a new translation will be generated and stored.
   """
   try:
       # Validate request parameters
       if not request.text:
           raise HTTPException(status_code=400, detail="Text cannot be empty")
       
       if not request.source_lang or not request.target_lang:
           raise HTTPException(status_code=400, detail="Source and target languages must be specified")
       
       # Check if we already have this translation
       existing = crud.get_translation_record(
           db=db, 
           original_text=request.text, 
           source_lang=request.source_lang, 
           target_lang=request.target_lang
       )
       
       if existing:
           # Return existing translation
           return {
               "original_text": request.text,
               "translated_text": existing.translated_text
           }
       
       # Translation not found, get it from the API
       response = client.chat.completions.create(
           model="Provider-7/gpt-4o-mini",
           messages=[
               {"role": "system", "content": "You are a translator. Only output the translated text - no explanations, no additional text, no quotes."},
               {"role": "user", "content": f"Translate this {request.source_lang} text to {request.target_lang}: {request.text}"}
           ]
       )
       
       # Extract the translation
       translated_text = response.choices[0].message.content.strip()
       
       # Store in database
       translation = crud.create_translation_record(
           db=db,
           original_text=request.text,
           translated_text=translated_text,
           source_lang=request.source_lang,
           target_lang=request.target_lang
       )
       
       # Return the response
       return {
           "original_text": request.text,
           "translated_text": translated_text
       }
       
   except Exception as e:
       # Log the error
       print(f"Translation error: {str(e)}")
       
       # Return appropriate error response
       raise HTTPException(
           status_code=500,
           detail=f"Translation failed: {str(e)}"
       )

@app.get("/health")
def health_check():
   """
   Simple health check endpoint to verify the API is running
   """
   return {"status": "healthy", "message": "Translation API is up and running"}

if __name__ == "__main__":
   import uvicorn
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)