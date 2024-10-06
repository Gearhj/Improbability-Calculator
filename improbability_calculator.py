import pandas as pd
import streamlit as st

# Load synthetic population data
def load_population_data():
    return pd.read_csv('synthetic_population_data_1980_to_2024.csv.gz', compression='gzip')

# Function to get population from dataset
def get_population(location, year, month, gender, population_data):
    # Normalize the location to handle case sensitivity and whitespace
    location = location.strip().title()  # Convert to title case and remove any leading/trailing whitespace

    # Convert month from name to number
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    month_num = month_mapping.get(month)

    # Filter the dataset for the specific location, year, month, and gender
    filtered_data = population_data[
        (population_data['City'] == location) &
        (population_data['Year'] == year) &
        (population_data['Month'] == month_num) &
        (population_data['Gender'] == gender)
    ]

    # Data validation
    if filtered_data.empty:
        st.error(f"No data found for {location} in {year} {month} for {gender}. Please check your inputs and try again.")
        return None
    else:
        return filtered_data['Population'].iloc[0]  # Return the exact population value without any averaging

def number_to_words(n):
    # Function to convert large numbers to words
    # Supports up to septillion (1e24)
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

    # Load population data
    population_data = load_population_data()

    # Get unique states/countries and cities
    unique_states = population_data['State'].unique()
    selected_state = st.selectbox("Select the state/country where you met your partner:", unique_states)

    filtered_cities = population_data[population_data['State'] == selected_state]['City'].unique()
    selected_city = st.selectbox("Select the city/town where you met your partner:", filtered_cities)

    # Get months
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    selected_month = st.selectbox("Select the month you met your partner:", months)

    # User Inputs
    with st.form(key='user_inputs'):
        meeting_year = st.number_input("Enter the year you met your partner:", min_value=1950, max_value=2024, value=1992)
        gender = st.radio("Select your gender:", ("Male", "Female"))
        your_age_at_meeting = st.number_input("Enter your age at the time of meeting:", min_value=0, max_value=120, value=22)
        partner_age_at_meeting = st.number_input("Enter your partner's age at the time of meeting:", min_value=0, max_value=120, value=19)
        married = st.radio("Did you get married?", ("Yes", "No"))
        
        if married == 'Yes':
            marriage_year = st.number_input("Enter the year you got married:", min_value=1950, max_value=2024, value=1998)
        else:
            marriage_year = None
        
        child_birth_year = st.number_input("Enter your child's birth year:", min_value=1950, max_value=2024, value=2001)
        st.write("""
            To estimate the number of sexual encounters, we need to know how frequently you and your partner
            were intimate during the period leading up to your child's conception.
        """)
        avg_intercourse_per_month = st.number_input(
            "Enter the average number of times you and your partner had sexual intercourse per month during the period between your marriage (or when you started trying to conceive) and your child's conception:",
            min_value=0, max_value=100, value=10)
        
        submitted = st.form_submit_button("Calculate Improbability")
    
    if submitted:
        # Calculate Timeframes
        conception_year = child_birth_year - 1  # Assuming conception approximately one year before birth
        if marriage_year:
            conception_period_months = (conception_year - marriage_year) * 12
        else:
            conception_period_months = (conception_year - meeting_year) * 12
        
        # Population and Demographics
        population = get_population(selected_city, meeting_year, selected_month, gender, population_data)
        if population is None:
            st.stop()  # Stop execution if population data is invalid
        
        # Age Range for Potential Partners
        legal_age = 18
        age_difference = 5  # Assuming acceptable age difference is ±5 years
        
        # Calculate your potential partners
        min_partner_age = max(legal_age, your_age_at_meeting - age_difference)
        max_partner_age = your_age_at_meeting + age_difference
        
        # Assuming uniform age distribution
        age_range_years = max_partner_age - min_partner_age + 1
        percentage_in_age_range = (age_range_years / 80)  # Assuming lifespan of 80 years
        potential_partners = population * 0.5 * percentage_in_age_range  # 50% opposite gender
        
        # Number of New People Met
        avg_new_people_per_year = 50  # Adjust as needed
        years_until_conception = (marriage_year - meeting_year) if marriage_year else 2
        total_new_people_met = avg_new_people_per_year * years_until_conception
        total_new_people_met = min(total_new_people_met, potential_partners)
        
        # Probability of Meeting
        prob_meeting = total_new_people_met / potential_partners if potential_partners > 0 else 0
        prob_meeting = min(prob_meeting, 1)  # Cannot exceed 1
        
        # Probability of Starting a Relationship
        prob_mutual_attraction = 0.1  # 10%
        prob_initiate_relationship = 0.5  # 50%
        prob_starting_relationship = prob_mutual_attraction * prob_initiate_relationship
        
        # Probability of Marriage
        if married == 'Yes':
            prob_marriage = 0.2  # 20%
        else:
            prob_marriage = 0.05  # Adjusted probability if not married
        
        # Combined Social Probability
        combined_social_prob = prob_meeting * prob_starting_relationship * prob_marriage
        
        # Biological Probability of Child's Conception
        # Probability of Ovulating Specific Egg
        total_eggs = 400  # Average number of ovulations in a lifetime
        ovulations_during_period = conception_period_months
        prob_specific_egg = 1 - (1 - 1/total_eggs) ** ovulations_during_period if total_eggs > 0 else 0
        
        # Probability of Specific Sperm Fertilizing the Egg
        sperm_per_ejaculation = 200_000_000
        total_ejaculations = avg_intercourse_per_month * conception_period_months
        total_sperm = total_ejaculations * sperm_per_ejaculation
        prob_specific_sperm = 1 / total_sperm if total_sperm > 0 else 0
        
        # Probability of Successful Conception
        prob_successful_conception = 0.3  # 30%
        
        # Combined Biological Probability
        combined_biological_prob = prob_specific_egg * prob_specific_sperm * prob_successful_conception
        
        # Total Improbability
        total_improbability = combined_social_prob * combined_biological_prob
        
        # Ensure numerical values are fully displayed
        combined_biological_prob_str = f"{combined_biological_prob:.12f}" if combined_biological_prob > 0 else "0.000000000000"
        total_improbability_str = f"{total_improbability:.12f}" if total_improbability > 0 else "0.000000000000"
        
        # Output Results in Bullet Point Format
        st.markdown("## Results")
        st.markdown(f"""
        - **Estimated population of {selected_city} ({gender}) in {int(meeting_year)} {selected_month}**: {population:,.0f}
        - **Your acceptable partner age range at the time**: {int(min_partner_age)} - {int(max_partner_age)} years old
        - **Estimated number of potential partners in this age range**: {int(potential_partners):,}
        - **Estimated number of new people you met during that period**: {int(total_new_people_met):,}
        - **Probability of meeting your partner**: {prob_meeting * 100:.2f}%
        - **Probability of starting a relationship after meeting**: {prob_starting_relationship * 100:.2f}%
        - **Probability of the relationship leading to marriage**: {prob_marriage * 100:.2f}%
        - **Combined probability of meeting, dating, and marrying your partner**: {combined_social_prob:.10f}
        - **Probability of ovulating the specific egg during that period**: {prob_specific_egg * 100:.6f}%
        - **Probability of the specific sperm fertilizing the egg**: {prob_specific_sperm:.12f}
        - **Probability of successful conception**: {prob_successful_conception * 100:.0f}%
        - **Combined biological probability of conceiving your specific child**: {combined_biological_prob_str}
        - **Total improbability of your specific child being born**: {total_improbability_str}
        """)
        
        # Display odds as "1 in X"
        if total_improbability > 0:
            odds = int(1 / total_improbability)
            odds_in_words = number_to_words(odds)
            st.markdown(f"- **As a fraction**: 1 in {odds:,}")
            st.markdown(f"- **In words**: One in {odds_in_words}")
        else:
            st.markdown("- **As a fraction**: Probability is effectively zero.")
        
        # Verbal Description
        st.markdown("### Verbal description of the improbability:")
        if total_improbability > 1e-6:
            st.write("The probability is relatively small but not negligible.")
        elif total_improbability > 1e-12:
            st.write("The probability is extremely small, less than one in a trillion.")
        else:
            st.write("The probability is astronomically small, less than one in a sextillion.")
        
        # Perspective Comparisons
        st.markdown("### To put this into perspective:")
        st.write("- The number of stars in the observable universe is estimated to be around 1 septillion (1e24).")
        st.write("
