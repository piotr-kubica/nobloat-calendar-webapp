
# Nobloat Calendar Web App

Simple, no-bloat calendar and note-taking web application built with Vue (frontend) and Flask (backend).

---

## Features

- **Mark calendar days**: Tap or click to mark days and add notes.
- **Note-taking**: Attach short notes to any calendar day.
- **User authentication**: Login system with a default demo user.
- **Persistent storage**: Data is stored in a SQLite database (auto-created on first run).
- **Mobile-friendly**: Responsive design for mobile and desktop.

---

## Screenshot

Screenshot from app on mobile:
<img src="cal-image.jpg" alt="calendar app on mobile" width="300"/>

---

## Default User

- **Username**: `demouser`
- **Password**: `nobloat`

To add more users, either modify the backend code and redeploy, or use `sqlite3` inside the backend container.

---

## Local Deployment

You can run the app locally using Docker Compose:

```bash
git clone https://github.com/piotr-kubica/nobloat-calendar-webapp.git
cd nobloat-calendar-webapp
docker-compose up --build
```

The frontend will be available at [http://localhost:5173](http://localhost:5173) and the backend API at [http://localhost:5000](http://localhost:5000).

---

## Adding Users

To add a user manually:

1. Enter the backend container:
	```bash
	docker exec -it nobloat-calendar-backend-1 bash
	```
2. Use `litecli` or `sqlite3` to modify the database:
    ```bash
	litecli /data/acitivities.db
	```
	```bash
	sqlite3 /data/acitivities.db
	```
4. Insert a new user as needed.

---

## Deployment (Portainer Example)

You can deploy directly from the GitHub repository using Portainer:

1. Go to **Stacks** → **Add stack** → **Repository**.
2. Enter the repository URL and deploy.

---

## License

See [LICENSE](LICENSE).
