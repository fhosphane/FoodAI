import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import dotenv_values
import sys
# Load environment variables
env_vars = dotenv_values()

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
spreadsheet_id = env_vars.get('GOOGLE_SHEETS_ID')

def insert_data(values):
    range_ = 'YEMEK!A2'
    request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption='RAW',
        body={'values': [values]}
    )
    response = request.execute()
    print('Data appended.')

def get_link_from_meal_name(meal):
    response = requests.get(f"https://www.nefisyemektarifleri.com/ara/?s={meal}")
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find("div", class_="recipe-cards")
    return div.find("a")["href"]

def get_recipe_info(yemek_linki):
    response = requests.get(yemek_linki)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        video_url = soup.find('meta', itemprop='contentUrl')['content']
    except TypeError:
        video_url = "null"
    
    img_tag = soup.find('div', class_='recipe-single-img').find('img')
    image_url = img_tag['src'] if img_tag else "null"
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

def main():
    meal_name = sys.argv[1]
    meal_link = get_link_from_meal_name(meal_name)
    if meal_link:
        title, link, image_url, video_url, ingredients, blockquote_text = get_recipe_info(meal_link)
        insert_data([title, link, image_url, video_url, ingredients, blockquote_text])
    else:
        print("Meal not found.")

if __name__ == "__main__":
    main()

