#!/usr/bin/python

from bs4 import BeautifulSoup
from requests import get
import re
import requests
import csv
from itertools import zip_longest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os.path
from csv_diff import load_csv, compare
import json
from datetime import datetime

with open("config.json", "r") as f:
    my_dict = json.load(f)

prospectMotorsURL = my_dict["prospectMotorsURL"]
prospectMotorsPage = requests.get(prospectMotorsURL)
prospectMotorsSoup = BeautifulSoup(prospectMotorsPage.content,
                                   'html.parser')

emailfrom = my_dict["emailFrom"]
emailto = my_dict["emailTo"]
password = my_dict["password"]
port = my_dict["port"]
server = my_dict["server"]
fileToSend = my_dict["fileToSend"]
oldCarsCsvFile = my_dict["oldCarsCsvFile"]

cars_list = []

# GET CAR DETAILS

car_items = [
    'item-engine',
    'item-transmission',
    'item-body',
    'item-nct',
    'item-owner',
    'item-colour',
]
car_list_append = [
    'car_engines_list',
    'car_transmissions_list',
    'car_body_types_list',
    'car_nct_years_list',
    'car_owners_list',
    'car_colours_list',
]

car_details_list = []
prospect_car_details = prospectMotorsSoup.find_all('div',
                                                   class_='tittle-list-car')
for car_detail in prospect_car_details:
    sep = ', '
    start = '<strong>'
    end = ', '
    car = str(re.search('%s(.*)%s' % (start, end),
                        str(car_detail)).group(1))
    car = re.sub('&lt;/strong&gt; ', '', car)
    car = re.sub('</strong> ', '', car)
    car = car[0:24]
    car = car.split(sep, 1)[0]
    car = re.sub('(\\b[ A-Za-z_@./#&+-] \\b|\\b [ A-Za-z_@./#&+-]\\b)',
                 '', car)
    car_details_list.append(car)
cars_list.append(car_details_list)

for (i, j) in zip(car_items, car_list_append):
    j = []
    car_engines = prospectMotorsSoup.find_all('li', class_=i)
    for car_engine in car_engines:
        start = '/>'
        end = '\n'
        engine = str(re.search('%s(.*)%s' % (start, end),
                               str(car_engine)).group(1))
        j.append(engine)
    cars_list.append(j)

car_odometer_counts_list = []
car_odometer_counts = prospectMotorsSoup.find_all('li',
                                                  class_='item-odometer')
for car_odometer_count in car_odometer_counts:
    start = '/>'
    end = ' miles'
    odometer_count = str(re.search('%s(.*)%s' % (start, end),
                                   str(car_odometer_count)).group(1))
    car_odometer_counts_list.append(odometer_count)
cars_list.append(car_odometer_counts_list)

car_years_list = []
car_years = prospectMotorsSoup.find_all('li', class_='item-year')
for car_year in car_years:
    start = 'Year '
    end = '\n'
    car_year = str(re.search('%s(.*)%s' % (start, end),
                             str(car_year)).group(1))
    car_years_list.append(car_year)
cars_list.append(car_years_list)

car_prices_list = []
car_prices = prospectMotorsSoup.find_all('span', class_='uprice')
for car_price in car_prices:
    start = '€'
    end = '</'
    car_price = str(re.search('%s(.*)%s' % (start, end),
                              str(car_price)).group(1))
    car_prices_list.append(car_price)
cars_list.append(car_prices_list)

# CREATE CSV FILES

if os.path.isfile('./' + fileToSend):
    os.rename(fileToSend, oldCarsCsvFile)

    export_data = zip_longest(fillvalue='', *cars_list)
    with open('cars.csv', 'w', encoding='ISO-8859-1', newline='') as \
            myfile:
        wr = csv.writer(myfile)
        wr.writerow((
            'Details',
            'Engine Size',
            'Transmission',
            'Body Type',
            'Odometer Count (Miles)',
            'NCT Year',
            'No. of Owners',
            'Colour',
            'Year',
            'Price',
        ))
        wr.writerows(export_data)
    myfile.close()

    diff = compare(load_csv(open(fileToSend), key='Price'),
                   load_csv(open(oldCarsCsvFile), key='Price'))

    json_str = json.dumps(diff)
    resp = json.loads(json_str)
    resp = json.dumps(resp['added'], indent=1)

    if resp != '[]':
        # EMAIL

        msg = MIMEMultipart()
        msg['From'] = emailfrom
        msg['To'] = emailto
        msg['Subject'] = \
            'New Prospect Motors Car(s) - {date}'.format(date=str(datetime.now().strftime('%d/%m/%Y %H:%M'
                                                                                          )))
        emailBody = '{newCars}'.format(newCars=resp)
        emailBody = MIMEText(emailBody)
        msg.attach(emailBody)

        server = smtplib.SMTP(server, port)
        server.starttls()
        server.login(emailfrom, password)
        server.sendmail(emailfrom, emailto, msg.as_string())
else:

    export_data = zip_longest(fillvalue='', *cars_list)
    with open('cars.csv', 'w', encoding='ISO-8859-1', newline='') as \
            myfile:
        wr = csv.writer(myfile)
        wr.writerow((
            'Details',
            'Engine Size',
            'Transmission',
            'Body Type',
            'Odometer Count (Miles)',
            'NCT Year',
            'No. of Owners',
            'Colour',
            'Year',
            'Price',
        ))
        wr.writerows(export_data)
    myfile.close()
