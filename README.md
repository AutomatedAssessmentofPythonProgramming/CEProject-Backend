# Backend

## install && Dependencies

        python -m venv env
        pip install -r requirements.txt

install grader-utils

        git clone --depth 1 https://github.com/apluslms/python-grader-utils.git
        cd python-grader-utils
        pip install .

comment code

setting.py

        INSTALLED_APPS = [
        ...
        #'django.contrib.admin',
        ...
        ]

api/urls.py
authentication/urls.py

        urlpatterns = [
        ...
        #path('admin/', admin.site.urls) 
        ...
        ]

create file .env or env.bat in window

        source .env // call env.bat in window

run migrate database

        python manage.py migrate

uncomment admin

setting.py

        INSTALLED_APPS = [
        ...
        'django.contrib.admin',
        ...
        ]

api/urls.py
authentication/urls.py

        urlpatterns = [
        ...
        path('admin/', admin.site.urls) 
        ...
        ]

run again

        python manage.py migrate
        python manage.py runserver

## PATH

        /api/exercise/

- method post

create exercise

        /api/exercise/{pk}

- method get

get an exercise by id

- method patch

updated an exercise specified by id

- mothod delete

delete an exercise by id

        /api/submission-list/

- method get

get all our submissions wait to fix!!! submission models

        /api/team/

- method post

create team

        /api/team/{pk}

- method get

get a team by id

- method patch

updated a team by id

- method delete

delete a team by id

        /api/team/{pk}/exercises

- method get

get team's exercises through workbooks

        /api/team/{pk}/members/

- method get

get team's members through membership

        /api/team-list/

- method get

        /api/team/{pk}/exercises

- method get

get exercises of team by teamId

        /api/exercise/{pk}/submit

- method post

submit exercise

        /api/workbook/

- method post

create workbook

        /api/workbook/{pk}

- method get

get exercise by id

- method patch

updated exercise by id

- method delete

delete exercise by id

        /add-member/

- method post

add member to team by using inviteCode

        /submission/{exerciseId}/team/{teamID}

- method get

Get list of user that submit exercises filter by teamId and exerciseId

get user

        /auth/register/
        /auth/login/
        /auth/logout/
        /auth/email-verify/
        /auth/token-refresh/
        /auth/user/profile/
        /auth/request-reset-email/
        /auth/password-reset-complete
        /auth/password-reset/<uidb64>/<token>/

## Error

ลืม source .env ทำให้เกิด error 530, b'5.7.0 Authentication Required.
