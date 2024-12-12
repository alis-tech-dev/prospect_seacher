import re
from os import getenv

from dotenv import load_dotenv

load_dotenv()


LOCATIONS = [
    "Berlin",
    "München",
    "Munich",
    "Hamburg",
    "Frankfurt am Main",
    "Stuttgart",
    "Düsseldorf",
    "Köln",
    "Cologne",
    "Dresden",
    "Hannover",
    "Leipzig",
    "Bremen",
    "Nürnberg",
    "Nuremberg,"
    "Dortmund",
    "Essen",
    "Duisburg",
    "Bochum",
    "Wuppertal",
    "Bonn",
    "Mannheim",
    "Karlsruhe",
    "Augsburg",
    "Wiesbaden",
    "Gelsenkirchen",
    "Münster",
    "Mainz",
    "Rostock",
    "Kassel",
    "Freiburg",
    "Braunschweig",
    "Magdeburg",
    "Kiel",
    "Chemnitz",
    "Aachen",
    "Halle",
    "Lübeck",
    "Erfurt",
    "Oberhausen",
    "Oldenburg",
    "Potsdam",
    "Saarbrücken",
    "Regensburg",
    "Ingolstadt",
    "Würzburg",
    "Wolfsburg",
    "Heidelberg",
    "Baden-Württemberg",
    "Bayern",
    "Hessen",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Saarland",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thüringen",
    "Bavaria",
    "Hesse",
    "Lower Saxony",
    "North Rhine-Westphalia",
    "Rhineland-Palatinate",
    "Saxony",
    "Saxony-Anhalt",
    "Thuringia"
]

POSITIONS = [
    "Fachkraft für Arbeitssicherheit",
    "Logistikmanager",
    "Wartung",
    "HSE",
    "SHE",
    "QHSE",
    "Logistikmanager",
    "Wartungsmanager",
    "Facility Manager",
    "Arbeitsschutz",
    "Sicherheitsingenieurwesen",
    "Sicherheitsingenieur",
    "Sicherheitsspezialist",
    "Industrieller Sicherheitsspezialist",
    "EHS Manager",
    "Umweltschutzspezialist",
    "Senior Sicherheitsinspektor",
    "Koordinator für Arbeitsplatzsicherheit",
    "Berater für Arbeitsgesundheit",
    "Sicherheitskontrolleur",
    "Spezialist für Risikomanagement",
    "Sicherheitsberater",
    "Sicherheitsaufsicht",
    "Risikoingenieur",
    "Schutzspezialist",
    "Experte für Risikobewertung",
    "Sicherheitssystem-Betreiber",
    "Arbeitsschutz-Kontrolleur",
    "Spezialist für Notfallreaktionen",
    "Ingenieur für Arbeits- und Gesundheitsschutz",
    "Spezialist für Gerätesicherheit",
    "Facility Sicherheitsmanager",
    "Sicherheitsspezialist",
    "EHS",
    "Sicherheit",
    "Gesundheit und Sicherheit",
    "logistic manager",
    "maintenance manager",
    "facility manager",
    "Occupational Safety",
    "Safety Engineering",
    "Safety Engineer",
    "Safety Specialist",
    "Industrial Safety Specialist",
    "EHS Manager",
    "Environmental Safety Specialist",
    "Senior Safety Inspector",
    "Workplace Safety Coordinator",
    "Occupational Health Advisor",
    "Safety Controller",
    "Risk Management Specialist",
    "Safety Consultant",
    "Safety Supervisor",
    "Risk Engineer",
    "Protection Specialist",
    "Risk Assessment Expert",
    "Safety System Operator",
    "Labor Protection Controller",
    "Emergency Response Specialist",
    "Occupational Health and Safety Engineer",
    "Equipment Safety Specialist",
    "Facilities Safety Manager",
    "Security Specialist",
    "EHS",
    "safety",
    "health and safety",
]

# POSITIONS = ["EHS"]
# LOCATIONS = ["Spain"]


CONTACTS = []
HUNTER_API_KEY = getenv("HUNTER_API_KEY")
PAD_NAME_API_KEY = getenv("PAD_NAME_API_KEY")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
ESPO_API_KEY = getenv("ESPO_API_KEY")
CSE_ID = getenv("CSE_ID")

EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")
SENDER_EMAIL = "top.win.casino777@gmail.com"

CREDENTIALS_FILE ="credentials.json"
TOKEN_FILE = 'token.json'

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

URL = "https://www.googleapis.com/customsearch/v1"
ESPO_URL = "https://www.crm.alis-is.com"
ALEDO_URL = "https://www.aledo-de.alis-is.com"
PAD_URL = f"https://www.sklonovani-jmen.cz/api?klic={PAD_NAME_API_KEY}&"

