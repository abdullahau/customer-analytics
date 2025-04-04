
data {
    int<lower=0> N;
    array[N] int<lower=0> X;
    vector<lower=0>[N] T;
    vector<lower=0>[N] t_x;
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
        real tx = t_x[n];
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
    array[N] int X_rep;
    vector[N] t_x_rep;

    for (n in 1:N) {
        real lambda_n = gamma_rng(r, alpha);
        real p_n = beta_rng(a, b);
        real current_time = 0;
        int x = 0;
        real tx = 0;
        int active = 1;

        while (active && current_time < T[n]) {
            real wait = exponential_rng(lambda_n);
            if (current_time + wait > T[n]) {
                break;
            } else {
                current_time += wait;
                x += 1;
                tx = current_time;
                if (bernoulli_rng(p_n)) {
                    active = 0;
                }
            }
        }
        X_rep[n] = x;
        t_x_rep[n] = tx;
    }
}
