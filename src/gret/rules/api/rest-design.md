# REST API Design Golden Rules

This document specifies the standard conventions for URL structure, HTTP methods, status codes, and payload formatting for RESTful web services.

---

## 1. URL Structure & Naming

1. **Use Nouns, Not Verbs**:
   - Good: `GET /api/v1/users`, `POST /api/v1/orders`
   - Bad: `GET /api/v1/getUsers`, `POST /api/v1/createOrder`
2. **Use Plural Nouns for Collections**:
   - Collection: `/api/v1/products`
   - Item: `/api/v1/products/{id}`
   - Nested Resource: `/api/v1/users/{id}/orders`
3. **Kebab-case for Multi-word Path Segments**:
   - Good: `/api/v1/order-items`
   - Bad: `/api/v1/order_items`, `/api/v1/orderItems`

---

## 2. HTTP Methods & Idempotency

- `GET`: Safe & Idempotent. Retrieve resources.
- `POST`: Neither safe nor idempotent. Create new sub-resources or trigger custom actions (`/orders/{id}/cancel`).
- `PUT`: Idempotent. Full replacement of target resource.
- `PATCH`: Idempotent or non-idempotent. Partial update.
- `DELETE`: Idempotent. Remove target resource.

---

## 3. Standard HTTP Status Codes

- `200 OK`: Successful retrieval or synchronous update.
- `201 Created`: Successful creation (include `Location` header pointing to new URI).
- `204 No Content`: Successful operation with empty body (e.g., `DELETE`).
- `400 Bad Request`: Validation failure or malformed payload.
- `401 Unauthorized`: Authentication missing or invalid.
- `403 Forbidden`: Authenticated, but lacks authorization permissions.
- `404 Not Found`: Target resource does not exist.
- `409 Conflict`: Business rule or state conflict (e.g., duplicate unique constraint).
- `500 Internal Server Error`: Unhandled server-side fault.

---

## 4. Standard Error Response Envelope (RFC 7807 Pattern)

Always return a structured JSON error response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The payload contains invalid field values.",
    "details": [
      {
        "field": "email",
        "issue": "Invalid email address format."
      }
    ]
  }
}
```
