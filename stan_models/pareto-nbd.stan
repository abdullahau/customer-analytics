//Copyright 2018 Aaron Goodman <aaronjg@stanford.edu>. Licensed under the GPLv3 or later.

data{
    int NC;
    vector[NC] p1x; //use vector rather than int
    vector[NC] tx;
    vector[NC] t;
}
parameters{
    real log_r;
    real log_alpha;
    real log_s;
    real log_beta;

    vector[NC] log_lambda;
    vector[NC] log_mu;
}

transformed parameters{
    vector[NC] likelihood;
    real r = exp(log_r);
    real alpha = exp(log_alpha);
    real s = exp(log_s);
    real beta = exp(log_beta);

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
    target += NC*(r * log_alpha - lgamma(r));
    target += r*log_lambda - alpha*exp(log_lambda);
    target += NC*(s * log_beta - lgamma(s));
    target += s*log_mu - beta*exp(log_mu);

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
