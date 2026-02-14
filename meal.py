import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values()
def get_sheet():
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if not os.path.exists(service_account_file):
        return None  # Sheets devre dışı

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
spreadsheet_id = env_vars.get('GOOGLE_SHEETS_ID')

def insert_data(values):
    service = get_sheet()
    if service is None:
        print("Google Sheets disabled (credentials.json missing)")
        return {"error": "Sheets disabled"}
    range_ = "YEMEK!A2"
    request = service.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption="RAW",
        body={"values": [values]},
    )
    response = request.execute()
    print("Data appended.")
    return response

    

def get_link_from_meal_name(meal):
    url = f"https://www.nefisyemektarifleri.com/ara/?s={meal}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    div = soup.find("div", class_="recipe-cards")
    if div is None:
        print("DEBUG: recipe-cards not found. First 500 chars:", response.text[:500])
        return None
    a = div.find("a")
    if not a or not a.get("href"):
        print("Could not find recipe link. HTML may have changed.")
        return None
    return a["href"]

    

def get_recipe_info(yemek_linki):
    response = requests.get(yemek_linki)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        video_url = soup.find('meta', itemprop='contentUrl')['content']
    except TypeError:
        video_url = "null"
    
    img_div = soup.find("div", class_="recipe-single-img")
    img_tag = img_div.find("img") if img_div else None
    image_url = img_tag.get("src") if img_tag else "null"
    try:
        blockquote_text = soup.blockquote.get_text(strip=True)
    except AttributeError:
        blockquote_text = "null"
    recipe_div = soup.select_one('div.recipe-materials-div')
    if recipe_div:
        title = recipe_div.find('h2', class_='recipe-content-titles').text.strip()
        ingredients = [ingredient.text.strip() for ingredient in recipe_div.find_all('li', itemprop='recipeIngredient')]
    else:
        title, ingredients = "null", []
    return title, yemek_linki, image_url, video_url, "\n".join(ingredients), blockquote_text


def setup_google_sheets_api():
    env_vars = dotenv_values()
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials), env_vars.get('GOOGLE_SHEETS_ID')


def get_data(service, spreadsheet_id, range_):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_).execute()
    return result.get('values', [])


def print_data(values):
    if not values:
        print('No data found.')
    else:
        for row in values:
            print(' || '.join(row))