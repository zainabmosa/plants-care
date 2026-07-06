import pandas as pd
from datetime import datetime , date


def read():
    return pd.read_csv("plants.csv")



# 1 : add plant
def add_plant_data(name, location, date, water, sunlight, photo ): # 1
    
    df=read()
    
    new = pd.DataFrame([{
        "name": name,
        "location": location,
        "date": date,
        "water": water,
        "sunlight": sunlight,
        "last_watered": date ,
        "photo": photo }])
    
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv("plants.csv", index=False)



# 2 : record care
def record_care(name, activity):
    
    new = pd.DataFrame([{
        "name": name,
        "activity": activity,
        "date": date.today()}])

    df = pd.read_csv("care_history.csv")
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv("care_history.csv", index=False)



# 3 : View Due Plants
def get_due_plants():

    plants = read()
    history = pd.read_csv("care_history.csv")

    last = history[history["activity"] == "Watering"] \
    .groupby("name")["date"].max()
    
    df = plants.merge(last, on="name", how="left")

    df["last_date"] = pd.to_datetime(df["date_y"])

    df["days"] = (pd.Timestamp.today() - df["last_date"]).dt.days

    due = df[df["days"] >= df["water"]]

    return due



# 4 : search_plants 
def search_plants(t):
    
    df = read()
    
    re = df[(df["name"].str.contains(t,case=False)) | (df["location"].str.contains(t, case=False))]
    
    return re



# 6 : add growth
def add_growth(name, height):
    new = pd.DataFrame([{"name"  : name, "height": height, "date" : date.today() }])
 
    df = pd.read_csv("growth.csv")
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv("growth.csv", index=False)



# 7: Seasonal Reminder 
def seasonal_reminder():

    month = datetime.now().month
    if month in [12, 1, 2]:
        return "Winter ❄️ : Reduce watering" 
        
    elif month in [6, 7, 8]:
        return "Summer ☀️ : Increase watering"
        
    else:
        return "Normal 🌿"    


# 8 : diagnose
def diagnose(symptom):

    if symptom == "Yellow Leaves":
        return "Overwatering 💧"

    elif symptom == "Dry Leaves":
        return "Needs more water 💧"

    elif symptom == "Brown Tips":
        return "Needs more sunlight ☀️"

        

# 9 :  adjust_schedule      
def adjust_schedule(water):
    
    month = datetime.now().month
    
    if month in [12, 1, 2]:     
        season = "Winter"
        new_water = water + 1
        
    elif month in [3, 4, 5]:     
        season = "Spring"
        new_water = water
        
    elif month in [6, 7, 8]:     
        season = "Summer"
        new_water = max(1, water - 1)
        
    else:                        
        season = "Autumn"
        new_water = water
        
    return season, new_water
