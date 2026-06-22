import os
import json
import traceback
from sqlmodel import select
import google.generativeai as genai

# 🟢 FIXED IMPORTS: Points to your new modular folders
from app.core.database import engine, AsyncSession
from app.models.ticket import Ticket

# Connect Google AI SDK to your local environment token keys securely
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modern alternative model fallbacks
AVAILABLE_MODELS = [
    "gemini-2.5-flash",      # Newest stable
    "gemini-2.0-flash",      # Modern lightning fast 
    "gemini-1.5-flash"       # Production stable fallback
]
DEFAULT_GENAI_MODEL = os.getenv("GENAI_MODEL", AVAILABLE_MODELS[0])

async def ai_based_ticket(tiket_id: int, feedback_text: str):
    print(f"\n[AI PIPELINE] -> Starting background worker thread for Ticket #{tiket_id}...")
    
    try:
        prompt = f"""
        Analyze this customer support feedback text:
        "{feedback_text}"
        
        Provide your analysis in raw JSON format with the exact keys below:
        {{
            "urgency_level": "Low, Medium, or High",
            "customer_sentiment": "One or two words describing their emotional state",
            "suggested_action": "Brief instruction for the customer support agent",
            "draft_reply": "A polite, direct professional response resolving their feedback"
        }}
        """
        
        response = None
        models_to_try = [DEFAULT_GENAI_MODEL] + [m for m in AVAILABLE_MODELS if m != DEFAULT_GENAI_MODEL]
        
        for model_name in models_to_try:
            try:
                print(f" -> Connecting to AI node variant: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Force structured API validation configurations to clean raw markdown clutter
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                print(f" -> Model response canvas successfully extracted from: {model_name}")
                break  
            except Exception as model_err:
                print(f" [!] Variant entry '{model_name}' skipped. Reason: {model_err}")
                if model_name == models_to_try[-1]:
                    raise model_err

        # Safely capture text output blocks from the generation payload
        generated_text = None
        if hasattr(response, "text") and response.text:
            generated_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            generated_text = response.candidates[0].content.parts[0].text

        if not generated_text:
            raise ValueError("The target artificial intelligence module generated an empty text canvas.")

        # Strip out markdown backtick wrapper tags if present
        cleaned_text = generated_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        # Compile string data blocks securely into Python dictionary maps
        ai_generated_data = json.loads(cleaned_text)
        print(" -> Data structural dictionary compiled smoothly.")

        # 🟢 FIXED TRANSACTION: Open an explicit asynchronous session context using your centralized engine
        async with AsyncSession(engine) as session:
            statement = select(Ticket).where(Ticket.id == tiket_id)
            result = await session.execute(statement)
            ticket_from_db = result.scalar_one_or_none()
            
            if ticket_from_db:
                ticket_from_db.urgency_level = ai_generated_data.get("urgency_level", "Medium")
                ticket_from_db.customer_sentiment = ai_generated_data.get("customer_sentiment", "Neutral")
                ticket_from_db.draft_reply = ai_generated_data.get("draft_reply", "Thank you for your feedback.")
                ticket_from_db.suggested_action = ai_generated_data.get("suggested_action", "Review Required!")
                
                await session.commit()
                print(f"[AI PIPELINE SUCCESS] -> Ticket #{tiket_id} data updated completely in Supabase!\n")
            else:
                print(f" [!] WARNING: Ticket #{tiket_id} was missing inside your DB layout cache.\n")
                
    except Exception as e:
        print("\n" + "="*60)
        print(f"🚨 CRITICAL BACKGROUND PIPELINE EXCEPTION ON TICKET #{tiket_id} 🚨")
        print(f"Error Blueprint Type: {type(e).__name__}")
        print(f"Error Message Context: {e}")
        print("-"*60)
        print("EXPLICIT DETAILED SYSTEM RUNTIME TRACEBACK:")
        traceback.print_exc()  
        print("="*60 + "\n")