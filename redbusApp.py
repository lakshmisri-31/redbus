import streamlit as st
import pandas as pd
import mysql.connector

# Function to connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="redbus_project"
    )

# Function to fetch data from the database
def fetch_data_from_db():
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bus_routes")  # Make sure 'state' column is included
    data = cursor.fetchall()
    connection.close()
    return pd.DataFrame(data)

# Function to map bustypes to AC Sleeper and Non-AC Sleeper
def map_bustype(bustype):
    if any(keyword in bustype.lower() for keyword in ["a/c", "ac", "volvo", "benz", "mercedes", "scania"]):
        return "AC Sleeper"
    else:
        return "Non-AC Sleeper"

# Function to map cities to states
def get_state_cities_mapping():
    return {
        "Telangana": ["Hyderabad"],
        "Andhra Pradesh": [
            "Vijayawada", "Kakinada", "Vishakhapatnam", "Chittoor", "Tirupati", "Kadapa", "Ongale", "Anantapur"
        ],
        "Tamil Nadu": ["Chennai"]
    }

# Streamlit App
st.title("RedBus Data Explorer")

# Fetch data
data = fetch_data_from_db()

if not data.empty:
    # Apply mapping to bustype
    data['bustype'] = data['bustype'].apply(map_bustype)

    st.sidebar.title("Filters")
    
    # State Filter with Alert Logic
    state_cities_mapping = get_state_cities_mapping()
    states = list(state_cities_mapping.keys())
    selected_state = st.sidebar.selectbox("Select State", ["All"] + states)

    if selected_state != "All":
        cities_in_state = state_cities_mapping[selected_state]
        st.sidebar.write(f"Cities in {selected_state}: {', '.join(cities_in_state)}")
        data = data[data['route_name'].str.contains('|'.join(cities_in_state), case=False)]
    
    # Filter by Route Name
    route_names = data['route_name'].unique()
    selected_route = st.sidebar.selectbox("Select Route Name", ["All"] + list(route_names))
    
    # Filter by Price Range
    min_price, max_price = st.sidebar.slider(
        "Select Price Range",
        int(data['price'].min()),
        int(data['price'].max()),
        (int(data['price'].min()), int(data['price'].max()))
    )
    
    # Filter by Bus Type
    selected_bus_type = st.sidebar.selectbox("Select Bus Type", ["All", "AC Sleeper", "Non-AC Sleeper"])
    
    # Filter by Departure Time
    departure_times = data['departing_time'].unique()
    selected_departure_time = st.sidebar.multiselect("Select Departure Time", ["All"] + list(departure_times), default=["All"])
    
    # Filter by Star Rating
    min_rating, max_rating = st.sidebar.slider(
        "Select Star Rating Range",
        float(data['star_rating'].min()),
        float(data['star_rating'].max()),
        (float(data['star_rating'].min()), float(data['star_rating'].max()))
    )
    
    # Filter by Seats Available
    min_seats, max_seats = st.sidebar.slider(
        "Select Seats Available Range",
        int(data['seats_available'].min()),
        int(data['seats_available'].max()),
        (int(data['seats_available'].min()), int(data['seats_available'].max()))
    )
    
    # Apply Filters
    filtered_data = data.copy()
    
    if selected_route != "All":
        filtered_data = filtered_data[filtered_data['route_name'] == selected_route]
    
    if selected_bus_type != "All":
        filtered_data = filtered_data[filtered_data['bustype'] == selected_bus_type]
    
    if "All" not in selected_departure_time:
        filtered_data = filtered_data[filtered_data['departing_time'].isin(selected_departure_time)]
    
    filtered_data = filtered_data[
        (filtered_data['price'].astype(float) >= min_price) &
        (filtered_data['price'].astype(float) <= max_price) &
        (filtered_data['star_rating'].astype(float) >= min_rating) &
        (filtered_data['star_rating'].astype(float) <= max_rating) &
        (filtered_data['seats_available'].astype(int) >= min_seats) &
        (filtered_data['seats_available'].astype(int) <= max_seats)
    ]
    
    # Display Filtered Data
    st.write(f"Showing {len(filtered_data)} buses after applying filters.")
    st.dataframe(filtered_data)
else:
    st.error("No data available in the database.")
