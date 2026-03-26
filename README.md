# GAN Studio

GAN Studio is a production-style full-stack project for GAN-powered image workflows. It combines a Next.js frontend, FastAPI backend, PyTorch GAN models, PostgreSQL-ready SQLAlchemy models, local or S3-backed storage, and Celery workers for background training.

## 1. Architecture

### Stack

- Frontend: Next.js 15, React 19, Tailwind CSS, Axios
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT auth
- ML layer: PyTorch DCGAN, CycleGAN generator pipeline, StyleGAN integration stub
- Database: PostgreSQL in production, SQLite fallback for local quickstart
- Storage: Local filesystem by default, optional AWS S3
- Async jobs: Celery + Redis
- Real-time updates: FastAPI WebSockets

### Text Architecture Diagram

```text
┌────────────────────────────────────────────────────────────────────┐
│                           Next.js Frontend                         │
│ Home | Generate | Transform | Dashboard | Auth | Training Charts  │
└───────────────┬───────────────────────────────────────┬────────────┘
                │ REST/JSON + multipart                │ WebSocket
                ▼                                       ▼
┌────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend                          │
│ Auth | Generate | Upload | Transform | Train | Images | Jobs      │
│ Rate limit | Validation | Logging | Static file serving           │
└───────────────┬───────────────────────────────┬────────────────────┘
                │                               │
                ▼                               ▼
┌──────────────────────────────┐   ┌────────────────────────────────┐
│ SQLAlchemy / PostgreSQL      │   │ Storage Service                 │
│ users                        │   │ local files or AWS S3           │
│ generated_images             │   │ generated image URLs            │
│ training_jobs                │   └────────────────────────────────┘
└───────────────┬──────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────────┐
│                 Celery Worker + Redis Queue                        │
│ background DCGAN training | checkpoint save | metrics persistence  │
└───────────────┬────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────────┐
│                          PyTorch Model Layer                       │
│ DCGAN Generator/Discriminator | CycleGAN Generator | checkpoints   │
└────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User signs up or logs in from the Next.js frontend.
2. JWT is stored in `localStorage` and attached to all API requests.
3. `POST /api/v1/generate` samples DCGAN latent noise, creates images, stores them locally or on S3, and persists metadata.
4. `POST /api/v1/upload` stores original files, while `POST /api/v1/transform` runs CycleGAN translation and saves the transformed output.
5. `POST /api/v1/train` creates a training job row and dispatches a Celery task through Redis.
6. The Celery worker trains the DCGAN, writes checkpoints to `storage/models`, and saves loss metrics back into `training_jobs`.
7. Dashboard polls REST endpoints and listens to `/ws/{user_id}` for real-time job updates.

## 2. Backend

### Backend Folder Structure

```text
backend/
├── app.py
├── celery_worker.py
├── Dockerfile
├── requirements.txt
└── app/
    ├── api/
    │   ├── deps.py
    │   ├── router.py
    │   └── routes/
    │       ├── auth.py
    │       ├── images.py
    │       └── training.py
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   ├── logging.py
    │   ├── rate_limit.py
    │   └── security.py
    ├── ml/
    │   ├── cyclegan.py
    │   ├── dcgan.py
    │   └── stylegan.py
    ├── models/
    │   ├── image.py
    │   ├── training_job.py
    │   └── user.py
    ├── schemas/
    │   ├── auth.py
    │   ├── image.py
    │   └── training.py
    ├── services/
    │   ├── gan_service.py
    │   ├── realtime.py
    │   ├── storage.py
    │   └── training_service.py
    ├── websockets/
    │   └── router.py
    └── worker/
        ├── celery_app.py
        └── tasks.py
```

### API Contracts

#### `POST /api/v1/auth/register`

- Request:

```json
{
  "email": "user@example.com",
  "password": "StrongPass123",
  "full_name": "Ava Stone"
}
```

- Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Ava Stone",
    "is_active": true,
    "created_at": "2026-03-26T00:00:00"
  }
}
```

#### `POST /api/v1/auth/login`

- Request:

