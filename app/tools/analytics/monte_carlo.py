import numpy as np
from langchain.tools import tool

@tool
def monte_carlo_risk_assessment(scenario: str) -> str:
    """Run a Monte Carlo probability simulation for any scenario.
    Input: describe the scenario you want to assess risk for.
    Returns: probability estimate with confidence interval.
    """
    # General-purpose risk simulation
    # Variables represent unknown threat factors
    iterations = 50_000
    rng = np.random.default_rng()
    #Draw from beta distribution (bounded 0-1, good fro probabilities)
    factor_a = rng.beta(2,6,iterations) # primary risk factor
    factor_b = rng.beta(1,8,iterations) # secondary risk factor
    factor_c = rng.beta(2,6,iterations) # environmental risk factor
    
    #Combined risk score
    risk = (factor_a * 0.5) + (factor_b*0.3) + (factor_c*0.2)
    
    probability = float(np.mean(risk > 0.4))
    ci_low,ci_high = np.percentile(risk, [2.5,97.5])
    mean_risk = float(np.mean(risk))
    worst_case = float(np.percentile(risk,95))
    return ( 
        f'Monte Carlo simulation ({iterations:,} iterations):\n' 
        f'Scenario risk probability: {probability:.1%}\n' 
        f'Mean risk score: {mean_risk:.3f}\n' 
        f'95th percentile (worst case): {worst_case:.3f}\n' 
        f'95% confidence interval: [{ci_low:.3f}, {ci_high:.3f}]' 
    )