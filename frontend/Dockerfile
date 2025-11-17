FROM python:3.9-slim

WORKDIR /app

# Copy everything in the frontend folder into the image
COPY . .

# Serve static files (index.html, etc.) with Python's HTTP server
EXPOSE 80
CMD ["python", "-m", "http.server", "80"]
