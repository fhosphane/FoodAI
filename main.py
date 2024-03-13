from fastapi import FastAPI
import meal
app = FastAPI()

@app.get("/getAll")
def get_all_meal():
    service, spreadsheet_id = meal.setup_google_sheets_api()
    range_ = 'YEMEK!A1:F5000'
    values = meal.get_data(service, spreadsheet_id, range_)
    meal.print_data(values)
    return {"data": values}

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

@app.get("/add/{meal_name}")
def add_meal(meal_name):

    meal_link = meal.get_link_from_meal_name(meal_name)
    if meal_link:
        title, link, image_url, video_url, ingredients, blockquote_text = meal.get_recipe_info(meal_link)
        title = title.replace(" İçin Malzemeler","").replace("Tarifi","").replace("Nasıl Yapılır?","").strip()
        meal.insert_data([title, link, image_url, video_url, ingredients, blockquote_text])
        return {meal_name: [title,link,image_url,video_url,ingredients,blockquote_text]}
    else:
        print("Meal not found.")
        return {meal_name: "null"}
