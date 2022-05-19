import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --------------------------------
# Base Functions
# --------------------------------
# Function to Load csv
def load_csv(file):
    csv = pd.read_csv(file, sep=",")
    return csv

# Load in List of ISO 3166 country code Infomation
df_continents = load_csv("./data/additional/continents2.csv")
sub_regions = [
    "Latin America and the Caribbean",
    "Sub-Saharan Africa"
]
african_regions = [
    "Eastern Africa",
    "Middle Africa",
    "Southern Africa",
    "Western Africa"
]

# For Plotting Plot 1
def plot_1(df):
    df_m_deaths_joined = df.merge(df_continents,how="left",left_on="Code",right_on="alpha-3")
    df_m_deaths_joined_grouped = df_m_deaths_joined.groupby(["Year","sub-region"])["Deaths - Malaria - Sex: Both - Age: Age-standardized (Rate) (per 100,000 people)"]
    df_plot = pd.DataFrame(df_m_deaths_joined_grouped.mean()) \
        .reset_index() \
        .rename({"Deaths - Malaria - Sex: Both - Age: Age-standardized (Rate) (per 100,000 people)":"average"},axis='columns') \

    fig = px.line(df_plot, x="Year", y="average",
        color="sub-region",
        title='Average Malaria Deaths by Region from Years ' + str(df_plot["Year"].min()) + ' to ' + str(df_plot["Year"].max()),
        labels={
            'sub-region':"Sub-region",
            'average':'Average Malaria Deaths (per 1,000 population at risk)'
        },
        hover_data={
            'average':':.2f'
        }
    )
    fig.update_traces(mode="markers+lines")
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            )
        )
    )
    return fig,df_plot

def plot_2(df,region = "Sub-Saharan Africa"):
    df_m_inc_joined = df.merge(df_continents,how="left",left_on="Code",right_on="alpha-3")
    df_m_inc_joined[["alpha-3","region","sub-region"]] = df_m_inc_joined[["alpha-3","region","sub-region"]].fillna("Others") #Remove null rows
    df_plot = df_m_inc_joined[(df_m_inc_joined["sub-region"] == region)] \
    .rename({"Incidence of malaria (per 1,000 population at risk) (per 1,000 population at risk)":"incidence"},axis='columns')

    # To average the incendence of Malaria by "Intermediate-region"
    df_plot = df_plot.groupby(["intermediate-region","Year"])["incidence"].mean()
    df_plot = df_plot.reset_index()

    fig = px.line(df_plot, x="Year", y="incidence",
        color="intermediate-region",
        title='Incidence of Malaria by Region in '+ region +' from Years ' + str(df_plot["Year"].min()) + ' to ' + str(df_plot["Year"].max()),
        labels={'incidence':'Average Incidence of malaria (per 1,000 population at risk)'},
        hover_data={
        'incidence':':.2f'
        }
    )
    fig.update_traces(mode="markers+lines")
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)

    return fig,df_plot

def plot_3(df,region = "Western Africa"): # Default to Western Africa
    df_m_deaths_age_joined = df.merge(df_continents,how="left",left_on="code",right_on="alpha-3")
    df_m_deaths_age_joined[["alpha-3","region","sub-region"]] = df_m_deaths_age_joined[["alpha-3","region","sub-region"]].fillna("Others")
    df_plot = df_m_deaths_age_joined[df_m_deaths_age_joined["intermediate-region"]==region]
    df_plot = df_plot.groupby(["year","age_group"])["deaths"].mean().reset_index()

    fig = px.line(df_plot, x="year", y="deaths",
        color="age_group",
        title='Average Malaria Deaths by Age Group in '+region+' from Years ' + str(df_plot["year"].min()) + ' to ' + str(df_plot["year"].max()),
        labels={'deaths':'Average Deaths'},
        hover_data={
        'deaths':':,.2f'
        }
    )
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(df_plot["year"].unique()),
            ticktext = list(range(df_plot["year"].min(),df_plot["year"].max()+1,1))
        )
    )
    fig.update_traces(mode="markers+lines")
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            )
        )
    )
    return fig,df_plot

# --------------------------------