```json
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

- Response: same as register

#### `POST /api/v1/generate`

- Request:

```json
{
  "model_type": "dcgan",
  "num_images": 4,
  "latent_dim": 100,
  "checkpoint_name": "dcgan-latest.pt",
  "image_size": 64,
  "prompt": "high contrast portrait experiment"
}
```

- Response:

```json
{
  "model_type": "dcgan",
  "images": [
    {
      "id": "uuid",
      "model_type": "dcgan",
      "prompt": "high contrast portrait experiment",
      "original_filename": null,
      "storage_key": "generated-abc.png",
      "public_url": "/storage/images/generated-abc.png",
      "width": 64,
      "height": 64,
      "created_at": "2026-03-26T00:00:00"
    }
  ],
  "message": "images generated successfully"
}
```

#### `POST /api/v1/upload`

- Content type: `multipart/form-data`
- Field: `file`
- Response:

```json
{
  "image_id": "uuid",
  "filename": "input.jpg",
  "url": "/storage/images/upload-abc.jpg",
  "message": "upload complete"
}
```

#### `POST /api/v1/transform`

- Content type: `multipart/form-data`
- Fields:
  - `file`
  - `direction`
  - `checkpoint_name`
- Response: `GeneratedImageResponse`

#### `POST /api/v1/train`

- Request:

```json
{
  "model_type": "dcgan",
  "dataset_name": "mnist",
  "epochs": 10,
  "batch_size": 64,
  "latent_dim": 100,
  "learning_rate": 0.0002,
  "beta1": 0.5,
  "image_size": 64
}
```

- Response:

```json
{
  "id": "uuid",
  "model_type": "dcgan",
  "dataset_name": "mnist",
  "status": "queued",
  "epochs": 10,
  "batch_size": 64,
  "latent_dim": 100,
  "learning_rate": "0.0002",
  "beta1": "0.5",
  "image_size": 64,
  "checkpoint_path": null,
  "metrics_json": null,
  "error_message": null,
  "created_at": "2026-03-26T00:00:00",
  "updated_at": "2026-03-26T00:00:00"
}
```

#### `GET /api/v1/images`

- Response: list of generated/uploaded/transformed images for the authenticated user

### Error Handling and Validation

- Pydantic request models validate input ranges, lengths, and allowed enums
- Duplicate registration returns `409`
- Invalid credentials return `401`
- Invalid file uploads return `400`
- Unsupported model flows return `400` or `501`
- Per-IP rate limiting returns `429`

## 3. GAN Models

### DCGAN

- Files:
  - [`backend/app/ml/dcgan.py`](/C:/Users/HP/Documents/New%20project/backend/app/ml/dcgan.py)
  - [`backend/app/services/training_service.py`](/C:/Users/HP/Documents/New%20project/backend/app/services/training_service.py)

### Implemented Components

- Generator with transposed convolutions, batch norm, ReLU, and Tanh output
- Discriminator with strided convolutions, batch norm, LeakyReLU, and sigmoid output
- BCE loss for adversarial training
- Adam optimizers with configurable `learning_rate` and `beta1`
- Dataset loaders for MNIST and CelebA
- Checkpoint persistence under `storage/models`

### CycleGAN

- File:
  - [`backend/app/ml/cyclegan.py`](/C:/Users/HP/Documents/New%20project/backend/app/ml/cyclegan.py)

- Included:
  - Residual generator blocks
  - Reflection padding
  - Downsampling and upsampling path
  - Inference pipeline for uploaded images

### StyleGAN

- File:
  - [`backend/app/ml/stylegan.py`](/C:/Users/HP/Documents/New%20project/backend/app/ml/stylegan.py)

- Current state:
  - Integration stub included for production handoff
  - Intended for external pretrained checkpoint hookup

## 4. Frontend

### Frontend Folder Structure

```text
frontend/
├── app/
│   ├── dashboard/page.tsx
│   ├── generate/page.tsx
│   ├── globals.css
│   ├── layout.tsx
│   ├── login/page.tsx
│   ├── page.tsx
│   ├── register/page.tsx
│   └── transform/page.tsx
├── components/
│   ├── auth-form.tsx
│   ├── generate-form.tsx
│   ├── image-grid.tsx
│   ├── navbar.tsx
│   ├── protected-route.tsx
│   ├── training-panel.tsx
│   └── upload-transform-form.tsx
├── lib/
│   ├── api.ts
│   └── auth.ts
└── types/
    └── index.ts
