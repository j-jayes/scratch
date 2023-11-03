# Hisco to Hisclass abbreviation

## Overview

This R project aims to process historical international standard
classification of occupations (HISCO) codes to social-economic status
(hisclass) levels. The project includes transforming HISCO codes from an
Excel spreadsheet into two hisclass levels: 12-level and 7-level
classifications, and then mapping these to their respective abbreviated
titles.

## Installation

Before running the script, you need to ensure that you have R installed
on your system. The following R packages are required:

- `tidyverse`
- `devtools`
- `hisco`
- `readxl`
- `here`

You can install these packages using the following commands in your R
console:

``` r
install.packages("tidyverse")
install.packages("devtools")
install.packages("readxl")
install.packages("here")
devtools::install_github("junkka/hisco")
```

## Usage

The script can be broken down into several steps:

1.  **Setting up the environment:** Loading the necessary libraries.
2.  **Creating lookup tables:** Define mappings between HISCO codes and
    hisclass levels (both 12-level and 7-level).
3.  **Reading the data:** Import the HISCO codes from an Excel file.
4.  **Processing the data:** Apply the mappings to convert HISCO codes
    to hisclass levels and join the data with the lookup tables to get
    the desired outputs.

### Code Breakdown

- **Environment Setup:** The required libraries are loaded into the R
  environment.

- **Lookup Table Creation:** `hisclass_12_tbl` and `hisclass_7_tbl`
  tibbles are created using predefined mappings to associate numerical
  hisclass identifiers with their corresponding titles.

- **Data Reading:** HISCO codes are read from an Excel file located in
  the “data” directory relative to the project root.

- **Data Processing:** HISCO codes are converted to hisclass 12 levels
  using the `hisco_to_ses()` function. Then the data is joined with
  `hisclass_table` to populate both hisclass 12 and hisclass 7 levels
  and their corresponding titles.

## Data Files

The script assumes that there is an Excel file named
`hisco_to_hisclass.xlsx` in the `data` directory of your project. The
file should contain HISCO codes to be processed.

## Running the Script

To run the script, open the R file in your R environment and execute the
code. Ensure that your current working directory is set to the project
root and that the `data` folder with the Excel file is correctly placed
in the root.

## What will we use?

``` r
library(tidyverse)
```

    Warning: package 'tidyverse' was built under R version 4.2.3

    Warning: package 'ggplot2' was built under R version 4.2.3

    Warning: package 'tidyr' was built under R version 4.2.2

    Warning: package 'purrr' was built under R version 4.2.2

    Warning: package 'stringr' was built under R version 4.2.2

    Warning: package 'forcats' was built under R version 4.2.3

    ── Attaching core tidyverse packages ──────────────────────── tidyverse 2.0.0 ──
    ✔ dplyr     1.0.10     ✔ readr     2.1.3 
    ✔ forcats   1.0.0      ✔ stringr   1.5.0 
    ✔ ggplot2   3.4.3      ✔ tibble    3.1.8 
    ✔ lubridate 1.8.0      ✔ tidyr     1.3.0 
    ✔ purrr     1.0.1      
    ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
    ✖ dplyr::filter() masks stats::filter()
    ✖ dplyr::lag()    masks stats::lag()
    ℹ Use the conflicted package (<http://conflicted.r-lib.org/>) to force all conflicts to become errors

``` r
# Data for the first part
hisclass_12_numbers <- c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
hisclass_12_labels <- c("Higher managers", "Higher professionals", "Lower managers", 
              "Lower professionals, clerical and sales personnel",
              "Lower clerical and sales personnel", "Foremen", 
              "Medium-skilled workers", "Farmers and fishermen", 
              "Low-skilled workers", "Low-skilled farm workers", 
              "Unskilled workers", "Unskilled farm workers")

# Data for the second part
hisclass_7_numbers <- c(1, 2, 3, 4, 5, 6, 7)
hisclass_7_labels <- c("Elite", "White collar", "Foremen", 
              "Medium-skilled workers", "Farmers and fishermen", 
              "Low-skilled workers", "Unskilled workers")

# Creating the tibbles
hisclass_12_tbl <- tibble(hisclass_12 = hisclass_12_numbers, Title_hisclass_12 = hisclass_12_labels)
hisclass_7_tbl <- tibble(hisclass_7 = hisclass_7_numbers, Title_hisclass_7 = hisclass_7_labels)

hisclass_table <- hisclass_12_tbl %>%
  mutate(cross_walk = case_when(
    hisclass_12 %in% c(1, 2) ~ 1,
    hisclass_12 %in% c(3, 4, 5) ~ 2,
    hisclass_12 %in% c(6) ~ 3,
    hisclass_12 %in% c(7) ~ 4,
    hisclass_12 %in% c(8) ~ 5,
    hisclass_12 %in% c(9, 10) ~ 6,
    hisclass_12 %in% c(11, 12) ~ 7,
  )) %>% 
  inner_join(hisclass_7_tbl, by = c("cross_walk" = "hisclass_7")) %>% 
  rename("hisclass_7" = "cross_walk")
```

## Getting Hisclass from HISCO

``` r
library(devtools)
```

    Loading required package: usethis

    Warning: package 'usethis' was built under R version 4.2.2

``` r
install_github("junkka/hisco")
```

    WARNING: Rtools 3.5 found on the path at C:/Rtools is not compatible with R 4.2.1.

    Please download and install Rtools 4.2 from https://cran.r-project.org/bin/windows/Rtools/ or https://www.r-project.org/nosvn/winutf8/ucrt3/, remove the incompatible version from your PATH.

    Skipping install of 'hisco' from a github remote, the SHA1 (87fbc019) has not changed since last install.
      Use `force = TRUE` to force installation

``` r
library(hisco)
```

## Read in data from excel

``` r
library(here)
```

    Warning: package 'here' was built under R version 4.2.3

    here() starts at C:/Users/User/Documents/Recon/scratch

``` r
df <- readxl::read_excel(here("data", "hisco_to_hisclass.xlsx"))
```

## Process

What we want to do is create two more columns - one for the hisclass at
12 level, and one for the the hisclass at 7 level.

To do this, we need to use the `hisco_to_ses(hisco_codes, "hisclass")`
function.

``` r
df %>% 
  mutate(hisclass_12 = hisco_to_ses(hisco, "hisclass")) %>% 
  inner_join(hisclass_table)
```

    Warning: `select_()` was deprecated in dplyr 0.7.0.
    ℹ Please use `select()` instead.
    ℹ The deprecated feature was likely used in the dplyr package.
      Please report the issue at <https://github.com/tidyverse/dplyr/issues>.

    Joining, by = "hisclass_12"

    # A tibble: 9 × 6
         id hisco hisclass_12 Title_hisclass_12          hisclass_7 Title_hisclass_7
      <dbl> <dbl>       <dbl> <chr>                           <dbl> <chr>           
    1     1 22670           6 Foremen                             3 Foremen         
    2     2 22675           6 Foremen                             3 Foremen         
    3     3 22680           6 Foremen                             3 Foremen         
    4     4 22690           6 Foremen                             3 Foremen         
    5     5 30000           5 Lower clerical and sales …          2 White collar    
    6     6 31000           5 Lower clerical and sales …          2 White collar    
    7     7 31020           4 Lower professionals, cler…          2 White collar    
    8     8 31030           2 Higher professionals                1 Elite           
    9     9 31040           4 Lower professionals, cler…          2 White collar    
