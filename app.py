from flask import Flask, render_template, request, redirect
from extensions import db
from Config import Configuration
from models import Product, Inventory, Location
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config.from_object(Configuration)

db.init_app(app)


context = {}
context['products'] = []


def get_products():
    products = Product.query.all()
    result = []
    for product in products:
        invs = Inventory.query.filter(Inventory.product_id == product.id).all()
        inv_quantity = [str(inv.quantity) for inv in invs]

        locs = Location.query.filter(Location.id == product.id).all()
        loc_name = [loc.name for loc in locs]
        inv_quantity = ' '.join(inv_quantity)
        loc_name = ' '.join(loc_name)
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': inv_quantity,
            'location_name': loc_name
        }
        result.append(product_data)
    return result


@app.route('/')
@app.route('/products')
def index():
    products = get_products()

    return render_template('products.html', products=products)


@app.route('/add_products', methods=['GET', 'POST'])
def add_product():
    if request.method == "POST":
        try:
            p = Product(name=request.form.get('name'), description=request.form.get('description'), price=request.form.get('price'))

            db.session.add(p)
            db.session.flush()
            db.session.commit()
            context['products'].append(p)
            redirect('/products')

        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
    return render_template('products.html')


@app.route('/add_locations', methods=['GET', 'POST'])
def add_locations():
    products = get_products()

    if request.method == "POST":
        try:
            quantity = 0
            l = Location(name=request.form.get('name'))

            db.session.add(l)
            db.session.flush()

            id_last_rec_loc = int(l.id)
            id_last_rec_prod = int(products[-1]['id'])
            if id_last_rec_loc == id_last_rec_prod:
                inv = Inventory(product_id=id_last_rec_prod, location_id=id_last_rec_loc, quantity=quantity)
                db.session.add(inv)
                db.session.flush()
                db.session.commit()

        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

    return render_template('products.html', products=products)


@app.route('/add_quantity', methods=['GET', 'POST'])
def add_quantity():

    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    products = Product.query.all()

    if request.method == "POST":
        try:
            loc = Inventory.query.filter(Inventory.product_id == product_id).first()
            if loc:
                quantity += loc.quantity

                Inventory.query.filter(Inventory.product_id == product_id,
                                       Inventory.location_id == loc.id).update({'quantity': quantity})
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

    return render_template('products.html', products=products)


@app.route('/delete_prod', methods=['GET', 'POST'])
def delete_prod():
    product_id = request.form.get('product_id')
    products = Product.query.all()
    if request.method == "POST":
        try:
            prod = Product.query.filter(Product.id == product_id).first()
            if prod:

                Inventory.query.filter(Inventory.product_id == product_id).update({'quantity': 0})
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

    return render_template('products.html', products=products)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=Configuration.DEBUG)
