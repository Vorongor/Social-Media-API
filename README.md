### Social Media API Service
A robust, scalable RESTful API built with Django and Django REST Framework (DRF). This platform provides the core backend infrastructure for a social media application, featuring user authentication, social networking graphs (follow/unfollow), content creation, and asynchronous task scheduling.

### **Features**

1) 🔐 Authentication & User Management
 - Secure Registration: User signup with email and password validation.

 - Token-Based Auth: Secure login/logout flow using Token Authentication.

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
3. Task Queue: Celery (with Redis/RabbitMQ broker)
4. Authentication: DRF Token Authentication 
5. Documentation: Swagger/OpenAPI (or Redoc)

### 🏗 API Architecture

| Endpoint | Method | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `/api/auth/register/` | `POST` | Create a new user account | No |
| `/api/auth/login/` | `POST` | Obtain authentication token | No |
| `/api/auth/logout/` | `POST` | Invalidate token and sign out | Yes |
| `/api/profiles/` | `GET/PUT` | Manage/Update your own profile | Yes |
| `/api/profiles/{username}/` | `GET` | View another user's profile | Yes |
| `/api/users/{id}/follow/` | `POST` | Follow/Unfollow a specific user | Yes |
| `/api/posts/` | `GET/POST` | List personal feed or create a new post | Yes |
| `/api/posts/{id}/` | `GET/DELETE` | Retrieve or delete a specific post | Yes |
| `/api/posts/{id}/like/` | `POST` | Like or unlike a specific post | Yes |
| `/api/posts/{id}/comments/` | `GET/POST` | View or add comments to a post | Yes |
| `/api/posts/scheduled/` | `POST` | Schedule a post for a future date | Yes |


### **Getting started:**