PADY = {
    "nominative": 1,  # називний, nominativ
    "genitive": 2,    # родовий, genitiv
    "dative": 3,      # давальний, dativ
    "accusative": 4,  # знахідний, akuzativ
    "vocative": 5,    # кличний, vokativ
    "local fall": 6,  # місцевий, místní pád
    "ablative": 7,   # орудний, ablativ
    "gender": 0
}

FORBIDDEN_DOMAINS = [
    ".gov",
    "gov.",
    "linkedin",
    "facebook",
    "microsoft",
    "wikipedia",
    "tiktok",
    "reddit",
    "google",
    "youtube",
    ".edu"

]

VALID_ADDRESS_REGEXP = re.compile(
    r"""
    ^(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+
    (?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*
    |"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]
    |\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")
    @
    (?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+
    [a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?
    |\[
    (?:
    (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
    (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?
    |[a-zA-Z0-9-]*[a-zA-Z0-9]:
    (?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]
    |\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)
    \])$
    """, re.VERBOSE
)


email_patterns = [
    "{first}.{last}",
    "{last}.{first}",
    "{first_initial}.{last}",
    "{first_initial}_{last}",
    "{first_initial}-{last}",
    "{first_initial}{last}",
    "{first}_{last}",
    "{first}-{last}",
    "{first}{last}",
    "{last}_{first}",
    "{last}-{first}",
    "{last}{first}",
    "{last}",
    "{last}.{first_initial}",
    "{last}_{first_initial}",
    "{last}-{first_initial}",
    "{first}{last_initial}",
    "{last_initial}{first}",
    "{first_initial}.{middle_initial}.{last}",
    "{first_initial}-{middle_initial}-{last}",
    "{first_initial}_{middle_initial}_{last}",
    "{last}.{first_initial}123"
]

emails_with_middle = [
    "{middle}{first}",
    "{middle}.{first}",
    "{middle}_{first}",
    "{middle}{last}",
    "{middle}_{last}",
    "{middle}.{last}",
    "{first}.{middle}",
    "{first}_{middle}",
    "{first}.{middle}",
    "{first}_{middle}",
    "{first}{middle}",
    "{first}.{middle}.{last}",
    "{first}.{middle}_{last}",
    "{first}.{middle}-{last}",
    "{middle}",
    "{first}.{last_initial}{middle}",
    "{first}.{middle_initial}.{last}",
    "{last}-{middle}.{first}",
    "{first}.{middle_initial}.{last}",
    "{first}{middle_initial}{last}",
    "{middle_initial}.{last}.{first}"
]

emails = [
    "info",
    "support",
    "contact",
    "contacts",
    "business",
    "purchase",
    "help",
    "hello",
    "sales"
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/114.0.1823.67 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_8) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.79 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; MiTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (Linux; Tizen 6.0; SAMSUNG SM-T835) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.0 Chrome/87.0.4280.101 Mobile Safari/537.36",
    "Mozilla/5.0 (PlayStation 5; PlayStation 4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/537.36",
    "Mozilla/5.0 (Xbox; U; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
]

senders = [
    "marcel.jongejan@heffiq.nl",
    "manager@petrostax.com",
    "cvasquez@kaycol.com",
    "ohaddar@tesla.com",
    "david.14.wilson@morrisonsplc.co.uk",
    "jelena.borovica@volga.rs",
    "regis.charles@magna.com",
    "Ion.Bugarin@swissport.com",
    "christosbharat@gmail.com",
    "andreas.benkoe@forvia.com",
    "Daniel@collinsadelaide.com",
    "gerryweston@dtengineering.org.uk",
    "stephen.jessup@linamar.com",
    "John.Shiring@magna.com",
    "timo.muddemann@rhenus.com",
    "markus.tischler@rosenberger.com",
    "jessica.yaeger@monti-inc.com",
    "luka.topic@dzida.ba",
    "markus.klie@mubea.com",
    "pg@scanlox.com",
    "artur.wandl@zf.com",
    "fabian.theymann@qvc.com",
    "stefan.piechowiak@ornua.com",
    "jeremy.thiebaut.ext@valeo.com",
    "rahul_sonar@rediffmail.com",
    "supply@lmpe-procurement.com",
    "jafar.attar@konecranes.com",
    "philipp.leyrer@linde-mh.at",
    "serhii.bondar@flex.com",
    "iandres@segurilight.com",
    "jarocha@sonaearauco.com",
    "markus.eberharter@innio.com",
    "kha@kfa.co.za",
    "e.pfeffer@techsign.fr",
    "e.pfeffer@techsign.fr",
    "mehmetali.ekingen@anamine.co.ao",
    "hareth.n@platin-jo.com",
    "hareth.n@platin-jo.com",
    "trasupmarocco@gmail.com",
    "annely.mengel@ericsson.com",
    "barbora@avaltar.com"
]

