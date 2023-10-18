import requests
from file_path import file_path

# property number: 1 to 295840

base_url = 'https://www.padctn.org/prc/property/'
for property_number in range(1,4):
    url = base_url+str(property_number)
    response = requests.get(url)
    html = response.text

    # Open the file in write mode and write the HTML content
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(html)
    print(f"URL {property_number} written to output file.")

