
data {
  int<lower=0> N;               // Number of customers
  array[N] int<lower=0> X;      // Number of transactions per customer
  vector[N] T;                  // Total time observed per customer
  vector[N] Tx;                 // Time of last purchase
}

parameters {
  real log_r;
  real log_alpha;
  real log_a;
  real log_b;
}

transformed parameters {
  real<lower=0> r = exp(log_r);
  real<lower=0> alpha = exp(log_alpha);
  real<lower=0> a = exp(log_a);
  real<lower=0> b = exp(log_b);
}

model {
  // Weakly informative priors in log-space for numerical stability
  log_r ~ normal(0, 2);
  log_alpha ~ normal(0, 2);
  log_a ~ normal(0, 2);
  log_b ~ normal(0, 2);

  for (n in 1:N) {
    real x = X[n];
    real tx = Tx[n];
    real t = T[n];

    if (x > 0) {
      real d1 = lgamma(r + x) - lgamma(r);
      real d2 = lgamma(a + b) + lgamma(b + x) - lgamma(b) - lgamma(a + b + x);
      real d3 = r * log(alpha) - (r + x) * log(alpha + tx);
      real c3 = (alpha + tx) / (alpha + t);
      real c4 = a / (b + x - 1);

      // Log-Sum-Exp for numerical stability
      real max_term = fmax(log(c3), log(c4));
      target += d1 + d2 + d3 + log_sum_exp(log(c3) - max_term, log(c4) - max_term) + max_term;
    } 
    else {
      real d1 = r * log(alpha) - r * log(alpha + t);
      target += d1;
    }
  }
}
