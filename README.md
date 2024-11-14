🌍 CSV Address Enhancer Web Application 🌎
Bienvenue dans l'application web interne CSV Address Enhancer pour Winback ! 🎉

📚 Vue d'ensemble
Ce projet est une application web développée en Python permettant aux utilisateurs de télécharger un fichier CSV contenant des données géographiques (latitude et longitude). L'application convertit et formate automatiquement le fichier en ajoutant les informations d'adresse (ville, code postal, pays) nécessaires, selon le modèle BDD-SSO.csv.

✨ Fonctionnalités
Interface Web Simple : Permet le téléchargement de fichiers CSV via une interface intuitive. 🖥️
Conversion de Données : Traite automatiquement les fichiers CSV en ajoutant les informations d’adresse. 🔄
Intégration avec l'API Google Maps : Utilise l'API Google Maps Geocoding pour récupérer des informations précises sur les adresses. 🗺️
Sortie CSV Améliorée : Permet de télécharger un fichier CSV enrichi avec les colonnes d'adresse ajoutées. 📥
Gestion des Erreurs : Affiche des messages d'erreur clairs et des conseils en cas de problème lors du traitement. 🚨
🚀 Comment ça fonctionne
Télécharger votre fichier CSV : L'application accepte un fichier CSV contenant au minimum des colonnes de Latitude et Longitude. 📄
Traitement des données :
Lecture et formatage du fichier CSV, y compris le nettoyage des données.
Récupération des informations d'adresse (ville, code postal, pays) via l'API Google Maps.
Mise en cache des résultats pour éviter les appels API redondants.
Télécharger le fichier enrichi : Une fois le traitement terminé, un lien de téléchargement est fourni pour récupérer le fichier CSV converti. 📂
🛠️ Instructions d'installation
Prérequis
Python 3.x installé sur votre machine. 🐍
pip pour la gestion des packages Python. 📦
Une clé d'API valide pour Google Maps Geocoding. 🔑
Étapes d'installation
Clonez le dépôt :

bash
Copier le code
git clone https://github.com/votre-repo/CSV-Address-Enhancer.git
cd CSV-Address-Enhancer
Créez un environnement virtuel (optionnel mais recommandé) :

bash
Copier le code
python3 -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate
Installez les packages requis :

bash
Copier le code
pip install -r requirements.txt
Configurez votre clé API Google Maps :

Créez un fichier .env dans le répertoire racine du projet.
Ajoutez-y la ligne suivante, en remplaçant your_api_key_here par votre clé d'API :
makefile
Copier le code
GOOGLE_MAPS_API_KEY=your_api_key_here
Lancez l'application :

bash
Copier le code
python app.py
Accédez à l'interface web :

Ouvrez votre navigateur web et naviguez vers http://127.0.0.1:5000.
Vous verrez la page de téléchargement de l'application web. 🌐
📁 Structure du projet
app.py : Script principal contenant la logique backend.
templates/index.html : Modèle HTML pour l'interface web.
static/ :
styles.css : Styles CSS pour la page web.
script.js : JavaScript pour la gestion du formulaire et des interactions.
uploads/ : Répertoire où les fichiers téléchargés sont stockés temporairement.
processed/ : Répertoire où les fichiers CSV traités sont enregistrés.
📝 Instructions d'utilisation
Préparez votre fichier CSV :

Assurez-vous que votre fichier CSV contient les colonnes Latitude et Longitude en format décimal.
Téléchargez le fichier :

Cliquez sur le bouton "Télécharger" de la page web.
Sélectionnez votre fichier CSV et soumettez le formulaire.
Attendez le traitement :

L'application va traiter le fichier et un indicateur de chargement s'affichera.
Téléchargez le fichier enrichi :

Une fois le traitement terminé, un lien de téléchargement s'affiche pour récupérer votre fichier CSV enrichi.
⚠️ Notes importantes
Limites d'utilisation de l'API : Faites attention aux quotas de requêtes de l'API Google Maps Geocoding pour éviter de les dépasser. ⏳
Sécurité de la clé API : Gardez votre clé d'API sécurisée et ne l'exposez pas publiquement. 🔐
Confidentialité des données : Les fichiers téléchargés sont traités en local et ne sont pas transmis vers des serveurs externes. 🛡️
💡 Technologies utilisées
Python 3 : Langage de programmation pour le développement backend.
Flask : Framework web pour la gestion des requêtes HTTP.
Pandas : Bibliothèque de manipulation de données pour la lecture et le traitement des fichiers CSV.
Google Maps Geocoding API : Service pour obtenir des informations d'adresse à partir de coordonnées géographiques.
HTML, CSS, JavaScript : Technologies frontend pour la création de l'interface web.
🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à soumettre des issues ou des pull requests pour améliorer le projet. 🤗

📄 Licence
Ce projet est sous licence MIT.

📬 Contact
Pour toute question ou suggestion, veuillez contacter le responsable du projet. 📧
