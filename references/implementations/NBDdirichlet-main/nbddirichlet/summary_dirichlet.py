# summary_dirichlet

import numpy as np
import pandas as pd

def summary_dirichlet(dobj):
    M = dobj.M  # Use the current M value
    result = {}
    summary_types = ["buy", "freq", "heavy", "dup"]
    freq_cutoff = 5  # You may want to make this configurable
    heavy_limit = range(5, dobj.nstar + 1)  # You may want to make this configurable
    dup_brand = 0  # You may want to make this configurable
    digits = 4  # You may want to make this configurable

    for tt in summary_types:
        if tt == "buy":
            r = np.zeros((dobj.nbrand, 3))
            for j in range(dobj.nbrand):
                r[j, 0] = dobj.brand_pen(j)
                r[j, 1] = dobj.brand_buyrate(j)
                r[j, 2] = dobj.wp(j)

            result[tt] = pd.DataFrame(r, index=dobj.brand_name, 
                                      columns=["pen_brand", "pur_brand", "pur_cat"]).round(digits)

        elif tt == "freq":
            def prob_r(r, j):
                return sum(dobj.Pn(n) * dobj.p_rj_n(r, n, j) for n in range(r, dobj.nstar + 1))

            r = np.zeros((dobj.nbrand, freq_cutoff + 2))
            for j in range(dobj.nbrand):
                r[j, :] = [prob_r(r, j) for r in range(freq_cutoff + 1)] + [sum(prob_r(r, j) for r in range(freq_cutoff + 1, dobj.nstar + 1))]

            result[tt] = pd.DataFrame(r, index=dobj.brand_name, 
                                      columns=[str(i) for i in range(freq_cutoff + 1)] + [f"{freq_cutoff+1}+"]).round(digits)

        elif tt == "heavy":
            Pn_sum = sum(dobj.Pn(n) for n in heavy_limit)
            r = np.zeros((dobj.nbrand, 2))
            for j in range(dobj.nbrand):
                p0 = 1 - dobj.brand_pen(j, limit=heavy_limit)
                r[j, 0] = 1 - p0 / Pn_sum
                r[j, 1] = dobj.brand_buyrate(j, limit=heavy_limit) * dobj.brand_pen(j) / (Pn_sum - p0)

            result[tt] = pd.DataFrame(r, index=dobj.brand_name, columns=["Penetration", "Avg Purchase Freq"]).round(digits)

        elif tt == "dup":
            k = dup_brand
            r = np.zeros(dobj.nbrand)
            r[k] = 1
            b_k = dobj.brand_pen(k)
            others = [j for j in range(dobj.nbrand) if j != k]

            for j in others:
                p0 = sum(dobj.Pn(i) * dobj.p_rj_n(0, i, [k, j]) for i in range(dobj.nstar + 1))
                b_j_k = 1 - p0
                b_j = dobj.brand_pen(j)
                b_jk = b_j + b_k - b_j_k
                b_j_given_k = b_jk / b_k
                r[j] = b_j_given_k

            result[tt] = pd.Series(r, index=dobj.brand_name).round(digits)

    return result