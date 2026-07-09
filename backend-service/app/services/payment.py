import httpx   
import uuid
import os 
from fastapi import HTTPException, status


CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")

class ChapaPaymentService:
    @staticmethod
    async def initialize_chapa_payment(order_id: str, amount: float, currency: str, email: str, full_name: str) -> dict:
        
        tx_ref = f"fastmarket-{order_id}-{uuid.uuid4()}"
        
        names = full_name.split(" ")
        first_name = names[0] if names else "Customer"
        last_name = names[-1] if len(names) > 1 else "User"
        
    
        BASE_URL = "http://127.0.0.1:8007" 
        FRONTEND_URL = "http://localhost:3000"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": f"{BASE_URL}/api/order/payment/webhook",
            "return_url": f"{FRONTEND_URL}/checkout/success?tx_ref={tx_ref}", # 👈 Point to your frontend success page
            "customization[title]": "FastMarket Checkout",
            "customization[description]": f"Payment for Order #{order_id}"
        }