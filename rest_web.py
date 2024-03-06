#Adam Johnson
#RESTful DB MidTerm
#3/1/2024


from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Establish connection to the WAMP SQL DB and upload .csv file
hostname = "127.0.0.1"
uname = "root"
pwd = ""
dbname = "zipcodes"
engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
tables = pd.read_csv(r"zip_code_database.csv", dtype={"Population": int})
tables.rename(columns={"zip": "zip_code"}, inplace=True)
tables.rename(columns={"Population": "population"}, inplace=True)
tables.to_sql('zipcodes', con=engine, if_exists='replace', index=False)

app = Flask(__name__)
app.debug = True

@app.route('/')
def zipcodes_dash():
    return render_template('login.html')


@app.route('/search', methods=['GET'])
def search():
    zip_code = request.args.get('zipCode')

    data = get_zip_results(zip_code)
    population = data.population if data is not None else None

    return render_template('gofecth.html', zipCode=zip_code, population=population)


def get_zip_results(zip_code):
    connection = engine.connect()
    query = text("SELECT * FROM zipcodes WHERE zip_code = :zip_code")
    result = connection.execute(query, {"zip_code": zip_code}).fetchone()
    connection.close()
    return result

@app.route('/update', methods=['POST'])
def update():
    zip_code = request.form['zipCode']
    population = request.form['population']

    if zip_code.isdigit() and population.isdigit():
        zip_code = int(zip_code)
        population = int(population)
        if 0 <= zip_code <= 99999 and population >= 0:
            connection = engine.connect()
            query = text("UPDATE zipcodes SET population = :population WHERE zip_code = :zip_code")
            connection.execute(query, {"zip_code": zip_code, "population": population})
            connection.close()
            return render_template('update_success.html')
    return render_template('update_fail.html')


# Run Flask
if __name__ == '__main__':
    app.run()