# Impact of the REV on Bike Share in Montreal

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I seek to estimate a causal effect by employing a difference-in-differences research design, comparing outcomes for treated Bixi stations - those located nearby to the REV paths - to those located further away. Outcomes include average weekly ridership, average trip duration, and average trip distance.

The project primilarly relies on ride-level data made freely available by Bixi for the period April 2014 - December 2024. I also use data from the City of Montreal, who has geocoded all of the city's bike paths, as well as weather data from Environment Canada.

## Context
In 2019, Valerie Plante, Mayor of Montreal and leader of Projet Montreal, announced that the city would be undertaking a project to build more, higher-quality bike infrastructure across the city, beginning in its central neighborhoods. This would include the construction of new, wide, and protected bike lanes with synchronized street lights to help Montrealers more comfortably and safely traverse larger distances. These paths would also be prioritized for snow clearing in winter, making them usable year-round.

Projet Montreal put forward plans to build 5 such axes:

- Axis 1: Berri-Lajeunesse-Saint-Denis: This axis is the longest in the REV network and provides North-South coverage in the center of the city. It links the boulevard Gouin with the rue Roy. The axis was inauguarateed on 11/07/2020.
- Axis 2: Viger-Saint-Antonine-Saint-Jacques: This axis serves a short East-West segment, predominantly in the city's Ville-Marie borough.
- Axis 3: Souligny: This axis, running East-West between the rue Honore-Beaugrand and avenue Hector, is furthest from the city center.
- Axis 4: Peel: This axis serves a short North-South corridor on Peel, a major commercial shopping street in the city's downtown core, between avenue des Pins and rue Smith.
- Axis 5: Bellechasse: An East-West Corridor running on Bellechase between de Gaspe and Chatelain, predominantly in the Rosemont-La Petite-Patrie borough, and intersecting with Axis 1 of the REV at Saint-Denis/Bellechasse.

