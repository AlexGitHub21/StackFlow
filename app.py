from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from Config import Configuration
from models import Product, Inventory, Location
import pymysql
from forms import AddProductForm, AddLocationForm, AddInventoryForm, ReduceQuantityForm
import decimal
from sqlalchemy.sql import func
pymysql.install_as_MySQLdb()
from flask import jsonify

app = Flask(__name__)

app.config.from_object(Configuration)

db.init_app(app)


def get_products():
    products = db.session.query(
        Product.id,
        Product.name,
        Product.description,
        Product.price,
        func.coalesce(Inventory.quantity, "").label("quantity"),
        func.coalesce(Location.name, "").label("location_name")
    ).select_from(Product) \
        .outerjoin(Inventory, Product.id == Inventory.product_id) \
        .outerjoin(Location, Inventory.location_id == Location.id) \
        .order_by(Product.id).all()
    return products


def record_product(name: str, desc: str, price: decimal):
    product = Product(
        name=name,
        description=desc,
        price=price
    )
    db.session.add(product)
    db.session.commit()
    return True


def record_location(name: str):
    location = Location.query.filter_by(name=name).first()
    if location:
        return False
    else:
        new_location = Location(name=name)
        db.session.add(new_location)
        db.session.commit()
        return True


def add_new_inventory(prod_id: int, loc_id: int, quantity: int):
    new_inventory = Inventory(
        product_id=prod_id,
        location_id=loc_id,
        quantity=quantity
    )
    db.session.add(new_inventory)
    db.session.commit()
    return quantity


def record_inventory(prod_id: int, loc_id: int, quantity: int):
    inventory = Inventory.query.filter_by(product_id=prod_id, location_id=loc_id).first()
    if inventory:
        # if inventory.location_id == loc_id:
        new_quantity = inventory.quantity + quantity
        inventory.quantity = new_quantity
        # rows = Inventory.query.filter_by(product_id=prod_id).update({'quantity': new_quantity})
        db.session.commit()
            # update_query = update(Inventory).where(Inventory.c.product_id == prod_id).values(quantity=new_quantity)
            # db.session.add(update_query)
            # db.session.commit()
        return new_quantity
        # else:
        #     return add_new_inventory(prod_id, loc_id, quantity)
    else:
        return add_new_inventory(prod_id, loc_id, quantity)


def update_quantity(prod_id: int, loc: str, quantity: int):
    location = Location.query.filter_by(name=loc).first()
    inventory = Inventory.query.filter_by(product_id=prod_id, location_id=location.id).first()
    if inventory:
        new_quantity = inventory.quantity - quantity
        if new_quantity >= 0:
            rows = Inventory.query.filter_by(product_id=prod_id, location_id=location.id).update({'quantity': new_quantity})
            db.session.commit()
            return new_quantity
        else:
            return new_quantity
    else:
        return quantity


@app.route('/')
@app.route('/products')
def index():
    products = get_products()
    locations = Location.query.all()
    location_form = AddLocationForm()
    product_form = AddProductForm()
    inventory_form = AddInventoryForm()
    reduce_quantity_form = ReduceQuantityForm()
    return render_template('products.html',
                           products=products,
                           locations=locations,
                           product_form=product_form,
                           location_form=location_form,
                           inventory_form=inventory_form,
                           reduce_form=reduce_quantity_form)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    products = get_products()
    locations = Location.query.all()
    location_form = AddLocationForm()
    product_form = AddProductForm()
    inventory_form = AddInventoryForm()
    reduce_quantity_form = ReduceQuantityForm()
    if product_form.validate_on_submit():

        new_product = record_product(product_form.name.data, product_form.description.data, product_form.price.data)
        product = Product.query.filter_by(name=product_form.name.data).first()
        print(id)
        if new_product:
            product = {"id": product.id, "name": product_form.name.data, "description": product_form.description.data,
                       "price": product_form.price.data, "quantity": "", "location_name": ""}
            print('Товар добавлен в БД')
            return jsonify(success=True, new_product=product)

        else:

            print("Ошибка добавление в БД")
            return jsonify(success=False)

    return render_template('products.html',
                           products=products,
                           locations=locations,
                           product_form=product_form,
                           location_form=location_form,
                           inventory_form=inventory_form,
                           reduce_form=reduce_quantity_form)


@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    products = get_products()
    locations = Location.query.all()
    location_form = AddLocationForm()
    product_form = AddProductForm()
    inventory_form = AddInventoryForm()
    reduce_quantity_form = ReduceQuantityForm()
    if location_form.validate_on_submit():
        new_location = record_location(location_form.name.data)
        if new_location:
            return jsonify(success=True, name=location_form.name.data)
        else:
            jsonify(success=False, error="Такая локация уже есть в БД")

    return render_template('products.html',
                           products=products,
                           locations=locations,
                           product_form=product_form,
                           location_form=location_form,
                           inventory_form=inventory_form,
                           reduce_form=reduce_quantity_form)


@app.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory():
    products = get_products()
    locations = Location.query.all()
    location_form = AddLocationForm()
    product_form = AddProductForm()
    inventory_form = AddInventoryForm()
    reduce_quantity_form = ReduceQuantityForm()
    if request.method == "POST":
        data = request.get_json(force=True)
        product_id = int(data.get('product_id'))
        location_id = int(data.get('location_id'))
        quantity = int(data.get('quantity'))

        new_quantity = record_inventory(product_id, location_id, quantity)
        product = Product.query.filter(Product.id == product_id).first()
        print(product.name)
        print(product.description)
        print(product.price)

        if new_quantity:
            location = Location.query.filter(Location.id == location_id).first()
            print('Запись проведена')
            data = {'name': product.name, 'description': product.description, 'price': product.price,
                    'newQuantity': new_quantity, 'newLocation': location.name}
            return jsonify(success=True, new_data=data)
        else:
            print("Ошибка добавление записи в БД")
            return jsonify({'error': 'Ошибка добавления в БД'}), 400  # Ошибка с кодом 400

    return render_template('products.html',
                           products=products,
                           locations=locations,
                           product_form=product_form,
                           location_form=location_form,
                           inventory_form=inventory_form,
                           reduce_form=reduce_quantity_form)




@app.route('/reduce_quantity', methods=['GET', 'POST'])
def reduce_quantity():
    # product_id = request.form.get('product_id')
    products = Product.query.all()
    reduce_quantity_form = ReduceQuantityForm()
    if request.method == "POST":
        data = request.get_json(force=True)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity'))
        location = data.get('location')

        new_quantity = update_quantity(product_id, location, quantity)

        if new_quantity >= 0:
            print('Запись проведена')
            data = {'newQuantity': new_quantity, 'newLocation': location}

            return jsonify(success=True, new_data=data)
        else:
            print("Количество товара не мб отрицательным")
            return jsonify(success=False, error="Количество товара не мб отрицательным")

    return render_template('products.html',
                           products=products,
                           reduce_form=reduce_quantity_form)


@app.route('/get_locations', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    location_list = [{'id': loc.id, 'name': loc.name} for loc in locations]
    return jsonify({'locations': location_list})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=Configuration.DEBUG)
