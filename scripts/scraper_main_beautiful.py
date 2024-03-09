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

# Array for column names
header = ["Map & Parcel", "Current Owner", "Mailing Address", "Zone", "Neighborhood",
          "Location", "Land Area (Acres)", "Most Recent Sale Date", "Most Recent Sale Price", "Deed Reference", "Tax District",
          "Assessment Year", "Land Value", "Improvement Value", "Total Appraisal Value", 
          "Assessment Classification", "Assessment Land", "Assessment Improvement", "Assessment Total",
          "Legal description",
          # Improvement attributes headers: 
          "Card #",
          "Building Type", "Year Built", "Square Footage", "Number of Living Units", "Building Grade", "Building Condition",
          "Rooms", "Beds", "Baths", "Half Bath", "Fixtures", 
          "Exterior Wall", "Frame Type", "Story Height", "Foundation Type", "Roof Cover"
             ]

#Array for entries (each element in the array will be a tuple)
data = []

base_url = 'https://www.padctn.org/prc/property/'
url_suffix = '/print'
for property_number in range(1,11):
    url = base_url+str(property_number)+url_suffix # Build the url to take info from
    response = requests.get(url) # request website
    html = response.text # store response (html from website)
    soup = BeautifulSoup(html, 'html.parser') # Parse the HTML using Beautiful Soup

    # Find the heading "GENERAL PROPERTY INFORMATION" 
    general_info_heading = soup.find('h4', {'class': 'featurette-heading'}, string='GENERAL PROPERTY INFORMATION')

    # Check if the heading is found
    if general_info_heading:

        # sections GENERAL PROPERTY INFORMATION, and CURRENT PROPERTY APPRAISAL
        property_infos = general_info_heading.find_all_next('li', limit=20) # Remember: element w/ index 5 is an empty <li> element

        # create row (commented out as it is in list comprehension underneath)
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

        # create row condensed in list comprehension (same code as commented out above)
        values = [item.text.split(':')[1].strip() for index, item in enumerate(property_infos) if index != 5] # does not remove unwanted spaces and periods in 'Map & Parcel' value

        # section LEGAL DESCRIPTION
        legal_description_heading = soup.find('h4', {'class': 'featurette-heading'}, string='LEGAL DESCRIPTION') # starting point
        legal_description = legal_description_heading.find_next('li').text.strip()
        values.append(legal_description)

        # section(s) IMPROVEMENT ATTRIBUTES
        improvement_attribute_headers = soup.find_all( string='IMPROVEMENT ATTRIBUTES - ')
        index = 0
        for attribute_header in improvement_attribute_headers:
            index+=1
            values_card = values[:] # make a copy of values
            values_card.append(str(index))
            improvement_attributes = attribute_header.find_all_next('li', limit=16)
            [values_card.append(item.text.split(':')[1].strip()) for item in improvement_attributes] #scrape the improvement attributes of the current card
            data.append(values_card)
    else:
        logging.info(f"No General Info found for parcel {property_number}")


df = pd.DataFrame(data, columns=header)

df.to_csv(file_path_csv, sep=';', mode='a', header=True, index=False)