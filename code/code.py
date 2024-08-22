#%% Section 1: Preliminaries
# Libraries
# General
from tqdm import tqdm
import os
import io
import pandas as pd
import numpy as np
import datetime as dt
import warnings

# Figures
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
mpl.rcParams.update(mpl.rcParamsDefault)
plt.rcParams["figure.figsize"] = (10,6)
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["legend.fontsize"] = 18
plt.rc("savefig", dpi = 300)
sns.set_theme(style = "ticks", font_scale = 1, font = "DejaVu Sans")

# Mapping
from geopy.distance import geodesic
from PIL import Image
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
pio.renderers.default = 'browser'

# Econometric Analysis
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from linearmodels.panel import PanelOLS

# Other
warnings.filterwarnings("ignore", category=FutureWarning, message="The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.")
warnings.filterwarnings("ignore", category=UserWarning, module='matplotlib.font_manager')
pd.set_option("display.expand_frame_repr", False)

# Filepath
if os.path.exists(""):
    # Personal Computer
    filepath = ""
else:
    # Computing Cluster
    filepath = ""


#%% Section 2: Creating Dataset
# Define Function for Importing Bixi Trip Data
def import_data():
    df = pd.DataFrame()
    for year in tqdm(range(2014,2025)):
        # Years with Bixi Trip Data Stored in Single File
        try:
            file = filepath + f"data/ridership/{year}/data_{year}.csv"
            df_temp = pd.read_csv(file, 
                                  low_memory = False, 
                                  engine = "c")
    
        # Years with Bixi Trip Data Stored Across Many Files
        except:
            df_temp = pd.DataFrame()
            for month in range(1,13):
                if month < 10:
                    file = filepath + f"data/ridership/{year}/OD_{year}-0{month}.csv"
                else:
                    file = filepath + f"data/ridership/{year}/OD_{year}-{month}.csv"
                if os.path.exists(file):
                    df_month = pd.read_csv(file, 
                                           low_memory = False, 
                                           engine = "c")
                    df_temp = pd.concat([df_temp, df_month])
                    
        # Merge in Bixi Station Names
        if any('name' in col.lower() and 'unnamed' not in col.lower() for col in df_temp.columns):
            pass
        else:
            for type in ["start", "end"]:
                df_temp = df_temp.rename(columns = {f"{type}_station_code": "code"})    
                df_temp['code'] = pd.to_numeric(df_temp['code'], errors='coerce').astype('Int64')
                df_temp = pd.merge(df_temp,
                                   pd.read_csv(filepath + f"data/ridership/{year}/Stations_{year}.csv", 
                                               usecols = ["code", "name"],
                                               dtype = {"code": "Int64"},
                                               low_memory = False,
                                               engine = "c"),
                                   on = "code",
                                   how = "left")
                df_temp = df_temp.rename(columns = {"code": f"{type}_station_code",
                                                    "name": f"{type}_name"})
                
        # Rename Variables
        rename_dict = {"STARTSTATIONNAME": "start_name",
                       "ENDSTATIONNAME": "end_name",
                       "STARTSTATIONARRONDISSEMENT": "start_borough",
                       "ENDSTATIONARRONDISSEMENT": "end_borough",
                       "STARTSTATIONLATITUDE": "start_lat",
                       "STARTSTATIONLONGITUDE": "start_long",
                       "ENDSTATIONLATITUDE": "end_lat",
                       "ENDSTATIONLONGITUDE": "end_long",
                       "STARTTIMEMS": "start_date",
                       "ENDTIMEMS": "end_date"}
        df_temp = df_temp.rename(columns = rename_dict)
    
        # Adjust Variable Types
        # Dates
        for date in ["start_date", "end_date"]:
            if year in [2023, 2024]:
                df_temp = df_temp[pd.to_numeric(df_temp[date], errors='coerce').notnull()]
                df_temp[date] = pd.to_datetime(df_temp[date], unit='ms')
            else:
                df_temp[date] = pd.to_datetime(df_temp[date], format = "ISO8601")

        # Other Variables
        dtype_dict = {
            'start_lat': 'float32',
            'start_long': 'float32',
            'end_lat': 'float32',
            'end_long': 'float32',
            "start_borough": "str",
            "end_borough": "str",
            "start_name": "str",
            "end_name": "str"}
        dtype_dict = {k: v for k, v in dtype_dict.items() if k in df_temp.columns}
        df_temp = df_temp.astype(dtype_dict)
        
        # Append Data
        df = pd.concat([df, df_temp])
        
    # Create Year Variable
    df["year"] = df["start_date"].dt.year
    
    # Drop Unneeded Variables
    drop_list = ["start_borough",
                 "end_borough",
                 "start_lat",
                 "start_long",
                 "end_lat",
                 "end_long",
                 "is_member",
                 "duration_sec",
                 "Unnamed: 0",
                 "Unnamed: 0.1",
                 "Unnamed: 0.2",
                 #"start_station_code",
                 #"end_station_code"
                 ]
    drop_list = [col for col in drop_list if col in df.columns]
    df = df.drop(drop_list, 
                 axis = 1)
    
    # Gather ID and Coordinates for Bixi Stations 
    df_stations = pd.read_excel(filepath + "data/ridership/id_crosswalk.xlsx")
    for type in ["start", "end"]:
        df_stations_temp = df_stations.rename(columns = {"id": f"{type}_id",
                                                         "name": f"{type}_name",
                                                         "code": f"{type}_code",
                                                         "latitude": f"{type}_lat",
                                                         "longitude": f"{type}_long"})
        df = pd.merge(df,
                      df_stations_temp,
                      on = [f"{type}_name", "year"],
                      how = "left")
        
    # Return DataFrame
    return df