```

### Pages

- Home: platform overview and CTA
- Generate: DCGAN generation form and result grid
- Transform: drag-and-drop upload with CycleGAN direction selection
- Dashboard: image history, training jobs, live job counts, loss chart
- Login/Register: JWT auth flow

### API Integration

- [`frontend/lib/api.ts`](/C:/Users/HP/Documents/New%20project/frontend/lib/api.ts) configures Axios with `NEXT_PUBLIC_API_URL`
- JWT is attached by a request interceptor
- Forms call backend APIs directly and update UI state on completion
- Dashboard opens a WebSocket to `NEXT_PUBLIC_WS_URL` for real-time training refreshes

## 5. Database Design

### SQL Tables

#### `users`

- `id UUID-like string PK`
- `email VARCHAR(255) UNIQUE`
- `password_hash VARCHAR(255)`
- `full_name VARCHAR(255)`
- `is_active BOOLEAN`
- `created_at TIMESTAMP`

#### `generated_images`

- `id PK`
- `user_id FK -> users.id`
- `model_type VARCHAR(32)`
- `prompt TEXT NULL`
- `original_filename VARCHAR(255) NULL`
- `storage_key VARCHAR(500)`
- `public_url VARCHAR(500)`
- `width INT`
- `height INT`
- `created_at TIMESTAMP`

#### `training_jobs`

- `id PK`
- `user_id FK -> users.id`
- `model_type VARCHAR(32)`
- `dataset_name VARCHAR(64)`
- `status VARCHAR(32)`
- `epochs INT`
- `batch_size INT`
- `latent_dim INT`
- `learning_rate VARCHAR(32)`
- `beta1 VARCHAR(32)`
- `image_size INT`
- `checkpoint_path VARCHAR(500) NULL`
- `metrics_json TEXT NULL`
- `error_message TEXT NULL`
- `created_at TIMESTAMP`
- `updated_at TIMESTAMP`

## 6. Storage System

- Local default:
  - Generated and uploaded files stored in `storage/images`
  - Served by FastAPI as `/storage/images/<filename>`
- S3 optional:
  - Enable with `AWS_S3_ENABLED=true`
  - Configure bucket, region, access key, and secret
  - Backend uploads local artifacts to S3 and stores the public URL

## 7. Authentication

- JWT access tokens created in [`backend/app/core/security.py`](/C:/Users/HP/Documents/New%20project/backend/app/core/security.py)
- Passwords hashed with `bcrypt` via `passlib`
- Protected API routes use `OAuth2PasswordBearer`
- Frontend uses a lightweight auth context and redirects anonymous users to `/login`

## 8. Async Processing

- `POST /train` creates the job row
- Celery uses Redis broker/backend
- Worker executes DCGAN training in background
- Metrics and checkpoint path are written back to `training_jobs`
- Dashboard charts metrics from `metrics_json`

## 9. Deployment

### Local Development

1. Copy `.env.example` to `.env`
2. Start services:

```powershell
docker compose up --build
```

3. URLs:
- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Redis: `localhost:6379`
- PostgreSQL: `localhost:5432`

### Backend Hosting

- Render or Railway for CPU-only inference and API hosting
- AWS ECS or GCP Cloud Run for containerized deployment
- GPU-backed training:
  - AWS EC2 `g5`/`g6`
  - GCP Compute Engine GPU
  - Kubernetes node pools with NVIDIA runtime

### Frontend Hosting

- Vercel:
  - set `NEXT_PUBLIC_API_URL`
  - set `NEXT_PUBLIC_WS_URL`
- Netlify also works if websocket endpoint is external

### Model Hosting Strategy

- Small checkpoints can live in app-attached storage or S3
- Larger StyleGAN checkpoints should live in S3, EFS, or a model registry
- Separate inference workers from training workers when scaling

## 10. DevOps and Scaling

- Docker Compose orchestrates frontend, backend, worker, Redis, PostgreSQL
- Rate limiting middleware protects the API edge
- Scale workers horizontally:

```powershell
docker compose up --scale worker=3
```

- Recommended production hardening:
  - move from SQLite to PostgreSQL
  - add Alembic migrations
  - put Nginx or a managed gateway in front
  - enable S3 and CDN for media delivery
  - use separate queues for training and inference

## 11. Documentation and Run Commands

### Backend only

```powershell
cd backend
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Worker

```powershell
celery -A backend.celery_worker.celery_app worker --loglevel=info
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Notes

- The repo defaults to CPU for safety. Set `DEFAULT_DEVICE=cuda` when deploying on a GPU machine.
- StyleGAN is scaffolded as an integration point, not a bundled heavy checkpoint.
- The CycleGAN route is inference-ready but expects a trained checkpoint for meaningful output quality.

