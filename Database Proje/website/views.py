from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import text

from .models import Department, Employee, Product, User, db, Cart

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':

        min_value = request.form.get('min_value')
        max_value = request.form.get('max_value')

        category = request.form.get('selected_category')

        if not max_value and min_value:
            query = text("SELECT * FROM PRODUCT WHERE price >= :val")
            products = db.session.execute(query, {'val': min_value}).all()
        elif not min_value and max_value:
            query = text("SELECT * FROM PRODUCT WHERE price <= :val")
            products = db.session.execute(query, {'val': max_value}).all()
        elif max_value and min_value:
            query = text("SELECT * FROM PRODUCT WHERE price BETWEEN :val1 AND :val2")
            products = db.session.execute(query, {'val1': min_value, 'val2': max_value}).all()
        else:
            query = text("SELECT * FROM PRODUCT WHERE category = :val")
            products = db.session.execute(query, {'val': category}).all()

        return render_template("/customer/home.html", user=current_user, products=products)

    products = Product.query.all()
    return render_template("/customer/home.html", user=current_user, products=products)


@views.route('/mycart', methods=['GET', 'POST'])
@login_required
def mycart():
    user_id = current_user.get_id()
    cart = Cart.query.filter_by(user_id=user_id).first()

    products = []

    if cart is not None:
        products = cart.products    

    return render_template('/customer/mycart.html', user=current_user, products=products)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        user_id = current_user.get_id()
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        adress = request.form.get('adress')

        user = User.query.filter_by(id=user_id).first()

        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.adress = adress
        db.session.commit()

        return redirect(url_for('views.home'))

    return render_template('/customer/profile.html', user=current_user)


@views.route('/admin/products', methods=['GET', 'POST'])
@login_required
def products():
    products = Product.query.all()
    return render_template("/admin/products.html", user=current_user, products=products)


@views.route('/admin/save_product', methods=['POST'])
@login_required
def save_product():
    id = request.form.get('id')
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    category = request.form.get('category')
    img_url = request.form.get('img_url')

    if id is None:
        # New product

        p = Product(name=name, quantity=quantity, price=price, category=category, img_url=img_url)
        db.session.add(p)
        db.session.commit()
    else:
        # Update product

        product = db.session.query(Product).get(id)
        product.name = name
        product.quantity = quantity
        product.price = price
        product.category = category
        product.img_url = img_url
        db.session.commit()

    return redirect(url_for('views.products'))


@views.route('/admin/product_detail/')
@views.route('/admin/product_detail/<product_id>', methods=['GET'])
@login_required
def product_detail(product_id=None):

    if product_id is not None:
        product = Product.query.get(product_id)
        return render_template("/admin/edit_product.html", user=current_user, product=product)
    else:
        product = Product()
        return render_template("/admin/edit_product.html", user=current_user, product=product)


@views.route('/admin/products/<product_id>')
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('views.products'))


@views.route('/mycart/<product_id>', methods=["GET"])
@login_required
def add_to_cart(product_id):
    user_id = current_user.get_id()
    product = Product.query.get(product_id)

    cart_item = Cart.query.filter_by(user_id=user_id).first()

    if cart_item is None:
        cart_item = Cart(user_id=user_id)

    cart_item.products.append(product)

    db.session.add(cart_item)
    db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/mycart/delete', methods=["POST"])
@login_required
def delete_from_cart():
    if request.method == "POST":
        product_id = request.form.get('product_id')

        user_id = current_user.get_id()
        cart = Cart.query.filter_by(user_id=user_id).first()

        product = Product.query.get(product_id)
        cart.products.remove(product)
        db.session.commit()

    return redirect(url_for('views.mycart'))


@views.route('/admin/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        adress = request.form.get('adress')

        filter_list = {"first_name": first_name, "last_name": last_name, "email": email, "phone_number": phone_number,
                       "adress": adress}

        t1 = "SELECT * FROM USER WHERE "

        for name, value in filter_list.items():
            if value != "":
                t1 += f"{name} LIKE '%{value}%' AND "

        t1 = t1[:-4]

        query = text(t1)
        users = db.session.execute(query)
        return render_template("/admin/customers.html", user=current_user, users=users)

    users = User.query.all()
    return render_template("/admin/customers.html", user=current_user, users=users)


@views.route('/admin/employees')
@login_required
def employees():
    employees = Employee.query.all()
    departments = Department.query.all()
    return render_template("/admin/employees.html", user=current_user,
                           employees=employees, departments=departments)
