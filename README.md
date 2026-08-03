# Customer Support NLP API

Turn unstructured customer messages into structured, workflow-ready ticket data.

This portfolio demonstration combines lightweight machine learning, transparent extraction rules, and a FastAPI service. It is designed to show a realistic first layer of support-ticket automation without using a large language model or an external inference API.

## Business Problem

Customer messages often arrive as unstructured text. A support team still needs to read each message, identify the business category, find important fields, and decide whether the ticket needs urgent attention.

This service automates that first pass:

```text
Customer Message
        ↓
FastAPI NLP Service
        ↓
Category + Priority + Extracted Entities
        ↓
CRM / Helpdesk Workflow
```

## What the API Does

### Text Classification

The classifier predicts one of three support categories:

- `billing`
- `delivery`
- `technical`

The model uses a scikit-learn pipeline:

```text
TF-IDF Vectorizer → Logistic Regression
```

The training data contains 30 balanced synthetic support examples. The saved model is loaded by FastAPI and is not retrained for each request.

### Entity Extraction

Transparent regular expressions extract the first match for:

- order IDs such as `ORD-10482`;
- email addresses;
- common phone-number formats;
- monetary values such as `£49.99` or `120 USD`;
- ISO, US, and common English date formats.

The API keeps the entity schema stable. Missing fields are returned as `null`.

### Priority Rules

Priority is assigned with explicit rules:

1. high-priority phrase match → `high`;
2. otherwise medium-priority phrase match → `medium`;
3. otherwise → `low`.

If classifier confidence is below `0.70`, the response sets `needs_review` to `true`.

## Example Request and Response

Request:

```json
{
  "text": "My order ORD-10482 has not arrived. Please contact me at customer@example.com."
}
```

Response:

```json
{
  "category": "delivery",
  "priority": "high",
  "entities": {
    "order_id": "ORD-10482",
    "email": "customer@example.com",
    "phone": null,
    "amount": null,
    "date": null
  },
  "keywords": ["order", "arrived"],
  "confidence": 0.7116,
  "needs_review": false
}
```

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check service and model loading status |
| `POST` | `/analyze` | Classify and enrich one support message |
| `GET` | `/docs` | Open FastAPI Swagger documentation |

## Run Locally

Create an environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Train the saved model and build the supporting keyword summary:

```bash
python scripts/train_model.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Analyze a message:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"My order ORD-10482 has not arrived. Please contact me at customer@example.com."}'
```

## Vue Frontend

The project also includes a beginner-friendly Vue 3 frontend. It calls the existing FastAPI endpoint and displays the category, priority, confidence, extracted entities, and keywords.

The frontend is intentionally small: one page component, a few focused child components, one API helper, and one stylesheet. It uses Vue fundamentals such as `ref`, `computed`, `v-model`, `v-if`, `v-for`, and event handlers before introducing routers, state libraries, or TypeScript.

Start the backend in one terminal:

```bash
uvicorn app.main:app --reload
```

Start Vue in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. The frontend uses `fetch` to send a `POST /analyze` request to the FastAPI service.

The default API URL is `http://127.0.0.1:8000`. To point the frontend at another local or hosted backend, copy the example environment file and edit the value:

```bash
cp .env.example .env
```

Then set `VITE_API_BASE_URL` in `frontend/.env` and restart the Vite dev server. The `.env` file is local-only and is ignored by Git.

The frontend also applies an 8-second request timeout. When the backend is offline or times out, the interface shows a clear error and exposes a `Retry` action in the API status indicator.

For local development, FastAPI allows the Vite origins `localhost:5173` and `127.0.0.1:5173` through CORS. The backend response schema is unchanged.

### Vue Learning Map

