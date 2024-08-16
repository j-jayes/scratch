import streamlit as st
import pandas as pd

# Load the data
file_path = 'data/cabri_document_data_matched_to_URLs.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Streamlit app
st.title("Document Count per Year, Type, and Domain")

# Dropdown to select country, sorted alphabetically
country = st.selectbox("Select a Country", sorted(df['country'].unique()))

# Filter the dataframe based on the selected country
filtered_df = df[df['country'] == country]

# New section: Summary of Document Types and Years
# Group by document_type_short and aggregate to find counts and most recent year
summary_df = filtered_df.groupby('document_type_short').agg(
    Document_Count=('year', 'size'),
    Most_Recent_Year=('year', 'max')
).reset_index()

# Display the summary table
st.subheader(f"Summary for {country}")
st.table(summary_df)

# New table: Count of domain by country
domain_count = filtered_df.groupby('domain').size().reset_index(name='Domain Count')
# sort by domain count
domain_count = domain_count.sort_values(by='Domain Count', ascending=False)
st.subheader(f"Domain Count for {country}")
st.table(domain_count)

# Add a line to break up the sections
st.markdown("---")

# Dropdown to select document type, sorted alphabetically
document_type = st.selectbox("Select a Document Type", sorted(filtered_df['document_type_short'].unique()))

# Filter further based on the selected document type
final_df = filtered_df[filtered_df['document_type_short'] == document_type]

# Count the number of documents per year
document_count = final_df.groupby('year').size().reset_index(name='Document Count')

# Count the number of documents per domain
domain_count = final_df.groupby('domain').size().reset_index(name='Domain Count')

# Add domain to the final table
final_df['domain'] = final_df['domain']

# Add a column for the image of the first page
base_url = "https://raw.githubusercontent.com/j-jayes/scratch/main/data/cabri_page_pictures/"
final_df['Image'] = final_df['download_link'].apply(
    lambda x: f'<img src="{base_url}{x.replace("/uploads/bia/", "").replace(".pdf", ".png")}" width="150">'
)

# Modify the Document URL to say "CABRI link"
final_df['Document URL'] = final_df['url'].apply(lambda x: f'<a href="{x}">CABRI link</a>')

# Display the document count
st.subheader(f"Document Count per Year for {country} - {document_type}")
st.table(document_count)

# Display the domain count
st.subheader(f"Domain Count for {country} - {document_type}")
st.table(domain_count)

# Display the table of documents with hyperlinks and images
st.subheader(f"Documents for {country} - {document_type}")
st.write(final_df[['title', 'year', 'domain', 'Image', 'Document URL']].to_html(escape=False), unsafe_allow_html=True)

# Apply custom CSS to fill the screen width
st.markdown(
    """
    <style>
    table {
        width: 100%;
        table-layout: fixed;
    }
    th, td {
        padding: 8px;
        text-align: left;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True
)
