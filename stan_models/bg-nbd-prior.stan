
data {
    int<lower=0> N;               // Number of customers
    vector<lower=0>[N] T;         // Total observation time per customer
}

parameters {
    real<lower=0> r;                        
    real<lower=0> alpha;                    
    real<lower=0, upper=1> phi_dropout;     
    real<lower=1> kappa_dropout;            
}

transformed parameters {
    real a = phi_dropout * kappa_dropout;
    real b = (1 - phi_dropout) * kappa_dropout; 
}

model {
    // Priors 
    r ~ weibull(2, 1);
    alpha ~ weibull(2, 10);
    phi_dropout ~ uniform(0,1);
    kappa_dropout ~ pareto(1,1);   
}

generated quantities {
    array[N] int X_pred;  // Simulated purchase counts
    array[10] int frequency_counts = rep_array(0, 10); // Histogram of purchase counts

    for (n in 1:N) {
        real p_active = beta_rng(a, b);   // Sample from Beta(a, b)
        real lambda = gamma_rng(r, alpha); // Sample purchase rate from Gamma(r, alpha)
        int purchases = poisson_rng(lambda * T[n]) * bernoulli_rng(p_active);
        X_pred[n] = purchases;

        // Aggregate counts for plotting
        if (purchases < 10) {
            frequency_counts[purchases + 1] += 1;  // Convert to 1-based index
        } else {
            frequency_counts[10] += 1;  // Bucket for 9+
        }
    }
}