| Vue concept | Where it appears | What it does |
| --- | --- | --- |
| `ref()` | `frontend/src/App.vue` | Stores reactive message, loading, error, and result state |
| `v-model` | Message textarea | Keeps the textarea and JavaScript value synchronized |
| `@click` | Analyze and sample buttons | Runs actions when the user clicks |
| `v-if` | Loading, error, empty, and result areas | Shows the correct UI state |
| `v-for` | Entity and keyword lists | Renders repeated API data |
| `fetch()` | `frontend/src/api.js` | Sends the browser request to FastAPI |
| `defineProps()` | `MessageInput.vue`, `ResultSummary.vue` | Receives data from the parent component |
| `defineEmits()` | `MessageInput.vue` | Sends user actions back to the parent |
| Reusable components | `SummaryCard.vue`, `ConfidenceMeter.vue` | Keeps repeated UI pieces small and consistent |
| `onMounted()` | `frontend/src/App.vue` | Runs the FastAPI health check after the page appears |
| `watch()` | `frontend/src/App.vue` | Clears an old error when the user edits the message |
| `computed()` | `frontend/src/App.vue` | Derives validation state and keeps it synchronized |
| Form validation | `App.vue` + `MessageInput.vue` | Prevents invalid requests before the API call |
| `import.meta.env` | `frontend/src/api.js` | Reads the API URL from Vite environment configuration |
| `AbortController` | `frontend/src/api.js` | Stops a request that has exceeded the timeout |
| Retry interaction | `frontend/src/App.vue` | Lets the user check the backend again after a network failure |

### Frontend and Backend Validation

The frontend checks for blank messages and messages over 5,000 characters so users receive immediate feedback. FastAPI validates the same boundary on the server because browser-side checks improve the experience but cannot be trusted as the final safety boundary.

### API Configuration and Network States

The API helper has one request path for both health checks and message analysis. It converts low-level browser failures into messages a user can understand:

```text
FastAPI available → request succeeds
FastAPI unavailable → offline status + clear error
Request takes too long → timeout message + Retry action
```

This is a small but important production habit: a frontend should explain what the user can do next when a dependency is unavailable.

### Lifecycle and Watchers

The top-right API indicator is connected to the real backend. When Vue mounts the page, `onMounted()` calls `GET /health`:

```text
Page mounted → health check → connected / degraded / offline status
```

The `watch(message, ...)` callback observes the textarea value. If the user changes the message after a validation error, the old error is cleared automatically. This keeps UI feedback close to the user action without putting that behavior inside the input component.

## Supporting Visual

The keyword chart is a small supporting view of the synthetic training examples. It is not a production analytics dashboard.

![Synthetic ticket keyword summary](outputs/keyword_summary.png)

## Suitable Client Scenarios

This workflow can be adapted for:

- customer-support inbox triage;
- CRM or helpdesk pre-processing;
- order-status and billing message routing;
- extracting fields from email or contact-form submissions;
- lightweight internal ticket automation.

## Limitations

- The training data is synthetic and intentionally small.
- This demo is English-only.
- The classifier is not benchmarked for production accuracy.
- Regex extraction covers common formats, not every international variation.
- No authentication, database, queue, deployment system, or CRM integration is included.

This is a portfolio demonstration, not a real client project, production support system, or safety-critical decision service.

## Project Structure

```text
case_1_fastapi_nlp_api/
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── schemas.py           # Pydantic request/response models
│   ├── classifier.py        # TF-IDF + Logistic Regression lifecycle
│   ├── extractor.py         # Regex entity extraction
│   └── rules.py             # Priority and keyword rules
├── data/
│   └── training_examples.csv
├── models/
│   └── intent_classifier.joblib
├── examples/
│   ├── sample_requests.json
│   └── sample_response.json
├── outputs/
│   └── keyword_summary.png
├── portfolio/
│   └── cover.png
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── api.js
│   │   ├── style.css
│   │   └── components/
│   │       ├── MessageInput.vue
│   │       ├── EntityList.vue
│   │       ├── ResultSummary.vue
│   │       ├── SummaryCard.vue
│   │       └── ConfidenceMeter.vue
│   ├── index.html
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── train_model.py
├── tests/
│   └── test_api.py
├── README.md
└── requirements.txt
```
