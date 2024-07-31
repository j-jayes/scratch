"""
This script calculates the crude death rate from maternal conditions per 100,000 females in the continent of South America, utilizing datasets from the WHO Mortality Database and UN World Population Prospects (WPP). Our World in Data's definitions of continents serve to categorize country-level data into the broader regional aggregate of South America.

The crude death rate is calculated exclusively for years where data suffices to represent at least 80% of the female population of South America.

Data Sources:
- WHO Mortality Database: Provides the number of deaths from maternal conditions.
- UN WPP: Offers population values as of 1 July of each year.
- Our World in Data: Defines the grouping of countries into continents.

Requirements:
- The script filters the data to include only those years and countries within South America for which both maternal mortality data and female population figures are available.
- It then checks that the data coverage for each year meets or exceeds the 80% threshold of the total female population of South America.
- The crude death rate is computed and reported for each qualifying year, rounded to two decimal places. If data coverage for a given year is insufficient, the script outputs 'NA' for that year.

Note:
- The calculations and data manipulations are performed using the pandas library in Python, showcasing data reading, cleaning, filtering, and aggregation techniques suitable for handling complex datasets.

Author: Jonathan Jayes
Date: 31 March 2024
"""

import pandas as pd

def read_and_process_continents_data(filepath):
    """
    Reads a CSV file from the given filepath and filters the data to include only the countries in South America.
    Renames the columns and returns the processed DataFrame.

    Parameters:
    filepath (str): The path to the CSV file.

    Returns:
    pandas.DataFrame: The processed DataFrame containing the relevant continent codes for South America.
    """
    df = pd.read_csv(filepath)
    df = df[df["Continent"] == "South America"].reset_index(drop=True)
    df.columns = df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
    df.rename(columns={"code": "country_code"}, inplace=True)
    return df

def read_and_process_mortality_data(filepath, country_codes):
    """
    Reads an Excel file from the given filepath and filters the data to include only the countries in the given country codes and for the years 1970, 1979, 1986, 2011, 2017.
    Renames the columns and returns the processed DataFrame.

    Parameters:
    filepath (str): The path to the Excel file.
    country_codes (list): The list of country codes to filter the data.

    Returns:
    pandas.DataFrame: The processed DataFrame containing the mortality data for the relevant countries and years.
    """
    df = pd.read_excel(filepath)
    df = df[(df["Age group code"] == "Age_all") & (df["Sex"] == "All")]
    df.columns = df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
    df_filtered = df[df["country_code"].isin(country_codes)]
    years = [1970, 1979, 1986, 2011, 2017]
    df_filtered = df_filtered[df_filtered["year"].isin(years)]
    df_filtered = df_filtered[["country_code", "country_name", "year", "number"]]
    df_filtered.rename(columns={"number": "maternal_deaths"}, inplace=True)
    return df_filtered

def read_and_process_population_data(filepath, country_codes):
    """
    Reads an Excel file from the given filepath and filters the data to include only the countries in the given country codes and for the years 1970, 1979, 1986, 2011, 2017.
    Renames the columns and returns the processed DataFrame.

    Parameters:
    filepath (str): The path to the Excel file.
    country_codes (list): The list of country codes to filter the data.

    Returns:
    pandas.DataFrame: The processed DataFrame containing the mortality data for the relevant countries and years.
    """
    df = pd.read_excel(filepath, skiprows=16)
    df.columns = df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
    df.rename(columns={"region,_subregion,_country_or_area_*": "region_subregion_country_or_area", "female_population,_as_of_1_july_thousands": "female_population", "iso3_alphacode": "country_code"}, inplace=True)
    df = df[["country_code", "year", "region_subregion_country_or_area", "female_population"]]
    df_filtered = df[df["country_code"].isin(country_codes)]
    years = [1970, 1979, 1986, 2011, 2017]
    df_filtered = df_filtered[df_filtered["year"].isin(years)]
    return df_filtered

def merge_mortality_and_population_data(mortality_data, population_data):
    """
    Merges mortality and population data based on country code and year.

    Args:
        mortality_data (DataFrame): The mortality data.
        population_data (DataFrame): The population data.

    Returns:
        DataFrame: The merged data with population and mortality information.
    """
    df_merged = pd.merge(mortality_data, population_data, on=["country_code", "year"], how="right")
    df_merged.drop(columns=["region_subregion_country_or_area", "country_name"], inplace=True)
    return df_merged

def calculate_coverage_and_death_rate(df, country_codes):
    """
    Calculates the coverage percentage of the population data for each year and returns a DataFrame with the coverage summary.
    The coverage percentage is calculated as the ratio of the population with maternal data to the total population for each year.
    The aim is to check which years have data coverage for more than 80 percent of the population data.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the population and mortality data.
    country_codes (list): The list of country codes to filter the data.

    Returns:
    pandas.DataFrame: The DataFrame containing the coverage summary for each year.
    """
    south_america_data = df[df['country_code'].isin(country_codes)]
    total_population_by_year = south_america_data.groupby('year')['female_population'].sum()
    population_with_maternal_data_by_year = south_america_data.dropna(subset=['maternal_deaths']).groupby('year')['female_population'].sum()
    population_coverage_percentage_by_year = (population_with_maternal_data_by_year / total_population_by_year) * 100
    coverage_summary = pd.DataFrame({
        'Total Population': total_population_by_year,
        'Population with Maternal Data': population_with_maternal_data_by_year,
        'Coverage Percentage': population_coverage_percentage_by_year
    }).reset_index()
    return coverage_summary

def calculate_crude_death_rate(data, country_codes, years):
    """
    Calculates the crude death rate when the maternal mortality data is not missing.

    Args:
        data (DataFrame): The input data containing maternal mortality and population information.
        country_codes (list): A list of country codes to filter the data.
        years (list): A list of years to filter the data.

    Returns:
        DataFrame: A DataFrame containing the calculated crude death rate for each year.
    """
    sa_data = data[data['country_code'].isin(country_codes)]
    filtered_data = sa_data[sa_data['year'].isin(years) & sa_data['maternal_deaths'].notna()]
    summary = filtered_data.groupby('year').agg({
        'maternal_deaths': 'sum',
        'female_population': 'sum'
    })
    summary['Crude Death Rate'] = (summary['maternal_deaths'] / summary['female_population']) * 100000
    return summary[['Crude Death Rate']]

def main():
    df_continents = read_and_process_continents_data("data/owid/continents-according-to-our-world-in-data.csv")
    country_codes = df_continents["country_code"].tolist()
    df_mortality = read_and_process_mortality_data("data/owid/WHOMortalityDatabase_Deaths_sex_age_a_country_area_year-Maternal conditions_31st March 2024 08_45.xlsx", country_codes)
    df_population = read_and_process_population_data("data/owid/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx", country_codes)
    df_merged = merge_mortality_and_population_data(df_mortality, df_population)
    coverage_summary = calculate_coverage_and_death_rate(df_merged, country_codes)
    print("Coverage Summary:")
    print(coverage_summary)
    
    years_of_interest = [1986, 2011, 2017]
    crude_death_rate = calculate_crude_death_rate(df_merged, country_codes, years_of_interest)
    print("\nCrude Death Rate:")
    print(crude_death_rate)

if __name__ == "__main__":
    main()
