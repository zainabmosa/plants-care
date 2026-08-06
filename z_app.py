import pandas as pd
import streamlit as st
from helper import *


st.set_page_config(page_title="Plant Care Tracker", page_icon="🌿", layout="wide")
st.sidebar.title("🌿 Plant Care Tracker")
today = pd.Timestamp.today().date()

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] h1 {
        font-size: 26px !important;
    }
    section[data-testid="stSidebar"] label {
        font-size: 18px !important;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] p {
        font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,)

def go_to_add_plant():
    st.session_state["menu"] = "🌱 Add Plant"

def go_to_care_plant():
    st.session_state["menu"] = "🍃 Record Care"
    
def go_to_growth_plant():
    st.session_state["menu"] = "🎋 Track Growth"
    
def go_home():
    st.session_state["menu"] = "🏡 Home Page"
    
c = st.sidebar.radio(
    "Choose options ❣️",
    [
        "🏡 Home Page",
        "🌱 Add Plant",
        "🔍 Search Plants",
        "🍃 Record Care",
        "🎋 Track Growth",
        "🕧 View Due Plants",
        "🩺 AI Plant Doctor",
        "🌦️ Seasonal Care"
    ],
    key="menu"
)



if c =="🏡 Home Page":
    df = read()
    
            
    all_tab , care_tab, growth_tab = st.tabs(["🌿 All Plants","🪴 Care History", "🌿 Growth History"])  
    # all plants
    with all_tab:
        st.subheader("🌿 All Plants")

        if df.empty:
            st.warning("No plants added yet 🌱")
        else:
            st.dataframe(df, use_container_width=True)
            st.subheader("🌱 Plant Image")

            plant = st.selectbox("Choose plant", df["Name"])
            photo = df.loc[df["Name"] == plant, "Photo"].iloc[0]

            if pd.isna(photo) or str(photo).strip() == "":
                st.info("No image available for this plant.")
            else:
                st.image(photo)
        st.button("🌱 Add Plant",on_click=go_to_add_plant)

        
    # Care History Tab
    with care_tab:
        st.subheader("🪴 Care History")

        history = pd.read_csv(CARE_FILE)

        if history.empty:
            st.info("No care activities have been recorded yet.")
        else:
            st.dataframe(history, use_container_width=True)
        st.button("🍃 Record Care",on_click=go_to_care_plant)


    # Growth History Tab
    with growth_tab:
        st.subheader("🌿 Growth History")

        growth_df = pd.read_csv(GROWTH_FILE)

        if growth_df.empty:
            st.info("No growth measurements have been recorded yet.")
        else:
            st.dataframe(growth_df, use_container_width=True)
        st.button("🎋 Track Growth",on_click=go_to_growth_plant)
        


