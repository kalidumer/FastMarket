# FastMarket - Full-Stack E-Commerce Platform

FastMarket is a high-performance, responsive full-stack e-commerce application built with a modern decoupled architecture. It features a **FastAPI** backend with asynchronous database interactions, a **React + TypeScript** single-page application frontend powered by **Redux Toolkit & RTK Query**, and an automated testing suite for both backend and frontend layers.

---

## Tech Stack & Architecture

### **Frontend**
* **Framework:** React 18 with TypeScript & Vite
* **State Management:** Redux Toolkit & RTK Query (Caching & Async Mutations)
* **Routing:** React Router v6 (Protected Routes & Nested Layouts)
* **Styling:** Tailwind CSS (Responsive Design & Dynamic Dark Mode)
* **Testing:** Vitest + React Testing Library + JSDOM

### **Backend**
* **Framework:** FastAPI (Python 3.11)
* **Database & ORM:** PostgreSQL + SQLAlchemy / Tortoise ORM
* **Authentication:** JWT (JSON Web Tokens) with Passlib/Bcrypt password hashing
* **Testing:** Pytest + HTTPX / TestClient

---

## Repository Structure

```text
FastMarket/
├── backend-service/
│   ├── app/
│   │   ├── api/             # Auth, Product, and Cart API endpoints
│   │   ├── core/            # Config, Security, and JWT utilities
│   │   ├── models/          # Database ORM models
│   │   └── main.py          # FastAPI application entry point
│   ├── test/
│   │   ├── __init__.py
│   │   └── test_api.py      # Pytest backend API integration tests
│   └── conftest.py          # Pytest fixtures and test setup
│
├── frontend-service/
│   ├── src/
│   │   ├── components/      # UI components (ProductCard, Navbar, MainLayout)
│   │   ├── pages/           # Route views (Home, Login, Cart)
│   │   ├── store/           # Redux store & RTK Query API slices
│   │   └── test/            # Vitest setup & component tests
│   └── vite.config.ts       # Vite & Vitest configuration
│
└── README.md
