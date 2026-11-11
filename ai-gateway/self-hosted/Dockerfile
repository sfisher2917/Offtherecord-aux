FROM node:22-alpine
WORKDIR /app
COPY server.js ./server.js
ENV HOST=0.0.0.0 PORT=8080 ENABLED=false ZERO_COST_VERIFIED=false
USER node
EXPOSE 8080
CMD ["node", "server.js"]
