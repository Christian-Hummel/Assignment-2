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

    response1 = client.post("/supervisor/", json={
        "name":"JasonBourne",
        "address":"Unknown Street 55, 2234 Dallas",
        "salary": 10000,
        "nationality": "USA"
    })


    assert response1.status_code == 400

    parsed1 = response1.get_json()
    error1 = parsed1["message"]

    assert error1 == "Please insert your first and last name seperated by a space"

    response2 = client.post("/supervisor/", json={
        "name": "Harry Styles",
        "address": "123 Elm Street, Springfield",
        "salary": 8000,
        "nationality": "USA"
    })

    assert response2.status_code == 400

    parsed2 = response2.get_json()

    error2 = parsed2["message"]

    assert error2 == "Supervisor already registered"




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

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    agent_response = client.post("/supervisor/employee", headers=headers, json={
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

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response1 = client.post(f"/supervisor/employee", headers=headers, json={
        "name": "Franz",
        "address":"Baumgartenweg 23, 4728 Kottingbrunn",
        "salary": 2900,
        "nationality": "Austria"
    })

    assert response1.status_code == 400

    parsed_response1= response1.get_json()
    error1 = parsed_response1["message"]

    assert error1 == "Please insert your first and last name seperated by a space"

    response2 = client.post(f"/supervisor/employee", headers=headers, json={
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

    user = db.session.query(User).filter_by(id=4).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    supervisor_id = user.manager_id


    response_supervisor = client.get(f"/supervisor/{supervisor_id}/info", headers=headers)


    assert response_supervisor.status_code == 200

    parsed_supervisor = response_supervisor.get_json()
    supervisor_response = parsed_supervisor["supervisor"]

    assert supervisor_response["name"] == "Scarlett Johansson"
    assert supervisor_response["address"] == "101 Maple Road, Smallville"
    assert supervisor_response["email"] == "Scarlett.Johansson@hammertrips.com"
    assert supervisor_response["salary"] == 18234
    assert supervisor_response["nationality"] == "USA"


def test_get_supervisor_info_error(client,agency):

    user = db.session.query(User).filter_by(id=4).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/supervisor/382/info", headers=headers)

    assert response.status_code == 400

    parsed = response.get_json()
    error = parsed["message"]

    assert error == "Supervisor not found"

def test_get_supervisor_agents(client,agency):

    user = db.session.query(User).filter_by(id=17).first()

    supervisor_id = user.manager_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/supervisor/team", headers=headers)

    assert response.status_code == 200


    parsed_team = response.get_json()
    team_response = parsed_team["travelagents"]

    assert len(team_response) == 1


def test_get_supervisor_agents_error(client,agency):

    user = db.session.query(User).filter_by(id=1).first()

    supervisor_id = user.manager_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/supervisor/team", headers=headers)

    assert response.status_code == 400

    parsed = response.get_json()
    error = parsed["message"]

    assert error == "There are no travel agents under your supervision yet"

def test_assign_agent_nexpertnpreference(client,agency):

    response_customer = client.post("/customer/",json={
        "name": "Tom Brady",
        "address": "Champion Road 23, 2340 Tampa Bay",
        "email": "No199@nflpatriots.us",
        "budget": 25000,
        "preference": "string"
    })

    parsed_customer = response_customer.get_json()
    customer_response = parsed_customer["customer"]
    customer_id = customer_response["customer_id"]


    user = db.session.query(User).filter_by(id=2).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=240).first()

    employee_id = agent.employee_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }



    response = client.post(f"/supervisor/assign/{employee_id}", headers=headers, json={
        "customer_id": customer_id
    })

    assert response.status_code == 200

    parsed = response.get_json()

    assert parsed == "TravelAgent Christopher Lee has been assigned to Tom Brady"


def test_assign_agent_expert(client,agency):

    customer = db.session.query(Customer).filter_by(customer_id=720).first()

    customer_id = customer.customer_id

    customer.expert = True

    user = db.session.query(User).filter_by(id=3).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=245).first()

    employee_id = agent.employee_id



    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.post(f"/supervisor/assign/{employee_id}", headers=headers, json={
        "customer_id": customer_id
    })

    assert response.status_code == 200

    parsed = response.get_json()

    assert parsed == "TravelAgent Philipp Lienhart has been assigned to Marie Tharp"



def test_assign_agent_nexpertpreference(client,agency):

    customer = db.session.query(Customer).filter_by(customer_id=719).first()

    customer_id = customer.customer_id

    user = db.session.query(User).filter_by(id=5).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=255).first()

    employee_id = agent.employee_id


    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.post(f"/supervisor/assign/{employee_id}", headers=headers, json={
        "customer_id": customer_id
    })

    assert response.status_code == 200

    parsed = response.get_json()

    assert parsed == "TravelAgent Jane Smith has been assigned to Alfred Nobel"