df = import_data()


# Define Function for Selecting Modal Bixi Station Name and Coordinates
def replace_with_mode(group, type, target):
    # Construct the column name using type and target
    col_name = f"{type}_{target}"
    # Use pandas mode to find the most frequent value
    mode_series = group[col_name].mode()
    if not mode_series.empty:
        # Gather Mode and Perform Replacement
        mode_value = mode_series[0]
        group[col_name] = mode_value
    return group


# Defne Function for Cleaning Imported Data
def clean_data(df):      
    # Replace Name with Modal Name by Bixi Station ID
    for type in ["start", "end"]:
        grouped = df.groupby(f'{type}_id')
        df = grouped.apply(lambda group: replace_with_mode(group, type, target = "name"))
        df = df.reset_index(drop=True)
        
    # Replace Coordinates with Modal Coordinates by Bixi Station ID-Year
    for type in ["start", "end"]:
        grouped = df.groupby([f'{type}_id', 'year'])
        for target in ["lat", "long"]:
            df = grouped.apply(lambda group: replace_with_mode(group, type, target))
            df = df.reset_index(drop=True)
    
    # Interpolate Missing End Date
    df['end_date'] = df['end_date'].fillna(df['start_date'])
    
    # Return DataFrame
    return df
        
    
df = clean_data(df)


#%% Section 3: Creating Variables of Interest
# Number of Trips
df["trip_count"] = 1

# Define Function for Calculating Distance Between Stations
def haversine_distance(data, lat1, long1, lat2, long2):
    # Radius of Earth
    R = 6371.0

    # Convert Coordinates to Radians
    lat1_rad = np.radians(data[lat1])
    lon1_rad = np.radians(data[long1])
    lat2_rad = np.radians(data[lat2])
    lon2_rad = np.radians(data[long2])

    # Take Difference in Coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Apply Haversine Distance Formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # Calculate Distance
    distance = (R * c)

    return distance


# Trip Distance
df['trip_distance'] = haversine_distance(df, "start_lat", "start_long", "end_lat", "end_long")
df["trip_distance"].replace(0, np.nan, inplace=True)

# Trip Duration
df["trip_duration"] = (df['end_date'] - df['start_date']).dt.total_seconds() / 60
df = df[df["trip_duration"] < 1440]
df = df[df["trip_duration"] > (1/60)]

# Rectangularize Dataset
dates = pd.date_range(start='2014-01-01', end='2024-07-31', freq='D')
stations = df['start_id'].unique()
all_combinations = pd.MultiIndex.from_product([dates, stations], names=['start_date', 'start_id']).to_frame(index=False)
all_combinations["start_date"] = pd.to_datetime(all_combinations["start_date"]).dt.date
df["start_date"] = pd.to_datetime(df["start_date"]).dt.date
df_merged = pd.merge(all_combinations, 
                     df, 
                     on=['start_date', 'start_id'], 
                     how='left')

# Fill Missing Coordinates
for col in df_merged.columns:
    if ("lat" in col) or ("long" in col):
        df_merged[col] = df_merged.groupby('start_id')[col].apply(lambda group: group.ffill().bfill()).reset_index(level=0, drop=True)

# Fill Missing Outcomes
df_merged.fillna(
    {"trip_count": 0, 
     'trip_distance': 0, 
     "trip_duration": 0}, 
    inplace=True)