# --------------------------------
# Sidebar - Allows user to Upload data
# --------------------------------
st.sidebar.write("Sample Data: [Github Link](https://github.com/rfordatascience/tidytuesday/tree/master/data/2018/2018-11-13)")

with st.sidebar.header('File 1. Upload your "Malaria Deaths by Country for all ages across the world and time" data'):
    uploaded_file1 = st.sidebar.file_uploader("Upload your input file", type=["txt"],key='upload_df_m_deaths')
with st.sidebar.header('File 2. Upload your "Malaria Incidence by Country for all ages across the world across time" data'):
    uploaded_file2 = st.sidebar.file_uploader("Upload your input file", type=["txt"],key='upload_df_m_inc')
with st.sidebar.header('File 3. Upload your "Malaria deaths by age group across the world and time" data'):
    uploaded_file3 = st.sidebar.file_uploader("Upload your input file", type=["txt"],key='upload_df_m_age')
# --------------------------------

# --------------------------------
# 1) Web App Title
# --------------------------------
st.title('*_Data Visualisation on Malaria in the World_*')

# --------------------------------
# Plot World Map
# --------------------------------
df_m_deaths = load_csv("./data/malaria_deaths.txt")
df_m_deaths_joined = df_m_deaths.merge(df_continents,how="left",left_on="Code",right_on="alpha-3")
df_m_deaths_joined_grouped_region = df_m_deaths_joined.groupby(["region","Code","Entity"])["Deaths - Malaria - Sex: Both - Age: Age-standardized (Rate) (per 100,000 people)"]
df_plot_overview = pd.DataFrame(df_m_deaths_joined_grouped_region.mean()) \
    .reset_index() \
    .rename({"Deaths - Malaria - Sex: Both - Age: Age-standardized (Rate) (per 100,000 people)":"average"},axis='columns')
# Filter only locations that are above the median value.
median_death = df_plot_overview["average"].median()
df_plot_overview = df_plot_overview[df_plot_overview["average"]>median_death]

fig = px.scatter_geo(df_plot_overview, 
                        title="Overview: Average Malaria Deaths (per 1,000 population at risk) from Years " + str(df_m_deaths_joined["Year"].min()) + " to " + str(df_m_deaths_joined["Year"].max()),
                        locations="Code",
                        size="average",
                        locationmode = "ISO-3",
                        color = "average",
                        custom_data=[
                              'Entity',
                              'region'
                        ],
                        hover_data = {'average':':.2f'},
                        hover_name = "Entity",
                        labels={
                              'average':'Average Malaria Deaths'
                        },
                        projection = 'natural earth'
                     )
