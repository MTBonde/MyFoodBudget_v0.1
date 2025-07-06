FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Copy and prepare startup script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Start Flask via custom entrypoint
CMD ["/entrypoint.sh"]
