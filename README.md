Requirements:
1. Docker
Optional Requirements:
1. Python 3.x
2. Postgres


Starting Locally:
1. Run Script: start
2. e.g. sh ./start
3. Open localhost:8000
4. Login with Credentials: 
    email: admin@admin.com
    password: admin
5. Create a new User
6. Edit newly created User and set Superuser status to checked
7. Logout, and Login with new User
8. Delete admin@admin.com User


Deploying to Heroku:
1. Follow instructions on Heroku
2. Create new app called: prevencija
3. Create Heroku API Key as its instructed on Heroku
4. Change existing HEROKU_API_KEY in deploy file to new one
5. Run sh ./deploy
6. Follow instructions from Starting Locally from 4-8# bigbrotherbigsister
