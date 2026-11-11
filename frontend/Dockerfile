# 1) Compila el frontend con Vite.
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vacío = misma dirección que la página: nginx reenvía /api al backend.
ENV VITE_API_URL=""
ENV VITE_USAR_SIMULADO=false
RUN npm run build

# 2) Sirve los archivos estáticos con nginx.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
