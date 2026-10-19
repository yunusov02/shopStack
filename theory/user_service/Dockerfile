# FROM node:latest

# WORKDIR /app

# ADD . .

# RUN npm install

# CMD ["node", "index.js"]




FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install 

COPY . .

CMD [ "node", "index.js" ]




# first build the image

# docker build --tag user-api:latest .

# then create container

# docker run --name user-api -d -p 3000:3000 user-api:latest

