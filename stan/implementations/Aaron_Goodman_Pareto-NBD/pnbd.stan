//Copyright 2018 Aaron Goodman <aaronjg@stanford.edu>. Licensed under the GPLv3 or later.

#include /pnbd_data.stan
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
#include /pnbdlikelihoodloop.stan
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
#include /pnbd_generatedquantities.stan
}
