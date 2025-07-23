# Dockerfile
FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create directories
RUN mkdir -p data logs

# Expose port (if needed for webhooks)
EXPOSE 3000

# Start the bot
CMD ["node", "bot.js"]
