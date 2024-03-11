import pandas as pd
# read the file, skipping the data information at the top
df = pd.read_excel("data/owid/WPP2022_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx", sheet_name="Estimates", skiprows=16)

df.columns = df.columns.str.replace("*", "").str.replace(",", "").str.strip().str.lower().str.replace(" ", "_")

df.rename(columns={"region_subregion_country_or_area": "country"}, inplace=True)

# filter dataframe for USA and UGA
df_usa_uga = df[(df["iso3_alpha-code"] == "USA") | (df["iso3_alpha-code"] == "UGA")]

# filter for year 2019
df_usa_uga_2019 = df_usa_uga[df_usa_uga["year"] == 2019]

# pivot data from wide to long format from 12th column onwards
id_vars = df_usa_uga_2019.columns[:11]

# Use melt function to pivot the DataFrame
df_usa_uga_2019_long = df_usa_uga_2019.melt(id_vars=id_vars, var_name='age_group', value_name='population')

# rename the column age_group to age_group_label
df_usa_uga_2019_long.rename(columns={'age_group': 'age_group_label'}, inplace=True)

# select columns country, age_group_index, and population
df_usa_uga_2019_long = df_usa_uga_2019_long[['country', 'age_group_label', 'population']]

# change population from population in thousands to population
df_usa_uga_2019_long['population'] = df_usa_uga_2019_long['population'] * 1000

# pivot wider so that the columns that remain are age_group_label and population_uga and population_usa
df_usa_uga_2019_long = df_usa_uga_2019_long.pivot(index='age_group_label', columns='country', values='population').reset_index()

# rename the columns from United States of America to population_usa and Uganda to population_uga
df_usa_uga_2019_long.rename(columns={'United States of America': 'population_usa', 'Uganda': 'population_uga'}, inplace=True)


df_usa_uga_2019_long.loc[
    df_usa_uga_2019_long['age_group_label'].isin(['85-89', '90-94', '95-99', '100+']), 'age_group_label'
] = '85+'

# Aggregate the values
df_usa_uga_2019_long = df_usa_uga_2019_long.groupby('age_group_label').sum().reset_index()


# create a mapping from age_group to an index
age_group_mapping = {
    '0-4': 0,
    '5-9': 1,
    '10-14': 2,
    '15-19': 3,
    '20-24': 4,
    '25-29': 5,
    '30-34': 6,
    '35-39': 7,
    '40-44': 8,
    '45-49': 9,
    '50-54': 10,
    '55-59': 11,
    '60-64': 12,
    '65-69': 13,
    '70-74': 14,
    '75-79': 15,
    '80-84': 16,
    '85+': 17
}

# create a new column age_group_index
df_usa_uga_2019_long['age_group_index'] = df_usa_uga_2019_long['age_group_label'].map(age_group_mapping)

# sort the data by age_group_index
df_usa_uga_2019_long.sort_values(by='age_group_index', inplace=True)

df_usa_uga_2019_long





age_specific_death_rates = {
    'Age group (years)': ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+'],
    'Death rate, United States, 2019': [0.04, 0.02, 0.02, 0.02, 0.06, 0.11, 0.29, 0.56, 1.42, 4.00, 14.13, 37.22, 66.48, 108.66, 213.10, 333.06, 491.10, 894.45],
    'Death rate, Uganda, 2019': [0.40, 0.17, 0.07, 0.23, 0.38, 0.40, 0.75, 1.11, 2.04, 5.51, 13.26, 33.25, 69.62, 120.78, 229.88, 341.06, 529.31, 710.40]
}

df_age_specific_death_rates = pd.DataFrame(age_specific_death_rates)

# create a column called age_group_index equal to the index
df_age_specific_death_rates['age_group_index'] = df_age_specific_death_rates.index

# rename Age group (years) to age_group_label
df_age_specific_death_rates.rename(columns={'Age group (years)': 'age_group_label'}, inplace=True)

# rename the columns Death rate, United States, 2019 and Death rate, Uganda, 2019 to United States of America and Uganda
df_age_specific_death_rates.rename(columns={'Death rate, United States, 2019': 'asdr_usa', 'Death rate, Uganda, 2019': 'asdr_uga'}, inplace=True)


# merge the dataframes on age_group_label AND age_group_index
merged_data = pd.merge(df_usa_uga_2019_long, df_age_specific_death_rates, on=['age_group_label', 'age_group_index'])


who_world_standard = {
    'age_group_label': ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+'],
    'who_world_standard_pop': [8.86, 8.69, 8.60, 8.47, 8.22, 7.93, 7.61, 7.15, 6.59, 6.04, 5.37, 4.55, 3.72, 2.96, 2.21, 1.52, 0.91, 0.63]
}

df_who_world_standard = pd.DataFrame(who_world_standard)

# merge the dataframes on age_group_label
merged_data = pd.merge(merged_data, df_who_world_standard, on='age_group_label')

merged_data.columns


# Calculating Crude Death Rate
total_deaths_us = (
    merged_data['asdr_usa'] * merged_data['population_usa'] / 100000
).sum()

total_population_us = merged_data['population_usa'].sum()
crude_death_rate_us = (total_deaths_us / total_population_us) * 100000

total_deaths_uganda = (
    merged_data['asdr_uga'] * merged_data['population_uga'] / 100000
).sum()
total_population_uganda = merged_data['population_uga'].sum()
crude_death_rate_uganda = (
                            total_deaths_uganda / total_population_uganda
                          ) * 100000

# Calculating Age-Standardized Death Rate
standard_population_total = merged_data['who_world_standard_pop'].sum()

standardized_death_rate_us = (
    (
            merged_data['asdr_usa'] * merged_data['who_world_standard_pop']
    ).sum() / standard_population_total
)
standardized_death_rate_uganda = (
    (
            merged_data['asdr_uga'] * merged_data['who_world_standard_pop']
    ).sum() / standard_population_total
)

# round to one decimal place
crude_death_rate_us = round(crude_death_rate_us, 1)
crude_death_rate_uganda = round(crude_death_rate_uganda, 1)
standardized_death_rate_us = round(standardized_death_rate_us, 1)
standardized_death_rate_uganda = round(standardized_death_rate_uganda, 1)

# make a table with the results
results = {
    'country': ['United States of America', 'Uganda'],
    'crude_death_rate': [crude_death_rate_us, crude_death_rate_uganda],
    'standardized_death_rate': [standardized_death_rate_us, standardized_death_rate_uganda]
}

df_results = pd.DataFrame(results)

df_results