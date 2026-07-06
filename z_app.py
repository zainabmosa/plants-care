import streamlit as st
from helper import *


st.sidebar.title("🌿Plant Care Tracker")

st.markdown("""
<style>
section[data-testid="stSidebar"] h1 {
    font-size: 26px !important;
}
</style>
""", unsafe_allow_html=True)

c = st.sidebar.radio('Choose options❣️',[
    "🌱 Add Plant",
    "🍃 Record Care",
    "🕧 View Due Plants",
    "🔍 Search Plants",
    "📋 View All Plants",
    "🎋 Track Growth",
    "🌿 Growth History",
    "🍁 Seasonal Reminder",
    "💉 Diagnose Plant",
    "🔨 Adjust Care Schedule"])


st.markdown("""
<style>
section[data-testid="stSidebar"] label {
    font-size: 18px !important;
    font-weight: bold;
}

section[data-testid="stSidebar"] p {
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)


# 1 : add plant
if c=="🌱 Add Plant": 

    st.title("🌱 Add Plant")
    
    name = st.text_input("Plant name")
    photo = st.text_input("Photo path")
    location = st.text_input("Location in home")
    date = st.date_input("Date acquired")
    water = st.number_input("Water frequency in days", min_value=1)
    sunlight = st.selectbox("Sunlight needs", ["Low", "Medium", "High"])
    
    if st.button("Save Plant"):
        
        df = read()
        
        name = name.strip()
        location = location.strip()
        
        if name == "":
            st.error("⚠️ Plant name can't be empty.")
            
        elif name.lower() in df["name"].str.lower().values:
            st.error("⚠️ Plant already exists.")
            
        elif location == "":
            st.error("⚠️ Location can't be empty.")  
            
        else:
            add_plant_data(name, location, date, water, sunlight, photo)
            st.success("Plant added successfully 🍀.")
            


# 2 : record care
if c=="🍃 Record Care":   
    
    st.title("🍃 Record Care")
    
    df = read()
    
    plant = st.selectbox("Choose a plant", df["name"])
    activity = st.selectbox("Choose activity",["Watering", "Fertilizing", "Repotting", "Pruning"])
    care_date=st.st.date_input("Date")
    
    if st.button("Save Care"):
        record_care(plant, activity,care_date)
        st.success("Care activity saved!")  



# 3 : View Due Plants
if c=="🕧 View Due Plants":
    
    st.subheader("🕧 View Due Plants")
    
    due = get_due_plants()

    if due.empty:
        st.success("All plants watered today 🌱")
    else:
        st.dataframe(due)



# 4 : search_plants 
if c=="🔍 Search Plants":
    
    st.subheader("🔍 Search Plants")
    t = st.text_input("Enter plant name or location")
    
    if st.button("Search"):
        re = search_plants(t)
        if re.empty:
            st.warning("No plants found")
        else:
            st.dataframe(re)



# 5 : View All Plants
if c=="📋 View All Plants": 
    
    df = read()
    st.subheader("🌿 All Plants")
    
    if df.empty:
        st.warning("No plants added yet 🌱")
        
    else:
        st.dataframe(df)
        st.subheader("🌱 Plant Image")

        df = read()
        
        plant = st.selectbox("Choose plant", df["name"])
        photo = df.loc[df["name"] == plant, "photo"].iloc[0]
        
    if pd.isna(photo) or photo == "":
            st.info("No image available for this plant.")
    else:
            st.image(photo)
    


# 6 : Track growth    
if c=="🎋 Track Growth":
    
    st.subheader("🎋 Track Growth")
    
    df = read()
    
    plant = st.selectbox("Choose plant", df["name"])
    height = st.number_input("Plant height (cm)", min_value=0.0)
    growth_date = st.date_input("Date")
    
    if st.button("Save Growth"):
        add_growth(plant, height, growth_date)
        st.success("Growth saved!")
        
if c=="🌿 Growth History":
    
    st.subheader("🌿 Growth History")

    growth_df = pd.read_csv("growth.csv")
    st.dataframe(growth_df)


# 7: Seasonal Reminder   
if c == "🍁 Seasonal Reminder":

    st.subheader("🍁 Seasonal Reminder")

    if st.button("Show Advice"):
        msg = seasonal_reminder()
        st.info(msg)

        

# 8 : diagnose
if c=="💉 Diagnose Plant":
    
    st.subheader("💉 Diagnose Plant")
    
    symptom = st.selectbox("Select symptom",["Yellow Leaves", "Dry Leaves", "Brown Tips"])
    
    if st.button("Diagnose"):
        st.success(diagnose(symptom))    



# 9 :  adjust_schedule 
if c== "🔨 Adjust Care Schedule":
    
    st.subheader( "🔨 Adjust Care Schedule")
    
    df = read()
    
    if df.empty:
        st.warning("No plants added yet 🌱")
        
    else:
        plant = st.selectbox("Choose Plant", df["name"])
        selected = df[df["name"] == plant]
        water = int(selected["water"].iloc[0])
        
        season,new_water = adjust_schedule(water)
        
        st.info(f"""🌱 Recommendation for {plant} In this season: {season} 💧 Water every {new_water} days """)