# Create Other Date Variables
df_merged["start_date"] = pd.to_datetime(df_merged["start_date"])
df_merged["end_date"] = pd.to_datetime(df_merged["end_date"])
df_merged['weekly_date'] = df_merged['start_date'] - pd.to_timedelta(df_merged['start_date'].dt.weekday, unit='d')
df_merged['monthly_date'] = df_merged['start_date'].dt.to_period('M').dt.to_timestamp()
df_merged["monthly_date"] = df_merged["monthly_date"].dt.date


#%% Section 4: Identify Treated Bixi Stations
df_paths = gpd.read_file(filepath + "data/bike_network/reseau_cyclable.geojson")

# Identify REV Segments by Axis
list_axis1 = [21598, 24146, 21597, 21599, 21355, 23819, 21601, 21601, 21027, 21026, 21600, 21601, 24147, 21025, 21024, 26063, 25554, 25912, 25913, 25911, 21023, 25553, 21030, 23821, 21029, 21357, 21356, 21028, 21359, 25584, 21358, 25585, 25796, 25833, 26136, 25866, 21360, 24187, 22907, 25865, 25627, 22906, 25626, 22905, 25618, 20705, 25617, 20704, 25616, 24826, 22908, 25615, 20726, 20725, 20724, 24635, 24031, 24342, 25218, 25609, 25608, 25607, 25878, 26137, 25613, 25848, 26139, 26140, 25849, 25851, 26142, 25850, 26141, 25813, 26138, 25634, 25633, 25632, 25233, 22212, 25631, 20181, 25874, 25526, 22186, 33616, 33618, 33617, 33620, 33622, 33621, 33619, 33624, 33626, 33625, 33623, 33628, 33630, 33629, 33627, 25241, 25641, 30443]
df_rev = df_paths[df_paths['ID_CYCL'].isin(list_axis1)]

# Define Function for Calculating Distance Between Point and Line
def point_to_line_distance(point, start, end):
    # Convert Coordinates to Arrays
    point = np.array(point)
    start = np.array(start)
    end = np.array(end)

    # Project Point Onto Line
    line_vec = end - start
    point_vec = point - start
    line_len = np.dot(line_vec, line_vec)
    projection = np.dot(point_vec, line_vec) / line_len

    # Bound Projection Value Between 0 and 1
    projection = max(0, min(1, projection))

    # Find Closest Point to Line Segment
    closest_point = start + projection * line_vec

    # Calculate Distance Between Point and Closest Point on Line Segment
    return geodesic(point, closest_point).meters


# Define Function for Calculating Distance from Bixi Station to REV Path
def station_to_path_distance(station_coords, path_coords, treated_threshold, control_threshold):
    # Initialize Treatment Status
    treated = None
    
    # Initialize Minimum Distance
    min_distance = float('inf')
    
    # Iterate Over REV Path Segments
    for i in range(len(path_coords) - 1):
        start_vertex = (path_coords[i][1], path_coords[i][0])
        end_vertex = (path_coords[i + 1][1], path_coords[i + 1][0])

        # Calculate Distance from Bixi Station to Rev Path
        distance = point_to_line_distance(station_coords, start_vertex, end_vertex)
        
        # Treated
        if distance <= treated_threshold:
            return 1, distance  
        
        # Control
        elif distance <= control_threshold:
            treated = 0
            if distance < min_distance:
                min_distance = distance
        
    # Return Treatment Status and Distance
    if treated is not None:
        # Handle case where no valid min_distance was found
        return treated, min_distance if min_distance != float('inf') else None
    
    # Other
    return None, None


# Define Function for Assigning Stations to Treatment
def assign_stations_to_treatment(data):
    # Identify Unique Bixi Stations
    unique_stations = data.groupby("start_id")[["start_lat","start_long"]].mean().reset_index()
    unique_stations = unique_stations.dropna()
    
    # Initialize Treatment Dictionary
    treated_dict = {}
    
    # Iterate Over Bixi Stations
    for index, station_row in tqdm(unique_stations.iterrows(), total=unique_stations.shape[0]):
        station_coords = (station_row['start_lat'], station_row['start_long'])
        start_id = station_row["start_id"]
        
        # Initialize Treatment Status and Distance to REV Path
        treated = None
        min_distance = float('inf')  
        
        # Iterate Over REV Path Segments
        for _, path_row in df_rev.iterrows():
            path_geometry = path_row['geometry']
            coords_list = list(path_geometry.coords)
            
            # Calculate Distance Between Bixi Station and REV Path Segment
            result, distance = station_to_path_distance(station_coords, 
                                                        coords_list, 
                                                        treated_threshold = 100, 
                                                        control_threshold = 300)
            
            # Treated
            if result == 1:
                treated = 1 
                min_distance = distance 
                break
            
            # Control
            elif result == 0:
                treated = 0
                if distance < min_distance:
                    min_distance = distance
        
        # Other
        if treated == 0 and min_distance == float('inf'):
            min_distance = None  
        
        # Store Treatment Status and Distance in Dictionary
        treated_dict[start_id] = {"treated": treated,
                                  "rev_distance": min_distance}
    
    # Convert Dictionary to DataFrame
    df_treated = pd.DataFrame.from_dict(treated_dict, orient='index').reset_index()
    df_treated.columns = ['start_id', 'treated', 'rev_distance']
    
    # Return Treatment Classification
    return df_treated


