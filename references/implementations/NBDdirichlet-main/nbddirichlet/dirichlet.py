# dirichlet.py

import numpy as np
from scipy import stats, special, optimize
import pandas as pd  # Add this import statement

class Dirichlet:
    def __init__(self, cat_pen, cat_buyrate, brand_share, brand_pen_obs, brand_name=None,
                 cat_pur_var=None, nstar=50, max_S=30, max_K=30, check=False):
        """
        Initializes the Dirichlet model with the given parameters.

        Parameters:
            cat_pen (float): Category penetration.
            cat_buyrate (float): Category buying rate.
            brand_share (list of float): List of brand market shares.
            brand_pen_obs (list of float): List of observed brand penetrations.
            brand_name (list of str, optional): List of brand names. Defaults to None.
            cat_pur_var (float, optional): Category purchase variance. Defaults to None.
            nstar (int, optional): Maximum number of purchases. Defaults to 50.
            max_S (int, optional): Maximum value of S parameter. Defaults to 30.
            max_K (int, optional): Maximum value of K parameter. Defaults to 30.
            check (bool, optional): Flag for checking. Defaults to False.

        Returns:
            None
        """
        self.cat_pen = cat_pen
        self.cat_buyrate = cat_buyrate
        self.brand_share = brand_share
        self.brand_pen_obs = brand_pen_obs
        self.nbrand = len(brand_pen_obs)
        self.brand_name = brand_name if brand_name is not None else [f"B{i+1}" for i in range(self.nbrand)]
        self.cat_pur_var = cat_pur_var
        self.nstar = nstar
        self.max_S = max_S
        self.max_K = max_K
        self.check = check

        self.M0 = self.M = cat_pen * cat_buyrate
        self.K = self._estimate_K()
        self.S = self._estimate_S()

    def _estimate_K(self):
        """
        Estimates the parameter K based on the given conditions.

        Returns:
            float: The estimated value of parameter K.
        """
        if self.cat_pur_var is None:
            cp = np.log(1 - self.cat_pen)
            eq1 = lambda K: (K * np.log(1 + self.M / K) + cp) ** 2
            r = optimize.minimize_scalar(eq1, bounds=(0.0001, self.max_K), method='bounded')
            return r.x
        else:
            return self.M ** 2 / (self.cat_pur_var - self.M)

    def _estimate_S(self):
        """
        Estimates the value of S using the given observations.

        Returns:
            float: The estimated value of S.
        """
        def eq2(S, j):
            """
            Calculate the squared difference between the target penetration rate and the observed penetration rate for a given brand.

            Parameters:
                S (float): The estimated value of parameter S.
                j (int): The index of the brand.

            Returns:
                float: The squared difference between the target penetration rate and the observed penetration rate.
            """
            t_pen = 1 - sum(self.Pn(i) * self.pzeron(i, j, S) for i in range(self.nstar + 1))
            o_pen = self.brand_pen_obs[j]
            return (t_pen - o_pen) ** 2

        Sall = [optimize.minimize_scalar(eq2, args=(j,), bounds=(0.0001, self.max_S), method='bounded').x
                for j in range(self.nbrand)]

        bp = np.percentile(Sall, [25, 75])
        outliers = [s for s in Sall if s < bp[0] - 1.5 * (bp[1] - bp[0]) or s > bp[1] + 1.5 * (bp[1] - bp[0])]
        schoose = [s for s in Sall if s not in outliers]
        
        if not schoose:  # If all values are outliers, use the median
            return np.median(Sall)
        
        return np.average(schoose, weights=[self.brand_share[i] for i, s in enumerate(Sall) if s in schoose])

    def pzeron(self, n, j, S):
        """
        Calculate the probability of observing zero events for a given brand and time period.

        Parameters:
            self: Instance of the Dirichlet class.
            n (int): The number of events.
            j (int): The index of the brand.
            S (float): The value of parameter S.

        Returns:
            float: The probability of observing zero events.
        """
        alphaj = S * self.brand_share[j]
        if n == 0:
            return 1
        a = np.arange(n)
        num = np.log(S - alphaj + a)
        den = np.log(S + a)
        return np.exp(np.sum(num - den))

    def p_rj_n(self, rj, n, j):
        """
        Calculate the probability of choosing a certain brand given the number of events, brand share, and total parameter S.
        
        Parameters:
            self: Instance of the Dirichlet class.
            rj (int): Number of events for brand j.
            n (int): The total number of events.
            j (int or list): The index or indices of the brand(s).
        
        Returns:
            float: The probability of choosing the specified brand(s) given the parameters.
        """
        alphaj = self.S * np.sum([self.brand_share[x] for x in j]) if isinstance(j, (list, np.ndarray)) else self.S * self.brand_share[j]
        return special.comb(n, rj) * special.beta(alphaj + rj, self.S - alphaj + n - rj) / special.beta(alphaj, self.S - alphaj)

    def Pn(self, n):
        """
        Calculate the probability of observing n events based on the parameters K, M, and the given input n.

        Parameters:
            n (int): The number of events.

        Returns:
            float: The probability of observing n events.
        """
        if n == 0:
            return np.exp(-self.K * np.log(1 + self.M / self.K))
        a = np.arange(n)
        g = np.sum(np.log(self.K + a) - np.log(1 + a))
        return np.exp(-self.K * np.log(1 + self.M / self.K) + g + n * np.log(self.M / (self.M + self.K)))

    def brand_pen(self, j, limit=None):
        """
        Calculate the brand penetration given the brand index j and an optional limit.
        
        Parameters:
            self: The Dirichlet object.
            j (int): The index of the brand.
            limit (range, optional): The range of values to consider. Defaults to None.
        
        Returns:
            float: The brand penetration.
        """
        if limit is None:
            limit = range(self.nstar + 1)
        p0 = sum(self.Pn(i) * self.p_rj_n(0, i, j) for i in limit)
        return 1 - p0

    def brand_buyrate(self, j, limit=None):
        """
        Calculate the buying rate for a specific brand.

        Args:
            j (int): The index of the brand.
            limit (range, optional): The range of values to consider. Defaults to None.

        Returns:
            float: The buying rate.
        """
        if limit is None:
            limit = range(1, self.nstar + 1)
        
        def buyrate_n(n, j):
            rate = np.arange(1, n + 1)
            return np.sum(rate * self.p_rj_n(rate, n, j))

        numerator = sum(self.Pn(n) * buyrate_n(n, j) for n in limit)
        return numerator / self.brand_pen(j)

    def wp(self, j, limit=None):
        """
        Calculate the weighted probability for a specific brand.

        Args:
            self: The Dirichlet object.
            j (int): The index of the brand.
            limit (range, optional): The range of values to consider. Defaults to None.

        Returns:
            float: The weighted probability.
        """
        if limit is None:
            limit = range(1, self.nstar + 1)
        numerator = sum(n * self.Pn(n) * (1 - self.p_rj_n(0, n, j)) for n in limit)
        return numerator / self.brand_pen(j)

    def period_set(self, t):
        self.M = self.M0 * t
        self.K = self._estimate_K()
        # S remains unchanged
        # self.S = self._estimate_S()  # Remove this line

    def period_print(self):
        """
        Print the multiple of the base time period and the current value of M.

        This function calculates the multiple of the base time period by dividing M by M0 and prints it along with the current value of M.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        print(f"Multiple of Base Time Period: {self.M/self.M0:.2f}, Current M = {self.M}")

    def __str__(self):
        """
        Returns a string representation of the Dirichlet model with the number of brands.

        :return: A string with the format "Dirichlet Model with {self.nbrand} brands".
        :rtype: str
        """
        return f"Dirichlet Model with {self.nbrand} brands"

    def chi_square_test(self):
        observed = np.array(self.brand_pen_obs)
        expected = np.array([self.brand_pen(j) for j in range(self.nbrand)])
        
        # Normalize expected frequencies to sum to the same total as observed
        expected = expected * (observed.sum() / expected.sum())
        
        chi2, p_value = stats.chisquare(observed, expected)
        return chi2, p_value

    def mape(self):
        observed = np.array(self.brand_pen_obs)
        predicted = np.array([self.brand_pen(j) for j in range(self.nbrand)])
        return np.mean(np.abs((observed - predicted) / observed)) * 100

    def rmse(self):
        observed = np.array(self.brand_pen_obs)
        predicted = np.array([self.brand_pen(j) for j in range(self.nbrand)])
        return np.sqrt(np.mean((observed - predicted)**2))

    def correlation(self):
        observed = np.array(self.brand_pen_obs)
        predicted = np.array([self.brand_pen(j) for j in range(self.nbrand)])
        return np.corrcoef(observed, predicted)[0, 1]

    def percent_differences(self):
        observed = np.array(self.brand_pen_obs)
        predicted = np.array([self.brand_pen(j) for j in range(self.nbrand)])
        percent_diff = (predicted - observed) / observed * 100
        return pd.Series(percent_diff, index=self.brand_name)