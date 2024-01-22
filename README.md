# E-Commerce App

A Django REST Framework application for managing products, orders, and product statistics. It contains CRUD operations on products and orders, provides sales statistics of certain products and has a setup for confirmation and payment reminding emails which are managed by Celery and Redis.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
- [Usage](#usage)
  - [Product Operations](#product-operations)
  - [Order Operations](#order-operations)
  - [Product Statistics](#product-statistics)
- [API Documentation](#api-documentation)
- [License](#license)

## Features

- List, create, update, and delete products (sellers and admins only).
- Create orders (authenticated users only).
- List orders (sellers and admins only).
- Calculate and retrieve statistics on the most ordered products within a specified date range (sellers and admins only).

### Tech Stack

- Django
- Django REST Framework
- drf-spectacular
- SQLite
- Redis
- Celery
- Docker
- docker-compose
- django-allauth

### Installation
The easiest way to get started is to proceed to main directory of the app and run:
```
```bash
docker-compose up -d --build
```
and then to run the container:
```bash
docker-compose up
```

To log in to the admin panel (/admin/), use the following credentials:

- **Login:** testsuperuser
- **Password:** test12345

You can create your new test users from there and login on /accounts/login. For more URLs check out [API Documentation](#api-documentation).

### Tests
To run tests execute this command while container with the app is running
```bash
docker exec -it ecommerce_backend pytest .
```

### Usage
# Product Operations

- **List Products:** `GET /products`
  - Retrieve a list of all products with search, ordering, and pagination capabilities.

- **Retrieve Product:** `GET /products/{pk}`
  - Retrieve details of a specific product by its primary key.

- **Create Product:** `POST /products/create`
  - Create a new product. Only accessible to sellers and admins.

- **Update Product:** `PUT /products/{pk}`
  - Update details of a specific product by its primary key. Only accessible to sellers and admins.

- **Delete Product:** `DELETE /products/{pk}`
  - Delete a specific product by its primary key. Only accessible to sellers and admins.

# Order Operations

- **Create Order:** `POST /orders/create`
  - Create a new order. Only accessible to authenticated users.

- **List Orders:** `GET /orders`
  - Retrieve a list of all orders. Only accessible to sellers and admins.

# Product Statistics

- **Product Statistics:** `POST /orders/product_statistics`
  - Calculate and retrieve statistics on the most ordered products within a specified date range. Only accessible to sellers and admins.

# API Documentation

- Access the documentation at [http://0.0.0.0:8000/api/schema/docs](http://0.0.0.0:8000/api/schema/docs) (this host only in the container - localhost if running locally).

# License

This project is licensed under the MIT License.

