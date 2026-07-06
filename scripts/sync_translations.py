#!/usr/bin/env python3
# flake8: noqa: E501
"""Apply reviewed project translations and keep British English source-complete."""

from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parents[1]

FR = {
    "%(count)s bt.": "%(count)s bt.",
    "Out of stock": "Rupture",
    "My selection": "Ma sélection",
    "Search wines": "Rechercher des vins",
    "Search for a wine, estate or grape": "Rechercher un vin, un domaine ou un cépage",
    "Filters": "Filtres",
    "wines": "vins",
    "More filters": "Plus de filtres",
    "Apply filters": "Appliquer les filtres",
    "Your selection is empty": "Votre sélection est vide",
    "Add your first wine or clear the active filters.": "Ajoutez votre premier vin ou effacez les filtres actifs.",
    "Default Shelf": "Étagère par défaut",
    "Default storage for wines": "Stockage par défaut pour les vins",
    "Cellar": "Cave",
    "(opens in new tab)": "(s’ouvre dans un nouvel onglet)",
    "Storage Name": "Nom du stockage",
    "The selected row exceeds the number of rows in the storage.": "La rangée sélectionnée dépasse le nombre de rangées du stockage.",
    "The selected column exceeds the number of columns in the storage.": "La colonne sélectionnée dépasse le nombre de colonnes du stockage.",
    "Finish Bottle": "Terminer la bouteille",
    'Are you sure you have finished the bottle "%(name)s" from "%(storage)s"? It will be marked as consumed in your history.': "Avez-vous terminé la bouteille « %(name)s » du stockage « %(storage)s » ? Elle sera marquée comme consommée dans votre historique.",
    "Open Bottle": "Ouvrir la bouteille",
    "Bottles": "Bouteilles",
    "Contents": "Contenu",
    "Drink by": "À boire avant",
    "Back to Storages": "Retour aux stockages",
    "Your Storages": "Vos stockages",
    "No storages yet.": "Aucun stockage pour le moment.",
    "Email Notifications": "Notifications par e-mail",
    "Reminder to finish your opened wine(s)": "Rappel pour terminer vos bouteilles ouvertes",
    "Name contains": "Le nom contient",
    "Wine Type": "Type de vin",
    "Source": "Source",
    "Country": "Pays",
    "Sweetness": "Sucrosité",
    "Enter the name of the region the wine is from.": "Saisissez le nom de la région d’origine du vin.",
    "Enter the name of the appellation of the wine.": "Saisissez l’appellation du vin.",
    "Enter the barcode number of the wine as indicated on the label or scan using the button below.": "Saisissez le code-barres indiqué sur l’étiquette ou scannez-le avec le bouton ci-dessous.",
    "Drink soon": "À boire bientôt",
    "References": "Références",
    "Bottles in stock": "Bouteilles en stock",
    "Regions": "Régions",
    "Create Wine": "Créer le vin",
    "Scan again": "Scanner à nouveau",
    "General Settings": "Paramètres généraux",
    "My rating": "Ma note",
    "Serving": "Service",
    "Tasting notes": "Notes de dégustation",
    "No tasting notes yet.": "Aucune note de dégustation pour le moment.",
    "Temperature": "Température",
    "Not assigned": "Non renseigné",
    "Remove a bottle": "Retirer une bouteille",
    "Add to stock": "Ajouter au stock",
    "Edit": "Modifier",
    "Scan": "Scanner",
    "Full details": "Fiche complète",
    "Close wine details": "Fermer la fiche du vin",
    "Cell": "Case",
    "ABV": "Taux d’alcool",
}

