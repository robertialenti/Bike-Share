# Impact of the REV on Montreal's Bike Share Program

This project aims to assess how the development of the Reseau Express Velo (REV) - a recently built network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I employ a difference-in-differences research design, comparing outcomes for Bixi stations located alongside the REV to those located farther away, to assess the REV's impact on bikesharing. Outcomes include average weekly ridership, average trip duration, and average trip distance. 

## Context
In 2019, Valerie Plante, Mayor of Montreal and leader of Projet Montreal, announced that the city would be undertaking a project to build more, higher-quality bike infrastructure, beginning in its central neighborhoods. This would include the construction of new, wide, well sign-posted, and protected bike lanes with synchronized street lights to help Montrealers more comfortably and safely traverse large distances. These paths would also be prioritized for snow clearing in winter, making them usable year-round. You can read more about the REV [here](https://montreal.ca/articles/le-rev-un-reseau-express-velo-4666).

Projet Montreal put forward plans to build 5 such axes:

- Axis 1: Berri-Lajeunesse-Saint-Denis: This axis is the longest in the REV network and provides North-South coverage in the center of the city. It links the boulevard Gouin with the rue Roy. The axis was inauguarateed on 11/07/2020.
- Axis 2: Viger-Saint-Antonine-Saint-Jacques: This axis serves a short East-West segment between rue Guy and rue De Coucelle, predominantly in the city's Ville-Marie borough.
- Axis 3: Souligny: This axis, running East-West between the rue Honore-Beaugrand and avenue Hector, is furthest from the city center.
- Axis 4: Peel: This axis serves a short North-South corridor on Peel, a major commercial shopping street in the city's downtown core, between avenue des Pins and rue Smith.
- Axis 5: Bellechasse: An East-West axis running on Bellechase between de Gaspe and Chatelain, predominantly in the Rosemont-La Petite-Patrie borough, and intersecting with Axis 1 of the REV at Saint-Denis/Bellechasse.

While the REV has been touted as a success by bike enthusiasts, this is the first attempt - as far as I know - to causally evaluate the its effect on rideshare utilization.

## Data
The project primilarly relies on ride-level data made freely available by Bixi for the period April 2014 - July 2024. I also use data from the City of Montreal, which has geocoded all of the city's existing bike network, as well as daily weather data from Environment Canada.

- Bixi, Rides: https://bixi.com/en/open-data/
- City of Montreal, Bike Network: https://donnees.montreal.ca/dataset/pistes-cyclables
- Environment Canada, Daily Weather in Montreal: https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=51157

## Code
Code for the project is written entirely in Python and separated into 8 sections. I run the code primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory. To run the code without modification, store the Bixi ride-level data in year-specific folders in `data/ridership/`, geocoded bike network data from the City of Montreal in `data/bike_network/`, and weather data from Environment Canada in `data/weather/`. In the same project directory, create empty folders called `figures` and `output` to collect results.

### 1. Preliminaries
In this section, I simply import modules that I'll need to conduct the work. I take advantage of a number of widely used libraries for data science, spatial analysis, and econometrics.

### 2. Importing and Cleaning Data
I begin by reading and appending Bixi's ride-level microdata. In some years, Bixi provides ride-level data by month, while in other years all of the ridership data is included in a single dataset. Variable names change somewhat through time, as do date formats. The code handles these intertemporal inconsistencies. The dataset includes all of the approximately 62 million rides completed on Bixi bikes between April 2014 and July 2024.

In order to generate aggregate statistics by station, it is important to have a unique and time-invariant station identifier. The ride-level data from Bixi provides two potentially useful identifiers: $\text{Station Name}$ and $\text{Station Code}$. However, both can be unreliable as the same station may use different names or different station codes, in the same year and through time.

To address this issue, I group Bixi stations together based on whether I believe docking stations with different names actually refer to the same station. I do so by retaining unique station names and sorting by coordinates. I create a crosswalk file, `data/ridership/id_crosswalk.xlsx`, which I merge with the ride-level microdata. I also update station names and coordinates. For each value of Station ID, I replace each station's name with its modal station name. For each Station ID-Year pair, I replace the station's coordinates with its modal coordinates.

Here is an example with just six observations, which are sufficient for illustrating the process. These trips, taken just a few minutes apart on the same day in 2018, are found to originate from seemingly different stations with different station names and codes. Grouping by either station name or station code would be erroneous. In reality, all of these trips should originate from the same Bixi station, installed at Vendome Metro since 2014. This becomes evident when verifying the location of the Bixi docking stations with manual validation. 

| Year | Date | Station Name | Latitude | Longitude | Station Code |
| ---- | ---- | ------------ | -------- | --------- | ------------ | 
| 2018 | 2018-04-23 17:42 | de Vendôme / de Maisonneuve | 45.4744 | -73.604 | 6418 |
| 2018 | 2018-04-23 18:00 | de Vendôme / de Maisonneuve | 45.4744 | -73.604 | 6418 |
| 2018 | 2018-04-23 18:03 | Marlowe / de Maisonneuve | 45.4739 | -73.6047 | 6080 |
| 2019 | 2019-06-10 17:45 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4739 | -73.6047 | 6080 |
| 2019 | 2019-06-10 17:49 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4739 | -73.6047 | 6080 |
| 2019 | 2019-06-10 17:50 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4739 | -73.6047 | 6080 |

After merging the ride-level data with the crosswalk, these observations are assigned the same $\text{Station ID}$. The station's name is replaced with its mode while the station's latitude and longitude are replaced with their year-specific modes. This ensures that I capture changes to the docking station's precise location, which may change somewhat from year to year.

| Year | Date | Station Name | Latitude | Longitude | Station ID |
| ---- | ---- | ------------ | -------- | --------- | ---------- |
| 2018 | 2018-04-23 17:47 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4744 | -73.604 | 174 |
| 2018 | 2018-04-23 18:00 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4744 | -73.604 | 174 |
| 2018 | 2018-04-23 18:03 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4744 | -73.604 | 174 |
| 2019 | 2019-06-10 17:45 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4739 | -73.6047 | 174 |
| 2019 | 2019-06-10 17:49 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4744 | -73.6047 | 174 |
| 2019 | 2019-06-10 17:50 | Métro Vendôme (de Marlowe / de Maisonneuve) | 45.4739 | -73.6047 | 174 |

### 3. Creating Outcome Variables
Here, I create three outcome variables: trip count, trip distance, and trip duration.

Trip count measures the number of trips undertaken, by Bixi station and date.

As Bixi does not provide trip-level GPS data, which would be needed to track the precise journey undertaken by a user, I instead measure trip distance as the Haversine distance between the starting and ending station. I recognize that this is a flawed measure and a lower bar for the actual distance traversed on any given trip. For all trips with a distance of 0 - that is, trips beginning and ending at the same docking station - I replace trip distance with a missing value. As such, these trips will not be included in regression analysis in instances where the outcome of interest is trip distance.

Trip duration is calculated as the difference between a journey's start time and end time.

I remove Bixi trips with implausible distances or journey times to reduce the impact of outliers on parameter estimates. This removes relatively few observations.

### 4. Identifying Treated Bixi Stations
Rather than consider all axes of the REV, I focus exclusively on Axis 1 because it provides the best case study for assessing the REV's impact. Other axes were rolled out in a more staggered fashion, and were subject to delays and additional works. Axis 1, on the other hand, was inaugurated in its entirety on the same day and has been subject to fewer disruptions in the years since.

I define treated Bixi stations as those located within 100 meters of the REV path and control stations as those located between 100 and 300 meters from the REV. These thresholds are informed by the existing literature, which finds that up to 500 meters is a reasonable distance to walk to bikeshare stations. I select a lower threshold, in large part because of high Bixi station density in the neighborhood served by the REV's Axis 1.

The City of Montreal maintains a database with information on all bike paths in the city. Each path is subdivided into segments, each of which is precisely geocoded. As such, I can simply assign stations to treatment by employing the following procedure:

1. Select a Bixi station.
2. For each Bixi station, iterate through every segment of the REV.
3. For each REV segment, create a polygon using the coordinates bounding the segment.
4. Calculate the distance between the Bixi station and each pair of vertices forming the polygon for the segment.
5. If the distance is less than 100 meters, assign the Bixi station to treatment.
6. If the distance is beteween 100 meters and 300 meters, continue iterating through REV segments. If no other REV segment is found to be less than 100 meters from the Bixi station, assign the Bixi station to the control group.
7. If the distance between the Bixi station and the REV is never found to be less than 300 meters, assign the station to neither the treatment nor the control group.
8. Return the treatment status and distance between Bixi station and REV path.

Here is a plot showing the location of the REV Axis 1. Bixi stations are classified as either Treated, Control, or Other, depending on how far they are located from the path of the REV's Axis 1.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/treated_stations.png" width="900" height="500">

### 5. Exploring Data
At this point, I have all of the variables needed to generate descriptive statistics and perform the econometric analysis. Here is a description of the variables.

I first plot average daily ridership by month, for every month between January 2014 and July 2024. Clearly, there is strong seasonality in bike ridershp, with usage of Bixi peaking in summer months. I verify that daily ridership calculated from the microdata lines up with Bixi's self-reported ridership statistics.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/average_daily_ridership.png" width="425" height="250">

Next, I plot average daily ridership by day of the week in July 2024. In line with expectations, Saturday and Friday are the most popular days for bikesharing.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/average_daily_ridership_dayofweek.png" width="425" height="250">

Finally, I plot the number of active Bixi stations over time, only in months in which the service is operating. Note that, in the winter of 2023, Bixi piloted a project whereby it operated around 150 stations in the city's core for the first. This explains the sharp and temporary decline in the number of active Bixi stations. In 2024, the rideshare service operated around 900 stations.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/number_stations.png" width="425" height="250">

Given that the data is spatial in nature, I generate some maps as well. First, I present a static map showing Bixi usage during the week ending 07-31-2024, the last week with available data. Each bubble represents a Bixi station. The bubble's color scales in accordance with the number of bikeshare trips originating from that station while the bubble's size scales with the total distance travelled by bikeshare users on trips originating from that station.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/static_map.png" width="900" height="500">

It's also informative to animate the previous static image. In doing so, it's clear to see the gradual expansion of the network into neighborhoods further from the city center, as well as increased rideshare usage, both at the extensive and intensive margins.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/gif_map.gif" width="900" height="500">

### 6. Preparing Data for Econometric Analysis
Before I can perform regressions, I make the following adjustments. First, I convert key variables for the difference-in-difference regressiont to binary type. Second, I seasonally adjust the outcome variables. Finally, I merge in additional covariates measuring daily mean temperature, precipitation, and amount of snow on ground in Montreal.

### 7. Assessing Parallel Trends
To ensure that outcomes evolved similarly prior to treatment for both treatment and control groups, and to verify that bikeshare activity at treated stations did not somehow frontrun the completion of the REV, I plot seasonally adjusted outcomes in event time. The event time variable measures time elapsed since the inauguration of the REV's Axis 1 on 11/07/2020. In an effort to better assess trends, I plot only a single month, November, for every year.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/did_combined.png">

Outcomes evolved quite similarly for both treated and control groups prior to the construction of the REV's Axis 1. At the time of treatment, usage of Bixi stations in both treated and control groups notably increased and began to grow more quickly in November 2020, following the REV's completion. Ridership increases more for treated stations than for control stations, and remains more elevated through the post-treatment period.

### 8. Model Estimation
I estimate a standard difference-in-difference model with $\text{Post}$, $\text{Treated}$, and $\text{Post} \times \text{Treated}$ terms. In addition to the key difference-in-differences regressors, I include a control for the distance between the Bixi station and the REV path as well as distance between the Bixi station and the city's central business district. Finally, I include observable weather-related covariates that I think may impact outcomes, including temperature, precipitation, and the amount of snow on the ground, as well as a full set of monthly dummies. Robust standard errors are used. The regressions are performed at the weekly-station level as outcomes are much less noisy than at a daily frequency. The most comprehensive specification is shown below:

$Y_{it} = \alpha + \beta_{1}\text{Treated}\_{i} + \beta_{2}\text{Post}\_{t} + \beta_{3}(\text{Treated}\_{i} \times \text{Post}\_{t}) + \beta_{4}\text{Distance to REV}\_{it} + \beta_{5}\text{Distance to CBD}\_{it} + \sum_{n}\beta_{n}X_t + \epsilon_{it}$

Where:
- $( Y_{it} )$ is the seasonally adjusted outcome variable for Bixi station $i$ in week $t$.
- $( \alpha )$ is the intercept.
- $\( \text{Treated}_i )$ is a binary variable indicating the treatment group (1 if treated, 0 if control).
- $\( \text{Post}_t )$ is a binary variable indicating the post-treatment period (1 if after treatment, 0 if before). The treatment date is 11/07/2020.
- $\( \text{Treated}_i \times \text{Post}_t )$ is the difference-in-difference estimator, and is calculated as the interaction of the post-treatment period and the treatment group.
- $\( \text{Distance to REV}\_{it} )$ is the distance, in hundreds of meters, between Bixi station $i$ and the nearest segment of the REV path in week $t$
- $\( \text{Distance to CBD}_{it} )$ is the distance between Bixi station $i$ in week $t$ and the central business district of Montreal.
- $\( X_t )$ is a vector of time-specific covariates, including mean temperature (degrees celcius), precipitation (mm), and snow on ground (cm), as well as monthly dummies for months 1 through 11.
- $\( \epsilon_{it} )$ is the error term. Robust standard errors are used.

Because I am concerned about heterogenous treatment effects - that is, ____ - I also choose to estimate a two-way fixed effects (TWFE) model. This model absorbs all time-invariant, station specific factors, as well as _____. 

$Y_{it} = \theta_{i} + \mu_{t} + \delta(\text{Treated}\_{i} \times \text{Post}\_{t}) + \epsilon_{it}$

Where: 


Estimation results are exported as a LaTeX file, which is then interpreted in Overleaf.

## Discussion of Results																											
Here are the regression results. For each outcome, I estimate three models. Each successive specification includes additional covariates.

![image](https://github.com/user-attachments/assets/c3be360a-e56c-4241-94b6-c616ad8d73ae)

The difference-in-difference estimator captures the treatment effect. It is found to be positive, statistically significant, and economically meainngful for all three outcomes. In particular, results indicate that, holding all else equal, stations located in close proximity to the REV see around 54 more weekly trips than those located further away. Trips originating from treated stations end 43 meters farther and last around 32 seconds longer, on average. If the research design used is convincing, then improvements in Bixi usage are a direct result of the REV's completion, rather than some confounding factor.

Distance to REV path is negatively and significantly related with number of trips taken. Parameter estimates suggest that, for every kilometer further a Bixi station is from the REV, the number of weekly trips taken falls by nearly 12, on average. Distance to the REV has a comparatively smaller effect on trip distance and trip duration. This may be explained by the fact that proximity to the REV impacts an individual's decision whether to use ridesharing, but does not necessarily affect how long they choose to rent a bike. 

Distance to the CBD is always negative and statistically significant. This is consistent with the fact that the city center is denser with amenities, has more comprehensive bike coverage, and a denser network of Bixi docking stations.

Other control variables have the expected sign, with temperature being positiely associated with ridesharing while precipitation and snow on ground are found to be negatively related with ridesharing. The addition of these controls, as well as monthly dummies, is not found to significantly impact parameter estimates. 

I find the sign, magnitude, and statistical significance of the key results to be robust to changes in the treated/control thresholds and the addition of monthly dummies.

Results indicate that the REV broadly improved ridership at stations located nearest to its path. However, without ride-level user IDs it is impossible for me to infer whether increased usage is the result of new Bixi users being induced by the REV, or simply a spatial reallocation of existing users. That is, it is possible the treatment effect is being driven by existing Bixi users choosing to rent their bikes from a Bixi station closer to the REV path after its completion, rather than new users choosing to use the bikeshare program.
