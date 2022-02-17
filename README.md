# Car Dealership Website Scraper
### Python script that scrapes a local car dealership for cars for sale. 

## Overview: 
This script will initially gather a list of cars for sale from the dealership and then add then to a CSV file. 

When used in conjunction with cronjob (to run every few minutes), the script will once again scrape the website, rename the existing CSV file, and then save the newly gathered list to a CSV file (as the name of the original CSV file to avoid the clutter and memory loss from many duplicate CSV files).

The script then compares the two CSV files and looks for any differences (i.e., new cars). If any are found, the script then sends only the new car listings to a specified email address.

## Technical Approach:
This script uses the `requests` and `BeautifulSoup` libraries to initially scrape the dealership website using the HTML elements from the webpage for details on each listed car (such as make, model, year, price, engine size, etc.) and then adds them to a CSV file. 

After it has first been run, the script will once again scrape the website, rename the existing CSV file (`oldCarsList.csv`), and then save the newly gathered list to a CSV file (as the name of the original CSV file (`cars.csv`) to avoid the clutter and needless memory loss from many duplicate CSV files).

The script then uses the `csv_diff` library to compare the two CSV files and looks for any differences (i.e., new cars). If any are found, the script then uses the `smtplib`, `MIMEText`, and `MIMEMultipart` libraries to send only the new car listings to a specified email address in a JSON format.

```json
{
  "Details": "2014 Ford Fiesta",
  "Engine Size": "1.0 Petrol",
  "Transmission": "Manual",
  "Body Type": "Hatchback",
  "Odometer Count (Miles)": "109,620",
  "NCT Year": "Jun-23",
  "No. of Owners": "3 Owners",
  "Colour": "Blue",
  "Year": "2014",
  "Price": "10,950"
}
```

I use this in conjunction with cronjob (to run every few minutes) on a RaspberryPi Zero to keep an eye out for good deals on new cars as soon as they appear.
