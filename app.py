import os

import pandas as pd
import plotly.express as px
import streamlit as st

if __name__ =='__main__':

    # read data from excel file
    # use streamlit "cache_data" decorator to cache this data so it doesn't get ...
    # ... retrieved EVERY time we refresh the page

    # setup streamlit
    st.set_page_config(
        page_title='Sales Dashboard',
        page_icon=':bar_chart:',
        layout='wide'
    )

    @st.cache_data
    def get_data_from_excel():
        '''file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supermarkt_sales.xlsx')
        df = pd.read_excel(file_path, header=3, usecols='B:R', nrows=1000)
        '''
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supermarkt_sales.csv')
        df = pd.read_csv(file_path, header=0)
        df['hour'] = df['time'].apply(lambda x: str(x.hour)) # cast to string to avoid FORCED sorting on chart axis
        df['week_beginning_monday'] = df['date'].apply(lambda x: x - pd.Timedelta(x.weekday(), 'day'))
        
        return df
    
    def get_column_display_names(column_names):
        key_names = column_names
        val_names = [column_name.replace('_', ' ').title() for column_name in column_names]
        return dict(zip(key_names, val_names))
    
    def get_grouped_data(data_df, group_by_column, aggregation_column, aggregation_type, sort_values=True, sort_ascending=True):        
        if sort_values:
            output = data_df.groupby(group_by_column)[[aggregation_column]].agg(aggregation_type).sort_values(by=aggregation_column, ascending=sort_ascending)
        else:
            output = data_df.groupby(group_by_column)[[aggregation_column]].agg(aggregation_type)
        return output
    
    def create_line_chart(data_df, display_column, title):
        chart = px.line(
            data_df,
            y=display_column,            
            title=f'<b>{title}</b>',
            color_discrete_sequence = ['#0083B8'] * data_df.shape[0],
            template='plotly_white'
        )

        # remove background colour and gridlines    
        chart.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=(dict(showgrid=False))
        )
        
        return chart
    
    def create_bar_chart(data_df, display_column, title):        
        chart = px.bar(
            data_df,
            x=data_df.index,
            y=display_column,
            orientation='v',
            title=f'<b>{title}</b>',
            color_discrete_sequence = ['#0083B8'] * data_df.shape[0],
            template='plotly_white'
        )

        # remove background colour and gridlines    
        chart.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=(dict(showgrid=False))
        )

        return chart    
    
    def display_charts(data_df, display_column, title_prefix):
        columns = [
            'city',
            'customer_type',
            'gender',
            'product_line',
            'payment_method',
        ]

        figs = []
        for column in columns:            
            grouped_df = get_grouped_data(data_df, column, display_column, 'sum')
            figs.append(create_bar_chart(grouped_df, display_column, f'{title_prefix} by {column.replace("_", " ").title()}'))

        grouped_df = get_grouped_data(data_df, 'week_beginning_monday', display_column, 'sum', sort_values=False)        
        figs.append(create_line_chart(grouped_df, display_column, f'{title_prefix} by Week (Beginning Monday)'))
        
        for i in range(2):
            columns = st.columns(3)
            for j in range(3):
                columns[j].plotly_chart(figs[(3*i)+j], use_container_width=True)
    
    df = get_data_from_excel()

    ############# 1) SIDE BAR #############

    metric_options = {
        'Revenue': 'total',
        'Unit Sales': 'quantity',
        'Gross Profit': 'gross_income'
    }

    # reverse mapping
    #metric_options_reverse = dict(zip(metric_options.values(), metric_options.keys()))

    st.sidebar.header('Metric Selection:')
    metric = st.sidebar.selectbox(
        'Select a Metric',
        options=metric_options.keys()
    )
    
    st.sidebar.header('Data Filters:')
    city = st.sidebar.multiselect(
        'Select City',
        options=df['city'].unique(),
    )

    customer_type = st.sidebar.multiselect(
        'Select Customer Type',
        options=df['customer_type'].unique()
    )

    gender = st.sidebar.multiselect(
        'Select Gender',
        options=df['gender'].unique()        
    )

    product_line = st.sidebar.multiselect(
        'Select Product Line',
        options=df['product_line'].unique()        
    )

    payment_method = st.sidebar.multiselect(
        'Select Payment Method',
        options=df['payment_method'].unique()        
    )

    if city == []:
        city = df['city'].unique()
    if customer_type == []:
        customer_type = df['customer_type'].unique()
    if gender == []:
        gender = df['gender'].unique()
    if product_line == []:
        product_line = df['product_line'].unique()
    if payment_method == []:
        payment_method = df['payment_method'].unique()

    filtered_df = df.query(
        'city in @city & customer_type in @customer_type & gender in @gender & product_line in @product_line & payment_method in @payment_method'
    )

    ############# 2) MAIN PAGE #############

    ############# 2A) TOP #############

    st.title(':bar_chart: Sales Dashboard')
    st.markdown('##')

    # TOP KPIs
    total_revenue = filtered_df['total'].sum()
    average_revenue_per_transaction = filtered_df['total'].mean()

    total_unit_sales = filtered_df['quantity'].sum()
    average_unit_sales_per_transaction = filtered_df['quantity'].mean()

    average_rating = filtered_df['rating'].mean()
    star_rating = ':star:' * int(round(average_rating,0))

    column_1, column_2, column_3, column_4, column_5 = st.columns(5)

    with column_1:
            st.subheader('Total Revenue:')
            st.subheader(f'${total_revenue:,.0f}')

    with column_2:
        st.subheader('Avg. Revenue per Transaction:')
        st.subheader(f'${average_revenue_per_transaction:.2f}')
    
    with column_3:
        st.subheader('Total Unit Sales:')
        st.subheader(f'{total_unit_sales:,.0f}')
    
    with column_4:
        st.subheader('Avg. Unit Sales per Transaction:')
        st.subheader(f'{average_unit_sales_per_transaction:,.1f}')

    with column_5:
        st.subheader('Average Rating:')
        st.subheader(f'{average_rating:.1f} {star_rating}')        

    st.markdown('---')

    ############# 2B) METRIC BAR CHARTS #############

    st.subheader(f'{metric} Breakdown')
    display_charts(filtered_df, metric_options[metric], metric)

    ############# 2C) RAW DATA #############
    st.markdown('---')
    st.subheader('Raw Data')
    st.dataframe(df)

    ############# 3) HIDE STREAMLIT INFO #############
    hide_st_style = '''
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    '''

    st.markdown(hide_st_style, unsafe_allow_html=True)