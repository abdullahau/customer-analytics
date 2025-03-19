
data {
  int<lower=0> N;                 // Number of customers
  array[N] int<lower=0> X;        // Number of transactions per customer
  vector[N] T;                    // Total time observed per customer
  vector[N] Tx;                   // Time of last purchase
}

parameters {
  real<lower=0> alpha;      // Purchase rate (Poisson process)
  real<lower=0> r;          // Shape parameter of Gamma for lambda
  real<lower=0> a;          // Beta-Geometric parameter (shape a)
  real<lower=0> b;          // Beta-Geometric parameter (shape b)
}

model {
  // Priors
  alpha ~ gamma(1, 0.1);   // Prior for lambda scale
  r ~ gamma(1, 0.1);        // Prior for r
  a ~ gamma(1, 0.1);    // Prior for a
  b ~ gamma(1, 0.1);    // Prior for b

  for (n in 1:N) {
    real x = X[n];
    real tx = Tx[n];
    real t = T[n];

    if (x > 0) {
      real d1 = lgamma(r + x) - lgamma(r) + lgamma(a + b) + lgamma(b + x) - lgamma(b) - lgamma(a + b + x);
      real d2 = r * log(alpha) - (r + x) * log(alpha + tx);
      real c3 = pow((alpha + tx) / (alpha + t), r + x);
      real c4 = a / (b + x - 1);

      target += d1 + d2 + log(c3 + c4);
    } else {
      real d1 = lgamma(r + x) - lgamma(r) + lgamma(a + b) + lgamma(b + x) - lgamma(b) - lgamma(a + b + x);
      real d2 = r * log(alpha) - (r + x) * log(alpha + tx);
      real c3 = pow((alpha + tx) / (alpha + t), r + x);

      target += d1 + d2 + log(c3);
    }
  }
}
