# Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker Desktop installed
- `.env` file configured (copy from `.env.example`)

### 1. Configure Environment
Create `.env` in project root:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn
```

### 2. Start All Services
```bash
docker-compose up -d
```

This starts:
- Redis (port 6380)
- Backend API (port 8000)
- Worker (background jobs)
- Frontend (port 3000)

### 3. Verify Services
```bash
# Check all containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/api/v1/health/redis

# Access frontend
open http://localhost:3000
```

### 4. Stop Services
```bash
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Manual Deployment

### Backend

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment
Create `backend/.env`:
```env
REDIS_URL=redis://localhost:6380/0
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-key
SENTRY_DSN=your-sentry-dsn
ENVIRONMENT=production
```

#### Run API
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Run Worker
```bash
cd backend
python worker.py
```

### Frontend

#### Install Dependencies
```bash
npm install
```

#### Configure Environment
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

#### Build and Run
```bash
npm run build
npm start
```

---

## Production Deployment

### Option 1: Docker Compose (Recommended)

1. **Set up server** (Ubuntu 22.04 or similar)
2. **Install Docker** and Docker Compose
3. **Clone repository**
4. **Configure `.env`** with production values
5. **Run**: `docker-compose up -d`
6. **Set up reverse proxy** (Nginx/Caddy) for HTTPS
7. **Configure domain** and SSL certificates

### Option 2: Platform-as-a-Service

#### Backend (Railway, Render, Fly.io)
1. Connect GitHub repository
2. Set environment variables
3. Deploy API and Worker as separate services
4. Provision Redis addon

#### Frontend (Vercel, Netlify)
1. Connect GitHub repository
2. Set environment variables
3. Deploy with automatic builds

---

## Environment Variables Reference

### Backend
| Variable | Required | Description |
|----------|----------|-------------|
| `REDIS_URL` | Yes | Redis connection string |
| `SUPABASE_JWT_SECRET` | Yes | JWT signing secret |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service key |
| `SENTRY_DSN` | No | Sentry error tracking |
| `ENVIRONMENT` | No | Environment name (production/staging) |

### Frontend
| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon key |

---

## Monitoring

### Health Checks
- API: `GET /api/v1/health/redis`
- Metrics: `GET /api/v1/metrics/queues`
- Workers: `GET /api/v1/metrics/workers`

### Logs
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Manual
tail -f backend/logs/app.log
```

### Sentry Integration
Set `SENTRY_DSN` to enable error tracking and performance monitoring.

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
worker:
  deploy:
    replicas: 3  # Run 3 worker instances
```

### Load Balancing
Use Nginx or cloud load balancer to distribute traffic across multiple API instances.

---

## Backup

### Redis Data
```bash
# Backup
docker exec pulsecompass-redis redis-cli SAVE
docker cp pulsecompass-redis:/data/dump.rdb ./backup/

# Restore
docker cp ./backup/dump.rdb pulsecompass-redis:/data/
docker restart pulsecompass-redis
```

### Database
Follow Supabase backup procedures for PostgreSQL data.

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Redis connection issues
```bash
# Test Redis
docker exec pulsecompass-redis redis-cli ping

# Check network
docker network inspect pulsecompass_default
```

### Worker not processing jobs
```bash
# Check worker logs
docker-compose logs worker

# Verify Redis connection
docker exec pulsecompass-worker python -c "from core.redis import get_redis; print(get_redis().ping())"
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secrets
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring/alerts
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Secrets in environment variables (not code)

---

## CI/CD

GitHub Actions workflow is configured in `.github/workflows/ci-cd.yml`:
- Runs tests on push
- Builds Docker images
- Deploys to production on main branch

Configure secrets in GitHub repository settings.
