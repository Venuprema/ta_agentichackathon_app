# Wendy's Hackathon – Streamlit app for Cloud Run
# Port 8080, address 0.0.0.0 for container networking

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate data at build time (so container has CSVs without .env)
RUN python scripts/generate_data.py --output-dir /app/data

# Cloud Run expects HTTP on PORT (default 8080)
ENV PORT=8080
EXPOSE 8080

# Streamlit: port from env, listen on all interfaces
CMD streamlit run streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true
