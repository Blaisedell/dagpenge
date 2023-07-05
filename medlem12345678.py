import json

### Dictionaries for use in "Udbetalinger.json"
Medlem = {
    "Navn": "Palle Jensen",
    "Adresse": "Byvej 25",
    "Postnummer": "6000",
    "By": "Kolding"
}
Arbejdsgiver = {
    "Navn": "Specialisterne",
    "Adresse": "Lautruphøj 1",
    "Postnummer": "2750",
    "By": "Ballerup",
    "CVR-nummer": "27351034"
}
Akasse = {
    "Navn": "Magistrenes Akasse",
    "Adresse": "Peter Bangs Vej 30",
    "Postnummer": "2000",
    "By": "Frederiksberg"
}
Header = {
    "Ydelse": "Dagpenge",
    "Medlemsnummer": "12345678",
    "Personnummer": "2501852117",
    "Udskrivningsdato": ""
}
Dagpengespecifikationer = {
    "Periode": {
      "Startdato": "",
      "Slutdato": ""
    },
    "Timer": None,
    "Timesats": None,
    "Dagpengebeløb": None,
    "Atp": None,
    "Brutto udbetaling": None,
    "Skat": None,
    "Netto udbetaling": None
}
Footer = {
    "Indsat på konto": "Nem konto",
    "Dispositionsdato": "",
    "Til udbetaling": None
}