DE = {
    "%(count)s bt.": "%(count)s Fl.",
    "Out of stock": "Nicht vorrätig",
    "My selection": "Meine Auswahl",
    "Search wines": "Weine suchen",
    "Search for a wine, estate or grape": "Nach Wein, Weingut oder Rebsorte suchen",
    "Filters": "Filter",
    "wines": "Weine",
    "More filters": "Weitere Filter",
    "Apply filters": "Filter anwenden",
    "Your selection is empty": "Ihre Auswahl ist leer",
    "Add your first wine or clear the active filters.": "Fügen Sie Ihren ersten Wein hinzu oder löschen Sie die aktiven Filter.",
    "Default Shelf": "Standardregal",
    "Default storage for wines": "Standardlager für Weine",
    "Cellar": "Keller",
    "(opens in new tab)": "(wird in einem neuen Tab geöffnet)",
    "Storage Name": "Lagername",
    "Enter the name of the storage.": "Geben Sie den Namen des Lagers ein.",
    "Enter the number of rows in the storage.": "Geben Sie die Anzahl der Reihen im Lager ein.",
    "Enter the number of columns in the storage.": "Geben Sie die Anzahl der Spalten im Lager ein.",
    "Finish Bottle": "Flasche leeren",
    'Are you sure you have finished the bottle "%(name)s" from "%(storage)s"? It will be marked as consumed in your history.': "Haben Sie die Flasche „%(name)s“ aus „%(storage)s“ geleert? Sie wird im Verlauf als konsumiert markiert.",
    "Open Bottle": "Flasche öffnen",
    "Description": "Beschreibung",
    "Contents": "Inhalt",
    "Wine": "Wein",
    "Drink by": "Trinken bis",
    "Edit": "Bearbeiten",
    "Remove": "Entfernen",
    "Delete Bottle": "Flasche löschen",
    "Bottle History": "Flaschenverlauf",
    "Back to Storages": "Zurück zu den Lagern",
    "Your Storages": "Ihre Lager",
    "History": "Verlauf",
    "No storages yet.": "Noch keine Lager vorhanden.",
    "Email Notifications": "E-Mail-Benachrichtigungen",
    "Settings": "Einstellungen",
    "Reminder to finish your opened wine(s)": "Erinnerung, geöffnete Weine zu leeren",
    "Name contains": "Name enthält",
    "Youngest First": "Jüngste zuerst",
    "Wine Type": "Weinart",
    "Source": "Quelle",
    "Sweetness": "Süße",
    "Enter the name of the region the wine is from.": "Geben Sie die Herkunftsregion des Weins ein.",
    "Enter the name of the appellation of the wine.": "Geben Sie die Appellation des Weins ein.",
    "Enter the barcode number of the wine as indicated on the label or scan using the button below.": "Geben Sie den Barcode vom Etikett ein oder scannen Sie ihn mit der Schaltfläche unten.",
    "Upload an image of the front label.": "Laden Sie ein Bild des vorderen Etiketts hoch.",
    "Upload an image of the back label.": "Laden Sie ein Bild des hinteren Etiketts hoch.",
    "Personal collection": "Persönliche Sammlung",
    "My wine cellar,": "Mein Weinkeller,",
    "curated": "gepflegt",
    "like a tasting notebook.": "wie ein Verkostungsbuch.",
    "Follow your bottles, vintages and favourites. A cellar to explore, not administer.": "Verfolgen Sie Ihre Flaschen, Jahrgänge und Favoriten. Ein Keller zum Entdecken, nicht zum Verwalten.",
    "Drink soon": "Bald trinken",
    "References": "Referenzen",
    "Bottles in stock": "Flaschen auf Lager",
    "Regions": "Regionen",
    "AI Upload": "KI-Upload",
    "Upload a photo of the bottle label and let AI fill in the details.": "Laden Sie ein Foto des Flaschenetiketts hoch und lassen Sie die KI die Details ausfüllen.",
    'To use AI-based wine creation a valid AI model and API key need to be configured. See <a href="https://the-broke-sommeliers.github.io/wine-cellar/setup/deployment/#ai-setup">the docs</a> for more information.': 'Für die KI-basierte Weinerfassung müssen ein gültiges KI-Modell und ein API-Schlüssel konfiguriert sein. Weitere Informationen finden Sie in der <a href="https://the-broke-sommeliers.github.io/wine-cellar/setup/deployment/#ai-setup">Dokumentation</a>.',
    "Delete Wine": "Wein löschen",
    "Create Wine": "Wein anlegen",
    "Stock": "Bestand",
    "No bottles in stock.": "Keine Flaschen auf Lager.",
    "Scan again": "Erneut scannen",
    "Main navigation": "Hauptnavigation",
    "Wine Cellar home": "Wine-Cellar-Startseite",
    "Toggle navigation": "Navigation ein- oder ausblenden",
    "My cellar": "Mein Keller",
    "Scan": "Scannen",
    "Add wine": "Wein hinzufügen",
    "Change language": "Sprache ändern",
    "Current language": "Aktuelle Sprache",
    "Account settings": "Kontoeinstellungen",
    "General Settings": "Allgemeine Einstellungen",
    "My rating": "Meine Bewertung",
    "Serving": "Serviertemperatur",
    "Tasting notes": "Verkostungsnotizen",
    "No tasting notes yet.": "Noch keine Verkostungsnotizen.",
    "Temperature": "Temperatur",
    "Not assigned": "Nicht zugewiesen",
    "Remove a bottle": "Flasche entfernen",
    "Add to stock": "Zum Bestand hinzufügen",
    "Full details": "Vollständige Details",
    "Close wine details": "Weindetails schließen",
    "Cell": "Fach",
    "ABV": "Alkoholgehalt",
}

