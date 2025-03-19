data {
  int<lower=0> n_cust;
  vector<lower=0>[n_cust] x;
  vector<lower=0>[n_cust] time_of_last_txn;
  vector<lower=0>[n_cust] observation_time;
}
transformed data {
  vector<lower=0>[n_cust] x_one;
  x_one <- x + 1;
}
parameters {
  real<lower=0> lambda_sd; 
  real<lower=0> mu_sd; 
  real log_lambda_mean; // poisson rate parameter
  real log_mu_mean; // churn/dropout rate parameter

  vector[n_cust] lambda_raw;
  vector[n_cust] mu_raw;
}
transformed parameters {
  vector<lower=0>[n_cust] lambda;
  vector<lower=0>[n_cust] mu;

  lambda <- exp(log_lambda_mean + lambda_sd * lambda_raw);
  mu <- exp(log_mu_mean + mu_sd * mu_raw);
}
model {
  // local variables
  vector[n_cust] ll1;
  vector[n_cust] ll2;
  vector[n_cust] mu_lambda;
  vector[n_cust] log_lambda;
  vector[n_cust] log_mu;
  vector[n_cust] log_mu_lambda;

  log_lambda_mean ~ normal(-3, 0.25);
  lambda_sd ~ normal(0,0.5);
  log_mu_mean ~ normal(-3, 0.25);
  mu_sd ~ normal(0,0.5);

  lambda_raw ~ normal(0,1); // implies lambda ~ lognormal(log_lambda_mean, lambda_sd)
  mu_raw ~ normal(0,1);  // uses the same parameterization trick

  mu_lambda <- mu + lambda;
  log_mu_lambda <- log(mu_lambda);
  log_lambda <- log(lambda);
  log_mu <- log(mu);

  ll1 <- x .* log_lambda + log_mu - log_mu_lambda - time_of_last_txn .* (mu_lambda);
  ll2 <- (x_one) .* log_lambda - log_mu_lambda - observation_time .* (mu_lambda);

  increment_log_prob(log(exp(ll1) + exp(ll2)));
}