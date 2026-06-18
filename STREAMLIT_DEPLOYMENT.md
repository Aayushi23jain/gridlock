# Streamlit Deployment Guide

## Quick Deployment

### Streamlit Cloud (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Streamlit deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `app.py` as main file
   - Click "Deploy"

### Requirements Files

#### `requirements.txt` (Python dependencies)
✅ **Ready for Streamlit Cloud deployment**

- CPU-optimized PyTorch versions
- All necessary Python packages
- Version constraints for stability
- Compatible with Streamlit Cloud environment

#### `apt_packages.txt` (System dependencies)
⚠️ **Optional for Streamlit Cloud**

- Only needed for container-based deployments
- Most system packages are pre-installed on Streamlit Cloud
- May be needed for advanced PDF processing

## Configuration Files

### `.streamlit/config.toml` ✅
Current configuration is optimized for production:
- Headless mode enabled
- CORS disabled for security
- Custom dark theme
- Performance optimized

## Deployment Checklist

### Before Deploying

- [x] `requirements.txt` is up to date
- [x] `app.py` is the main entry point
- [x] `.streamlit/config.toml` configured
- [x] No hardcoded local paths
- [x] Database uses relative paths
- [x] Model files are included or downloadable

### Large File Handling

**Issue:** YOLOv8 model file (`yolov8n.pt`, ~6MB) and test data may be too large.

**Solutions:**

1. **Include model in repository** (if small enough)
   ```bash
   git add yolov8n.pt
   git commit -m "Add YOLOv8 model"
   ```

2. **Download model on startup** (recommended)
   Add to `app.py`:
   ```python
   def download_model():
       from ultralytics import YOLO
       model_path = "yolov8n.pt"
       if not os.path.exists(model_path):
           YOLO(model_path)  # Downloads automatically
   
   # Call at startup
   download_model()
   ```

3. **Use external storage** for large files
   - AWS S3
   - Google Cloud Storage
   - Cloudflare R2

## Environment Variables

Streamlit Cloud supports secrets for sensitive data:

**Set in Streamlit Cloud:**
- API keys (if using external services)
- Database URLs (if using external database)
- Configuration settings

**Access in code:**
```python
import os
api_key = os.getenv("API_KEY", "default_value")
```

## Performance Optimization

### Memory Management
```python
# In app.py, add caching
@st.cache_resource
def get_pipeline():
    return TrafficViolationPipeline()

# Cache heavy operations
@st.cache_data
def process_large_image(image_path):
    # Processing logic
    pass
```

### File Upload Limits
```python
# In .streamlit/config.toml
[server]
maxUploadSize = 200  # MB
```

## Troubleshooting

### Common Issues

**1. Out of Memory**
- Reduce image resolution
- Use model quantization
- Limit concurrent users

**2. Slow Startup**
- Cache model loading
- Use lazy loading
- Optimize imports

**3. PDF Processing Errors**
- System packages may be needed
- Use container deployment
- Implement fallback options

**4. Model Download Fails**
- Check network connectivity
- Use mirror URLs
- Pre-download and include model

## Monitoring

### Streamlit Cloud Features
- Built-in metrics dashboard
- Resource usage monitoring
- Error logging
- User analytics

### Custom Monitoring
```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Violation detected: {violation_type}")
```

## Scaling

### Free Tier Limitations
- CPU-only processing
- Limited memory
- Community support
- Some restrictions

### Paid Tier Benefits
- GPU support (for faster inference)
- More memory
- Priority support
- Custom domains
- Advanced security

## Alternative Deployments

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Railway, Render, or other platforms
- Similar to Streamlit Cloud
- May require different configuration
- Check platform-specific requirements

## Security Considerations

### File Upload Security
```python
# Validate file types
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4'}

def validate_file(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    return file_ext in ALLOWED_EXTENSIONS
```

### Rate Limiting
```python
# Implement rate limiting for API usage
import time
from functools import wraps

def rate_limit(max_calls=10, period=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Rate limiting logic
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Cost Estimation

### Streamlit Cloud Pricing
- **Free:** $0/month (limited resources)
- **Pro:** $12/month (more resources)
- **Team:** Custom pricing

### Resource Usage
- **Memory:** ~500MB base + model size
- **CPU:** Variable based on usage
- **Storage:** Included in plan

## Backup and Recovery

### Database Backup
```python
# Implement periodic backups
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/violations_db_{timestamp}.db"
    shutil.copy("storage/violations.db", backup_path)
    return backup_path
```

### Evidence Storage
- Use external storage for long-term
- Implement cleanup policies
- Archive old evidence files

## Support and Resources

### Official Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [Deployment Guide](https://docs.streamlit.io/deploy)

### Community
- [Streamlit Forum](https://discuss.streamlit.io)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

### Project-Specific
- Check project README for usage
- Review test files for examples
- Use test data for validation