FR_JS = {
    "Opening camera…": "Ouverture de la caméra…",
    "Camera access requires HTTPS on a phone. Open this page through a secure HTTPS address.": "L’accès à la caméra nécessite HTTPS sur un téléphone. Ouvrez cette page avec une adresse HTTPS sécurisée.",
    "No camera is available, or this browser does not support camera access.": "Aucune caméra n’est disponible ou ce navigateur ne permet pas d’y accéder.",
    "Camera access was denied. Allow camera access in your browser settings, then try again.": "L’accès à la caméra a été refusé. Autorisez-le dans les paramètres du navigateur, puis réessayez.",
    "No code found. Hold the bottle label steady inside the frame.": "Aucun code détecté. Maintenez l’étiquette de la bouteille immobile dans le cadre.",
    "Label detected. Keep still…": "Étiquette détectée. Ne bougez plus…",
    "Photo captured. Analysing the label…": "Photo prise. Analyse de l’étiquette…",
    "The automatic label analysis failed. You can try again or upload a photo manually.": "L’analyse automatique de l’étiquette a échoué. Vous pouvez réessayer ou importer une photo.",
    "Take photo": "Prendre la photo",
    "Try again": "Réessayer",
    "Upload a photo": "Importer une photo",
}

DE_JS = {
    "Opening camera…": "Kamera wird geöffnet…",
    "Camera access requires HTTPS on a phone. Open this page through a secure HTTPS address.": "Der Kamerazugriff erfordert HTTPS auf einem Smartphone. Öffnen Sie diese Seite über eine sichere HTTPS-Adresse.",
    "No camera is available, or this browser does not support camera access.": "Es ist keine Kamera verfügbar oder dieser Browser unterstützt den Kamerazugriff nicht.",
    "Camera access was denied. Allow camera access in your browser settings, then try again.": "Der Kamerazugriff wurde verweigert. Erlauben Sie ihn in den Browsereinstellungen und versuchen Sie es erneut.",
    "No code found. Hold the bottle label steady inside the frame.": "Kein Code erkannt. Halten Sie das Flaschenetikett ruhig im Rahmen.",
    "Label detected. Keep still…": "Etikett erkannt. Bitte stillhalten…",
    "Photo captured. Analysing the label…": "Foto aufgenommen. Etikett wird analysiert…",
    "The automatic label analysis failed. You can try again or upload a photo manually.": "Die automatische Etikettenanalyse ist fehlgeschlagen. Versuchen Sie es erneut oder laden Sie ein Foto hoch.",
    "Take photo": "Foto aufnehmen",
    "Try again": "Erneut versuchen",
    "Upload a photo": "Foto hochladen",
}

DE_PLURALS = {
    "Recorded Wine": ("Erfasster Wein", "Erfasste Weine"),
    "Wine in Stock": ("Wein auf Lager", "Weine auf Lager"),
    "Bottle in Stock": ("Flasche auf Lager", "Flaschen auf Lager"),
}


def apply(locale: str, translations: dict[str, str], domain: str = "django") -> None:
    path = ROOT / "locale" / locale / "LC_MESSAGES" / f"{domain}.po"
    catalog = polib.pofile(path)
    for entry in catalog:
        if entry.msgid in translations:
            entry.msgstr = translations[entry.msgid]
            entry.flags = [flag for flag in entry.flags if flag != "fuzzy"]
        if locale == "de_DE" and entry.msgid in DE_PLURALS:
            singular, plural = DE_PLURALS[entry.msgid]
            entry.msgstr_plural = {"0": singular, "1": plural}
            entry.flags = [flag for flag in entry.flags if flag != "fuzzy"]
        if entry.msgid.strip() == "%(counter)s wine · sorted by recent additions":
            if locale == "fr_FR":
                entry.msgstr_plural = {
                    "0": "%(counter)s vin · classé par ajout récent",
                    "1": "%(counter)s vin · classé par ajout récent",
                    "2": "%(counter)s vins · classés par ajouts récents",
                }
            else:
                entry.msgstr_plural = {
                    "0": "%(counter)s Wein · nach neuesten Einträgen sortiert",
                    "1": "%(counter)s Weine · nach neuesten Einträgen sortiert",
                }
            entry.flags = [flag for flag in entry.flags if flag != "fuzzy"]
    catalog.save(path)


def complete_english() -> None:
    for domain in ("django", "djangojs"):
        path = ROOT / "locale" / "en_GB" / "LC_MESSAGES" / f"{domain}.po"
        catalog = polib.pofile(path)
        for entry in catalog:
            if entry.obsolete:
                continue
            if entry.msgid_plural:
                entry.msgstr_plural = {"0": entry.msgid, "1": entry.msgid_plural}
            else:
                entry.msgstr = entry.msgid
            entry.flags = [flag for flag in entry.flags if flag != "fuzzy"]
        catalog.save(path)


if __name__ == "__main__":
    apply("fr_FR", FR)
    apply("de_DE", DE)
    apply("fr_FR", FR_JS, "djangojs")
    apply("de_DE", DE_JS, "djangojs")
    complete_english()
