from flask import Flask, request, jsonify
import mysql.connector


app = Flask(__name__)


def database_connection():
    endpoint = "mydatabase.cluster-czccoi8ia5vv.us-east-1.rds.amazonaws.com"
    port = '3306'
    username = 'admin'
    password = 'alexedge'
    database_name = 'myDB'

    cnx = mysql.connector.connect(
    host=endpoint,
    port=port,
    user=username,
    password=password,
    database=database_name
    )
    return cnx


# Table creation query
create_table_query = """
CREATE TABLE IF NOT EXISTS products (
    name VARCHAR(100),
    price VARCHAR(100),
    availability BOOLEAN
)
"""

# Execute the table creation query during application startup
with database_connection() as cnx:
    cursor = cnx.cursor()
    cursor.execute(create_table_query)
    cnx.commit()
    cursor.close()
    


@app.route("/store-products", methods=["POST"])
def store_data():

    if request.method == "POST":
        try:
            payload = request.get_json()
            print("Received payload:")
            print(payload)

            if "products" in payload:
                products = payload["products"]

                # payload data
                with database_connection() as insert_data:
                    cursor = insert_data.cursor()

                    for product in products:
                        name = product['name']
                        price = product['price']
                        availability = product['availability']

                        query = "INSERT INTO myDB.products (name, price, availability) VALUES (%s, %s, %s)"
                        values = (name, price, availability)

                        cursor.execute(query, values)

                    insert_data.commit()
                    cursor.close()

                return jsonify({"message": "Success."}), 200
            else:
                return "No products found in the payload", 400

        except Exception as e:
            print("Error processing payload:", str(e))
            return "Error processing payload", 500

    else:
        return "Method Not Allowed", 405
    

@app.route("/list-products", methods=["GET"])
def get_products():
    if request.method == "GET":
        try:
            # Connect to the database
            with database_connection() as get_data:
                cursor = get_data.cursor()

                # Execute the SELECT query
                cursor.execute("SELECT name, price, availability FROM products")

                # Fetch all the products from the database
                rows = cursor.fetchall()

                # Create a list of products
                products = []
                for row in rows:
                    product = {
                        "name": row[0],
                        "price": row[1],
                        "availability": bool(row[2])
                    }
                    products.append(product)

                return jsonify({"products": products}), 200
        except Exception as e:
            # Return an error message with appropriate status code
            return str(e), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