# Assign Bixi Stations to Treatment
df_treated = assign_stations_to_treatment(df_merged)

# Create Treatment Variable
df_merged = pd.merge(df_merged, 
                     df_treated, 
                     on='start_id', 
                     how='left')

# Create Post Variable
df_merged['post'] = (df_merged['start_date'] >= pd.Timestamp('2020-11-07')).astype(int)


#%% Section 5: Exploring Data
# 1. Average Daily Bixi Ridership Over Time
df_plot = df_merged
df_plot = df_plot.groupby("monthly_date")["trip_count"].sum().reset_index()
df_plot["trip_count"] = df_plot["trip_count"]/30.25

ax = sns.barplot(data = df_plot, x = 'monthly_date', y = 'trip_count', color = "blue")
plt.grid(False)
ticks = ax.get_xticks()
ax.set_xticks(ticks[::12])
plt.xticks(rotation=45)
plt.ylabel("Average Daily Trips")
plt.xlabel("")
plt.title("Average Number of Daily Bixi Trips, Jan 2014 - July 2024")
plt.savefig(filepath + "figures/average_daily_ridership.png", bbox_inches = "tight")
plt.show()

# 2. Average Daily Bixi Trips per Day of Week in July 2024
df_plot = df_merged
df_plot = df_plot[df_plot["start_date"].dt.year == 2024]
df_plot = df_plot[df_plot["start_date"].dt.month == 7]
df_plot = df_plot.groupby("start_date")["trip_count"].sum().reset_index()
df_plot["day_week"] = df_plot['start_date'].dt.day_name()
df_plot = df_plot.groupby("day_week")["trip_count"].mean().reset_index()
df_plot = df_plot.sort_values(by = "trip_count", ascending = False)

ax = sns.barplot(data = df_plot, x= 'day_week', y = 'trip_count', color = "blue")
plt.grid(False)
ticks = ax.get_xticks()
plt.ylabel("Average Daily Trips")
plt.xlabel("")
plt.title("Average Number of Daily Bixi Trips per Day of Week, July 2024")
plt.savefig(filepath + "figures/average_daily_ridership_dayofweek.png", bbox_inches = "tight")
plt.show()

# 3. Number of Bixi Stations Over Time
df_plot = df_merged
df_plot = df_plot[df_plot["trip_count"] > 0]
df_plot = df_plot.groupby(["monthly_date"])["start_id"].nunique().reset_index()

ax = sns.lineplot(data = df_plot, x = 'monthly_date', y = 'start_id', color = "blue")
plt.grid(False)
plt.ylim([0,1000])
ticks = ax.get_xticks()
plt.ylabel("Number of Stations in Operation")
plt.xlabel("")
plt.title("Number of Stations in Operation, Jan 2014 - July 2024")
plt.savefig(filepath + "figures/number_stations.png", bbox_inches = "tight")
plt.show()


#%% Section 6: Mapping
# 1. Map of Usage by Bixi Station
df_map = df_merged
df_map = df_map.groupby(["start_id", "weekly_date"]).agg(
    {"trip_count": "sum",
     "trip_distance": "sum",
     "start_lat": "mean",
     "start_long": "mean",
     "start_name": "first"}).reset_index()

df_map["weekly_date"] = pd.to_datetime(df_map["weekly_date"])
df_map['weekly_date_str'] = df_map['weekly_date'].dt.strftime('%Y-%m-%d')
df_map = df_map.sort_values(by = "weekly_date")

