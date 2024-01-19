# Django Todo App

A Django REST Framework application for managing products, orders, and product statistics.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
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

## Getting Started

### Prerequisites

- Django
- Django REST Framework
- drf-spectacular
- SQLite

### Installation
To setup the app locally after cloning the repository create a virtual environment and install requirements.txt:

```bash
git clone git@github.com:szymon-zuk/E-commerce-App.git
cd E-commerce-App/ecommerceapp
python -m venv venv
source ./bin/activate
pip install -r requirements.txt
```
Then apply migrations and run the server:
```bash
python manage.py migrate
python manage.py runserver
```
If you want to use Docker (easier way to get started) being in the main directory ot the app run:
```bash
cd ecommerceapp
docker-compose up -d --build
```
and then to run the container:
```bash
docker-compose up
```

To log in to the admin panel, use the following credentials:

- **Login:** testsuperuser
- **Password:** test12345

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

- Access the documentation at [http://localhost:8000/api/schema/docs](http://localhost:8000/api/schema/docs)

# License

This project is licensed under the MIT License.

