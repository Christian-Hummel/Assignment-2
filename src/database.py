from flask_sqlalchemy import SQLAlchemy




# Initialize the database
db = SQLAlchemy()
# add database tables


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))

    manager_id = db.Column(db.Integer, db.ForeignKey('supervisor.employee_id'))

class Supervisor(db.Model):
    __tablename__ = "supervisor"
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    address = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    salary = db.Column(db.Integer,nullable=False)
    nationality = db.Column(db.String(20),nullable=False)
    role = db.Column(db.String(20),nullable=False, default='supervisor')

    account = db.relationship('User', backref='Supervisor', uselist=False)
    teammembers = db.relationship('TravelAgent', backref='Supervisor')
    messages = db.relationship('Message', backref='Supervisor')


class Message(db.Model):
    __tablename__ = "message"
    message_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(50), nullable=False)
    offer_id = db.Column(db.Integer, nullable=False, default=0)
    percentage = db.Column(db.Integer, nullable=False, default=0)

    supervisor_id = db.Column(db.Integer, db.ForeignKey('supervisor.employee_id'),nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.employee_id'),nullable=False)


# joined table travelAgent and country

agent_country = db.Table(
    'agent_country',
    db.Column('country_id', db.Integer, db.ForeignKey('country.country_id')),
    db.Column('employee_id', db.Integer, db.ForeignKey('travel_agent.employee_id'))

)

class AgentStats(db.Model):
    __tablename__ = "agent_stats"
    stats_id = db.Column(db.Integer, primary_key=True)
    num_customers = db.Column(db.Integer, nullable=False)
    num_trips = db.Column(db.Integer, nullable=False, default=0)
    total_revenue = db.Column(db.Integer, nullable=False, default=0)

    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.employee_id'),nullable=False)


class TravelAgent(db.Model):
    __tablename__ = "travel_agent"
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    address = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    salary = db.Column(db.Integer,nullable=False)
    nationality = db.Column(db.String(20),nullable=False)
    role = db.Column(db.String(20),nullable=False, default='travelAgent')

    supervisor_id = db.Column(db.Integer, db.ForeignKey('supervisor.employee_id'), nullable=False)
    stats = db.relationship('AgentStats', backref='TravelAgent', uselist=False)
    countries = db.relationship('Country', secondary='agent_country', back_populates='agents')
    customers = db.relationship('Customer', backref='TravelAgent')
    offers = db.relationship('Offer', backref='TravelAgent')
    messages = db.relationship('Message', backref='TravelAgent')



class Customer(db.Model):
    __tablename__ = "customer"
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    address = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    budget = db.Column(db.Integer, nullable=False)
    preference = db.Column(db.String(20), default='None')
    expert = db.Column(db.Boolean, unique=False, default=False)

    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.employee_id'), nullable=False)
    offers = db.relationship('Offer', backref='Customer')

    def __str__(self):
        return self.name

# joined table country and activity
country_activity = db.Table(
    'country_activity',
    db.Column('country_id', db.Integer, db.ForeignKey('country.country_id')),
    db.Column('activity_id', db.Integer, db.ForeignKey('activity.activity_id'))
)

# joined table offer and activity
offer_activity = db.Table(
    'offer_activity',
    db.Column('offer_id', db.Integer, db.ForeignKey('offer.offer_id')),
    db.Column('activity_id', db.Integer, db.ForeignKey('activity.activity_id'))
)

class Country(db.Model):
    __tablename__ = "country"
    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    activities = db.relationship('Activity', secondary='country_activity', back_populates='countries')
    agents = db.relationship('TravelAgent', secondary='agent_country', back_populates='countries')

    def __str__(self):
        return self.name



class Activity(db.Model):
    __tablename__ = "activity"
    activity_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer,nullable=False)

    countries = db.relationship('Country', secondary='country_activity', back_populates='activities')
    offers = db.relationship('Offer', secondary='offer_activity', back_populates='activities')

    def __str__(self):
        return self.name

class Offer(db.Model):
    __tablename__ = "offer"
    offer_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)

    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.employee_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    activities = db.relationship('Activity', secondary='offer_activity', back_populates='offers')




    # Relations
    # many to many with Activities : activities can be used for many different offers - c
    # one to many with Customer : a Customer can receive many offers -
                                ## an offer is created for one customer - c
    # one to many with TravelAgent : an agent can create many offers -
                                ## one offer is created by one agent - c