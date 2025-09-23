# Use official Node.js LTS image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --only=production

# Copy all source files
COPY . ./

# The build-flag script needs a passphrase to encrypt the flag.
# We can pass it as a build argument. The server also needs this passphrase
# to decrypt the flag later, so we set it as an environment variable.
ARG FLAG_PASSPHRASE_ARG="a_default_passphrase_for_the_build"
ENV FLAG_PASSPHRASE=$FLAG_PASSPHRASE_ARG
RUN npm run build-flag

# Expose the challenge port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
