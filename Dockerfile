FROM ubuntu:latest
LABEL authors="andreiut"

FROM python:3.12.0

ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    curl \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcups2 \
    libxss1 \
    libgconf-2-4 \
    libnss3-dev \
    libxshmfence1 \
    libgbm1 \
    libgtk-3-0 \
    xvfb


# Install Google Chrome
# Download and install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/google-chrome-stable_current_amd64.deb && \
    apt-get install -y /tmp/google-chrome-stable_current_amd64.deb && \
    rm /tmp/google-chrome-stable_current_amd64.deb

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=127.0.0 && \
    wget -O /tmp/chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.88/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver_linux64.zip -d /tmp/ && \
    mkdir -p /usr/local/bin && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Clean up
RUN rm -rf /tmp/* && \
    apt-get clean

# Verify installations
RUN google-chrome --version && chromedriver --version
RUN echo "chrome: $(which google-chrome)" && echo "chromedriver: $(which chromedriver)"

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "news_scrapper.py"]