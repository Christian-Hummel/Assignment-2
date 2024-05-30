import pytest

from src.database import Supervisor, TravelAgent, Customer, Country, Activity, User, db

from tests.fixtures import app, client, agency

from flask_jwt_extended import create_access_token


def test_add_supervisor(client,agency):

    response = client.post("/supervisor/", json={
        "name":"Warren Buffet",
        "address":"103 Avenue, 4932 New York",
        "salary": 20000,
        "nationality":"USA"
    })


    assert response.status_code == 200


    parsed = response.get_json()
    supervisor_response = parsed["supervisor"]


    assert supervisor_response["name"] == "Warren Buffet"
    assert supervisor_response["address"] == "103 Avenue, 4932 New York"
    assert supervisor_response["salary"] == 20000
    assert supervisor_response["nationality"] == "USA"


def test_add_supervisor_error(client, agency):

    response = client.post("/supervisor/", json={
        "name":"JasonBourne",
        "address":"Unknown Street 55, 2234 Dallas",
        "salary": 10000,
        "nationality": "USA"
    })


    assert response.status_code == 400

    parsed = response.get_json()
    error = parsed["message"]

    assert error == "Please insert your first and last name seperated by a space"


def test_register_supervisor(client,agency):

    supervisor = db.session.query(Supervisor).filter_by(employee_id=201).first()

    supervisor_id = supervisor.employee_id

    response = client.post(f"/supervisor/{supervisor_id}/register",json={
        "username":"Tommy",
        "password":"Loki"
    })

    assert response.status_code == 200

    parsed = response.get_json()
    user_response = parsed["user"]

    assert user_response["id"] == 19
    assert user_response["username"] == "Tommy"


def test_register_supervisor_errors(client,agency):


    supervisor = db.session.query(Supervisor).filter_by(employee_id=13).first()


    supervisor_id = supervisor.employee_id



    response = client.post(f"/supervisor/{supervisor_id}/register", json={
        "username": "Harry",
        "password": "Stylish"
    })


    response1 = client.post(f"/supervisor/{supervisor_id}/register", json={
        "username": "Harry",
        "password": "Music"
    })


    assert response1.status_code == 400

    parsed=response1.get_json()
    error_response1 = parsed["message"]

    assert error_response1 == "This user already exists"

    response2 = client.post(f"/supervisor/734/register", json={
        "username": "Markus",
        "password": "Styles"
    })

    assert response2.status_code == 400

    parsed_nfound = response2.get_json()
    error_response2 = parsed_nfound["message"]

    assert error_response2 == "Supervisor not found"


def test_supervisor_login(client, agency):

    supervisor = db.session.query(Supervisor).filter_by(employee_id=212).first()
    supervisor_id = supervisor.employee_id

    register_response = client.post(f"/supervisor/{supervisor_id}/register", json={
        "username":"Karen",
        "password":"asdfalhsdf"
    })

    register_parsed = register_response.get_json()
    response_register = register_parsed["user"]
    username = response_register["username"]


    login_response = client.post("/supervisor/login", json={
        "username": username,
        "password": "asdfalhsdf"
    })

    assert login_response.status_code == 200




def test_supervisor_login_errors(client,agency):

    login_response1 = client.post("/supervisor/login", json={
        "username": "Ferdinand",
        "password": "asdfasdg"
    })

    assert login_response1.status_code == 400

    parsed_response1 = login_response1.get_json()
    error1 = parsed_response1["message"]

    assert error1 == "User does not exist"

    login_response2 = client.post("/supervisor/login", json={
        "username": "Tom",
        "password": "1234"
    })

    assert login_response2.status_code == 400

    parsed_response2 = login_response2.get_json()
    error2 = parsed_response2["message"]

    assert error2 == "Incorrect Password"


def test_add_agent(client,agency):

    before = TravelAgent.query.count()

    user = db.session.query(User).filter_by(id=13).first()

    supervisor_id = user.manager_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    agent_response = client.post(f"/supervisor/{supervisor_id}/employee", headers=headers, json={
        "name":"Keanu Reeves",
        "address": "Runaway Street 24, 3829 Minnesota",
        "salary": 3000,
        "nationality": "USA"
    })


    assert agent_response.status_code == 200

    parsed_agent = agent_response.get_json()
    agent_response = parsed_agent["travelAgent"]

    assert agent_response["name"] == "Keanu Reeves"
    assert agent_response["address"] == "Runaway Street 24, 3829 Minnesota"
    assert agent_response["email"] == "Keanu.Reeves@hammertrips.com"
    assert agent_response["salary"] == 3000
    assert agent_response["nationality"] == "USA"
    assert agent_response["supervisor_id"] == 135


    assert TravelAgent.query.count() == before + 1


def test_add_agent_errors(client,agency):

    user = db.session.query(User).filter_by(id=15).first()

    supervisor_id = user.manager_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response1 = client.post(f"/supervisor/{supervisor_id}/employee", headers=headers, json={
        "name": "Franz",
        "address":"Baumgartenweg 23, 4728 Kottingbrunn",
        "salary": 2900,
        "nationality": "Austria"
    })

    assert response1.status_code == 400

    parsed_response1= response1.get_json()
    error1 = parsed_response1["message"]

    assert error1 == "Please insert your first and last name seperated by a space"

    response2 = client.post(f"/supervisor/{supervisor_id}/employee", headers=headers, json={
        "name": "Franz",
        "address":"Baumgartenweg 23, 4728 Kottingbrunn",
        "salary": 5000,
        "nationality": "Austria"
    })

    assert response2.status_code == 400

    parsed_response2 = response2.get_json()
    error2 = parsed_response2["message"]

    assert error2 == "Please enter a salary amount in Euro from 2000 to 4000"


def test_get_supervisor_info(client,agency):

    user = db.session.query(User).filter_by(id=14).first()

    supervisor_id = user.manager_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }


    supervisor_response = client.get("/supervisor/info", headers=headers)


    assert supervisor_response.status_code == 200