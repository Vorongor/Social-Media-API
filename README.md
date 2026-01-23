### Social Media API Service
A robust, scalable RESTful API built with Django and Django REST Framework (DRF). This platform provides the core backend infrastructure for a social media application, featuring user authentication, social networking graphs (follow/unfollow), content creation, and asynchronous task scheduling.

### **Features**

1) 🔐 Authentication & User Management
 - Secure Registration: User signup with email and password validation. (d)

 - Token-Based Auth: Secure login/logout flow using Token Authentication. (b/u)

 - Profile Management: Customizable user profiles including bios, avatars, and searchable metadata.

 - User Discovery: Search functionality to find other users by username or specific criteria.
2) 🤝 Social Graph
 - Follow System: Ability to follow and unfollow users to curate a personal feed.

 - Network Visibility: Endpoints to retrieve lists of followers and following counts.
3) 📝 Content Engine
 - Post Creation: Support for text-based posts with optional media attachments.

 - Smart Feed: Personalized retrieval of posts from the user's "Following" list.

 - Discovery: Search and filter posts via hashtags or keywords.

 - Interactions (Optional): Full support for liking/unliking posts and a nested commenting system.
4) ⏲️ Advanced Functionality
 - Scheduled Posts: Integration with Celery and Redis to allow users to schedule posts for future publication.

 - Permissions & Security: Granular Object-Level Permissions ensuring users can only edit or delete their own content.

### **🛠 Tech Stack**
1. Framework: Django
2. API Toolkit: Django REST Framework
3. Task Queue: Celery (with Redis broker)
4. Authentication: DRF Token Authentication 
5. Documentation: Swagger/OpenAPI (and Redoc)

### 🏗 API Architecture

| Endpoint                                   | Method              | Description                               | Auth Required |
|:-------------------------------------------|:--------------------|:-------------------------------------------|:-------------:|
| `/api/users/register/`                     | `POST`              | Register a new user                        | No            |
| `/api/users/login/`                        | `POST`              | User login                                 | No            |
| `/api/users/logout/`                       | `POST`              | User logout                                | Yes           |
| `/api/users/token/refresh/`                | `POST`              | Refresh access token                       | No            |
| `/api/users/token/verify/`                 | `POST`              | Verify access token                        | No            |
| `/api/users/`                              | `GET`               | Search and list user profiles              | Yes           |
| `/api/users/{id}/`                         | `GET`               | Retrieve specific user profile             | Yes           |
| `/api/users/me/`                           | `GET`               | Retrieve current user profile              | Yes           |
| `/api/users/me/`                           | `PUT`               | Update current user profile (full)         | Yes           |
| `/api/users/me/`                           | `PATCH`             | Update current user profile (partial)      | Yes           |
| `/api/users/{id}/follow/`                  | `POST`              | Follow or unfollow a user                  | Yes           |
| `/api/users/following/`                    | `GET`               | List users I follow                        | Yes           |
| `/api/users/subscribers/`                  | `GET`               | List my subscribers                        | Yes           |
| `/api/posts/`                              | `GET`               | List all posts                             | Yes           |
| `/api/posts/`                              | `POST`              | Create a new post                          | Yes           |
| `/api/posts/{id}/`                         | `GET`               | Retrieve a specific post                   | Yes           |
| `/api/posts/{id}/`                         | `PUT`               | Update a post (full)                       | Yes           |
| `/api/posts/{id}/`                         | `PATCH`             | Update a post (partial)                    | Yes           |
| `/api/posts/{id}/`                         | `DELETE`            | Delete a post                              | Yes           |
| `/api/posts/{id}/comments/`                | `POST`              | Add a comment to a post                    | Yes           |
| `/api/posts/{post_id}/comments/{id}/`      | `GET`               | Retrieve a specific comment                | Yes           |
| `/api/posts/{post_id}/comments/{id}/`      | `PUT`               | Update a specific comment                  | Yes           |
| `/api/posts/{post_id}/comments/{id}/`      | `DELETE`            | Delete a specific comment                  | Yes           |
| `/api/posts/{id}/likes/`                   | `POST`              | Like or unlike a post                      | Yes           |
| `/api/posts/my-blog/`                      | `GET`               | Retrieve my posts                          | Yes           |
| `/api/posts/subscriptions/`                | `GET`               | Retrieve posts from subscriptions          | Yes           |

### **Getting started:**
1) Create .env file, than copy and populate data from .env.sample
```env
# Django
SECRET_KEY=test-key-p%a$2tq6!x2g&e9!-0i(u8%ppgh9y0jdey8znugj+xdzw)7=i*
# PostgreSQL
POSTGRES_DB=media_db
POSTGRES_USER=media_user
POSTGRES_PASSWORD=media_vector_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
# Celery
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
```
2) Start project
``` sh
    docker-compose up --build
```
3) Create superuser and test the app:
```sh
    docker-compose exec wed python manage.py createsuperuser
```

### **If you need run any command via docker compose**
```sh
    docker compose exec <app_name> <command> 
```
app names:
- redis > Redis database
- db > PostgreSQL database
- web > Django app
- celery > Celery workers and tasks
- celery-beat > Celery beat schedule and tasks