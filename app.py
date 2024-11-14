from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import requests
import os
import uuid
import chardet
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Configuration de ton API Key Google Maps
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
            city = postal_code = country = None
            
            for component in address_components:
                if 'locality' in component['types']:
                    city = component['long_name']
                if 'postal_code' in component['types']:
                    postal_code = component['long_name']
                if 'country' in component['types']:
                    country = component['long_name']
            
            # Cache the result
            cache[(lat, lon)] = (city, postal_code, country)
            return city, postal_code, country
        else:
            return None, None, None
    except Exception as e:
        print(f"Error for coordinates ({lat}, {lon}): {e}")
        return None, None, None

# Assurez-vous que le dossier 'uploads' existe
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
            # Sauvegarder le fichier téléchargé
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Détecter l'encodage du fichier
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']

            # Lire le fichier CSV avec l'encodage détecté
            df = pd.read_csv(file_path, sep=';', encoding=encoding)

            # Remplacer les virgules par des points dans les colonnes de latitude et longitude
            df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
            df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)

            # Ajouter des colonnes vides si elles ne sont pas déjà présentes
            df['City'] = df.get('City', None)
            df['ZIP code'] = df.get('ZIP code', None)
            df['Country'] = df.get('Country', None)

            # Initialiser le cache
            cache = {}

            # Définir une fonction pour traiter chaque ligne
            def process_row(index, row):
                if pd.isna(row['City']) or pd.isna(row['ZIP code']) or pd.isna(row['Country']):
                    city, postal_code, country = get_address_info(row['Latitude'], row['longitude'], cache)
                    return index, city, postal_code, country
                return index, row['City'], row['ZIP code'], row['Country']

            # Utiliser ThreadPoolExecutor pour le traitement parallèle
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(process_row, index, row) for index, row in df.iterrows()]
                for future in as_completed(futures):
                    index, city, postal_code, country = future.result()
                    df.at[index, 'City'] = city
                    df.at[index, 'ZIP code'] = postal_code
                    df.at[index, 'Country'] = country

            # Enregistrer le DataFrame mis à jour dans un fichier CSV
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
    return send_from_directory('uploads', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)