FROM python:3.9

WORKDIR /app

# Copy requirements and script
COPY requirements.txt .
COPY main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set up Kaggle credentials
# Note: You'll need to provide your kaggle.json file
COPY kaggle.json /root/.kaggle/
RUN chmod 600 /root/.kaggle/kaggle.json

# Run script
CMD ["python", "main.py"]
