# Documentation for APIs

1. **CRUD API for Shop:**
   
   End-point: /main/shop/
   
   Authentication Needed: NO
   
2. **API for initial-sync:**

   End-point: /main/shipments-sync/initial-sync/
   
   Authentication Needed: NO
   
   sample response:
   
   `{
        "message": "Async Tasks have been started."
   }`
   
3. **API for access-token:**

   End-point: /main/login/token/
   Method: POST
   
   Authentication Needed: NO
   
   sample request:
   
   `{
        "clientId": "00ac91e8-29ba-4bad-9bcc-4d5ada331e1a",
        "clientSecret": "cGWcMT2KP5h6gsWyd8ZnA8fSorDSalMUZl59OIUM_ZnF-Vzcsckrl_WnBqikQE8ZceBWa3FO5z514WyBjdJgxg"
   }`
   
   sample response:
   
   `{
        "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiIwMGFjOTFlOC0yOWJhLTRiYWQtOWJjYy00ZDVhZGEzMzFlMWEiLCJjbGllbnRfc2VjcmV0IjoiY0dXY01UMktQNWg2Z3NXeWQ4Wm5BOGZTb3JEU2FsTVVabDU5T0lVTV9abkYtVnpjc2NrcmxfV25CcWlrUUU4WmNlQldhM0ZPNXo1MTRXeUJqZEpneGciLCJleHAiOjE1OTQ5Mjg0MTd9.ItO1QjSmKbFGPpmniaYdxB63E6GPDHcRzBB0dbp-2WQ",
        "tokenType": "Bearer"
   }`
    
4. **API for shipments-list**

   _paginated response_
   
   End-point: /main/shipments/
   Method: GET
   Params: page
   
   Authentication Needed: Yes
   
   sample response:
   
   `{
        "count": 60,
        "next": "/main/shipments/?page=2",
        "previous": null,
        "results": [
            {
                "shipmentId": 754628521,
                "shipmentDate": "2020-06-03T14:41:23Z",
                "shipmentReference": "P2020-3613",
                "transport": {
                    "transportId": 494945076
                },
                "shipmentItems": [
                    {
                        "orderItemId": "2408312775",
                        "orderId": "1115553243"
                    }
                ]
            }
        ]
    }`
   
   
5. **API for shipment-details:**

   End-point: /main/shipments/{shipment_id}/
   Method: GET
   
   Authentication Needed: Yes
   
   sample response:
   
   `
   {
        "shipmentId": 768709761,
        "shipmentDate": "2020-07-15T17:49:53Z",
        "shipmentReference": "",
        "transport": {
            "transportId": 509436276,
            "transporterCode": "TNT",
            "trackAndTrace": "3SKABA920959857",
            "shippingLabelId": null,
            "shippingLabelCode": ""
        },
        "shipmentItems": [
            {
                "id": 20,
                "orderItemId": "2423668707",
                "orderId": "1126133241",
                "orderDate": "2020-07-14T07:35:16Z",
                "latestDeliveryDate": "2020-07-14T22:00:00Z",
                "ean": "8720299036802",
                "title": "Contactloze Infrarood Koortsthermometer - Lichaam en Voorhoofd - Temperatuurmeter voor bedrijven",
                "quantity": 1,
                "offerPrice": "240.95",
                "offerCondition": "NEW",
                "offerReference": "",
                "fulfilmentMethod": "FBR",
                "shipment": 768709761
            }
        ],
        "customerDetails": {
            "id": 70,
            "pickUpPointName": "",
            "salutationCode": "02",
            "firstName": "Jeannette",
            "surname": "Lutterman",
            "streetName": "Maarssenbroeksedijk",
            "houseNumber": "2",
            "houseNumberExtended": "",
            "addressSupplement": "",
            "extraAddressInformation": "",
            "zipCode": "3542DN",
            "city": "UTRECHT",
            "countryCode": "NL",
            "email": "2z3cbzpwighb6czjl27qkukdv5p2gc@verkopen.bol.com",
            "company": "Diversey BV",
            "vatNumber": "",
            "chamberOfCommerceNumber": "",
            "orderReference": "",
            "deliveryPhoneNumber": "",
            "type": "Customer"
        },
        "billingDetails": {
            "id": 75,
            "pickUpPointName": "",
            "salutationCode": "02",
            "firstName": "Jeannette",
            "surname": "Lutterman",
            "streetName": "Maarssenbroeksedijk",
            "houseNumber": "2",
            "houseNumberExtended": "",
            "addressSupplement": "",
            "extraAddressInformation": "",
            "zipCode": "3542 DN",
            "city": "UTRECHT",
            "countryCode": "NL",
            "email": "2z3cbzpwighb6czjl27qkukdv5p2gc@verkopen.bol.com",
            "company": "",
            "vatNumber": "",
            "chamberOfCommerceNumber": "",
            "orderReference": "",
            "deliveryPhoneNumber": "",
            "type": "Billing"
        }
   }
   `
   
**JWT token prefix: Bearer**