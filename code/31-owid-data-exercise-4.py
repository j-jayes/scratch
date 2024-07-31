import pandas as pd

def read_and_process_continents_data(filepath):
    df = pd.read_csv(filepath)
    df = df[df["Continent"] == "South America"].reset_index(drop=True)
    df.columns = df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
    df.rename(columns={"code": "country_code"}, inplace=True)
    return df

def read_and_process_mortality_data(filepath, country_codes):
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
    df = pd.read_excel(filepath, skiprows=16)
    df.columns = df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "").str.replace("-", "").str.lower()
    df.rename(columns={"region,_subregion,_country_or_area_*": "region_subregion_country_or_area", "female_population,_as_of_1_july_thousands": "female_population", "iso3_alphacode": "country_code"}, inplace=True)
    df = df[["country_code", "year", "region_subregion_country_or_area", "female_population"]]
    df_filtered = df[df["country_code"].isin(country_codes)]
    years = [1970, 1979, 1986, 2011, 2017]
    df_filtered = df_filtered[df_filtered["year"].isin(years)]
    return df_filtered

def merge_mortality_and_population_data(mortality_data, population_data):
    df_merged = pd.merge(mortality_data, population_data, on=["country_code", "year"], how="right")
    df_merged.drop(columns=["region_subregion_country_or_area", "country_name"], inplace=True)
    return df_merged

def calculate_coverage_and_death_rate(df, country_codes):
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

# Main function to orchestrate the data processing workflow
def main():
    df_continents = read_and_process_continents_data("data/owid/continents-according-to-our-world-in-data.csv")
    country_codes = df_continents["country_code"].tolist()
    df_mortality = read_and_process_mortality_data("data/owid/WHOMortalityDatabase_Deaths_sex_age_a_country_area_year-Maternal conditions_31st March 2024 08_45.xlsx", country_codes)
    df_population = read_and_process_population_data("data/owid/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx", country_codes)
    df_merged = merge_mortality_and_population_data(df_mortality, df_population)
    coverage_summary = calculate_coverage_and_death_rate(df_merged, country_codes)
    print(coverage_summary)

if __name__ == "__main__":
    main()
