from typing import List

import cvxpy as cvx
import numpy as np
import pandas as pd

from ..._portfolio.portfolio import PortfolioAsset, Portfolio
from ...common.enums import Currency


def compute(assets: List[PortfolioAsset], samples_count,
            start_period: pd.Period, end_period: pd.Period,
            currency: Currency):
    asset_rors = [a.rate_of_return().values for a in assets]
    mu = np.mean(asset_rors, axis=1)
    sigma = np.cov(asset_rors)

    optimal_portfolios: List[Portfolio] = []

    for idx, return_trg in enumerate(np.linspace(mu.min(), mu.max(), num=samples_count)):
        w = cvx.Variable(len(assets))
        ret = mu.T * w
        risk = cvx.quad_form(w, sigma)
        problem = cvx.Problem(cvx.Minimize(risk),
                              [cvx.sum(w) == 1,
                               w >= 0,
                               cvx.abs(ret - return_trg) <= 0.00001,
                               ])
        problem.solve()

        p = Portfolio(assets=assets,
                      weights=w.value,
                      start_period=start_period,
                      end_period=end_period,
                      currency=currency)
        assert p.rate_of_return().start_period == start_period + 1
        assert p.rate_of_return().end_period == end_period
        optimal_portfolios.append(p)

    return optimal_portfolios
