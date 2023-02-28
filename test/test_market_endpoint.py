def test_get_markets(client):
    rv = client.get("/markets")
    assert rv.status_code == 200
    assert rv.json == [
        {"code": "san-francisco", "currency": "USD", "name": "San Francisco"},
        {"code": "lisbon", "currency": "EUR", "name": "Lisbon"},
        {"code": "paris", "currency": "EUR", "name": "Paris"},
        {"code": "tokyo", "currency": "JPY", "name": "Tokyo"},
        {"code": "jerusalem", "currency": "ILS", "name": "Jerusalem"},
        {"code": "brisbane", "currency": "AUD", "name": "Brisbane"},
    ]