# Define Function for Specifying Map Parameters
def map_parameters(data, animation_frame, title, size_max):     
    # Specify Map Parameters
    fig = px.scatter_mapbox(data, 
                         lat = 'start_lat', 
                         lon = 'start_long',
                         size = 'trip_count',
                         color = "trip_distance",
                         animation_frame = animation_frame,
                         size_max = size_max,
                         opacity = 0.75,
                         hover_data = {"weekly_date_str": False,
                                       "start_lat": False,
                                       "start_long": False,
                                       "start_name": True},
                         labels = {"weekly_date_str": "Date",
                                   "start_name": "Station Name",
                                   "trip_count": "Total Number of Trips",
                                   "trip_distance": "Total Distance Travelled (km)"},
                         range_color = [0, 5000])
    
    # Adjust Map Position
    fig.update_layout(mapbox_style="open-street-map",
                      mapbox = dict(
                          center = go.layout.mapbox.Center(
                              lat = 45.515,
                              lon = -73.630),
                          zoom = 10.5))
    
    # Adjust Color Bar
    fig.update_layout(coloraxis_colorbar=dict(
        title = "Total Distance Travelled (km)",
        tickvals = [0, 1000, 2000, 3000, 4000, 5000],
        ticktext = ['0', '1000', '2000', '3000', '4000', '5000+'],
        ))
    
    # Add Title
    fig.update_layout(
        title = {
            "text": title,
            "font_size": 20,
            "x": 0.50})
    
    # Add Caption
    fig.update_layout(
        annotations = [dict(
        x= 0.50,
        y = -0.05,
        font_size = 12,
        showarrow = False,
        text = "")])
    
    # Adjust Map Size
    fig.update_layout(
        width = 1800,
        height = 1000) 
    
    # Return Map
    return fig


# Define Function for Creating Map
def map_station_usage(data, type): 
    # Static Map
    if type == "static":
        pio.renderers.default = 'browser'
        animation_frame = None
        title = "Bixi Usage in Montreal, July 2024"
        size_max = 20
        data = data[data["weekly_date"].dt.date == dt.date(2024,7,29)]
        fig = map_parameters(data, animation_frame, title, size_max)
        fig.show()
        
    # Animated Map
    elif type == "animated":
        pio.renderers.default = 'browser'
        animation_frame = "weekly_date_str"
        title = "Bixi Usage in Montreal, Jan 2014 - July 2024"
        size_max = 20
        fig = map_parameters(data, animation_frame, title, size_max)
        fig.show()
    
    # GIF Map
    elif type == "gif":
        images = []
        pio.renderers.default = 'png'
        animation_frame = None
        size_max = 20
        
        # Iterate Over Weeks
        for date in tqdm(data["weekly_date"].unique().tolist()):
            # Duplicate DataFrame 
            data_temp = data
            
            # Select Date
            date = pd.to_datetime(date).normalize()
            data_temp = data_temp[data_temp["weekly_date"] == date]
            date_str = date.strftime('%Y-%m-%d')
            title = f"Bixi Usage in Montreal, {date_str}"
            fig = map_parameters(data_temp, animation_frame, title, size_max)
            
            # Save Map as Image
            try:
                img_bytes = PlotlyImage.get(fig)
                image = PILImage.open(io.BytesIO(img_bytes))
                image.save(filepath + "figures/images/image" + date_str + ".png")
                images.append(image)
            except:
                break
            
        # Create GIF from Images
        image_files = [f for f in os.listdir(filepath + "figures/images") if f.endswith(('.png'))]
        image_files.sort()
        images = [Image.open(os.path.join(filepath + "figures/images", file)) for file in image_files]
        images[0].save(filepath + "figures/gif_map.gif",
                       save_all = True, 
                       append_images = images[1:], 
                       optimize = True, 
                       duration = 200, 
                       loop = 0)
        

# Create Map
map_station_usage(df_map, type = "gif")

# 2. Map of REV Path, Treated Bixi Stations, and Control Bixi Stations
df_station_treatment_status = df_merged
df_station_treatment_status = df_station_treatment_status.groupby(["start_id", "weekly_date"]).agg(
    {"rev_distance": "first",
     "treated": "first",
     "post": "first",
     "start_lat": "first",
     "start_long": "first"}).reset_index()

df_station_treatment_status = df_station_treatment_status[df_station_treatment_status["weekly_date"].dt.date == dt.date(2024, 7, 29)]
df_station_treatment_status.to_excel(filepath + "data/bike_network/station_treatment_status.xlsx")

