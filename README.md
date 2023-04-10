# Backend

## install && Dependencies
pip freeze > requirements.txt
pip install requirements.txt

## path
        /api/exercise/

- method post

create exercise

    /api/exercise/{id}

- method get

get an exercise by id

- method patch

modified an exercise specified by id

- mothod delete

delete an exercise by id

        /api/exercise/{id}/members

- method get

get student's submissions have to fix!! 

permission have to be staff

        /api/sibmission-list/

- method get

get all our submissions wait to fix!!! submission models

        /api/team/

- method post

create team

        /api/team/{id}

- method get

get a team by id

- method patch

modify a team by id

- method delete

delete a team by id

        /api/team/{id}/exercises

- method get

get team's exercises through workbooks

        /api/team/{id}/members/

- method get

get team's members through membership

        /api/teams-list/

- method get

get user's team

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