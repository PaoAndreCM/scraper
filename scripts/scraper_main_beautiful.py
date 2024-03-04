import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
import requests
from file_path import file_path
from file_path import file_path_csv
from file_path import log_file_path
# import csv
import logging

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# property number: 1 to 295840

# with open(file_path_csv, 'w', newline="") as file:
#     writer = csv.writer(file)
#     field = ["Map & Parcel", "Current Owner", "Mailing Address", "Zone", "Neighborhood"#, "Location", "Land Area (Acres)", "Most Recent Sale Date", "Most Recent Sale Price", "Deed Reference", "Tax District"
#              ]
#     writer.writerow(field)

# Array for column names
header = ["Map & Parcel", "Current Owner", "Mailing Address", "Zone", "Neighborhood",
          "Location", "Land Area (Acres)", "Most Recent Sale Date", "Most Recent Sale Price", "Deed Reference", "Tax District",
          "Assessment Year", "Land Value", "Improvement Value", "Total Appraisal Value", 
          "Assessment Classification", "Assessment Land", "Assessment Improvement", "Assessment Total",
          # Improvement attributes headers:
        #   "Building Type", "Year Built", "Square Footage", "Number of Living Units", "Building Grade", "Building Condition",
        #   "Rooms", "Beds", "Baths", "Half Bath", "Fixtures", 
        #   "Exterior Wall", "Frame Type", "Story Height", "Foundation Type", "Roof Cover"
             ]

#Array for entries (each element in the array will be a tuple)
data = []

base_url = 'https://www.padctn.org/prc/property/'
url_suffix = '/print'
for property_number in range(1401,1402):
    url = base_url+str(property_number)+url_suffix # Build the url to take info from
    response = requests.get(url) # request website
    html = response.text # store response (html from website)
    soup = BeautifulSoup(html, 'html.parser') # Parse the HTML using Beautiful Soup
   
    # Lines below used to store html in text file
    # with open(file_path, 'w', encoding='utf-8') as file:
    #     file.write(html)

    # Find the heading "GENERAL PROPERTY INFORMATION" 
    general_info_heading = soup.find('h4', {'class': 'featurette-heading'}, string='GENERAL PROPERTY INFORMATION')

    # Check if the heading is found
    if general_info_heading:

        # Retrieve the elements in sections GENERAL PROPERTY INFORMATION, and CURRENT PROPERTY APPRAISAL
        property_infos = general_info_heading.find_all_next('li', limit=20) # Remember: element w/ index 5 is an empty <li> element

        # create row 
        # values = []
        # for index, item in enumerate(property_infos):
        #     # in both cases below, split retrieved string from <li> element and only keep part after ':'
        #     # remove unwanted spaces and periods in 'Map & Parcel' value
        #     if index == 0:
        #         values.append(item.text.split(':')[1].strip().replace(" ", "").replace(".", ""))
        #     else:
        #         # element w/ index 5 is empty so skip it
        #         if index != 5:
        #             values.append(item.text.split(':')[1].strip())

        values = [item.text.split(':')[1].strip() for index, item in enumerate(property_infos) if index != 5] # does not remove unwanted spaces and periods in 'Map & Parcel' value

        data.append(values)
        # print(data)
    else:
        logging.info(f"No General Info found for parcel {property_number}")


df = pd.DataFrame(data, columns=header)

df.to_csv(file_path_csv, sep=';', mode='a', header=True, index=False)