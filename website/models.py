from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:localhost/dbName'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

association_table = db.Table('association_table',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'))
)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    category = db.Column(db.String(100))
    img_url = db.Column(db.String(1000))

    carts = db.relationship("Cart", secondary=association_table)

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    products = db.relationship("Product", secondary=association_table)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    phone_number = db.Column(db.String(50))
    adress = db.Column(db.String(250))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    works_for = db.relationship('Employee', backref='department', lazy=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
   

db.create_all()
db.session.commit()