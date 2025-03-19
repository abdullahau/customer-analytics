
data {
    int<lower=0> N;               
    array[N] int<lower=0> X;      
    vector<lower=0>[N] T;         
    vector<lower=0>[N] Tx;        
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
    // Priors:
    r ~ weibull(2, 1);                
    alpha ~ weibull(2, 10);           
    phi_dropout ~ uniform(0,1);       
    kappa_dropout ~ pareto(1,1);      

    for (n in 1:N) {
        int x = X[n];                 
        real tx = Tx[n];              
        real t = T[n];                

        if (x == 0) {
            target += r * (log(alpha) - log(alpha + t));
        } else {
            real beta_term1 = lbeta(a, b + x) - lbeta(a, b);  
            real gamma_term = lgamma(r + x) - lgamma(r);       
            real term1 = gamma_term + beta_term1 + r * log(alpha) - (r + x) * log(alpha + t);
            
            real beta_term2 = lbeta(a + 1, b + x - 1) - lbeta(a, b);
            real term2 = gamma_term + beta_term2 + r * log(alpha) - (r + x) * log(alpha + tx);
            
            target += log_sum_exp(term1, term2);
        }
    }
}

generated quantities {
    vector[N] log_lik;
    
    for (n in 1:N) {
        if (X[n] == 0) {
            log_lik[n] = r * (log(alpha) - log(alpha + T[n]));
        } else {
            log_lik[n] = (lgamma(r + X[n]) - lgamma(r)) 
                         + (lbeta(a, b + X[n]) - lbeta(a, b))
                         + r * log(alpha) - (r + X[n]) * log(alpha + T[n]);
        }
    }
}
