# Analysis of REV Development on Bike Share Ridership

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I do so by employing a difference-in-differences research design, comparing outcomes for treated Bixi stations, those located nearby to the REV paths, to those located further away. Outcomes include average weekly ridership, average trip duration, average trip distance, as well as new member uptake.

The project primilarly utilises ride-level data made freely available by Bixi for the period 2014-2024. I also use geodata from the City of Montreal and weather data from Statistics Canada.

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
In this section, I read adn append ride-level data made available by Bixi on its [open data portal](https://bixi.com/en/open-data/).


### 3. Creating Outcome Variables
Here, I create three outcome variables of interest, which we'll explore in greater depth below, and use in our econometric analysis.

## 4. Descriptive Statistics
 
Here is the resulting static map. ![](https://github.com/robertialenti/Bixi/raw/main/static_map.png)
