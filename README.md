# UPAK Ecosystem

UPAK (Universal Processing and API Kit) - A robust ecosystem featuring REST API, secure webhooks, and Telegram bot integration.

## Features

- **REST API**: Full-featured API with rate limiting and error handling
- **Secure Webhooks**: HMAC-SHA256 signature verification
- **Telegram Bot Integration**: Send notifications and messages
- **Rate Limiting**: Configurable rate limits per endpoint
- **Health Monitoring**: Built-in health checks and status endpoints
- **Docker Support**: Containerized deployment with Docker Compose
- **Comprehensive Testing**: Full test suite with pytest

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/v1/status` - API status and version info
- `GET|POST /api/v1/data` - Main data handling endpoint

### Integration Endpoints
- `POST /webhook` - Secure webhook handler
- `POST /telegram/send` - Send Telegram messages

## Quick Start

### Local Development

1. Install dependencies:
   ```bash
   make install
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Configure your environment variables in `.env`

4. Run the application:
   ```bash
   make run-dev
   ```

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   make docker-build
   make docker-run
   ```

## Testing

Run the full test suite:
```bash
make test
```

Run tests with verbose output:
```bash
make test-verbose
```

## Configuration

### Environment Variables

- `WEBHOOK_SECRET`: Secret key for webhook signature verification
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `TELEGRAM_CHAT_ID`: Default chat ID for Telegram messages
- `PORT`: Application port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

### Rate Limiting

- Default: 100 requests per hour
- API endpoints: 50 requests per minute
- Data endpoints: 30 requests per minute
- Telegram endpoints: 10 requests per minute

## Security Features

- HMAC-SHA256 webhook signature verification
- Rate limiting on all endpoints
- Input validation and sanitization
- Secure error handling
- Request logging and monitoring

## Monitoring

- Health check endpoint: `/health`
- Status endpoint: `/api/v1/status`
- Docker health checks included
- Comprehensive logging

## Version

Current version: **1.1.0**

## License

MIT License
