FROM node:18

# Install Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    xdg-utils \
    --no-install-recommends

# Copy app files
COPY . .

# Install dependencies
RUN npm install

# Start the app
CMD ["npm", "start"]
