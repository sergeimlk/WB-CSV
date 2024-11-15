from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import requests
import os
import uuid
import chardet
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

app = Flask(__name__)

# Configuration for Google Maps API Key
API_KEY = 'AIzaSyBO2n-TzeF3WRlNlVzN-rn8SzBL_1xym7I'

# Function to get address info from Google Maps API
def get_address_info(lat, lon, cache):
    if (lat, lon) in cache:
        return cache[(lat, lon)]
    
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK' and len(data['results']) > 0:
            address_components = data['results'][0]['address_components']
            formatted_address = data['results'][0].get('formatted_address', '').upper()
            city = postal_code = country = None
            
            # Parsing the address components with improved logging
            print(f"Coordinates: ({lat}, {lon})")
            print("Full API Response:", data)  # Log the full response for debugging

            for component in address_components:
                print("Address Component:", component)  # Log each address component for insight
                
                if 'locality' in component['types']:  # Primary city field
                    city = component['long_name'].upper()
                elif 'administrative_area_level_1' in component['types'] and not city:
                    city = component['long_name'].upper()  # Fallback to larger administrative area
                
                # Check for postal code in different possible fields
                if 'postal_code' in component['types']:
                    postal_code = component['long_name'].upper()
                
                if 'country' in component['types']:
                    country = component['long_name'].upper()
            
            # Debug if postal_code is missing or if it didn't parse correctly
            if not postal_code:
                print(f"No postal code found for coordinates ({lat}, {lon})")
                print("API Address Components:", address_components)

            # Cache the result if valid data is found
            if formatted_address or city or postal_code or country:
                cache[(lat, lon)] = (formatted_address, city, postal_code, country)
            return formatted_address, city, postal_code, country
        else:
            print(f"No results found for coordinates ({lat}, {lon})")
            return None, None, None, None
    except Exception as e:
        print(f"Error for coordinates ({lat}, {lon}): {e}")
        return None, None, None, None

# Ensure the 'uploads' folder exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Save the uploaded file
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Detect file encoding
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']

            # Read the CSV file with the detected encoding
            df = pd.read_csv(file_path, sep=';', encoding=encoding)

            # Replace commas with dots in latitude and longitude columns
            df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)

            # Add empty columns if not already present
            df['Address'] = df.get('Address', None)
            df['City'] = df.get('City', None)
            df['ZIP code'] = df.get('ZIP code', None)
            df['Country'] = df.get('Country', None)

            # Ensure ZIP code column is of string type
            df['ZIP code'] = df['ZIP code'].astype(str)

            # Initialize cache
            cache = {}

            # Define a function to process each row
            def process_row(index, row):
                if pd.isna(row['Address']) or pd.isna(row['City']) or pd.isna(row['ZIP code']) or pd.isna(row['Country']):
                    formatted_address, city, postal_code, country = get_address_info(row['Latitude'], row['longitude'], cache)
                    
                    # Only update if valid data is returned
                    address = formatted_address if formatted_address else row['Address']
                    city = city if city else row['City']
                    postal_code = postal_code.upper() if postal_code else row['ZIP code']  # Ensure uppercase
                    country = country if country else row['Country']
                    
                    # Log missing data if the API didn't return results
                    if not address or not city or not postal_code or not country:
                        print(f"Incomplete data for row {index}: Address={address}, City={city}, ZIP={postal_code}, Country={country}")

                    return index, address, city, postal_code, country
                return index, row['Address'], row['City'], row['ZIP code'].upper(), row['Country']  # Ensure uppercase for existing ZIP codes

            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(process_row, index, row) for index, row in df.iterrows()]
                for future in as_completed(futures):
                    index, address, city, postal_code, country = future.result()
                    df.at[index, 'Address'] = address.upper() if address else None  # Convert to uppercase
                    df.at[index, 'City'] = city
                    df.at[index, 'ZIP code'] = postal_code
                    df.at[index, 'Country'] = country
                    print(f"Processed row {index}: Address={address}, City={city}, ZIP={postal_code}, Country={country}")  # Debugging

            # Save the updated DataFrame to a new CSV file
            output_filename = 'processed_' + str(uuid.uuid4()) + '.csv'
            output_file_path = os.path.join('uploads', output_filename)
            df.to_csv(output_file_path, sep=';', index=False, encoding='utf-8')

            return jsonify({'filename': output_filename})
        else:
            return jsonify({'error': 'No file provided or file is not a CSV'}), 400
    except Exception as e:
        app.logger.error('Error processing file: %s', e)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory('uploads', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)