# Identify REV Bike Paths
df_paths = gpd.read_file(filepath + "reseau_cyclable.geojson")
list_axis1 = [21598, 24146, 21597, 21599, 21355, 23819, 21601, 21601, 21027, 21026, 21600, 21601, 24147, 21025, 21024, 26063, 25554, 25912, 25913, 25911, 21023, 25553, 21030, 23821, 21029, 21357, 21356, 21028, 21359, 25584, 21358, 25585, 25796, 25833, 26136, 25866, 21360, 24187, 22907, 25865, 25627, 22906, 25626, 22905, 25618, 20705, 25617, 20704, 25616, 24826, 22908, 25615, 20726, 20725, 20724, 24635, 24031, 24342, 25218, 25609, 25608, 25607, 25878, 26137, 25613, 25848, 26139, 26140, 25849, 25851, 26142, 25850, 26141, 25813, 26138, 25634, 25633, 25632, 25233, 22212, 25631, 20181, 25874, 25526, 22186, 33616, 33618, 33617, 33620, 33622, 33621, 33619, 33624, 33626, 33625, 33623, 33628, 33630, 33629, 33627, 25241, 25641, 30443]
df_rev = df_paths[df_paths['ID_CYCL'].isin(list_axis1)]

# Convert DataFrame to GeoDataFrame
df_map = gpd.GeoDataFrame(df_rev, geometry='geometry')

# Define Function for Creating Map
def map_rev_treated_control(data):
    # Extract Latitude and Longitude from LineString
    data['lon'] = data.geometry.apply(lambda x: list(x.coords)[0][0])
    data['lat'] = data.geometry.apply(lambda x: list(x.coords)[0][1])
    
    # Create List of Points in All LineStrings
    data['coords'] = data['geometry'].apply(lambda x: list(x.coords))
    
    # Explode Coordinates
    data = data.explode('coords')
    
    # Separate Exploded Coordinates into Latitude and Longitude
    data['lon'] = data['coords'].apply(lambda x: x[0])
    data['lat'] = data['coords'].apply(lambda x: x[1])
    
    # Merge in Treatment Status by Station
    df_station_treatment_status = pd.read_excel(filepath + "station_treatment_status.xlsx")
    
    # Recode Treatment Status
    df_station_treatment_status['treated'] = df_station_treatment_status['treated'].map(
        {0: 'Control', 
         1: 'Treated'}).fillna("Other")
    df_station_treatment_status = df_station_treatment_status.sort_values(by=['treated'], key=lambda x: x.map({'Treated': 0, 'Control': 1, 'Other': 2}))
    color_map = {"Control": 'red', 
                 "Treated": 'green',
                 "Other": "grey"}
    
    # Plot REV Path
    line_fig = px.line_mapbox(
        data,
        lon = 'lon',
        lat = 'lat',
        mapbox_style = "open-street-map",
        line_group = data.index,  # Ensure lines are grouped by the original geometry
    )
    
    # Adjust Line Color
    line_fig.update_traces(line=dict(color='black'))
    
    # Plot Bike Rental Stations
    scatter_fig = px.scatter_mapbox(
        df_station_treatment_status,
        lon = 'start_long',
        lat = 'start_lat',
        color = "treated",
        color_discrete_map = color_map,
        mapbox_style = "open-street-map",
    )
    
    # Adjust Scatter Size
    scatter_fig.update_traces(marker=dict(size=10))
    
    # Combine Line and Scatter Plots
    for trace in scatter_fig.data:
        line_fig.add_trace(trace)
    
    # Adjust Map Size
    line_fig.update_layout(
        width = 1800,
        height = 1000) 
    
    # Adjust Map Position
    line_fig.update_layout(mapbox = dict(
                              center = go.layout.mapbox.Center(
                                  lat = 45.540,
                                  lon = -73.630),
                              zoom = 12.5))
    
    # Add Legend Title
    line_fig.update_layout(
        legend_title_text = 'Treatment Status'
    )
    
    # Show Map
    line_fig.show()


# Create Map
map_rev_treated_control(df_map)


