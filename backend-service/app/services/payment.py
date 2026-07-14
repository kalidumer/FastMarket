import httpx
import os

class ChapaPaymentService:
    @classmethod
    async def initialize_chapa_payment(cls, order_id: str, amount: float, currency: str, email: str, full_name: str):
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        secret_key = os.getenv("CHAPA_SECRET_KEY")
        
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Build the exact dictionary structure Chapa expects
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": full_name.split()[0] if full_name else "Customer",
            "last_name": full_name.split()[1] if len(full_name.split()) > 1 else "Market",
            "tx_ref": f"fastmarket-tx-{order_id}", # Or pass the unique_tx_ref directly
            "callback_url": "http://localhost:8007/docs#/Order%20Management%20Related/chapa_payment_webhook_api_order_payment_webhook_post", # Your webhook callback url
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(chapa_url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Chapa API responded with status {response.status_code}: {response.text}")
                
            res_json = response.json()
            
            # Chapa returns data inside a 'data' object. We must unpack it safely.
            data = res_json.get("data")
            if not data or "checkout_url" not in data:
                raise Exception("Malformed response structure from Chapa API.")
                
            return {
                "checkout_url": data.get("checkout_url"),
                "tx_ref": payload["tx_ref"]
            }