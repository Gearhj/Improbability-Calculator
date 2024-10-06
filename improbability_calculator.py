def calculate_biological_probability(conception_period_months, avg_intercourse_per_month, mother_age):
    """Calculate biological probability with realistic parameters"""
    # Sperm probability calculations (based on medical research)
    sperm_per_ejaculation = 100_000_000  # Average sperm count per ejaculation
    viable_sperm_ratio = 0.25  # About 25% of sperm are viable
    sperm_reaching_fallopian = 1000  # Approximate number reaching fallopian tubes
    
    # Monthly fertility probability calculations
    fertile_days_per_cycle = 6  # Fertile window per cycle
    days_per_cycle = 28
    monthly_conception_probability = 0.25  # Base conception probability per cycle
    
    # Age-based fertility adjustment
    age_fertility_factors = {
        range(20, 25): 0.95,
        range(25, 30): 0.90,
        range(30, 35): 0.80,
        range(35, 40): 0.60,
        range(40, 45): 0.35,
        range(45, 50): 0.05
    }
    
    fertility_factor = 0.05  # Default for ages outside defined ranges
    for age_range, factor in age_fertility_factors.items():
        if mother_age in age_range:
            fertility_factor = factor
            break
    
    # Calculate probabilities
    timing_probability = fertile_days_per_cycle / days_per_cycle
    sperm_probability = (viable_sperm_ratio * sperm_reaching_fallopian) / sperm_per_ejaculation
    
    # Monthly try probability
    monthly_success_prob = (timing_probability * 
                          sperm_probability * 
                          monthly_conception_probability * 
                          fertility_factor)
    
    # Probability over the entire conception period
    total_attempts = conception_period_months * avg_intercourse_per_month
    overall_probability = 1 - (1 - monthly_success_prob) ** total_attempts
    
    return overall_probability

def number_to_words(n):
    """Convert large numbers to readable format with scientific notation"""
    if n < 1000:
        return str(n)
    
    # Define number names
    units = ['', 'thousand', 'million', 'billion', 'trillion',
             'quadrillion', 'quintillion', 'sextillion']
    
    # Convert to scientific notation for very large numbers
    if n >= 1e24:
        return f"{n:.2e} ({n:,.0f})"
    
    # Find the appropriate unit
    magnitude = 0
    while n >= 1000 and magnitude < len(units) - 1:
        n /= 1000
        magnitude += 1
    
    return f"{n:.2f} {units[magnitude]}"

def main():
    # [Previous setup code remains the same]
    
    if submitted:
        # Calculate demographic probabilities
        population_ratio = 1 / (your_population * (partner_population / your_population))
        
        # Social probabilities (more realistic values)
        prob_meeting = population_ratio * 0.01  # Chance of meaningful encounter
        prob_attraction = 0.3  # Mutual attraction
        prob_relationship = 0.3  # Starting relationship if attracted
        prob_marriage = 0.4 if married == "Yes" else 0.1
        
        # Biological probability
        biological_prob = calculate_biological_probability(
            conception_period_months,
            avg_intercourse_per_month,
            mother_age
        )
        
        # Total probability
        total_prob = (prob_meeting * 
                     prob_attraction * 
                     prob_relationship * 
                     prob_marriage * 
                     biological_prob)
        
        # Display results with both numeric and word representations
        st.markdown("## Results")
        st.markdown(f"""
        ### Demographic Factors
        - Your population group in {selected_city}, {selected_state}: {number_to_words(your_population)}
        - Potential partners population: {number_to_words(partner_population)}
        
        ### Social Probabilities
        - Meeting probability: 1 in {number_to_words(int(1/prob_meeting))}
        - Mutual attraction: {prob_attraction*100:.1f}%
        - Relationship formation: {prob_relationship*100:.1f}%
        - Marriage/commitment: {prob_marriage*100:.1f}%
        
        ### Biological Factors
        - Conception window: {conception_period_months} months
        - Mother's age at conception: {mother_age} years
        - Biological probability: 1 in {number_to_words(int(1/biological_prob))}
        
        ### Total Improbability
        The probability of your specific child being born is:
        1 in {number_to_words(int(1/total_prob))}
        """)
