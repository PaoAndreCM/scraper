import csv
import os
import time
from bs4 import BeautifulSoup
import requests
from file_path import file_path_csv
from file_path import log_file_path
import logging

# Function to create the CSV file and write column names if the file doesn't exist
def create_csv_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(["Map & Parcel", "Current Owner", "Mailing Address", "Zone", "Neighborhood",
          "Location", "Land Area (Acres)", "Most Recent Sale Date", "Most Recent Sale Price", "Deed Reference", "Tax District",
          "Assessment Year", "Land Value", "Improvement Value", "Total Appraisal Value", 
          "Assessment Classification", "Assessment Land", "Assessment Improvement", "Assessment Total",
          "Legal description",
          # Improvement attributes headers: 
          "Card #",
          "Building Type", "Year Built", "Square Footage", "Number of Living Units", "Building Grade", "Building Condition",
          "Rooms", "Beds", "Baths", "Half Bath", "Fixtures", 
          "Exterior Wall", "Frame Type", "Story Height", "Foundation Type", "Roof Cover",
          # Assosciated URL
          "Property #"
             ])

# Function to append a row to the CSV file
def append_row(file_path, row):
    with open(file_path, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(row)

# Function to check if a value is convertible to int
def is_numeric(s):
    try:
        float(s)  # Attempt to convert the string to a float
        return True  # If successful, the string is numeric
    except ValueError:
        return False  # If an error occurs, the string is not numeric    

# Function to get the next available row number
def get_last_row_number_and_property_number(file_path):
    with open(file_path, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        rows = list(reader)
        row_count = len(rows) # Num of written rows
        last_scraped_property = rows[-1][-1] # last property scraped
        if not is_numeric(last_scraped_property):
            last_scraped_property = 0
    return row_count, last_scraped_property  # Return the last row number written to and the property number corresponding to it

# Function to append new character at end of file if it doesn't have one yet (if file has been modified manualy, for example)
def ensure_last_char_is_newline(file_path):
    with open(file_path, 'ab+') as file:
            file.seek(-1, 2)  # Move the file pointer to the end of the file
            last_char = file.read(1)  # Read the last character
            # Check if the last character is a newline character
            if last_char != b'\n': # if file doesn't end in new line, append newline char to end of it
                file.write(b'\n')
            
            

start = time.time()
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
create_csv_file(file_path_csv)
ensure_last_char_is_newline(file_path_csv)

base_url = 'https://www.padctn.org/prc/property/'
url_suffix = '/print'
    

latest_row_number, property_num_start = get_last_row_number_and_property_number(file_path_csv) 
property_num_start = int(property_num_start) + 1

# property number: 1 to 295840 # as of 10 March 2024
property_num_end = 295840 # real
# property_num_end = property_num_start + 1 # for debugging
# property_num_end = 10 # custom

for property_number in range(property_num_start, property_num_end):
    url = base_url+str(property_number)+url_suffix # Build the url to take info from
    # request website
    try:
        response = requests.get(url)
        html = response.text # store response (html from website)
        if response.text:
            # Process the response
            logging.info(f"Successfully retrieved text for property {property_number} from URL: {url}")
        else:
            logging.error(f"Request for property {property_number} from URL: {url} failed.")
    except requests.RequestException as e:
        # Handle any exceptions that occurred during the request
        logging.error(f"An error occurred: {e}")
    
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
        # values = []
        # values.append(str(property_number))
        # create row condensed in list comprehension (same code as commented out above)
        values = [item.text.split(':')[1].strip() for index, item in enumerate(property_infos) if index != 5] # does not remove unwanted spaces and periods in 'Map & Parcel' value
        # [values.append(item.text.split(':')[1].strip()) for index, item in enumerate(property_infos) if index != 5] # does not remove unwanted spaces and periods in 'Map & Parcel' value
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
            values_card.append(str(index) +' of '+ str(len(improvement_attribute_headers)))
            improvement_attributes = attribute_header.find_all_next('li', limit=16)
            [values_card.append(item.text.split(':')[1].strip()) for item in improvement_attributes] #scrape the improvement attributes of the current card
            values_card.append(property_number)

            for value in values_card:
                logging.info(value)
                print(value)

            append_row(file_path_csv, values_card)
            latest_row_number+=1

            logging.info(f"Property number {property_number} card {index} of {len(improvement_attribute_headers)} successfully scraped to row number {latest_row_number}")

    else:
        logging.info(f"No General Info found for parcel {property_number}")

end = time.time()

logging.info(f"Execution time is {end-start}")