# Analysis of REV Development on Bike Share Ridership

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I employ a difference-in-differences research design, comparing outcomes for treated Bixi stations - those located nearby to the REV paths - to those located further away. Outcomes include average weekly ridership, average trip duration, average trip distance, as well as new member uptake.

The project primilarly relies on ride-level data made freely available by Bixi for the period April 2014 - December 2024. I also use geodata from the City of Montreal and weather data from Statistics Canada.

## Context
Projet Montreal - the City of Montreal's ___ - announced that it would be undertaking a project to build more, higher-quality bike infrastructure across the city, beginning in its central neighborhoods. This would include the construction of wide, protected bike lanes with few turns, and synchronized street lights to help Montrealers more comfortably and safely traverse large distances. 

In particular, Projet Montreal put forward plans to build 5 such axes. 

- Axis 1: Berri-Lajeunesse-Saint-Denis: This would serve as the longest section, and provide North-South coverage in the center of the city, ___.
- Axis 2: Viger-Saint-Antonine-Saint-Jacques:
- Axis 3: Souligny
- Axis 4: Peel
- Axxis 5: Bellechasse: An East-West Corridor running on Bellechase, predominantly in the Rosemont-La Petite Patrie borough, and intersecting with Axis 1 of the REV at 

You can read more about the REV here.

## Outline of Code
Code for the project is written entirely in Pyhon. The code is separated into 8 sections and ran primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory.

### 1. Importing and Cleaning Data
In this section, I read and append ride-level data made available by Bixi on its [open data portal](https://bixi.com/en/open-data/). For some years, Bixi provides ride-level data by month, while in other years only a single dataset is provided. Variable names change somewhat through time. 

Rather than rely on Bixi's ___, I group Bixi stations by ID through manual validation.


### 3. Creating Outcome Variables
Here, I create three outcome variables of interest, which we'll explore in greater depth below, and use in our econometric analysis.

### 4. Descriptive Statistics
In Figure 1, I plot average daily ridership by month, for every month over the Aprill 2014 - December 2024 period. Naturally, there is strong seasonality in bike ridershp.

In Figure 2, I plot average daily ridership by day of the week in 2024. In line with expectations, Friday and Saturday are the most popular days for bikesharing.

In Figure 3, I plot the number of active Bixi stations over time, only in months in which the service is operating. Note that, in the winter of 2023, Bixi piloted a project whereby it operated around 150 stations in the city's core.
 
Here is a static map showing Bixi usage in July 2024, the last week with available data. Each bubble represents a Bixi station. The bubble's color scales in accordance with the number of bikeshare trips undertaken that month, while its size scales with the total distance travelled by bikeshare users that month. 
![](https://github.com/robertialenti/Bixi/raw/main/static_map.png)

It's also informative to see a GIF, mapping data for each week since April 2014. In doing so, it's clear to see the gradual expansion of the network as well as the ___, both at the extensive and intensive margins.


### 5. Identifying Treated Bixi Stations

### 6. Preparing Data for Econometric Analysis

### 7. Model Estimation

### 8. Robustness
