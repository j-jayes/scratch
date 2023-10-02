import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dash_table

# Load the JSON file into a Pandas DataFrame
df = pd.read_json("data/document_links_1.json")

# df = df.head(1000)

# Remove rows with NaN values in the 'Country' column
df = df.dropna(subset=['Country'])

# Get a list of all the unique countries
countries = df['Country'].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': i, 'value': i} for i in countries],
        value='Algeria'
    ),
    dbc.Table(id='data-table')
])

@app.callback(
    Output('data-table', 'children'),
    [Input('country-dropdown', 'value')]
)
def update_table(country):
    # Filter the DataFrame based on the selected country
    filtered_df = df[df['Country'] == country]

    # Ensure 'Document type' contains only strings, not lists
    filtered_df['Document type'] = filtered_df['Document type'].apply(lambda x: x[0] if isinstance(x, list) else x)

    # Pivot the DataFrame to create the desired table
    table_df = pd.pivot_table(filtered_df, values='name', index='Document type',
                              columns='Year', aggfunc='count', fill_value=0)
    
    # Reset the index to allow 'Document type' to become a column in the DataTable
    table_df.reset_index(inplace=True)

    # Flatten multi-index columns
    table_df.columns = [' '.join(col).strip() if isinstance(col, tuple) else str(col) for col in table_df.columns.values]
    
    # Convert the DataFrame to a Dash DataTable
    # Convert the DataFrame to a Dash DataTable
    return dash_table.DataTable(
        id='table',
        columns=[{"name": str(i), "id": str(i)} for i in table_df.columns],
        data=table_df.to_dict('records'),
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': c,
                    'filter_query': '{{{0}}} eq 0'.format(c)},
                'backgroundColor': '#D3D3D3',
                'color': 'black'
            } for c in table_df.columns if c != 'Document type'] + 
            [{
                'if': {'column_id': c,
                    'filter_query': '{{{0}}} > 0 && {{{0}}} <= 3'.format(c)},
                'backgroundColor': '#90EE90',
                'color': 'black'
            } for c in table_df.columns if c != 'Document type'] +
            [{
                'if': {'column_id': c,
                    'filter_query': '{{{0}}} > 3'.format(c)},
                'backgroundColor': '#008000',
                'color': 'white'
            } for c in table_df.columns if c != 'Document type']
        )




if __name__ == '__main__':
    app.run_server(debug=True)
