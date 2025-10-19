import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime



def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


#permet d'importer les données des fichiers clubs
@app.route('/')
def index():
    print("=== Route index appelée ===")
    return render_template('index.html', clubs=clubs,)

#permet d'afficher le résumé après connexion
@app.route('/showSummary', methods=['POST'])
def showSummary():
    print("=== Route showSummary appelée ===")
    email = request.form['email']
    print(f"Email reçu: {email}")
    print(f"Clubs disponibles: {[c['email'] for c in clubs]}")
    
    club_list = [club for club in clubs if club['email'] == email]
    print(f"Club trouvé: {club_list}")
    
    if not club_list:
        print("AUCUN CLUB TROUVÉ - Redirection vers index")
        flash("Désolé, cette adresse email n'est pas reconnue.")
        return redirect(url_for('index'))
    
    # Afficher la page de bienvenue avec le club et les compétitions
    club = club_list[0]
    print(f"Club sélectionné: {club['name']}")
    return render_template('welcome.html', club=club, competitions=competitions)

#route pour afficher la page de réservation
@app.route('/book/<competition>/<club>')
def book(competition, club):
    print(f"=== Route book appelée: {competition} / {club} ===")
    foundClub = [c for c in clubs if c['name'] == club]
    foundCompetition = [c for c in competitions if c['name'] == competition]
    
    # Vérifier si le club et la compétition existent
    if not foundClub or not foundCompetition:
        print("ERREUR: Club ou compétition introuvable")
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    
    # Vérifier si la compétition est passée
    competition_date = datetime.strptime(foundCompetition[0]['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.now():
        print(f"ERREUR: Compétition passée ({foundCompetition[0]['date']})")
        flash("Impossible de réserver pour une compétition passée")
        return render_template('welcome.html', club=foundClub[0], competitions=competitions)
    
    # Afficher la page de réservation
    return render_template('booking.html', club=foundClub[0], competition=foundCompetition[0])



#route pour traiter l'achat des places
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    print("=== Route purchasePlaces appelée ===")
    competition_list = [c for c in competitions if c['name'] == request.form['competition']]
    club_list = [c for c in clubs if c['name'] == request.form['club']]

    # Vérifier si le club et la compétition existent
    if not competition_list or not club_list:
        print("ERREUR: Données invalides")
        flash("Erreur lors de la réservation")
        return redirect(url_for('index'))
    
    # Récupérer les données nécessaires
    competition = competition_list[0]
    club = club_list[0]
    placesRequired = int(request.form['places'])
    placesDisponibles = int(competition['numberOfPlaces'])
    
    # Vérifier si assez de places disponibles
    if placesRequired > placesDisponibles:
        print(f"ERREUR: Pas assez de places ({placesRequired} > {placesDisponibles})")
        flash(f"Seulement {placesDisponibles} place(s) disponible(s) pour cette compétition")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Vérifier si le club a assez de points
    if int(club['points']) < placesRequired:
        print(f"ERREUR: Pas assez de points ({club['points']} < {placesRequired})")
        flash(f"Vous n'avez pas assez de points. Points disponibles: {club['points']}")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Déduire les points et les places
    club['points'] = str(int(club['points']) - placesRequired)
    competition['numberOfPlaces'] = placesDisponibles - placesRequired
    
    # Afficher la confirmation
    print(f"Réservation: {placesRequired} places pour {club['name']} - Points restants: {club['points']}")
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


#route pour se déconnecter
@app.route('/logout')
def logout():
    print("=== Route logout appelée ===")
    return redirect(url_for('index'))

#point d'entrée de l'application
if __name__ == "__main__": 
    app.run(debug=True)