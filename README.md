# KarbonTarla

Tarladan, Karbon Borsasına — Türk çiftçilerini küresel karbon kredi pazarlarına bağlayan dijital platform.

## Hızlı Başlangıç

```bash
# 1. Ortam değişkenlerini düzenleyin
cp .env.example .env

# 2. Docker Compose ile tüm servisleri başlatın
docker compose up -d --build

# 3. Uygulamaya erişin
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# MinIO Console: http://localhost:9001
```

## Mimari

| Katman          | Teknoloji                         |
| --------------- | --------------------------------- |
| Frontend        | React 18 + TypeScript + Vite      |
| Backend         | FastAPI + SQLAlchemy Async         |
| Veritabanı      | PostgreSQL 15 + PostGIS            |
| Zaman Serisi    | TimescaleDB                        |
| Önbellek        | Redis 7                            |
| Nesne Depolama  | MinIO (S3-uyumlu)                  |
| IoT Broker      | Eclipse Mosquitto (MQTT)           |
| Görev Kuyruğu   | Celery + Redis                     |
| Konteyner       | Docker Compose                     |

## API Endpointleri

- `POST /api/v1/auth/register` — Kayıt
- `POST /api/v1/auth/login` — Giriş
- `GET  /api/v1/fields` — Tarla listesi
- `POST /api/v1/fields` — Tarla oluştur
- `GET  /api/v1/satellite/ndvi/{field_id}` — NDVI zaman serisi
- `POST /api/v1/carbon/calculate` — VM0042 karbon hesaplama
- `POST /api/v1/reports/generate` — MRV rapor oluştur
- `GET  /api/v1/marketplace/listings` — Pazar ilanları

## Karbon Hesaplama Metodolojisi

Verra VCS VM0042 — IPCC 2019 Tier 1:
- SOC_REF tablosu (iklim bölgesi + toprak tipi)
- FMG (yönetim faktörü) + FI (girdi faktörü)
- Belirsizlik kesintisi: %15
- Kalıcılık tamponu: %10
- CO₂/C oranı: 3.667

## Lisans

MIT
