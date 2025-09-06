Vue + Flask web app for simple calendar marking / note taking.

Screenshot from app on mobile
<img src="cal-image.jpg" alt="calendar app on mobile" width="300"/>


I'm using portainer to directly deploy from github repository (Create stack -> Repository).

The app contains a default user __demouser__ with password __nobloat__.
The database is stored inside a volume and will be created the first time the app runs.
To add a user change the code and redeploy or use sqlite3 from inside the backend container.
