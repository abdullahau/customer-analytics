
data {
    int<lower=0> N;
    vector<lower=0>[N] T;
}

generated quantities {
    real r = weibull_rng(2, 1);
    real alpha = weibull_rng(2, 10);
    real phi_dropout = uniform_rng(0, 1);
    real kappa_dropout = pareto_rng(1, 1);

    real a = phi_dropout * kappa_dropout;
    real b = (1 - phi_dropout) * kappa_dropout;

    array[N] int X_rep;
    vector[N] Tx_rep;

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
        Tx_rep[n] = tx;
    }
}
