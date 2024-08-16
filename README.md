# Impact of the REV on Bike Share in Montreal

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I seek to estimate a causal effect by employing a difference-in-differences research design, comparing outcomes for treated Bixi stations - those located nearby to the REV paths - to those located further away. Outcomes include average weekly ridership, average trip duration, and average trip distance.

The project primilarly relies on ride-level data made freely available by Bixi for the period April 2014 - December 2024. I also use geodata from the City of Montreal and weather data from Environment Canada.

## Context
In 2019, Valerie Plante, Mayor of Montreal and leader of Projet Montreal, announced that the city would be undertaking a project to build more, higher-quality bike infrastructure across the city, beginning in its central neighborhoods. This would include the construction of new, wider, protected bike lanes with synchronized street lights to help Montrealers more comfortably and safely traverse large distances. These paths would also be prioritized for snow clearing in winter, making them usable year-round.

Projet Montreal put forward plans to build 5 such axes:

- Axis 1: Berri-Lajeunesse-Saint-Denis: This axis is the longest in the REV network and provides North-South coverage in the center of the city. It links the boulevard Gouin with the rue Roy. The axis was inauguarateed on 11/07/2020.
- Axis 2: Viger-Saint-Antonine-Saint-Jacques: This axis serves a short East-West segment, predomianntly in the city's Ville-Marie borough. The axis was inauguarated on 03/31/2021.
- Axis 3: Souligny: This axis, running East-West between the rue Honore-Beaugrand and avenue Hector, is furthest from the city center.
- Axis 4: Peel: This axis serves a short North-South corridor on Peel, a major commercial shopping street in the city's downtown core.
- Axis 5: Bellechasse: An East-West Corridor running on Bellechase between de Gaspe and Chatelain, predominantly in the Rosemont-La Petite-Patrie borough, and intersecting with Axis 1 of the REV at Saint-Denis/Bellechasse.

In 2023, the city put forward plans to expand the network by 2027 with the aim of helping to increase the bike modal share to 15% in Montreal.

You can read more about the REV [here](https://montreal.ca/articles/le-rev-un-reseau-express-velo-4666).

## Outline of Code
Code for the project is written entirely in Python. The code is separated into 8 sections and ran primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory.

### 1. Preliminaries
In this section, I simply import modules that I'll need to conduct the work. I take advantage of a number of widely used libraries for data science, spatial analysis, and econometrics.

### 2. Importing and Cleaning Data
In this section, I read and append ride-level data made available on Bixi's [open data portal](https://bixi.com/en/open-data/). In some years, Bixi provides ride-level data by month, while in other years only a single dataset is provided. Variable names change somewhat through time. The code handles this inconsistencies.

Rather than rely on Bixi's ___, I group Bixi stations by ID through manual validation. I then merge the ride-level data to this file, assigning an ID and coordinates to every station.

For each station ID, I select the modal station name.

### 3. Creating Outcome Variables
Here, I create three outcome variables of interest, which we'll explore in greater depth below, and use in our econometric analysis.

I remove Bixi trips with implausible distances or journey times.

### 4. Identifying Treated Bixi Stations
I define "treated" Bixi stations as those located within 100 meters of the REV's path and "control" stations as those located between 100 and 250 meters from the REV. These thresholds are informed both by the existing litearture. When performing regressions, I present an alternative specification where I use a continuous variable measuring distance between each Bixi station and the REV path. The use of a continuous treatment variable is sensible in instances where the effect of the treatment is not binary, but rather likely to vary in strength.

The City of Montreal provides information on all bike paths in the city. Crucially, each segment of each bike path is geocoded.

I calculate the distance between the Bixi station and each line segment bounding the REV.

Here is a plot showing the location of the REV's Axis 1. Bixi stations are classified as either Treated, Control, or Other, depending on their distance from the path.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/axis1_map.png" width="900" height="500">

### 5. Descriptive Statistics
At this point, we have all of the variables we'll need to generate descriptive statistics and perform econometric analysis. Here is a description of the variables.
| Varaible Name | Type | Description |
| ------------- | ---- | ----------- |
| start_id | int | Unique ID for station where ride begins |
| start_date | datetime | Date and time that ride begins |
| start_name | str  | Name of station where ride begins |
| start_lat | float | Latitude of station where ride begins |
| start_long | float | Longitude of station where ride begins |
| end_id | float | Longitude of station where ride ends |
| end_date | datetime | Date and time that ride ends |
| end_name | float | Longitude of station where ride ends |
| end_lat | float | Longitude of station where ride ends |
| end_long  | float | Longitude of station where ride ends |
| count | int | 1 |
| distance | float | Haversine distance between start station and end station, in meters |
| duration | float | Duration between start station and end station, in minutes |
| treated | float | Treated = 1, Control = 0|
| post | float | Post-Treatment = 1, Pre-Treatment = 0 |

I first plot average daily ridership by month, for every month over the April 2014 - December 2024 period. Clearly, there is strong seasonality in bike ridershp, with usage of Bixi peaking in summer months. I verify that daily ridership calculated from the microdata lines up with Bixi's self-reported ridership statistics.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/average_daily_ridership.png" width="425" height="250">

Next, I plot average daily ridership by day of the week in 2024. In line with a priori expectations, Saturday and Friday are the most popular days for bikesharing.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/average_daily_ridership_dayofweek.png" width="425" height="250">

Finally, I plot the number of active Bixi stations over time, only in months in which the service is operating. Note that, in the winter of 2023, Bixi piloted a project whereby it operated around 150 stations in the city's core. In 2024, the rideshare service operated around 900 stations.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/number_stations.png" width="425" height="250">

In Figure 4, I present a static map showing Bixi usage during the week ending 07-31-2024, the last week with available data. Each bubble represents a Bixi station. The bubble's color scales in accordance with the number of bikeshare trips originating from that station while the bubble's size scales with the total distance travelled by bikeshare users on trips originating from that station.

<img src="https://github.com/robertialenti/Bixi/raw/main/figures/static_map.png" width="900" height="500">

It's also informative to animate the previous static image. In doing so, it's clear to see the gradual expansion of the network as well as the increased usage, both at the extensive and intensive margins.

### 6. Preparing Data for Econometric Analysis

Before I can perform regressions, I make the following ___. I create an event time variable, measuring number of days since the opening of Axis 1 on 11/07/2020. Next, I seasonally adjust the outcome variables by employing ___. Finally, I introduce additional covariates including daily mean temperature, precipitation, and amount of snow on ground in Montreal.

### 7. Assessing Parallel Trends

To ensure that outcomes evolved similarly prior to treatment, and to verify that rideshare users did not somehow frontrun the treatment, I plot outcomes in event time separately for treated and control groups.

### 8. Model Estimation
We begin by estimating a standard difference-in-difference model estimation, with post, treatment, and interaction terms, as well as controls. The regressions are performed at the weekly-station level as outcomes are much less noisy at a weekly level than at a daily level.

The coefficients of interest are found to be positive, statistically significant, and economically meaingful. 

We also use a two-way fixed effects 

What the regression results show is that the number, average distance, and average duration of rides taken at Bixi stations near the REV experienced a much greater increase following the path's construction than stations located further. If the identification strategy is convincing, than these parameter estimates are causal, and not simply correlative. That is, ____
