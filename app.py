from flask import Flask, redirect, request, render_template
from twilio.rest import Client
import requests
import requests_cache
import json

servicTypes = {
    's1': 'Shops, dealing with foods, groceries, fruits & amp vegetables, dairy &amp; milk booths, meat &amp; fish, animal fodder, pharmaceuticals, medicines and medical equipments, news papers distribution',
    's2': 'Banks, Insurance offices and ATMs, SEBI/Stock related offices.',
    's3': 'Telecommunications, Internet services, broadcasting and cable services, IT and IT enabled services',
    's4': 'Delivery of all essential goods including food, pharmaceuticals, medical equipments through e-commerce',
    's5': 'Petrol pumps, LPG, CNG, petroleum and gas retail and storage outlets',
    's6': 'Water supply, Power generation, transmission and distribution units and services',
    's7': 'Cold storage and warehousing services',
    's8': 'Private security services',
    's9': 'Manufacturing units of essential commodities',
    's10': 'Manufacturing units of non-essential commodities having onsite workers'
}

session = requests.Session()

account_sid = 'AC3e590437e14ae427bfa34ebb656fdb04'
auth_token = '7d4b0f7aca4e57d81e3592057de7ab3e'

client = Client(account_sid, auth_token)

app = Flask(__name__, static_url_path='/static')


@app.route('/')
@app.route('/register', methods=['GET'])
def get_register_form():
    res = session.get('https://api.covid19india.org/v4/data.json')
    info = res.json()
    districts = info['BR']['districts'].keys()
    return render_template('epass.form.html', services=servicTypes, districts=districts)


@app.route('/apply', methods=['POST'])
def register():
    contact = request.form['contact_no']
    name = request.form['name']
    loc1 = request.form['loc1']
    loc2 = request.form['loc2']
    fromDate = request.form['fromDate']
    toDate = request.form['toDate']
    fromTime = request.form['fromTime']
    toTime = request.form['toTime']
    service = servicTypes[request.form['service']]

    res = session.get('https://api.covid19india.org/v4/data.json')
    info = res.json()

    cases_loc1 = info['BR']['districts'][loc1]['total']['confirmed']
    cases_loc2 = info['BR']['districts'][loc2]['total']['confirmed']

    minCases = min(cases_loc1, cases_loc2)
    maxCases = max(cases_loc1, cases_loc2)

    diff = ((maxCases - minCases)/minCases)*100

    status = ''

    if diff >= 100:
        status = 'NOT CONFIRMED'
    else:
        status = 'CONFIRMED'

    message = client.messages.create(
        to=f'whatsapp:+91{contact}',
        from_='whatsapp:+14155238886',
        body=f'Hi {name},\nYour E-Pass Application\nfor travel between districts:\n{loc1}(total confirmed cases: {cases_loc1})\nand\n{loc2}(total confirmed cases: {cases_loc2})\nFrom: {fromDate} Till: {toDate}\nbetween the Time Frame: {fromTime} - {toTime}\nis *{status}*'
    )

    return render_template('epass.response.html', contact=contact, name=name, loc1=f'{loc1}(total confirmed cases: {cases_loc1})', loc2=f'{loc2}(total confirmed cases: {cases_loc2})',
                           service=service, fromDate=fromDate, toDate=toDate, fromTime=fromTime, toTime=toTime, status=status)


if __name__ == '__main__':
    app.run(debug=True)
