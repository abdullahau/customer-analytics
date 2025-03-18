
data {
  int<lower=0> N;             // Number of customers
  array[N] int<lower=0> X;          // Number of transactions per customer
  vector<lower=0>[N] T;       // Total observation time per customer
  vector<lower=0>[N] t_x;     // Time of last transaction (0 if X=0)
}

parameters {
  real<lower=0> r;            // Gamma shape for transaction rate (λ)
  real<lower=0> alpha;        // Gamma scale for λ
  real<lower=0> a;            // Beta shape 1 for dropout probability (p)
  real<lower=0> b;            // Beta shape 2 for p
}

model {
  // Weakly informative priors (adjust based on domain knowledge)
  r ~ gamma(1, 0.1);
  alpha ~ gamma(1, 0.1);
  a ~ gamma(1, 0.1);
  b ~ gamma(1, 0.1);

  for (i in 1:N) {
    if (X[i] == 0) {
      // Likelihood for X=0: (alpha/(alpha + T[i]))^r
      real log_term = r * (log(alpha) - log(alpha + T[i]));
      target += log_term;
    } else {
      // Term 1: B(a, b + X[i])/B(a, b) * gamma(r + X[i])/gamma(r) * (alpha/(alpha + T[i]))^{r + X[i]}
      real log_term1 = lbeta(a, b + X[i]) - lbeta(a, b)
                      + lgamma(r + X[i]) - lgamma(r)
                      + r * log(alpha) - (r + X[i]) * log(alpha + T[i]);

      // Term 2: B(a + 1, b + X[i] - 1)/B(a, b) * gamma(r + X[i])/gamma(r) * (alpha/(alpha + t_x[i]))^{r + X[i]}
      real log_term2 = lbeta(a + 1, b + X[i] - 1) - lbeta(a, b)
                      + lgamma(r + X[i]) - lgamma(r)
                      + r * log(alpha) - (r + X[i]) * log(alpha + t_x[i]);

      // Sum both terms (log-space)
      target += log_sum_exp(log_term1, log_term2);
    }
  }
}
