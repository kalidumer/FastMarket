import httpx   
import uuid
from fastapi import HTTPException,status


CHAPA_API_URL="https://api.chapa.co/v1/transaction/initialize"
CHAPA_SECRET_KEY="sk_test_2e0c1d3f7b8e4a5f9b6c1d3f7b8e4a5f"

class ChapaPaymentService:
    @staticmethod
    async def initialize_chapa_payment(order_id: str, amount: float, currency: str, email: str, full_name: str) -> dict:
        
        tx_ref = f"fastmarket-{order_id}-{uuid.uuid4()}"
        
        names = full_name.split(" ")
        first_name = names[0] if names else "Customer"
        last_name = names[-1] if len(names) > 1 else "User"
        
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": "https://yourdomain.com/api/orders/payment/webhook",
            "return_url": f"https://yourdomain.com/checkout/success?tx_ref={tx_ref}",
            "customization[title]": "FastMarket Checkout",
            "customization[description]": f"Payment for Order #{order_id}"
        }
        
        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(CHAPA_API_URL, json=payload, headers=headers,timeout=10.0)
            res_data = response.json()
            
            if(response.status_code != 200 or res_data.get("status") != "success"):
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to initialize payment with Chapa.")
            
            return{
                "checkout_url": res_data["data"]["checkout_url"],
                "tx_ref": tx_ref
            }
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment Gateway is temporarily unreachable: {str(exc)}"
            )
        