FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
COPY .npmrc ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