#%% Section 7: Prepare Data for Regressions
# Define Function for Preparing Dataset for Regressions
def prepare_regressions(data):
    # Select Relevant Variables
    df_regression = data.groupby(["start_id", "weekly_date"]).agg(
        {"trip_count": "sum",
         "trip_distance": "mean",
         "trip_duration": "mean",
         "rev_distance": "first",
         "treated": "first",
         "post": "first",
         "start_lat": "first",
         "start_long": "first"}).reset_index()
    
    # Convert Treatment Variables to Binary
    df_regression['post'] = df_regression['post'].astype(df_regression['post'].dtype)
    df_regression['treated'] = df_regression['treated'].astype(df_regression['treated'].dtype)
    
    # Seasonally Adjust Outcome Variables
    df_regression = df_regression.sort_values(by=['start_id', 'weekly_date'])
    df_regression.set_index('weekly_date', inplace=True)
    for outcome in ["trip_count", "trip_distance", "trip_duration"]:
        outcome_sa = f"{outcome}_sa"
        df_regression[outcome_sa] = df_regression.groupby('start_id')[outcome].transform(
            lambda x: seasonal_decompose(x, model='additive', period=52).resid + seasonal_decompose(x, model='additive', period=52).trend
        )
    
    # Distance to Central Business District
    df_regression["cbd_lat"] = 45.49963
    df_regression["cbd_long"] = -73.57092
    df_regression['cbd_distance'] = haversine_distance(df_regression, "start_lat", "start_long", "cbd_lat", "cbd_long")
    
    # Weather
    df_weather = pd.DataFrame()
    for year in range(2014,2025):
        df_weather_temp = pd.read_csv(filepath + f"weather/{year}.csv")
        df_weather = pd.concat([df_weather, df_weather_temp])
        
    df_weather = df_weather.rename(columns = {"Year": "year",
                                              "Month": "month",
                                              "Day": "day",
                                              "Mean Temp (°C)": "temp",
                                              "Total Precip (mm)": "precip",
                                              "Snow on Grnd (cm)": "snow_ground"})
    df_weather['snow_ground'] = df_weather['snow_ground'].fillna(0)
        
    df_weather['date'] = pd.to_datetime(df_weather[['year', 'month', 'day']])
    df_weather['weekly_date'] = df_weather['date'] - pd.to_timedelta(df_weather['date'].dt.weekday, unit='d')
    df_weather = df_weather.groupby("weekly_date").agg(
        {"temp": "mean",
         "precip": "mean",
         "snow_ground": "mean"}).reset_index()
    df_regression = pd.merge(df_regression,
                             df_weather[["weekly_date", "temp", "precip", "snow_ground"]],
                             on = "weekly_date",
                             how = "left")
    
    # Monthly Dummies 
    df_regression['month'] = pd.to_datetime(df_regression['weekly_date']).dt.month
    month_dummies = pd.get_dummies(df_regression['month'], prefix='month')
    df_regression = pd.concat([df_regression, month_dummies], axis=1)
    for col in df_regression.columns:
        if 'month_' in col:
            df_regression[col] = df_regression[col].astype(int)
            
    # Return DataFrame
    return df_regression


df_regression = prepare_regressions(df_merged)


#%% Section 8: Assessing Parallel Trends
# Define Function for Assessing Parallel Trends Assumption
def did_plot(data, outcomes):
    # Create Empty List for Plots
    images = []
    
    # Iterate Over Outcomes
    for outcome in outcomes:
        # Duplicate DataFrame
        df_plot = data
        
        # Create Event Time Variable
        event_date = pd.to_datetime('2020-11-07')
        df_plot["weekly_date"] = pd.to_datetime(df_plot["weekly_date"])
        df_plot['monthly_date'] = df_plot['weekly_date'].dt.to_period('M').dt.to_timestamp()
        df_plot['event_time'] = (df_plot['monthly_date'].dt.year - event_date.year) * 12 + (df_plot['monthly_date'].dt.month - event_date.month)
        
        # Display Single Month Per Year
        df_plot = df_plot[df_plot["monthly_date"].dt.month == 11]
        
        # Select Parameters
        if outcome == "trip_count_sa":
            ylabel = "Average Number of Weekly Trips per Bixi Station"
            title_label = "Number of Trips"
        elif outcome == "trip_distance_sa":
            ylabel = "Average Distance of Trip per Bixi Station (Kilometers)"
            title_label = "Trip Distance"
        elif outcome == "trip_duration_sa":
            ylabel = "Average Duration of Trip per Bixi Station (Minutes)"
            title_label = "Trip Duration"
        
        # Express Outcome by Station
        if outcome == "trip_count":
            df_plot = df_plot.groupby(["event_time", "treated"]).agg(
                count_stations = ("treated", "count"),
                **{f"{outcome}": (outcome, "sum")}
                ).reset_index()
            df_plot[outcome] = df_plot[outcome] / df_plot["count_stations"]
        else:
            df_plot = df_plot.groupby(["event_time", "treated"]).agg(
                **{f"{outcome}": (outcome, "mean")}
                ).reset_index()
        
        # Plot Outcome in Event Time
        treated_group = df_plot[df_plot['treated'] == 1]
        control_group = df_plot[df_plot['treated'] == 0]
        plt.plot(control_group['event_time'], control_group[outcome], marker = "o", linestyle='-', color='blue', label='Control Group')
        plt.plot(treated_group['event_time'], treated_group[outcome], marker = "o", linestyle='-', color='red', label='Treatment Group')
        
        # Add Vertical Line at Treatment Date
        plt.axvline(x=0, color='gray', linestyle='--')

        # Annotating Plot
        plt.title(f'Difference-in-Differences Plot in Event Time, {title_label}')
        plt.grid(False)
        plt.xlim(-62,62)
        plt.xlabel('Event Time (Months since 2020-11)')
        plt.ylabel(ylabel)
        plt.legend(loc = "upper left")
        plt.savefig(filepath + f"figures/did_{outcome}.png", bbox_inches='tight')
        
        # Show Plot
        plt.show()
        
        # Append Plot to List of Plots
        image_path = os.path.join(filepath, f"figures/did_{outcome}.png")
        image = Image.open(image_path)
        images.append(image)
        
    # Combine Plots
    total_width = sum(image.size[0] for image in images)
    max_height = max(image.size[1] for image in images)
    combined_image = Image.new('RGB', (total_width, max_height))
    current_width = 0
    for image in images:
        combined_image.paste(im=image, box=(current_width, 0))
        current_width += image.size[0]

    # Save Combined Plots
    combined_image.save(os.path.join(filepath, 'figures/did_combined.png'))
            

