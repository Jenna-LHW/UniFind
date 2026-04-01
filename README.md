# UniFind – Lost & Found Management System

## Overview

**UniFind** is a full-stack Lost & Found management system designed to help Uom students and staffs report, search, and recover lost or found items efficiently.

The system provides a **RESTful API** built with Django REST Framework, allowing seamless integration with web or mobile frontends.

## Features

### User Features

* Register and manage user profiles
* Report **lost items**
* Report **found items**
* Browse all lost and found items
* Contact system
* Leave reviews and feedback

### Admin Features

* Manage lost & found listings
* Respond to user messages
* Moderate reviews and replies

### API Features

* Fully RESTful endpoints
* CRUD operations for:

  * Lost Items
  * Found Items
  * Contact Messages
  * Reviews & Replies
* JSON responses for easy frontend integration

## Tech Stack

* **Backend:** Django
* **API:** Django REST Framework
* **Database:** SQLite (default) 


## Project Structure

```
UniFind/
│── UniFind/
│   ├── settings.py
│   ├── urls.py
│
│── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── forms.py
│   ├── urls.py
│
│── media/
│── db.sqlite3
│── manage.py
```

## Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/Jenna-LHW/UniFind.git
cd unifind
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Server

```bash
python manage.py runserver
```

## API Endpoints

Base URL:

```
http://127.0.0.1:8000/api/
```

### Items

| Method | Endpoint      | Description         |
| ------ | ------------- | ------------------- |
| GET    | /lost-items/  | List all lost items |
| POST   | /lost-items/  | Create lost item    |
| GET    | /found-items/ | List found items    |
| POST   | /found-items/ | Create found item   |

### Contact

| Method | Endpoint   | Description   |
| ------ | ---------- | ------------- |
| GET    | /messages/ | List messages |
| POST   | /messages/ | Send message  |

### Reviews

| Method | Endpoint  | Description     |
| ------ | --------- | --------------- |
| GET    | /reviews/ | List reviews    |
| POST   | /reviews/ | Add review      |
| POST   | /replies/ | Reply to review |

## Router Configuration

The API uses Django REST Framework's `DefaultRouter`:

```python
router.register(r'lost-items', LostItemViewSet)
router.register(r'found-items', FoundItemViewSet)
router.register(r'messages', ContactMessageViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'replies', ReviewReplyViewSet)
```
## Media Handling

* Uploaded images are stored in `/media/`
* Ensure this is configured in `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Future Improvements

* JWT Authentication
* Mobile app integration

## Inspiration

Adapted from a **group university assignment** for the Web and Mobile Development module at UoM.
