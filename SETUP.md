# Setup Guide - AI Voice Assistant

This guide will walk you through setting up the AI Voice Assistant application from scratch.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: At least 1GB free space

### Required Accounts & API Keys
- **Google Cloud Account**: For Gemini API access
- **Domain/Server**: For production deployment (optional)

### Browser Requirements
- **Chrome**: 60+ (recommended)
- **Firefox**: 55+
- **Safari**: 11+
- **Edge**: 79+

## 🔧 Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd ai-voice-assistant

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Environment

#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Option B: Using Conda
```bash
# Create conda environment
conda create -n ai-voice-assistant python=3.9
conda activate ai-voice-assistant
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# If you encounter issues, try upgrading pip first:
pip install --upgrade pip
```

#### Common Installation Issues

**PyAudio Installation (Windows)**
```bash
# If PyAudio fails to install, try:
pip install pipwin
pipwin install pyaudio
```

**Tesseract OCR Installation**

*Windows:*
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and note the installation path
3. Update `screen_analyzer.py` with the correct path:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

*macOS:*
```bash
brew install tesseract
```

*Linux (Ubuntu/Debian):*
```bash
sudo apt-get install tesseract-ocr
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Application Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000

# Optional: Voice Configuration
TTS_ENGINE=gtts
VOICE_GENDER=female
VOICE_LANGUAGE=en

# Optional: Widget Configuration
WIDGET_TITLE=AI Voice Assistant
WIDGET_THEME=modern
```

### Step 5: Obtain Google Gemini API Key

1. **Go to Google AI Studio**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Choose your Google Cloud project (or create a new one)
   - Copy the generated API key

3. **Add to Environment**
   - Paste the API key in your `.env` file:
   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```

### Step 6: Test the Installation

```bash
# Run the application
python app.py
```

You should see output similar to:
```
INFO:werkzeug: * Running on all addresses (0.0.0.0)
INFO:werkzeug: * Running on http://127.0.0.1:5000
INFO:werkzeug: * Running on http://[your-ip]:5000
```

### Step 7: Verify Setup

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Check the demo page** loads correctly
3. **Test the widget** appears in the bottom-right corner
4. **Try voice features** (allow microphone permissions when prompted)

## 🌐 Production Deployment

### Option 1: Simple Production Setup

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
```

Build and run:
```bash
# Build Docker image
docker build -t ai-voice-assistant .

# Run container
docker run -p 5000:5000 --env-file .env ai-voice-assistant
```

### Option 3: Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your-api-key

# Deploy
git push heroku main
```

#### AWS/GCP/Azure
- Use their respective container services
- Set up load balancer for multiple instances
- Configure SSL certificates
- Set up monitoring and logging

## 🔒 Security Configuration

### Production Environment Variables

```env
# Use strong secret key
SECRET_KEY=your-very-long-random-secret-key

# Disable debug mode
FLASK_DEBUG=False

# Restrict CORS origins
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Use HTTPS
FORCE_HTTPS=True
```

### SSL/HTTPS Setup

#### Using Nginx (Recommended)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🧪 Testing & Validation

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Demo page loads at `http://localhost:5000`
- [ ] Widget appears and is interactive
- [ ] Microphone permissions work
- [ ] Voice recognition responds
- [ ] AI responses are generated
- [ ] Screen sharing functions
- [ ] Chat interface works
- [ ] Widget is draggable
- [ ] Minimize/maximize works

### Automated Testing

```bash
# Run basic connectivity test
curl http://localhost:5000/api/config

# Test AI endpoint
curl -X POST http://localhost:5000/api/ai-query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'
```

### Performance Testing

```bash
# Install testing tools
pip install locust

# Run load test (create locustfile.py first)
locust -f locustfile.py --host=http://localhost:5000
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError" for dependencies
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements.txt
```

#### 2. Gemini API errors
- Verify API key is correct
- Check API quotas and billing
- Ensure API is enabled in Google Cloud Console

#### 3. Voice recognition not working
- Check microphone permissions in browser
- Ensure HTTPS in production (required for microphone access)
- Try different browsers

#### 4. Screen sharing fails
- Ensure HTTPS (required for screen capture)
- Check browser permissions
- Try different browsers

#### 5. Widget not loading on external sites
- Check CORS configuration
- Verify server URL is accessible
- Check browser console for errors

### Debug Mode

Enable detailed logging:
```bash
export FLASK_DEBUG=True
export PYTHONPATH=.
python app.py
```

### Log Analysis

Check application logs:
```bash
# View recent logs
tail -f app.log

# Search for errors
grep ERROR app.log
```

## 📊 Monitoring & Maintenance

### Health Checks

Create a health check endpoint:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### Monitoring Tools

- **Application Performance**: New Relic, DataDog
- **Uptime Monitoring**: Pingdom, UptimeRobot
- **Error Tracking**: Sentry, Rollbar

### Regular Maintenance

- **Update dependencies** monthly
- **Monitor API usage** and costs
- **Review logs** for errors
- **Test functionality** regularly
- **Backup configuration** and data

## 🔄 Updates & Upgrades

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages (be careful)
pip install --upgrade -r requirements.txt
```

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart application
# (method depends on your deployment)
```

## 📞 Support

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review the logs** for error messages
3. **Test with minimal configuration** first
4. **Check browser console** for JavaScript errors
5. **Verify API keys and permissions**

For additional help:
- Create an issue on GitHub
- Check the main README.md
- Review the API documentation

---

**Next Steps**: Once setup is complete, see the main README.md for usage examples and integration guides.

