# Analysis of REV Development on Bike Share Ridership

This project aims to assess how the development of the Reseau Express Velo (REV) - a network of high-quality bike infrastructure in Montreal's central neighborhoods - impacted usage of the city's bikeshare program, Bixi. I do so by employing a difference-in-differences research design, comparing outcomes for treated Bixi stations, those located nearby to the REV paths, to those located further away. Outcomes include average weekly ridership, average trip duration, average trip distance, as well as new member uptake.

The project primilarly utilises ride-level data made freely available by Bixi for the period 2014-2024. I also use data from the City of Montreal and weather data from Statistics Canada.

## Context

## Outline of Code
Code for the project is written entirely in Pyhon. The code is separated into 8 sections and ran primarily on a computing cluster, given that the complete raw dataset is too large to be saved in memory.
 
Here is the resulting static map. ![](https://github.com/robertialenti/Bixi/raw/main/static_map.png)
