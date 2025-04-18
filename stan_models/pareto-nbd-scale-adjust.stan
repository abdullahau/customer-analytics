//Copyright 2018 Aaron Goodman <aaronjg@stanford.edu>. Licensed under the GPLv3 or later.

data{
    int NC;
    vector[NC] p1x; //use vector rather than int
    vector[NC] tx;
    vector[NC] t;
}
parameters{
    real log_buy_a;
    real log_buy_b;
    real log_die_a;
    real log_die_b;
  
    vector[NC] log_lambda_raw;
    vector[NC] log_mu_raw;
}
transformed parameters{
    vector[NC] likelihood;

    real log_r = log_buy_a;
    real log_alpha = log_buy_a - log_buy_b;  
    real log_s = log_die_b;
    real log_beta = log_die_a - log_die_b;
  
    real r = exp(log_r);
    real alpha = exp(log_alpha);
    real s = exp(log_s);
    real beta = exp(log_beta);
  
    vector[NC] log_lambda = log_lambda_raw - log_alpha;
    vector[NC] log_mu = log_mu_raw - log_beta;
    
    vector[NC] lambdamu = exp(log_lambda) + exp(log_mu); 

  for(i in 1:NC){
    
    real log_lambda_mu = log_sum_exp(log_lambda[i],log_mu[i]);
    
    real part1 = p1x[i] .* log_lambda[i] + log_mu[i] - (lambdamu[i]) .* tx[i] -
      log_lambda_mu;
    real part2 = (p1x[i] + 1) * log_lambda[i] - (lambdamu[i]) * t[i] -
      log_lambda_mu;
    
    likelihood[i] = log_sum_exp(part1,part2);
  }  
}
model{
    target += -NC*lgamma(r);
    target += r*log_lambda_raw - exp(log_lambda_raw);
    target += -NC*lgamma(s);
    target += s*log_mu_raw - exp(log_mu_raw);
  
    
    target += log_r + log_alpha + log_s + log_beta;
    r ~ normal(1,1);
    alpha ~ normal(1,1);
    s ~ normal(1,1);
    beta ~ normal(1,1);
  
    target += likelihood;
}
generated quantities{
    real buy_mean = r/alpha;
    real buy_var = r/alpha^2;
    real die_mean = s/beta;
    real die_var = s/beta^2;
    array[NC] real Pactive;
    for (i in 1:NC){
        Pactive[i] = exp( p1x[i] * log_lambda[i] - (lambdamu[i])*t[i] - likelihood[i]);
    }  
}
