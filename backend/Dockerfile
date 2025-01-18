# Dockerfile for backend
FROM node:16

# Set the working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Download wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy the rest of your application code
COPY . .

# Expose the necessary port
EXPOSE 3001

# Command to start the app
CMD ["sh", "-c", "/usr/local/bin/wait-for-it mysql:3306 -- node index.js"]