def test_assign_agent_errors(client,agency):

    customer = db.session.query(Customer).filter_by(customer_id=701).first()

    customer_id = customer.customer_id

    user = db.session.query(User).filter_by(id=6).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=260).first()

    employee_id = agent.employee_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # customer is already connected to a TravelAgent

    response_assigned = client.post(f"/supervisor/assign/{employee_id}",headers=headers,json={
        "customer_id": customer_id
    })

    assert response_assigned.status_code == 400

    parsed_assigned = response_assigned.get_json()
    error_assigned = parsed_assigned["message"]

    assert error_assigned == "This customer has already been assigned to a TravelAgent"

    # TravelAgent not registered in the agency

    response_agent = client.post("supervisor/assign/594", headers=headers, json={
        "customer_id": customer_id
    })

    assert response_agent.status_code == 400

    parsed_agent = response_agent.get_json()
    error_agent = parsed_agent["message"]

    assert error_agent == "TravelAgent not found"

    # Customer not registered in the agency

    response_customer = client.post(f"supervisor/assign/{employee_id}", headers=headers, json={
        "customer_id": 493
    })

    assert response_customer.status_code == 400

    parsed_customer = response_customer.get_json()
    error_customer = parsed_customer["message"]

    assert error_customer == "Customer not found"

def test_get_all_customers(client,agency):

    user = db.session.query(User).filter_by(id=2).first()

    count = Customer.query.count()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response_customers = client.get("/supervisor/customers", headers=headers)

    assert response_customers.status_code == 200

    parsed_customers = response_customers.get_json()

    customers_response = parsed_customers["customers"]

    assert count == len(customers_response)


def test_get_all_customers_error(client,agency):

    empty = db.session.query(Customer).delete()

    user = db.session.query(User).filter_by(id=2).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response_customers = client.get("/supervisor/customers", headers=headers)

    assert response_customers.status_code == 400

    parsed_customers = response_customers.get_json()
    customers_error = parsed_customers["message"]

    assert customers_error == "There are no customers currently registered"


def test_get_customer_by_id(client,agency):

    user = db.session.query(User).filter_by(id=2).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("supervisor/customer/719", headers=headers)

    assert response.status_code == 200

    parsed = response.get_json()
    customer_response = parsed["customer"]

    assert customer_response["name"] == "Alfred Nobel"
    assert customer_response["address"] == "Mining Road 5, 1120 Stockholm"
    assert customer_response["email"] == "Alfred.Nobel@chemistry.se"
    assert customer_response["budget"] == 27000
    assert customer_response["preference"] == "France"
    assert not customer_response["expert"]
    assert not customer_response["travel_agent_id"]


def test_get_customer_by_id_error(client,agency):

    user = db.session.query(User).filter_by(id=2).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("supervisor/customer/345", headers=headers)

    assert response.status_code == 400

    parsed = response.get_json()
    error = parsed["message"]

    assert error == "Customer not found"


def test_get_agent_by_id(client,agency):

    user = db.session.query(User).filter_by(id=2).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=255).first()

    employee_id = agent.employee_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get(f"/supervisor/agent/{employee_id}", headers=headers)

    assert response.status_code == 200

    parsed_agent = response.get_json()

    agent_response = parsed_agent["travelAgent"]

    assert agent_response["name"] == "Jane Smith"
    assert agent_response["address"] =="Elm Street 12, 5678 Gotham"
    assert agent_response["email"] == "Jane.Smith@hammertrips.com"
    assert agent_response["salary"] == 3200
    assert agent_response["nationality"] == "Canada"
    assert len(agent_response["customers"]) == 1
    assert len(agent_response["countries"]) == 3
    assert agent_response["supervisor_id"] == 56


def test_get_agent_by_id_error(client,agency):
    user = db.session.query(User).filter_by(id=2).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=255).first()

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get("/supervisor/agent/483", headers=headers)

    assert response.status_code == 400

    parsed = response.get_json()
    error = parsed["message"]

    assert error == "TravelAgent not found"


def test_increase_agent_salary(client,agency):

    user = db.session.query(User).filter_by(id=7).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=265).first()

    employee_id = agent.employee_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    assert agent.salary == 3300

    response_raise = client.post(f"/supervisor/agent/{employee_id}/raise", headers=headers, json={
        "percentage_increase": 5
    })

    assert response_raise.status_code == 200

    parsed_raise = response_raise.get_json()

    assert parsed_raise == "TravelAgent Emily Davis updated salary is 3465"

def test_increase_agent_salary_errors(client,agency):

    user = db.session.query(User).filter_by(id=7).first()

    agent = db.session.query(TravelAgent).filter_by(employee_id=265).first()

    employee_id = agent.employee_id

    access_token = create_access_token(user)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response_invalid = client.post(f"/supervisor/agent/{employee_id}/raise", headers=headers,json={
        "percentage_increase": 0
    })

    assert response_invalid.status_code == 400

    parsed_invalid = response_invalid.get_json()
    error1 = parsed_invalid["message"]

    assert error1 == "Please insert a real number from 1 to 100"

    response_diffteam = client.post("/supervisor/agent/280/raise", headers=headers, json={
        "percentage_increase": 40
    })

    assert response_diffteam.status_code == 400

    parsed_diffteam = response_diffteam.get_json()
    error2 = parsed_diffteam["message"]

    assert error2 == "This TravelAgent is not a member of your team"