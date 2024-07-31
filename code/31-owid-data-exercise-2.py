# At Our World in Data, we often need to aggregate country-level data to broader regional aggregates, such as continents or income groups. 

# Using the data from the WHO Mortality Database, we would like you to write a python script to calculate the crude death rate from maternal conditions, per 100,000 females, for the continent of South America. 

# You should use the following resources: 
# WHO Mortality Database - Number of deaths from maternal conditions - available here 
# UN WPP - Population values (as of 1 July) - available here
# Our World in Data's definition of continents - available here 
# The aggregate should only be calculated for years when there is data available for any combination of countries such that at least 80% of the female population of South America for that year is represented in the data. 

# Please submit the values you have calculated for the years listed below, with values rounded to two decimal places. If there is not sufficient data available to calculate an aggregate for a given year, please write ‘NA’.

# Plan of action: first check the population data for South America and make sure that it is complete for the years we are interested in.



import pandas as pd
# read in df_continents from "data/owid/continents-according-to-our-world-in-data.csv"
df_continents = pd.read_csv("data/owid/continents-according-to-our-world-in-data.csv")

# filter for South America
df_continents = df_continents[df_continents["Continent"] == "South America"]

# reset index
df_continents.reset_index(drop=True, inplace=True)

# print the dataframe
print(df_continents)

# make df_continents snake case with .columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
df_continents.columns = df_continents.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
# change code to country_code
df_continents.rename(columns={"code": "country_code"}, inplace=True)

# read in data from "data/owid/WHOMortalityDatabase_Deaths_sex_age_a_country_area_year-Maternal conditions_31st March 2024 08_45.xlsx"
df_mortality = pd.read_excel("data/owid/WHOMortalityDatabase_Deaths_sex_age_a_country_area_year-Maternal conditions_31st March 2024 08_45.xlsx")

# filter the data so that "Age group code" == "Age_all" and sex == "All"
df_mortality = df_mortality[(df_mortality["Age group code"] == "Age_all") & (df_mortality["Sex"] == "All")]

df_mortality.columns
# make columns snake_case by replacing spaces with underscores and removing special characters and lowercasing
df_mortality.columns = df_mortality.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()

# filter for South America by checking if the country code is in df_continents["country_code"]
df_mortality_filtered = df_mortality[df_mortality["country_code"].isin(df_continents["country_code"])]

# write df_mortality_filtered to "data/owid/WHO_mortality_filtered.csv"
df_mortality_filtered.to_csv("data/owid/WHO_mortality_filtered.csv", index=False)

# check which values of country_code are missing from df_mortality_filtered that were in df_continents
missing_country_codes = df_continents[~df_continents["country_code"].isin(df_mortality_filtered["country_code"])]

# South Georgia and the South Sandwich Islands are unpopulated, so we can ignore them


# filter df_mortality_filtered for years 1970, 1979, 1986, 2011, 2017
years = [1970, 1979, 1986, 2011, 2017]
df_mortality_filtered_years = df_mortality_filtered[df_mortality_filtered["year"].isin(years)]

df_mortality_filtered_years.to_csv("data/owid/WHO_mortality_filtered_years.csv", index=False)

df_mortality_filtered_years.columns

# select columns country_code, country_name, year, number
df_mortality_filtered_years = df_mortality_filtered_years[["country_code", "country_name", "year", "number"]]

# rename number to maternal_deaths
df_mortality_filtered_years.rename(columns={"number": "maternal_deaths"}, inplace=True)

# make a heatmap to show which years have data for which countries
import seaborn as sns
import matplotlib.pyplot as plt

# pivot the data so that the columns are the years, the index is the country code, and the values are the number of deaths
df_mortality_filtered_years_pivot = df_mortality_filtered_years.pivot(index="country_code", columns="year", values="number")

# fill in missing values with 0
# df_mortality_filtered_years_pivot.fillna(1000, inplace=True)

# make a heatmap
plt.figure(figsize=(10, 10))

sns.heatmap(df_mortality_filtered_years_pivot, cmap="Blues", annot=True, fmt=".0f")

plt.title("Number of deaths from maternal conditions by country and year")

plt.savefig("data/owid/heatmap_deaths_by_country_and_year.png")







# Now get the data for population from data/owid/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx
df_population = pd.read_excel("data/owid/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx", skiprows=16)

df_population.columns

# replace column names with snake case
df_population.columns = df_population.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()

df_population.columns
# rename region,_subregion,_country_or_area_* to region_subregion_country_or_area
df_population.rename(columns={"region,_subregion,_country_or_area_*": "region_subregion_country_or_area"}, inplace=True)
# rename female_population,_as_of_1_july_thousands to female_population
df_population.rename(columns={"female_population,_as_of_1_july_thousands": "female_population"}, inplace=True)
# rename iso3_alphacode to country_code
df_population.rename(columns={"iso3_alphacode": "country_code"}, inplace=True)

# select the columns we are interested in: iso3_alphacode, year, region_subregion_country_or_area and population
df_population = df_population[["country_code", "year", "region_subregion_country_or_area", "female_population"]]

# filter for South America by checking if the country code is in df_continents["country_code"]
df_population_filtered = df_population[df_population["country_code"].isin(df_continents["country_code"])]

# check which values of country_code are missing from df_population_filtered that were in df_continents
missing_country_codes = df_continents[~df_continents["country_code"].isin(df_population_filtered["country_code"])]

# filter for years 1970, 1979, 1986, 2011, 2017
df_population_filtered_years = df_population_filtered[df_population_filtered["year"].isin(years)]

# write df_population_filtered_years to "data/owid/filtered_female_population_years.csv"
df_population_filtered_years.to_csv("data/owid/filtered_female_population_years.csv", index=False)

df_population_filtered_years


# create a new dataframe called "df_merged" by merging df_mortality_filtered_years and df_population_filtered_years on "country_code" and "year". I want you to keep all of the rows of df_population_filtered_years
df_merged = pd.merge(df_mortality_filtered_years, df_population_filtered_years, on=["country_code", "year"], how="right")

# drop region_subregion_country_or_area column
df_merged.drop(columns="region_subregion_country_or_area", inplace=True)

# save to "data/owid/merged_mortality_population.csv"
df_merged.to_csv("data/owid/merged_mortality_population.csv", index=False)



# use df_population_filtered_years to draw a stacked bar chart of population by country and year
df_population_filtered_years_pivot = df_population_filtered_years.pivot(index="country_code", columns="year", values=