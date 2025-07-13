# 🌾 Farmer Portal (Microservice)

A microservice-based farmer platform empowering agricultural operations through seamless **transportation**, **e-commerce**, and **real-time auctions**, with an **open public dashboard** for product insights.

---

## 📘 Overview

**Agroir** is a digital solution designed to support farmers in three major verticals:
- **Transportation Service:** Book one-way truck journeys for efficient goods movement.
- **E-commerce Service:** Sell farmer-manufactured goods directly to consumers.
- **Auction Service:** Set fair market prices through bidding for daily-use products like cereals, vegetables, and fruits.
- **Open Dashboard:** Monitor real-time public insights, trends, and prices of all listed agricultural goods.

---

## 🧱 Architecture

Agroir is built on a **microservice architecture**, with each service responsible for an independent domain.

### Technologies Used
- **Backend:** Python (Django & Django REST Framework)
- **Database:** PostgreSQL
- **API Gateway:** FastAPI
- **Authentication:** JWT (role-based)
- **Frontend:** React (Frontend)
- **Communication:** REST APIs (future: RabbitMQ/Kafka for async messaging)

---

## 🚀 Microservices

| Service Name          | Description |
|-----------------------|-------------|
| `user_service`        | Handles authentication and authorization for Farmers, Transporters, and Consumers. |
| `transportation_service` | Enables transporters to list routes and farmers to book segment-based goods transport. |
| `ecom_service`        | Farmers can post, update, and manage product listings; Consumers can view and book. |
| `auction_service`     | Enables price bidding per product/zone, with real-time pricing updates and dashboards. |
| `open_dashboard_service` | Public-facing API to show insights and statistics of products per zone. |

---



### Prerequisites
- Python 3.10+
- PostgreSQL
- NodeJs 
- FASTAPI
