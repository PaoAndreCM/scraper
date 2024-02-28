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
header = ["Map & Parcel", "Current Owner", "Mailing Address", "Zone", "Neighborhood", "Location", "Land Area (Acres)", #"Most Recent Sale Date", "Most Recent Sale Price", "Deed Reference", "Tax District"
             ]

#Array for entries (each element in the array will be a tuple)
data = []

base_url = 'https://www.padctn.org/prc/property/'
url_suffix = '/print'
for property_number in range(1400,1401):
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
        # Find all <ul> elements, which contain the list elements we're interested in
        property_info_lists = soup.find_all('ul', {'class': 'att'} ) # TODO: Delete in future if not needed (not used atm)

        # Retrieve the elements in sections GENERAL PROPERTY INFORMATION, and CURRENT PROPERTY APPRAISAL
        property_infos = general_info_heading.find_all_next('li', limit=20) # Remember: element w/ index 5 is an empty <li> element
        print("property infos:")
        print(property_infos)

        index = 0
        # Iterate through each <ul> element
        for property_info_list in property_info_lists:
            # Find all <li> elements within the <ul>
            property_info_items = property_info_list.find_all('li')

            print()
            print(f"Property info items {index}")
            print(property_info_items)
            index+=1

            # Extract values from each list item
            # values = [item.text.strip().split(':').strip() for item in property_info_items]
            # values = [item.text.strip() for item in property_info_items]
            # data.append(values)
    else:
        logging.info(f"No General Info found for parcel {property_number}")


df = pd.DataFrame(data, columns=header)

df.to_csv(file_path_csv, mode='a', header=True, index=False)

# # Open the CSV file and write the values to separate columns
# with open(file_path_csv, 'a', newline='', encoding='utf-8') as csvfile:
#     writer = csv.writer(csvfile)

#     # Write the values to the CSV file
#     writer.writerow(values)

# print(f"CSV file '{file_path_csv}' created successfully.")