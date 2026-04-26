# Meta Pixel & Conversion Tracking Guide

This document explains **how Meta Pixel is implemented on Startinbox**, how events are fired from the **Next.js App Router frontend**, how they are **confirmed and deduplicated via the FastAPI backend**, and how **cookie consent** controls all tracking.

This is the single source of truth for future developers.

---

## 1. High-Level Architecture

```
User
 └─> Next.js (Meta Pixel – frontend intent)
      └─ event_id
         └─> FastAPI Backend (payment & success confirmation)
              └─ same event_id
                   └─> Meta Conversions API (server-side)
```

Key principles:

- Frontend = user intent
- Backend = source of truth
- Meta deduplicates using `event_id`

---

## 2. Consent Rules (IMPORTANT)

### Legal Requirement

- No tracking **before consent**
- Tracking allowed **only after explicit user acceptance**

### Behavior

- If user has **not accepted cookies** → Meta Pixel is NOT loaded
- If user **accepts cookies** → page reloads → Meta Pixel initializes

### Storage

Consent is stored in `localStorage` for **1 year** under:

```
startinbox_cookieConsent
```

Example value:

```json
{
	"value": true,
	"expiry": 1735689600000
}
```

Expired consent is treated as no consent.

---

## 3. Cookie Consent Hook

The hook controlling consent is:

```
useCookieConsent
```

Responsibilities:

- Read stored consent & expiry on load
- Show banner if consent is missing or expired
- Persist consent for one year
- Trigger a page reload after acceptance

### IMPORTANT

The reload is required so Meta Pixel initializes cleanly.

---

## 4. Meta Pixel Loading (Frontend)

### File

```
components/client/MetaPixel.tsx
```

### Rule

Meta Pixel **must not render** unless valid consent exists.

Pseudo-flow:

```ts
if (!hasMetaConsent()) return null;
loadMetaPixel();
```

This ensures:

- No Meta requests before consent
- Full GDPR / NDPR compliance

---

## 5. SPA Page View Tracking

Because this is a Next.js App Router application:

- Navigation is client-side
- PageView must be tracked on route change

Handled via:

```
MetaPageView component
```

This fires:

```
fbq('track', 'PageView')
```

whenever the route changes.

---

## 6. Event Tracking Utility

### File

```
lib/client/metaPixel.ts
```

### track(event, data)

Responsibilities:

- Generate a unique `event_id`
- Fire Meta Pixel event
- Return `event_id` for backend use

### Rule

ALL important events must use this helper.

---

## 7. Canonical Meta Events (FOR MARKETERS)

Only **standard Meta events** are used.

### Global (Automatic)

| Action                   | Meta Event |
| ------------------------ | ---------- |
| Page load / route change | PageView   |

---

### Authentication

| Action  | Meta Event           | When                   |
| ------- | -------------------- | ---------------------- |
| Sign in | Login                | After successful login |
| Sign up | CompleteRegistration | After account creation |

---

### Idea Validation (Core SaaS)

| Action      | Meta Event | When                        |
| ----------- | ---------- | --------------------------- |
| Submit idea | Lead       | After successful submission |

---

### Product Manager Service

| Action           | Meta Event       | When             |
| ---------------- | ---------------- | ---------------- |
| Start booking PM | InitiateCheckout | On booking start |

---

### Expert Consultation

| Action      | Meta Event       | When          |
| ----------- | ---------------- | ------------- |
| Book expert | InitiateCheckout | Booking start |

---

### Subscription Plan

| Action      | Meta Event       | When          |
| ----------- | ---------------- | ------------- |
| Select plan | InitiateCheckout | Booking start |

---

### Blogs & Content

| Action         | Meta Event  | When            |
| -------------- | ----------- | --------------- |
| View blog list | ViewContent | Blog index page |
| View blog post | ViewContent | Individual blog |

---

### Payments (CRITICAL)

| Action          | Meta Event       | When              |
| --------------- | ---------------- | ----------------- |
| Enter checkout  | InitiateCheckout | User intent       |
| Payment success | Purchase         | Backend-confirmed |

---

### Newsletter

| Action    | Meta Event | When          |
| --------- | ---------- | ------------- |
| Subscribe | Subscribe  | After success |

---

## 8. What NOT to Track

Do NOT track:

- UI-only button clicks
- Page scrolls
- Hover events
- Tabs or dropdowns

Reason: these break ad optimization quality.

---

## 9. Payment Provider Mapping (Backend)

### Providers Supported

- Stripe
- Paystack
- Flutterwave

### Rule

- Frontend fires `InitiateCheckout`
- Backend fires `Purchase`
- Same `event_id` must be used

Example mapping:

| Provider            | Event    | Source  |
| ------------------- | -------- | ------- |
| Stripe webhook      | Purchase | Backend |
| Paystack webhook    | Purchase | Backend |
| Flutterwave webhook | Purchase | Backend |

---

## 10. Deduplication (VERY IMPORTANT)

Meta deduplicates events using:

```
(event_name + event_id)
```

### Implementation

1. Frontend generates `event_id`
2. `event_id` is sent to backend\ n3. Backend sends same `event_id` to Meta CAPI

Result:

- Frontend + backend events count as **one conversion**

---

## 11. Backend: Meta Conversions API (FastAPI)

### Responsibilities

- Confirm success events (payments, registrations)
- Send server-side events to Meta
- Improve accuracy (iOS, ad blockers)

### Rule

Backend events are the **final authority** for money-related actions.

---

## 12. Environment Variables

### Frontend

```
NEXT_PUBLIC_META_PIXEL_ID=
```

### Backend

```
META_PIXEL_ID=
META_ACCESS_TOKEN=
```

---

## 13. Common Pitfalls (Avoid These)

❌ Tracking before consent
❌ Tracking button clicks instead of success
❌ Firing Purchase on frontend
❌ Using custom event names
❌ Double-counting payments

---

## 14. One-Sentence Contract (Engineering + Marketing)

> We track only Meta-standard funnel events—signups, leads, checkouts, and purchases—with user consent, server confirmation, and full deduplication.

---

## 15. Maintenance Notes

- If cookie consent is revoked → Meta Pixel must stop loading
- If routes change structure → verify PageView still fires
- If adding new paid features → map them to InitiateCheckout + Purchase

---

END OF DOCUMENT