In 2023, the city put forward plans to expand the network by 2027 with the aim of helping to increase the bike modal share to 15% in Montreal. You can read more about the REV [here](https://montreal.ca/articles/le-rev-un-reseau-express-velo-4666).

## Outline of Code
Code for the project is written entirely in Python. The code is separated into 8 sections and ran primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory.

### 1. Preliminaries
In this section, I simply import modules that I'll need to conduct the work. I take advantage of a number of widely used libraries for data science, spatial analysis, and econometrics.

### 2. Importing and Cleaning Data
In this section, I read and append ride-level data made available on Bixi's [open data portal](https://bixi.com/en/open-data/). In some years, Bixi provides ride-level data by month, while in other years all of the ridership data is included in a single dataset. Variable names change somewhat through time, as do date formats. The code handles these intertemporal inconsistencies. The dataset includes all of the approximately 62 million rides completed on Bixi bikes between April 2014 and July 2024.

Rather than rely on ____. Station names and IDs are somewhat unreliable as they ___ and can change through time. As a result, I group Bixi stations with a user-generated ID and manual validation. That is, I group stations - with similar names and ____ - to the same ID. I then merge the ride-level data to this file, assigning an ID and coordinates to every station. For each station ID, I select the modal station name. For each station ID-Date, I select the modal coordinates. Here is an example:

### 3. Creating Outcome Variables
Here, I create three outcome variables of interest: trip count, trip distance, and trip duration.

Trip count measures the number of trips by Bixi station and date.

As Bixi does not provide trip-level GPS data, which would be needed to track the precise journey undertaken by a user, I instead measure trip distance as the Haversine distance between the starting and ending station. I recognize that this is a flawed measure and a lower bar for the actual distance traversed on any given trip. To avoid measurement error, for all trips with a distance of 0 - that is, trips beginning and ending at the same docking station - I replace trip distance with a missing value. These trips will not be included in regression analysis.

Trip duration is calculated as the difference between a journey's start time and end time.

I remove Bixi trips with implausible distances or journey times to reduce the impact of outliers on parameter estimates.

### 4. Identifying Treated Bixi Stations
I define "treated" Bixi stations as those located within 100 meters of the REV path and "control" stations as those located between 100 and 300 meters from the REV. These thresholds are informed by the existing literature, which finds that up to 500 meters is a reasonable distance to walk to bikeshare stations. I select a lower threshold, in part, because of high Bixi station density in the neighborhood served by the REV's Axis 1.

Rather than consider all axes of the REV, I focus exclusively on Axis 1 because it provides the best case study for assessing the REV's impact. Other axes were rolled out in a more staggered fashion, and were subject to delays and additional works. Axis 1, on the other hand, was inaugurated in its entirety on the same day and has been subject to fewer disruptions in the years since.

The City of Montreal provides information on the location of all bike paths in the city, with each segment of each bike path geocoded. As such, there is no need for me to create geometries for all of the bike path segments. Instead, I can simply assign stations to treatment by employing the following procedure:

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

| Varaible Name | Type | Description |
| ------------- | ---- | ----------- |
| start_id | int | Unique ID for station where ride begins |
| start_date | datetime | Date and time that ride begins |
| start_name | str | Name of station where ride begins |
| start_lat | float | Latitude of station where ride begins |
| start_long | float | Longitude of station where ride begins |
| end_id | float | Longitude of station where ride ends |
| end_date | datetime | Date and time that ride ends |
| end_name | float | Longitude of station where ride ends |
| end_lat | float | Longitude of station where ride ends |
| end_long | float | Longitude of station where ride ends |
| count | int | 1 |
| distance | float | Haversine distance between start station and end station, in meters |
| duration | float | Duration between start station and end station, in minutes |
| treated | float | Treated = 1, Control = 0 |
| post | float | Post-Treatment = 1, Pre-Treatment = 0 |

I first plot average daily ridership by month, for every month over the April 2014 - July 2024 period. Clearly, there is strong seasonality in bike ridershp, with usage of Bixi peaking in summer months. I verify that daily ridership calculated from the microdata lines up with Bixi's self-reported ridership statistics.

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

Before I can perform regressions, I make the following adjustments. First, I convert key variables for the difference-in-difference regressiont to binary. Second, I seasonally adjust the outcome variables. Finally, I merge in additional covariates measuring daily mean temperature, precipitation, and amount of snow on ground in Montreal.

### 7. Assessing Parallel Trends

To ensure that outcomes evolved similarly prior to treatment for both treatment and control groups, and to verify that bikeshare activity at treated stations did not somehow frontrun the completion of the REV, I plot outcomes in event time. The event time variable measures time elapsed since the inauguration of the REV's Axis 1 on 11/07/2020. In an effort to better assess trends, I plot only a single month, November, for every year.

We see that outcomes evolved quite similarly prior to the construction of the REV's Axis 1. This gives me confidence that treated and control stations are similar, ___________. At the time of treatment, usage of Bixi stations in both treated and control groups increases and begins to grow more quickly. Outcomes improve more for treated stations than for control stations, and remain more elevated through the post-treatment period.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/did_trip_count_sa.png" width="425" height="250">

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/did_trip_distance_sa.png" width="425" height="250">

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/did_trip_duration_sa.png" width="425" height="250">

### 8. Model Estimation
I estimate a standard difference-in-difference model with \text{Post}, \text{Treatment}, and \text{Post \times Treatment} terms. In addition to the key difference-in-difference regressors, I also include a control for the distance between the Bixi station and the REV path as well as the interaction of the difference-in-difference regressor and the distance term, given that I expect the treatment effect to decline as the distance between ___ and the REV grows. I also include observable weather-related covariates that I think may impact outcomes, including temperature, precipitation, and the amount of snow on the ground, as well as a full set of monthly dummies. Robust standard errors are used. The regressions are performed at the weekly-station level as outcomes are much less noisy at a weekly level than at a daily level. The most comprehensive specification is shown below:

$Y_{it} = \alpha + \beta_{1}\text{Treated}\_{i} + \beta_{2}\text{Post}\_{t} + \beta_{3}(\text{Treated}\_{i} \times \text{Post}\_{t}) + \beta_{4}\text{Distance}\_{i} + \beta_{5}(\text{Treated}\_{i} \times \text{Post}\_{t} \times \text{Distance}\_{i}) + \sum_{n}\beta_{n}X_t + \epsilon_{it}$

Where:
- $( Y_{it} )$ is the seasonally adjusted outcome variable for Bixi station \text{i} in week \text{t}.
- $( \alpha )$ is the intercept.
- $\( \text{Treated}_i )$ is a binary variable indicating the treatment group (1 if treated, 0 if control).
- $\( \text{Post}_t )$ is a binary variable indicating the post-treatment period (1 if after treatment, 0 if before). The treatment date is 11/07/2020.
- $\( \text{Post}_t \times \text{Treated}_i )$ is the difference-in-difference estimator, and is calculated as the interaction of the post-treatment period and the treatment group.
- $\( \text{Distance}\_{i} )$ is the distance, in hundreds of meters, between Bixi station $\ i \$ and the nearest segment of the REV path.
- $\( \text{Post}_t \times \text{Treated}_i \times \text{Distance}\_{i} )$ is the interaction of distance, in hundreds of meters, and the difference-in-difference estimator.
- $\( X_t )$ is a vector of time-specific covariates, including mean temperature (degrees celcius), precipitation (mm), and snow on ground (cm), as well as monthly dummies for months 1 through 11.
- $\( \epsilon_{it} )$ is the error term. Robust standard errors are used.

Estimation results are exported as a LaTeX file, which is then interpreted in Overleaf.

## Discussion of Results	
![image](https://github.com/user-attachments/assets/5107d4d1-6b9d-4fb0-a4c6-3e5b7398e13c)


The difference-in-difference estimator captures the treatment effect. It is found to be positive, statistically significant, and economically meaingful for all three outcomes. In particular, the model indicates that stations located in close proximity to the REV see xx more monthly trips than those located further away. Trips originating from ___ are yy meters farther and zz minutes longer, on average. For comparison, the the mean number of monthly trips taken from a treated station in the pre-treatment period was ___, while the mean distance and mean duration of trips taken from these stations was yy meters and zz minutes.

Distance is negatively related with all three ridership outcomes. A coefficient estimate of -10.95 implies that, holding all else equal, for a one hundred meter increase in the distance between a Bixi station and the REV path, the number of average weekly trips falls by nearly 11. 

Other control variables have the expected sign, with temperature being positiely associated with ridesharing while precipitation and snow on ground are found to be negatively related with ridesharing.

I find the sign, magnitude, and statistical significance of the key results is robust to changes in the treated/control thresholds, the specification of monthly dummies, the omission of additional covariates, and the use of a two-way fixed effect (TWFE) model.

Without ride-level user IDs it is impossible for me to infer whether increased usage is the result of new Bixi users being induced by the REV, or simply a spatial reallocation of existing users. That is, it is possible the treatment effect is being driven by existing Bixi users choosing to rent their bikes from a Bixi station closer to the REV path after its completion, rather than new users choosing to use the bikeshare program.
