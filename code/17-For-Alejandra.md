For Alejandra
================

## Purpose

Regex test for removing the spaces between the numbers. The regex
`"(\\d) (\\d)"` looks for a number (`\\d`) followed by a space (``) and
another number (`\\d`), and replaces it with the first number (`\\1`)
followed by the second number (`\\2`).

``` r
library(tidyverse)

tbl <- tribble(
  ~input, ~desired_output,
  "1 234",   1234,
  # Here we have a leading space
  " 456",    456,
  "78 910",  78910,
  "12 345 678", 12345678
)

tbl %>% 
  mutate(output = str_replace_all(input, "(\\d) (\\d)", "\\1\\2"),
         output = str_squish(output),
         output = parse_number(output)) %>% 
  mutate(correct = identical(desired_output, output))
```

    # A tibble: 4 × 4
      input        desired_output   output correct
      <chr>                 <dbl>    <dbl> <lgl>  
    1 "1 234"                1234     1234 TRUE   
    2 " 456"                  456      456 TRUE   
    3 "78 910"              78910    78910 TRUE   
    4 "12 345 678"       12345678 12345678 TRUE   
