from typing import List

import cvxpy as cvx
import numpy as np
import pandas as pd

from ..._portfolio.portfolio import PortfolioAsset
from ..._settings import _MONTHS_PER_YEAR
from ...common.enums import Currency


class EfficientFrontierPoint:
    def __init__(self, weights: np.array, return_yearly: float, return_: float, risk: float, risk_yearly: float):
        self.weights = weights
        self.return_ = return_
        self.return_yearly = return_yearly
        self.risk_yearly = risk_yearly
        self.risk = risk


class EfficientFrontier:
    def __init__(self,
                 start_period: pd.Period, end_period: pd.Period,
                 currency: Currency):
        self.points: List[EfficientFrontierPoint] = []

    def add_point(self, point: EfficientFrontierPoint):
        self.points.append(point)


def compute(assets: List[PortfolioAsset], samples_count,
            start_period: pd.Period, end_period: pd.Period,
            currency: Currency) -> EfficientFrontier:
    asset_rors = [a.get_return().values for a in assets]
    mu = np.mean(asset_rors, axis=1)
    sigma = np.cov(asset_rors)

    efficient_frontier = EfficientFrontier(start_period=start_period, end_period=end_period, currency=currency)

    for idx, return_trg in enumerate(np.linspace(mu.min(), mu.max(), num=samples_count)):
        w = cvx.Variable(len(assets))
        ret = mu.T * w
        risk = cvx.quad_form(w, sigma)
        problem = cvx.Problem(objective=cvx.Minimize(risk),
                              constraints=[cvx.sum(w) == 1,
                                           w >= 0,
                                           cvx.abs(ret - return_trg) <= 1e-4,
                                           ])
        problem.solve(solver='ECOS_BB')

        ret_yearly = (ret.value + 1.) ** _MONTHS_PER_YEAR - 1.
        risk_yearly = \
            (risk.value ** 2 + (ret.value + 1.) ** 2) ** _MONTHS_PER_YEAR - (ret.value + 1.) ** (_MONTHS_PER_YEAR * 2)
        risk_yearly = np.sqrt(risk_yearly)
        point = EfficientFrontierPoint(weights=w.value,
                                       return_=ret.value,
                                       return_yearly=ret_yearly,
                                       risk_yearly=risk_yearly,
                                       risk=risk.value)
        efficient_frontier.add_point(point)

    return efficient_frontier