fig.update_layout(
    margin=dict(l=0, r=0, t=70, b=0),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('''
_Some of the highest average Malaria Deaths are found in countries in the continent of Africa, as seen by the more intensely coloured and larger sized circles on the map._
''')
# --------------------------------

st.markdown("---")

# --------------------------------
# Buttons for user to plot sample data without uploading, paired with observations based on the plots outputs.
# --------------------------------
btn_base_plot1 = st.button('Press to load Plot 1 using Base Dataset', key='button_base_plot1')
# info1 = st.info('Awaiting for file 1 to be uploaded.')
btn_base_plot2 = st.button('Press to load Plot 2 using Base Dataset', key='button_base_plot2')
# info2 = st.info('Awaiting for file 2 to be uploaded.')
btn_base_plot3 = st.button('Press to load Plot 3 using Base Dataset', key='button_base_plot3')
# info3 = st.info('Awaiting for file 3 to be uploaded.')

st.markdown("---")

# --------------------------------
# For Plot 1:
# --------------------------------
if uploaded_file1 is not None: # If user did upload the required file
    df = load_csv(uploaded_file1)
    output = plot_1(df)
    st.header('(Plot 1) *Average Malaria Death by Region*')
    st.write(output[1]) # Show DataFrame used to plot
    st.write('---')
    st.plotly_chart(output[0], use_container_width=True) # Plot

else: # If user did not upload the required file >> Use sample file
    if btn_base_plot1:
        df = load_csv("./data/malaria_deaths.txt")
        output = plot_1(df)
        st.header('(Plot 1) *Average Malaria Death by Region*')
        st.write(output[1]) # Show DataFrame used to plot
        st.write('---')
        st.plotly_chart(output[0], use_container_width=True) # Plot the graph
        st.markdown('''
        #### __Observations 1__
        1. General Trend
            * Generally, we see that Malaria deaths have been decreasing steadily for all regions from year 1990 onwards.
            * All regions except "Sub-saharan Africa" and "Melanesia", have had relatively low Malaria deaths throughout the time period of years 1990 to 2016.
            * The death toll for the rest of the world is nearly close to zero in comparison with the "Sub-Saharan Africa" and "Melanesia" regions.
        1. Malaria deaths in "Melanesia" rose significantly around year 1998, before falling after year 2004. The level of Malaria deaths eventually fall to levels comapriable to the other regions of the world (except "Sub-Saharan Africa").
        1. "Sub-saharan Africa" is a concern, given that it has consistently the highest Malaria Deaths compared to all the other regions in the world.
            * We should proceed to study further on the "Sub-saharan Africa" region to understand more.
        ''') # Give observations based on given base dataset.

# --------------------------------
# For Plot 2:
# --------------------------------
if uploaded_file2 is not None: # If user did upload the required file
    df = load_csv(uploaded_file2)
    option_region = st.selectbox(
    'Choose: Region with Intermediate-Regions to filter',
    sub_regions)
    output = plot_2(df,option_region)
    st.header('(Plot 2) *Incidence of Malaria by Region - ' + option_region +'*')
    st.write(output[1]) # Show DataFrame used to plot
    st.write('---')
    st.plotly_chart(output[0], use_container_width=True) # Plot

else: # If user did not upload the required file >> Use sample file
    if btn_base_plot2:
        df = load_csv("./data/malaria_inc.txt")
        output = plot_2(df)
        st.header('(Plot 2) *Incidence of Malaria by Region - Sub-Saharan Africa*')
        st.write(output[1]) # Show DataFrame used to plot
        st.write('---')
        st.plotly_chart(output[0], use_container_width=True) # Plot
        st.markdown('''
        #### __Observations 2__
        1. General Trend
            * Generally, the incidence of Malaria have been decreasing steadily over the recent years from year 2000 to year 2015.
            * Quite clearly, we can see that the incidence of Malaria is significantly lower for "Southern Africa".
        1. "Western Africa" remains consistently the highest incidence of Malaria over the years.
        1. We may want to study how "Southern Africa" is managing the spread of Malaria.
        1. We will continue to explore the dataset on the least controlled region in Sub-Saharan Africa, "Western Africa".
        ''') # Give observations based on given base dataset.

# --------------------------------
# For Plot 3:
# --------------------------------
if uploaded_file3 is not None: # If user did upload the required file
    df = load_csv(uploaded_file3)
    option_africa = st.selectbox(
    'Choose: Region to filter in Sub-Saharan Africa',
    african_regions)
    output = plot_3(df,option_africa)
    st.header('(Plot 3) *Malaria Deaths in the Least Controlled Region in Sub-Saharan Africa - ' + option_africa +'*')
    st.write(output[1]) # Show DataFrame used to plot
    st.write('---')
    st.plotly_chart(output[0], use_container_width=True) # Plot

else: # If user did not upload the required file >> Use sample file
    if btn_base_plot3:
        df = load_csv("./data/malaria_deaths_age.txt")
        output = plot_3(df)
        st.header('(Plot 3) *Malaria Deaths in the Least Controlled Region in Sub-Saharan Africa - Western Africa*')
        st.write(output[1]) # Show DataFrame used to plot
        st.write('---')
        st.plotly_chart(output[0], use_container_width=True) # Plot
        st.markdown('''
        #### __Observations 3__
        1. Generally, the average deaths for the Age Group of "Under 5" is significantly much higher than the rest of the Age Groups in "Western Africa".
        1. The death toll for the rest of the Age Groups are nearly close to zero when compared to the Age Group of "Under 5".
            * We should focus more resources on helping the Age Group of "Under 5" in "Western Africa" deal with the treatment of Malaria.
        ''') # Give observations based on given base dataset.