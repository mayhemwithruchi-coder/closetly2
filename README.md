# Closetly - Fashion Recommendation App

A personalized fashion recommendation platform with AI-powered price predictions, deployed on Render.

## Features

- Personalized fashion recommendations based on body type and color analysis
- AI-powered price prediction for fashion items
- Price comparison across multiple Indian retailers
- Responsive web interface with interactive quiz

## Deployment to Render

### Prerequisites

1. A [Render](https://render.com) account
2. This repository (already cloned)

### Deployment Steps

1. Go to your Render Dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository or upload your code
4. Configure the following settings:
   - **Name**: `closetly-fashion-india`
   - **Region**: `Singapore` (or your preferred region)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free` (or your preferred plan)

5. Add the following environment variables:
   - `PYTHON_VERSION`: `3.12.6`
   - `PORT`: `10000`

6. Click "Create Web Service"

### File Structure

```
.
├── backend/
│   ├── app.py              # Main Flask application
│   ├── render.yaml         # Render deployment configuration
│   ├── requirements.txt    # Python dependencies
│   └── closetly_india_complete.html  # Main HTML file
├── price_api_integration.js  # JavaScript for API integration
├── runtime.txt             # Python runtime version
└── README.md               # This file
```

### Local Development

To run the application locally:

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. Run the application:
   ```bash
   python backend/app.py
   ```

3. Open your browser to `http://localhost:10000`

### API Endpoints

- `GET /` - Main application interface
- `GET /health` - Health check endpoint
- `POST /predict` - Predict price for a single item
- `POST /compare` - Compare prices across retailers
- `POST /batch_predict` - Predict prices for multiple items

## Technologies Used

- Python Flask (Backend)
- HTML/CSS/JavaScript (Frontend)
- Render (Deployment)
- Gunicorn (WSGI Server)

## Troubleshooting

If you encounter issues during deployment:

1. Check that all required files are in the correct locations
2. Verify that the `requirements.txt` file contains all necessary dependencies
3. Ensure the `render.yaml` file is properly configured
4. Check the Render logs for specific error messages

For support, please open an issue on the repository.