# Literacy rates among adults - Data package

This data package contains the data that powers the chart ["Literacy rates among adults"](https://ourworldindata.org/grapher/literacy?v=1&csvType=full&useColumnShortNames=false&age_group=adult&sex=both) on the Our World in Data website. It was downloaded on February 22, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Literacy rate among adults aged 15+
Share of the population aged 15 years and older who can read and write.
Last updated: May 1, 2025  
Next update: May 2026  
Date range: 1970–2023  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
UNESCO Institute for Statistics (2025) – with minor processing by Our World in Data

#### Full citation
UNESCO Institute for Statistics (2025) – with minor processing by Our World in Data. “Literacy rate among adults aged 15+” [dataset]. UNESCO Institute for Statistics, “UNESCO Institute for Statistics (UIS) - Education” [original data].
Source: UNESCO Institute for Statistics (2025) – with minor processing by Our World In Data

### What you should know about this data
* Literacy is a foundational skill. Children need to learn to read so that they can read to learn. When we fail to teach this foundational skill, people have fewer opportunities to lead the rich and interesting lives that a good education offers.
* This indicator measures the percentage of people who can read and write a simple sentence about their daily life. It’s calculated as the number of people in a given age group who report being able to do so, divided by the total number in that group. UNESCO tracks this across different generations – including youth, adults, and older people – to show how literacy is changing over time.
* Most of the data comes from national surveys. In some countries, people are asked directly whether they can read and write; in others, they take a short test.
* In many high–income countries, literacy rates reached near–universal levels by the late 20th century. As a result, regular tracking has been scaled back, since changes are small and less relevant for education policy.
* This data tells us whether someone can read and write at a very basic level – for example, reading simple sentences or writing their name. But it doesn’t tell us whether they can use reading and writing in everyday life, like filling out a job application or reading health instructions. Those kinds of skills take more years of schooling and are much harder to measure, especially when comparing across countries and over time.

### How is this data described by its producer - UNESCO Institute for Statistics (2025)?
Percentage of the population age 15 and above who can, with understanding, read and write a short, simple statement on their everyday life. Generally, ‘literacy’ also encompasses ‘numeracy’, the ability to make simple arithmetic calculations. This indicator is calculated by dividing the number of literates aged 15 years and over by the corresponding age group population and multiplying the result by 100.

### Source

#### UNESCO Institute for Statistics – UNESCO Institute for Statistics (UIS) - Education
Retrieved on: 2025-05-01  
Retrieved from: https://databrowser.uis.unesco.org/resources/bulk  


    