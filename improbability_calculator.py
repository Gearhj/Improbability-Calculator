import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

# Load synthetic population data with error handling
def load_population_data():
    try:
        return pd.read_csv('synthetic_population_data_1985_to_2024.csv.gz', compression='gzip')
    except FileNotFoundError:
        # Create a minimal dataset for demonstration
        states = ['California', 'New York', 'Texas', 'Florida']
        cities = {
            'California': ['Los Angeles', 'San Francisco', 'San Diego'],
            'New York': ['New York City', 'Buffalo', 'Albany'],
            'Texas': ['Houston', 'Austin', 'Dallas'],
            'Florida': ['Miami', 'Orlando', 'Tampa']
        }
        data = []
        for state in states:
            for city in cities[state]:
                for year in range(1985, 2025):
                    for month in range(1, 13):
                        for gender in ['Male', 'Female']:
                            # Generate a reasonable population number
                            population = np.random.randint(100000, 5000000)
                            data.append({
                                'State': state,
                                'City': city,
                                'Year': year,
                                'Month': month,
                                'Gender': gender,
                                'Population': population
                            })
        return pd.DataFrame(data)

def get_population(location, year, month, gender, population_data):
    location = location.strip().title()
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    month_num = month_mapping.get(month)

    filtered_data = population_data[
        (population_data['City'] == location) &
        (population_data['Year'] == year) &
        (population_data['Month'] == month_num) &
        (population_data['Gender'] == gender)
    ]

    if filtered_data.empty:
        st.error(f"No data found for {location} in {year} {month} for {gender}. Using estimated population.")
        return 1000000  # Return a default population estimate
    
    return filtered_data['Population'].iloc[0]

def calculate_biological_probability(conception_period_months, avg_intercourse_per_month):
    # Enhanced biological probability calculations
    sperm_per_ejaculation = 200_000_000  # 200 million sperm per ejaculation
    sperm_reaching_egg = 200  # Only about 200 sperm typically reach the egg
    total_encounters = conception_period_months * avg_intercourse_per_month
    
    # Probability of specific sperm
    prob_specific_sperm = (1 / sperm_per_ejaculation) * (sperm_reaching_egg / sperm_per_ejaculation)
    
    # Egg probability
    total_eggs_lifetime = 400  # Average number of eggs released in lifetime
    eggs_during_period = conception_period_months / 12  # Roughly one egg per month
    prob_specific_egg = 1 / total_eggs_lifetime
    
    # Fertile window probability
    fertile_days_per_cycle = 6
    days_per_cycle = 28
    prob_fertile_timing = fertile_days_per_cycle / days_per_cycle
    
    # Conception success probability
    prob_successful_conception = 0.3  # 30% chance per cycle with perfect timing
    
    # Combined probability
    total_prob = (prob_specific_sperm * 
                 prob_specific_egg * 
                 prob_fertile_timing * 
                 prob_successful_conception)
    
    # Account for multiple attempts
    final_prob = 1 - (1 - total_prob) ** total_encounters
    
    return final_prob

def number_to_words(n):
    units = [
        '', ' thousand', ' million', ' billion', ' trillion',
        ' quadrillion', ' quintillion', ' sextillion', ' septillion'
    ]
    k = 1000
    if n < k:
        return str(n)
    for i, unit in enumerate(units):
        if n < k**(i + 1) * k:
            value = n / (k**i)
            return f"{value:,.2f}{unit}"
    return f"{n:,.2f}"

def main():
    st.set_page_config(page_title="Improbability Calculator", page_icon="✨", layout="centered")
    st.title("Improbability Calculator for a Specific Child's Birth")
    st.write("""
        This calculator estimates the improbability of your specific child being born,
        considering social and biological factors. Please provide the requested information below.
    """)

    try:
        # Load population data
        population_data = load_population_data()

        # Get unique states/countries and cities
        unique_states = sorted(population_data['State'].unique())
        selected_state = st.selectbox("Select the state/country where you met your partner:", unique_states)

        filtered_cities = sorted(population_data[population_data['State'] == selected_state]['City'].unique())
        selected_city = st.selectbox("Select the city/town where you met your partner:", filtered_cities)

        # Get months
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        selected_month = st.selectbox("Select the month you met your partner:", months)

        # User Inputs
        with st.form(key='user_inputs'):
            meeting_year = st.number_input("Enter the year you met your partner:", min_value=1985, max_value=2024, value=2000)
            gender = st.radio("Select your gender:", ("Male", "Female"))
            your_age_at_meeting = st.number_input("Enter your age at the time of meeting:", min_value=0, max_value=120, value=25)
            partner_age_at_meeting = st.number_input("Enter your partner's age at the time of meeting:", min_value=0, max_value=120, value=25)
            married = st.radio("Did you get married?", ("Yes", "No"))
            
            if married == 'Yes':
                marriage_year = st.number_input("Enter the year you got married:", min_value=1985, max_value=2024, value=2002)
            else:
                marriage_year = None
            
            child_birth_year = st.number_input("Enter your child's birth year:", min_value=1985, max_value=2024, value=2005)
            
            avg_intercourse_per_month = st.number_input(
                "Enter the average number of times you and your partner had sexual intercourse per month:",
                min_value=0, max_value=100, value=10)
            
            submitted = st.form_submit_button("Calculate Improbability")

        if submitted:
            # Calculate timeframes
            conception_year = child_birth_year - 1
            conception_period_months = (conception_year - meeting_year) * 12
            
            # Get population and calculate probabilities
            population = get_population(selected_city, meeting_year, selected_month, gender, population_data)
            
            # Social probabilities
            prob_meeting = min(1000 / population, 1)  # Probability of meeting any specific person
            prob_attraction = 0.1  # 10% chance of mutual attraction
            prob_relationship = 0.5  # 50% chance of starting relationship if attracted
            prob_marriage = 0.2 if married == 'Yes' else 0.05
            
            # Combined probabilities
            social_prob = prob_meeting * prob_attraction * prob_relationship * prob_marriage
            biological_prob = calculate_biological_probability(conception_period_months, avg_intercourse_per_month)
            total_prob = social_prob * biological_prob

            # Display results
            st.markdown("## Results")
            st.markdown(f"""
            ### Social Factors
            - Population of {selected_city} at time of meeting: {population:,}
            - Probability of meeting: 1 in {int(1/prob_meeting):,}
            - Probability of mutual attraction: {prob_attraction*100:.1f}%
            - Probability of relationship: {prob_relationship*100:.1f}%
            - Probability of marriage/commitment: {prob_marriage*100:.1f}%
            
            ### Biological Factors
            - Conception window: {conception_period_months} months
            - Total potential encounters: {int(conception_period_months * avg_intercourse_per_month):,}
            - Combined biological probability: 1 in {int(1/biological_prob):,}
            
            ### Total Improbability
            - Final probability: 1 in {number_to_words(int(1/total_prob))}
            """)

            st.success("""
            Your child's existence is truly remarkable! This calculation demonstrates why even small changes
            in the timeline could have massive implications for specific individuals being born.
            """)

    except Exception as e:
        st.error(f"""
        An error occurred while running the calculator. Please try again or contact support.
        Error details: {str(e)}
        """)

if __name__ == "__main__":
    main()
