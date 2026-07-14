import httpx
import os
from typing import Dict, Any

class ChapaPaymentService:

    CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"
    CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify"

    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        # Reads the secret key safely from environment variables
        secret_key = os.getenv("CHAPA_SECRET_KEY", "CHASECK_TEST-eQqJM6N59FEGwbDMdE4rmf5Crlh8U2pK")
        return {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }

    @classmethod
    async def initialize_chapa_payment(
        cls, 
        order_id: str, 
        amount: float, 
        currency: str, 
        email: str, 
        full_name: str,
        tx_ref: str
    ) -> Dict[str, Any]:
        
        # FIX 1: Executed the classmethod correctly to get headers dict
        headers = cls._get_headers()

        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else "Market"
        last_name = name_parts[1] if len(name_parts) > 1 else "Customer"

        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": os.getenv("CHAPA_CALLBACK_URL", "http://127.0.0.1:8007/docs#/Order%20Management%20Related/chapa_payment_webhook_api_order_payment_webhook_post"),
            "return_url": os.getenv("CHAPA_RETURN_URL", "https://www.google.com/")
        }

        async with httpx.AsyncClient() as client:
          
            response = await client.post(cls.CHAPA_API_URL, json=payload, headers=headers)
            res_data = response.json()

           
            if response.status_code != 200 or res_data.get("status") != "success":
                raise Exception(res_data.get("message", "Chapa payment initialization failed"))
            
            return {
                "checkout_url": res_data["data"]["checkout_url"],
                "tx_ref": tx_ref
            }

    @classmethod
    async def verify_chapa_payment(cls, tx_ref: str) -> Dict[str, Any]:
        headers = cls._get_headers()
        verify_url = f"{cls.CHAPA_VERIFY_URL}/{tx_ref}"

        async with httpx.AsyncClient() as client:
            response = await client.get(verify_url, headers=headers)
            res_data = response.json()

            if response.status_code != 200 or res_data.get("status") != "success":
                raise Exception(res_data.get("message", "Chapa payment verification failed"))

            return res_data