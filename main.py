from fastapi import FastAPI,HTTPException
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import meal
from gemini_client import suggest_recipe
app = FastAPI() 
class SuggestIn(BaseModel):
    ingredients: list[str]
@app.post("/suggest")
def suggest(body: SuggestIn):
    try:
        return suggest_recipe(body.ingredients)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class MealResponse(BaseModel):
    ok: bool
    meal: str
    source: str
cache = {}

@app.get("/getAll")
def get_all_meal():
    try:
        service, spreadsheet_id = meal.setup_google_sheets_api()
        range_ = "YEMEK!A1:F5000"
        values = meal.get_data(service, spreadsheet_id, range_)
        return {"data": values}
    except Exception:
        return {"error": "Google Sheets not configured"}

@app.get("/get/{meal_name}")
def get_meal(meal_name):
    service, spreadsheet_id = meal.setup_google_sheets_api()
    range_ = 'YEMEK!A1:F5000'
    values = meal.get_data(service, spreadsheet_id, range_)

    value = ""
    for i in values:
        if meal_name.lower() in i[0].lower():
            value = i
            break
    if not value:
        return add_meal(meal_name)

    return {meal_name: value}

@app.get("/add/{meal_name}", response_model=MealResponse)
def add_meal(meal_name: str):
    if meal_name in cache:
        return cache[meal_name]
    try:
        meal_link = meal.get_link_from_meal_name(meal_name)
        if not meal_link:
            raise HTTPException(status_code=404, detail="Meal not found or source page changed.")
        title, link, image_url, video_url, ingredients, blockquote_text = meal.get_recipe_info(meal_link)
        title = meal_name.capitalize()
        meal.insert_data([title, link, image_url, video_url, ingredients, blockquote_text])
        result = {"ok": True, "meal": meal_name, "source": meal_link}
        cache[meal_name] = result
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {e}")