# Create Difference-in-Difference Plot
did_plot(df_regression, ["trip_count_sa", "trip_distance_sa", "trip_duration_sa"])


#%% Section 9: Model Estimation
# Define Function for Estimating Treatment Effect
def estimation(data, outcomes, models):
    # Iterate Over Models
    for model in models:
        # Standard Difference-in-Differences Model
        if model == "standard":
            # Iterate Over Specifications
            for spec in range(1,4):
                # Iterate Over Outcomes
                for outcome in outcomes:
                    # Duplicate DataFrame
                    df_est = data
            
                    # Retain Relevant Variables
                    df_est = df_est[[outcome, "treated", "post", "rev_distance", "cbd_distance", "temp", "precip", "snow_ground"] + [f"month_{i}" for i in range(1, 12)]]
                    df_est['interaction'] = df_est["treated"]*df_est["post"]
                    df_est["rev_distance"] = df_est["rev_distance"] / 1000
                    df_est = df_est.replace([np.inf, -np.inf], np.nan).dropna()

                    # Specify Outcome and Regressors
                    y = df_est[outcome]
                    
                    if spec == 1:
                        X = sm.add_constant(df_est[['post', 'treated', 'interaction']])
                    if spec == 2:
                        X = sm.add_constant(df_est[['post', 'treated', 'interaction', "rev_distance", "cbd_distance"]])
                    if spec == 3:
                        X = sm.add_constant(df_est[['post', 'treated', 'interaction', "rev_distance", "cbd_distance", "temp", "precip", "snow_ground"]])
                    
                    # Estimate Model
                    model = sm.OLS(y, X).fit(cov_type = "HC3")
                    summary = model.summary()
                    
                    # View Estimation Results
                    print(summary)
                    
                    # Save Estimation Results as LaTeX File
                    with open(filepath + f'output/regression_{model}_{spec}_{outcome}.tex', 'w') as f:
                        f.write(summary.as_latex())
        
        # Two-Way Fixed Effects
        elif model == "twfe":
            for outcome in outcomes:
                # Duplicate DataFrame
                df_est = data
                
                # Retain Relevant Variables
                df_est = df_est[[outcome, "start_id", "weekly_date", "treated", "post"]]
                df_est['interaction'] = df_est["treated"] * df_est["post"]
                df_est = df_est.replace([np.inf, -np.inf], np.nan).dropna()
                if not isinstance(df_est.index, pd.MultiIndex):
                    df_est = df_est.set_index(['start_id', 'weekly_date'])
                
                # Specify Outcome and Regressors
                y = df_est[outcome]
                X = sm.add_constant(df_est[["interaction"]])
                
                # Estimate Model
                model = PanelOLS(y, X, entity_effects=True, time_effects=True)
                result = model.fit(cov_type='robust')
                summary = result.summary
                
                # View Estimation Results
                print(summary)
                
                # Save Estimation Results as LaTeX File
                with open(filepath + f'output/regression_{model}_{outcome}.tex', 'w') as f:
                    f.write(result.summary.as_latex())
                
                
# Perform Estimation for Various Outcomes
estimation(df_regression, 
           ["trip_count_sa", "trip_distance_sa", "trip_duration_sa"],
           ["standard"])