# Add plant manually
if c == "🌱 Add Plant":
    
    col, col3 = st.columns([18, 1])

    with col:
        st.title("🌱 Add Plant")

    with col3:
        st.button("🏠", on_click=go_home, key="home")

    col1, col2 = st.tabs(['✍️ Add Manually' , '🔎 Search Plant API'])
    with col1:
        
        name = st.text_input("Plant name")
        photo = st.text_input("Photo URL or photo path")
        location = st.text_input("Location in home")
        date = st.date_input("Date acquired", max_value = today)
        water = st.number_input("Watering frequency in days", min_value=1)
        Fertilizing = st.number_input("Fertilizing frequency in days", value=14)
        Repotting = st.number_input("Repotting frequency in days", value=365)
        Pruning = st.number_input("Pruning frequency in days", value=30)
        sunlight = st.selectbox("Sunlight needs", ["Low", "Medium", "High"])

        if st.button("Save Plant"):
            df = read()
            clean_name = name.strip()
            clean_location = location.strip()

            if clean_name == "":
                st.error("⚠️ Plant name can't be empty.")
            elif not df.empty and clean_name.lower() in df["Name"].fillna("").str.lower().values:
                st.error("⚠️ Plant already exists.")
            elif clean_location == "":
                st.error("⚠️ Location can't be empty.")
            else:
                add_plant_data(name, location, date, water, sunlight, photo,Fertilizing,Repotting,Pruning)
                st.success("Plant added successfully 🍀")
    with col2:
        st.write("Search for real plant information ""from the Perenual API.")

        query = st.text_input("Enter a plant name",placeholder="Example: Monstera")

        if st.button("Search API"):

            try:
                results = search_plant_api(query)

                st.session_state["plant_api_results"]= results

                if not results:
                    st.warning("No matching plants were found.")

                else:
                    st.success(f"Found {len(results)} plant(s).")
    
            except (ValueError, RuntimeError) as error:
                st.error(str(error))

        results = st.session_state.get("plant_api_results",[])

        if results:

            option_labels = [(f"{plant['common_name']} — "f"{plant['scientific_name']}")for plant in results]

            selected_label = st.selectbox("Choose a result",option_labels)

            selected_index = option_labels.index(selected_label)

            basic_selected = results[selected_index]

            try:
                selected = get_plant_details(basic_selected["id"])

            except RuntimeError as error:

                st.warning("Full plant details could not ""be loaded. Showing the available ""search information.")

                selected = basic_selected

            st.subheader("Plant Information")

            col1, col2 = st.columns([1, 2])

            with col1:

                if selected["image"]:

                    st.image(selected["image"],use_container_width=True)

                else:
                    st.info("No image is available.")
                
            with col2:
            
                watering_days, fertilizing_days, pruning_days, repotting_days = care_schedule(selected["watering"])            
                sunlight_level = sunlight_to_level(selected["sunlight"])
                plant_name = selected["common_name"].strip()


                st.write(f"**Common name:** {selected['common_name']}")
                st.write(f"**Scientific name:** {selected['scientific_name']}")
                st.write(f"**Watering:** Every {watering_days} days")
                st.write(f"**Fertilizing:** Every {fertilizing_days} days")
                st.write(f"**Repotting:** Every {repotting_days} days")
                st.write(f"**Pruning:** Every {pruning_days} days")
                st.write(f"**Sunlight:** {sunlight_level}")
         

            st.subheader("Add this plant to my tracker")
            
            plant_name = st.text_input("Plant name",value=selected["common_name"],key="api_name")
            location = st.text_input( "Location in home",key="api_location")

            acquired_date = st.date_input("Date acquired",max_value=today,key="api_date")
    
            suggested_water_days = watering_to_days(selected["watering"])

            suggested_sunlight = sunlight_to_level(selected["sunlight"])

            water = st.number_input("Watering frequency in days",min_value=1,value=watering_days,key="api_water")
        
            fertilizing = st.number_input("Fertilizing frequency in days",min_value=1,value=fertilizing_days,key="api_fertilizing")

            repotting = st.number_input("Repotting frequency in days",min_value=1,value=repotting_days,key="api_repotting")
    
            pruning = st.number_input("Pruning frequency in days",min_value=1,value=pruning_days,key="api_pruning")

        
            st.caption("All activity values is suggested ""from the API and can be changed.")

       
            sunlight_options = ["Low", "Medium", "High"]

            sunlight = st.selectbox("Sunlight needs",sunlight_options,index=sunlight_options.index(sunlight_level),key="api_sunlight")

            st.subheader("Care Schedule Summary")

            st.write(f"💧 **Watering:** Every {water} days")

            st.write(f"🌱 **Fertilizing:** "f"Every {fertilizing} days")

            st.write(f"🪴 **Repotting:** "f"Every {repotting} days")

            st.write(f"✂️ **Pruning:** "f"Every {pruning} days")

            st.write(f"☀️ **Sunlight:** {sunlight}")

            if st.button("Add API Plant"):

                df = read()
    
                plant_name = selected["common_name"].strip()

                if location.strip() == "":

                    st.error("⚠️ Location can't be empty.")

                elif (not df.empty and plant_name.lower()in df["Name"].fillna("").str.lower().values):

                    st.error("⚠️ Plant already exists.")

                else:

                    add_plant_data(plant_name,location.strip(),acquired_date,water,sunlight,selected["image"],fertilizing,repotting,pruning)

                    st.success("Plant imported from the ""API successfully 🌿")
                
#  Record care
if c == "🍃 Record Care":
    col, col3 = st.columns([18, 1])

    with col:
        st.title("🍃 Record Care")

    with col3:
        st.button("🏠", on_click=go_home, key="home")

    df = read()
    today = pd.Timestamp.today().normalize().date()

    if df.empty:
        st.warning("No plants added yet 🌱")
    else:
        plant = st.selectbox("Choose a plant", df["Name"])
        activity = st.selectbox("Choose activity",["Watering", "Fertilizing", "Repotting", "Pruning"],)
        care_date = st.date_input("Date", max_value=today)

        if st.button("Save Care"):
            record_care(plant, activity, care_date)
            st.success("Care activity saved!")


