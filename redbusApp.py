import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection function
@st.cache_resource
def get_database_connection():
    # Create the SQLAlchemy engine with PyMySQL
    engine = create_engine("mysql+pymysql://root:root@localhost/redbus_project")
    return engine

# Function to fetch data from the database
def fetch_data():
    engine = get_database_connection()
    query = "SELECT * FROM bus_routes"
    df = pd.read_sql(query, engine)
    return df

# Add colored title using Markdown
st.markdown('<h1 style="color: red;">RouteGuardian</h1>', unsafe_allow_html=True)


try:
    # Fetch data
    data = fetch_data()

    # Sidebar filters
    st.sidebar.header("Filters")

    # Route filter
    routes = data["route_name"].unique()
    selected_routes = st.sidebar.multiselect("Select Route(s)", routes, default=routes)

    # Bus Type filter
    bus_types = data["bustype"].unique()
    selected_bus_types = st.sidebar.multiselect("Select Bus Type(s)", bus_types, default=bus_types)

    # Price range filter
    min_price, max_price = st.sidebar.slider(
        "Select Price Range",
        float(data["price"].min()),
        float(data["price"].max()),
        (float(data["price"].min()), float(data["price"].max())),
    )

    # Star Rating filter
    min_rating, max_rating = st.sidebar.slider(
        "Select Star Rating Range",
        0.0,
        5.0,
        (0.0, 5.0),
        step=0.1,
    )

    # Seat Availability filter
    min_seats = st.sidebar.slider(
        "Minimum Seats Available",
        0,
        int(data["seats_available"].max()),
        0,
    )
    # Filter data
    filtered_data = data[
        (data["route_name"].isin(selected_routes))
        & (data["bustype"].isin(selected_bus_types))
        & (data["price"] >= min_price)
        & (data["price"] <= max_price)
        & (data["star_rating"] >= min_rating)
        & (data["seats_available"] >= min_seats)
    ]

    # Display filtered data
    st.subheader(f"Displaying {len(filtered_data)} Bus Route(s)")
    st.dataframe(filtered_data)

    # Optionally, export filtered data
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_bus_routes.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"An error occurred: {e}")
