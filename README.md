# Analysis of the REV on Bike Usage in Montreal

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I employ a difference-in-differences research design, comparing outcomes for treated Bixi stations - those located nearby to the REV paths - to those located further away. Outcomes include average weekly ridership, average trip duration, average trip distance, as well as new member uptake.

The project primilarly relies on ride-level data made freely available by Bixi for the period April 2014 - December 2024. I also use geodata from the City of Montreal and weather data from Statistics Canada.

## Context
In 2019, Valerie Plante, Mayor of Montreal and leader of Projet Montreal, announced that the city would be undertaking a project to build more, higher-quality bike infrastructure across the city, beginning in its central neighborhoods. This would include the construction of wide, protected bike lanes with few synchronized street lights to help Montrealers more comfortably and safely traverse large distances. These paths would also be prioritized for snow clearing in winter.

In particular, Projet Montreal put forward plans to build 5 such axes. 

- Axis 1: Berri-Lajeunesse-Saint-Denis: This axis is the longest in the REV network and provides North-South coverage in the center of the city. It links the boulevard Gouin with the rue Roy. The axis was inauguarateed on 11/07/2020.
- Axis 2: Viger-Saint-Antonine-Saint-Jacques: This axis serves a short East-West segment, predomianntly in the city's Ville-Marie borough. The axis was inauguarated on 03/31/2021.
- Axis 3: Souligny: This axis, running East-West between the rue Honore-Beaugrand and avenue Hector, is furthest from the city center.
- Axis 4: Peel: This axis serves a short North-South corridor on Peel, a major commercial shopping street in the city's downtown core.
- Axis 5: Bellechasse: An East-West Corridor running on Bellechase between de Gaspe and Chatelain, predominantly in the Rosemont-La Petite-Patrie borough, and intersecting with Axis 1 of the REV at Saint-Denis/Bellechasse.

In 2023, the city put forward plans to expand the network by 2027 with the eventual aim of increasing bike share to 15% in Montreal.

You can read more about the REV here.

## Outline of Code
Code for the project is written entirely in Pyhon. The code is separated into 8 sections and ran primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory.

### 1. Importing and Cleaning Data
In this section, I read and append ride-level data made available by Bixi on its [open data portal](https://bixi.com/en/open-data/). For some years, Bixi provides ride-level data by month, while in other years only a single dataset is provided. Variable names change somewhat through time. 

Rather than rely on Bixi's ___, I group Bixi stations by ID through manual validation.

### 3. Creating Outcome Variables
Here, I create three outcome variables of interest, which we'll explore in greater depth below, and use in our econometric analysis.

I remove Bixi trips with implausible distances or journey times. This removes very few trips.

### 4. Descriptive Statistics
In Figure 1, I plot average daily ridership by month, for every month over the April 2014 - December 2024 period. Clearly, there is strong seasonality in bike ridershp, with usage of Bixi peaking in summer months.
![](https://github.com/robertialenti/Bixi/raw/main/average_daily_ridership.png = 250x250)

In Figure 2, I plot average daily ridership by day of the week in 2024. In line with expectations, Friday and Saturday are the most popular days for bikesharing.

<img src="https://github.com/robertialenti/Bixi/raw/main/average_daily_ridership_dayofweek.png" width="416" height="250">

In Figure 3, I plot the number of active Bixi stations over time, only in months in which the service is operating. Note that, in the winter of 2023, Bixi piloted a project whereby it operated around 150 stations in the city's core.
![](https://github.com/robertialenti/Bixi/raw/main/number_stations.png =250x250)

In Figure 4, I present a static map showing Bixi usage during the week ending 07-31-2024, the last week with available data. Each bubble represents a Bixi station. The bubble's color scales in accordance with the number of bikeshare trips originating from that station while the bubble's size scales with the total distance travelled by bikeshare users on trips originating from that station.
![](https://github.com/robertialenti/Bixi/raw/main/static_map.png)

It's also informative to see a GIF, mapping data for each week since April 2014. In doing so, it's clear to see the gradual expansion of the network as well as the ___, both at the extensive and intensive margins.

### 5. Identifying Treated Bixi Stations
I define "treated" Bixi stations as those located within 100 meters of the REV's path and "control" stations as those located between 100 and 250 meters from the REV. These thresholds are informed both by the existing litearture. When performing regressions, I present an alternative specification where I use a continuous variable measuring distance between each Bixi station and the REV path. The use of a continuous treatment variable is sensible in instances where the effect of the treatment is not binary, but rather likely to vary in strength.

The City of Montreal provides information on all bike paths in the city. Crucially, each segment of each bike path has ____.

I calculate the distance between the Bixi station and each line segment bounding the REV.

Here is a plot showing the location of the REV's Axis 1. Bixi stations are classified as either Treated, Control, or Other, depending on their distance from the path.

![](https://github.com/robertialenti/Bixi/raw/main/axis1_map.png)

### 6. Preparing Data for Econometric Analysis

### 7. Model Estimation

### 8. Robustness
