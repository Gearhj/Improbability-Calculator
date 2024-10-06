import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

def load_population_data():
    try:
        df = pd.read_csv('synthetic_population_data_1985_to_2024.csv.gz', compression='gzip')
        return df
    except FileNotFoundError:
        st.error("Population data file not found. Please ensure the file exists in the correct location.")
        st.stop()

def get_population(location, year, month, gender, age_band, population_data):
    """Get population for specific demographic criteria"""
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
        (population_data['Gender'] == gender) &
        (population_data['Age_Band'] == age_band)
    ]

    if filtered_data.empty:
        st.error(f"No data found for {location} in {year} {month} for {gender} in age band {age_band}")
        return None
    
    return filtered_data['Population'].iloc[0]

def get_age_band(age):
    """Convert age to appropriate age band"""
    if age < 18:
        return '0-17'
    elif age < 25:
        return '18-24'
    elif age < 35:
        return '25-34'
    elif age < 45:
        return '35-44'
    elif age < 55:
        return '45-54'
    elif age < 65:
        return '55-64'
    else:
        return '65+'

def calculate_biological_probability(conception_period_months, avg_intercourse_per_month, mother_age):
    """Calculate biological probability with age considerations"""
    # Base sperm probability calculations
    sperm_per_ejaculation = 200_000_000
    sperm_reaching_egg = 200
    total_encounters = conception_period_months * avg_intercourse_per_month
    
    # Probability of specific sperm
    prob_specific_sperm = (1 / sperm_per_ejaculation) * (sperm_reaching_egg / sperm_per_ejaculation)
    
    # Age-adjusted egg probability
    total_eggs_lifetime = 400
    eggs_during_period = conception_period_months / 12
    
    # Age-based fertility adjustment
    if mother_age < 25:
        fertility_factor = 1.0
    elif mother_age < 30:
        fertility_factor = 0.9
    elif mother_age < 35:
        fertility_factor = 0.8
    elif mother_age < 40:
        fertility_factor = 0.5
    else:
        fertility_factor = 0.2
    
    prob_specific_egg = (1 / total_eggs_lifetime) * fertility_factor
    
    # Fertile window and conception probability
    fertile_days_per_cycle = 6
    days_per_cycle = 28
    prob_fertile_timing = fertile_days_per_cycle / days_per_cycle
    prob_successful_conception = 0.3 * fertility_factor
    
    # Combined probability
    total_prob = (prob_specific_sperm * 
                 prob_specific_egg * 
                 prob_fertile_timing * 
                 prob_successful_conception)
    
    # Account for multiple attempts
    final_prob = 1 - (1 - total_prob) ** total_encounters
    
    return final_prob

def number_to_words(n):
    units = ['', ' thousand', ' million', ' billion', ' trillion',
             ' quadrillion', ' quintillion', ' sextillion', ' septillion']
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
        considering demographic, social, and biological factors.
    """)

    # Load population data
    population_data = load_population_data()

    # Get unique states and cities
    unique_states = sorted(population_data['State'].unique())
    selected_state = st.selectbox("Select the state where you met your partner:", unique_states)

    filtered_cities = sorted(population_data[population_data['State'] == selected_state]['City'].unique())
    selected_city = st.selectbox("Select the city where you met your partner:", filtered_cities)

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    with st.form(key='user_inputs'):
        selected_month = st.selectbox("Select the month you met your partner:", months)
        meeting_year = st.number_input("Enter the year you met your partner:", 
                                     min_value=1985, max_value=2024, value=2000)
        
        col1, col2 = st.columns(2)
        with col1:
            your_gender = st.radio("Your gender:", ("Male", "Female"))
            your_age_at_meeting = st.number_input("Your age when you met:", 
                                                min_value=15, max_value=80, value=25)
        
        with col2:
            partner_age_at_meeting = st.number_input("Partner's age when you met:", 
                                                   min_value=15, max_value=80, value=25)
            married = st.radio("Did you get married?", ("Yes", "No"))
        
        if married == "Yes":
            marriage_year = st.number_input("Year of marriage:", 
                                          min_value=meeting_year, max_value=2024, 
                                          value=min(meeting_year + 2, 2024))
        else:
            marriage_year = None
        
        child_birth_year = st.number_input("Child's birth year:", 
                                          min_value=meeting_year, max_value=2024, 
                                          value=min(meeting_year + 4, 2024))
        
        avg_intercourse_per_month = st.number_input(
            "Average monthly intimate encounters:", 
            min_value=1, max_value=100, value=10)
        
        submitted = st.form_submit_button("Calculate Improbability")
    
    if submitted:
        # Get age bands for population filtering
        your_age_band = get_age_band(your_age_at_meeting)
        partner_age_band = get_age_band(partner_age_at_meeting)
        
        # Get relevant populations
        your_population = get_population(selected_city, meeting_year, selected_month, 
                                       your_gender, your_age_band, population_data)
        partner_population = get_population(selected_city, meeting_year, selected_month, 
                                          'Female' if your_gender == 'Male' else 'Male', 
                                          partner_age_band, population_data)
        
        if your_population is None or partner_population is None:
            st.stop()
        
        # Calculate probabilities
        # Meeting probability based on population size and age-appropriate matches
        prob_meeting = 1 / (your_population * (partner_population / your_population))
        
        # Social factors
        prob_attraction = 0.1  # Mutual attraction
        prob_relationship = 0.5  # Starting relationship if attracted
        prob_marriage = 0.2 if married == "Yes" else 0.05
        
        # Biological probability
        conception_period_months = (child_birth_year - (marriage_year or meeting_year)) * 12
        mother_age = (partner_age_at_meeting if your_gender == "Male" else your_age_at_meeting) + \
                    (child_birth_year - meeting_year)
        biological_prob = calculate_biological_probability(conception_period_months, 
                                                        avg_intercourse_per_month, 
                                                        mother_age)
        
        # Total probability
        total_prob = prob_meeting * prob_attraction * prob_relationship * \
                    prob_marriage * biological_prob
        
        # Display results
        st.markdown("## Results")
        st.markdown(f"""
        ### Demographic Factors
        - Your population group in {selected_city}: {your_population:,}
        - Potential partners population: {partner_population:,}
        
        ### Social Probabilities
        - Meeting probability: 1 in {int(1/prob_meeting):,}
        - Mutual attraction: {prob_attraction*100:.1f}%
        - Relationship formation: {prob_relationship*100:.1f}%
        - Marriage/commitment: {prob_marriage*100:.1f}%
        
        ### Biological Factors
        - Conception window: {conception_period_months} months
        - Mother's age at conception: {mother_age} years
        - Biological probability: 1 in {int(1/biological_prob):,}
        
        ### Total Improbability
        - The probability of your specific child being born: 1 in {number_to_words(int(1/total_prob))}
        """)
        
        st.success("""
        This calculation demonstrates the astronomical improbability of any specific person being born, 
        supporting the hypothesis that even minor changes to the past could have massive implications 
        for the existence of specific individuals.
        """)

if __name__ == "__main__":
    main()
