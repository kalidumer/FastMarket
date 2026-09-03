import pytest
import
# ==================tests for auth============

def test_login_success(client):
    response=client.post('/api/auth/login',json={"email":"user@example.com","password":"password"})
    assert response.status_code==200
    assert "access_token" in response.json()
    assert response.json()["token_type"]=="bearer"

def test_login_failure(client):
    response=client.post('/api/auth/login',json={
        "email":"wrongemail@example.com",
        "password":"wrongpassword"
    })

    assert response.status_code==401


#===========cart tests========================

def test_getcart_unauthorised(client):
    response=client.get('/api/cart')
    assert response.status_code==401

def test_add_to_cart(client,auth_headers):
    response=client.post('/api/cart',json={"product_id":1,"quantity":2},headers=auth_headers)
    assert response.status_code in [200,201]
    assert response.json()["product_id"]==1