#  View due plants
if c == "🕧 View Due Plants":
    
    col, col3 = st.columns([18, 1])

    with col:
        st.title("🕧 View Due Plants")

    with col3:
        st.button("🏠", on_click=go_home, key="home")
    due = get_due_plants()

    if read().empty:
        st.warning("No plants added yet 🌱")
    elif due.empty:
        st.success("🌼 Everything looks great! No plant care is needed today.")    
    else:
        st.dataframe(due, use_container_width=True)

        st.subheader("Today's Care Tasks 🌿")

        for _, row in due.iterrows():
            st.write(f"🌱 **{row['Plant']}** needs **{row['Activity']}**")


# Search saved plants
if c == "🔍 Search Plants":
    col, col3 = st.columns([18, 1])

    with col:
        st.title("🔍 Search Plants")

    with col3:
        st.button("🏠", on_click=go_home, key="home")    
    term = st.text_input("Enter plant name or location")

    if st.button("Search"):
        result = search_plants(term)

        if result.empty:
            st.warning("No plants found")
        else:
            st.dataframe(result, use_container_width=True)


#  Track growth
if c == "🎋 Track Growth":

    col, col3 = st.columns([18, 1])

    with col:
        st.title("🎋 Track Growth")

    with col3:
        st.button("🏠", on_click=go_home, key="home")    

    df = read()
    today = pd.Timestamp.today().normalize().date()

    if df.empty:
        st.warning("No plants added yet 🌱")
    else:
        plant = st.selectbox("Choose plant", df["Name"])
        height = st.number_input("Plant height (cm)", min_value=0.0)
        growth_date = st.date_input("Date", max_value=today)

        if st.button("Save Growth"):
            add_growth(plant, height, growth_date)
            st.success("Growth saved!")





#  AI Plant Doctor using OpenRouter LLM API
if c == "🩺 AI Plant Doctor":

    col, col3 = st.columns([18, 1])

    with col:
        st.title("🩺 AI Plant Doctor")

    with col3:
        st.button("🏠", on_click=go_home, key="home")    
    st.write("Choose a saved plant and describe the symptoms in your own words.")

    df = read()

    if df.empty:
        st.warning("Add a plant before using the AI Plant Doctor.")
    else:
        plant = st.selectbox("Choose plant", df["Name"])
        symptoms = st.text_area("Describe the symptoms",placeholder="Example: The leaves are yellow, soft, and falling after watering.",)

        if st.button("Ask AI Plant Doctor"):
            selected = df[df["Name"] == plant].iloc[0].to_dict()
            history = pd.read_csv(CARE_FILE)
            plant_history = history[history["Name"] == plant].tail(10)

            if plant_history.empty:
                history_text = "No care history is available."
            else:
                history_text = plant_history.to_string(index=False)

            try:
                with st.spinner("The AI Plant Doctor is preparing the report..."):
                    report = ai_plant_doctor(plant,symptoms,selected,history_text,)
                st.markdown(report)
                st.caption("This AI response is general plant-care guidance and may not identify the exact problem.")
            except (ValueError, RuntimeError) as error:
                st.error(str(error))
        

# Seasonal Care Page
if c == "🌦️ Seasonal Care":

    col1, col2 = st.columns([18, 1])

    with col1:
        st.title("🌦️ Seasonal Care")

    with col2:
        st.button("🏠",on_click=go_home,key="seasonal_home")

    adjust_tab, reminder_tab = st.tabs(["🔨 Adjust Care Schedule","🍁 Seasonal Reminder"])

    # Adjust Care Schedule
    with adjust_tab:

        df = read()

        if df.empty:
            st.warning("No plants added yet 🌱")

        else:
            plant = st.selectbox("Choose Plant",df["Name"],key="adjust_plant")

            selected = df[df["Name"] == plant]

            water = int(selected["Water"].iloc[0])

            season, new_water = adjust_schedule(water)

            st.info(f"🌱 Recommendation for {plant} "f"in {season}: water every "f"{new_water} days 💧")

    # Seasonal Reminder
    with reminder_tab:

        st.write("Get general plant-care advice ""based on the current season.")

        if st.button("Show Advice",key="show_seasonal_advice"):
            st.info(seasonal_reminder())        
