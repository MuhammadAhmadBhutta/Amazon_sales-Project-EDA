import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page configuration for a professional look
st.set_page_config(
    page_title="Amazon Sales EDA Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR THEME SETTINGS (Must be before main content for CSS injection) ---
st.sidebar.title("🎨 Dashboard Layout")
theme_choice = st.sidebar.select_slider(
    "Overall Visual Theme:",
    options=["Modern", "Vibrant", "Corporate"],
    value="Modern"
)

# Custom Theme Styling for the WHOLE app
if theme_choice == "Vibrant":
    bg_color = "#0E1117"
    sb_color = "#161B22"
    text_color = "#E6EDF3"
    card_bg = "#21262D"
    metric_color = "#58A6FF"
    
    main_scale = "Rainbow"
    reg_scale = "Plotly3"
    payment_scale = px.colors.qualitative.Alphabet
    plotly_template = "plotly_dark"
elif theme_choice == "Corporate":
    bg_color = "#FFFFFF"
    sb_color = "#F0F2F6"
    text_color = "#1F2937"
    card_bg = "#F9FAFB"
    metric_color = "#2563EB"
    
    main_scale = "Blues"
    reg_scale = "Cividis"
    payment_scale = px.colors.qualitative.D3
    plotly_template = "simple_white"
else: # Modern
    bg_color = "#F8F9FA"
    sb_color = "#FFFFFF"
    text_color = "#1A3E59"
    card_bg = "#FFFFFF"
    metric_color = "#2E86AB"
    
    main_scale = "Turbo"
    reg_scale = "Plotly3"
    payment_scale = px.colors.qualitative.Vivid
    plotly_template = "plotly_white"

# Inject Global CSS based on selection
st.markdown(f"""
    <style>
    /* Global Background and Text */
    .stApp, .main, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    /* Fixing the top header gap */
    [data-testid="stHeader"] {{
        background: {bg_color};
    }}

    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {sb_color};
        border-right: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Card / KPI Metric Boxes */
    div[data-testid="metric-container"] {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255,255,255,0.05);
    }}
    
    [data-testid="stMetricValue"] {{
        color: {metric_color};
        font-weight: bold;
    }}
    
    /* Text colors for all headers and labels */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: {text_color} !important;
    }}

    /* Multi-select styling improvement */
    div[data-baseweb="tag"] {{
        background-color: {metric_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Function to load and clean data
@st.cache_data
def load_data():
    # Use relative path since we are in c:\Amazon_sales Project EDA\
    file_path = os.path.join("Data", "amazon_sales_dataset.csv")
    if not os.path.exists(file_path):
        # Fallback to local if Data folder isn't found
        file_path = "amazon_sales_dataset.csv"
        
    df = pd.read_csv(file_path)
    
    # Data Cleaning: Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Map column names if they differ slightly from expectations
    # CSV has: order_id, order_date, product_id, product_category, price, 
    # discount_percent, quantity_sold, customer_region, payment_method, 
    # rating, review_count, discounted_price, total_revenue
    
    return df

# Load the dataset
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("---")
st.sidebar.title("🔍 Explore Data")
st.sidebar.markdown("Narrow down your analysis by category and region.")

category_options = sorted(df['product_category'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Product Categories:",
    options=category_options,
    default=category_options
)

region_options = sorted(df['customer_region'].unique())
selected_regions = st.sidebar.multiselect(
    "Select Customer Regions:",
    options=region_options,
    default=region_options
)

# Apply filters
filtered_df = df[
    (df['product_category'].isin(selected_categories)) & 
    (df['customer_region'].isin(selected_regions))
]

# Ensure dashboard is visible even if filters result in narrow data
if filtered_df.empty:
    st.warning("No data matches your current filters. Please adjust your criteria.")
    st.stop()

# --- MAIN DASHBOARD ---
st.title("📦 Amazon Sales Exploratory Data Analysis")
st.markdown("---")

# 1. Key Metrics (KPIs) with improved readability
kpi_row = st.container()
with kpi_row:
    kpi1, kpi2, kpi3 = st.columns(3)
    
    total_revenue = filtered_df['total_revenue'].sum()
    avg_rating = filtered_df['rating'].mean()
    total_quantity = filtered_df['quantity_sold'].sum()

    # Format Large Revenue Numbers (Compact Financial Notation)
    def format_money(val):
        if val >= 1_000_000:
            return f"${val / 1_000_000:.1f}M"
        elif val >= 1_000:
            return f"${val / 1_000:.1f}K"
        else:
            return f"${val:.2f}"

    with kpi1:
        st.metric(label="💰 Total Revenue", value=format_money(total_revenue), delta="Overall Sales")

    with kpi2:
        st.metric(label="⭐ Avg Rating", value=f"{avg_rating:.2f}", delta="Customer Rating")

    with kpi3:
        st.metric(label="🛒 Items Sold", value=f"{total_quantity:,}", delta="Order Count")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Category Performance Horizontal Bar
chart_row1 = st.container()
with chart_row1:
    st.subheader("🏆 Sales Performance by Category")
    rev_per_cat = filtered_df.groupby('product_category')['total_revenue'].sum().sort_values(ascending=True).reset_index()
    
    fig_best_seller = px.bar(
        rev_per_cat,
        x='total_revenue',
        y='product_category',
        orientation='h',
        title="Revenue Performance by Category",
        text_auto='.2s',
        color='total_revenue',
        color_continuous_scale=main_scale,
        template=plotly_template,
        labels={'total_revenue': 'Total Revenue ($)', 'product_category': 'Category'}
    )
    fig_best_seller.update_layout(
        title={
            'text': "Revenue Performance by Category",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 22}
        },
        showlegend=False, 
        height=500, 
        margin=dict(t=80, b=40, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color)
    )
    st.plotly_chart(fig_best_seller, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)

# 3. Regional Insights Side-by-Side
chart_row2 = st.container()
with chart_row2:
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("🌍 Revenue by Region")
        rev_per_region = filtered_df.groupby('customer_region')['total_revenue'].sum().reset_index()
        fig_region_rev = px.bar(
            rev_per_region,
            x='customer_region',
            y='total_revenue',
            title="Geographic Revenue Distribution",
            color='customer_region',
            color_discrete_sequence=payment_scale,
            template=plotly_template,
            labels={'total_revenue': 'Total Revenue ($)', 'customer_region': 'Region'}
        )
        fig_region_rev.update_layout(
            title={
                'text': "Geographic Revenue Distribution",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20}
            },
            margin=dict(t=80, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        st.plotly_chart(fig_region_rev, width="stretch")

    with row2_col2:
        st.subheader("⭐ Sentiment by Region")
        rating_per_region = filtered_df.groupby('customer_region')['rating'].mean().reset_index()
        fig_region_rating = px.bar(
            rating_per_region,
            x='customer_region',
            y='rating',
            title="Customer Satisfaction by Region",
            color='rating',
            color_continuous_scale=reg_scale,
            template=plotly_template,
            labels={'rating': 'Average Rating', 'customer_region': 'Region'}
        )
        fig_region_rating.update_yaxes(range=[0, 5])
        fig_region_rating.update_layout(
            title={
                'text': "Customer Satisfaction by Region",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20}
            },
            margin=dict(t=80, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        st.plotly_chart(fig_region_rating, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)

# 4. Payment Trends Side-by-Side
chart_row3 = st.container()
with chart_row3:
    row3_col1, row3_col2 = st.columns(2)
    
    with row3_col1:
        st.subheader("💳 Preferred Payment Methods")
        payment_counts = filtered_df['payment_method'].value_counts().reset_index()
        payment_counts.columns = ['payment_method', 'count']
        fig_payment_pie = px.pie(
            payment_counts,
            names='payment_method',
            values='count',
            title="Market Share of Payment Methods",
            hole=0.5,
            color_discrete_sequence=payment_scale,
            template=plotly_template
        )
        fig_payment_pie.update_layout(
            title={
                'text': "Market Share of Payment Methods",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20}
            },
            margin=dict(t=80, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        st.plotly_chart(fig_payment_pie, width="stretch")

    with row3_col2:
        st.subheader("🗺️ Regional Payment Behavior")
        fig_payment_region = px.histogram(
            filtered_df,
            x='customer_region',
            color='payment_method',
            barmode='group',
            title="Regional Payment Preferences",
            labels={'customer_region': 'Region', 'count': 'Transaction Count'},
            color_discrete_sequence=payment_scale,
            template=plotly_template
        )
        fig_payment_region.update_layout(
            title={
                'text': "Regional Payment Preferences",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 20}
            },
            legend_title="Method", 
            margin=dict(t=80, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        st.plotly_chart(fig_payment_region, width="stretch")

# 5. Interactive Explorer
st.subheader("🔎 Detailed Data Explorer")
with st.expander("📝 Click to see filtered raw data (Top 100 rows)"):
    st.dataframe(filtered_df.head(100), width="stretch")

st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>Amazon Sales Analysis EDA | Built for Ahmad AI Labs</p>", unsafe_allow_html=True)
