.. image:: https://travis-ci.org/okama-io/yapo.svg?branch=master
    :target: https://travis-ci.org/okama-io/yapo

YAPO
====

yapo is a Python package developed for quantitative finance and investments tasks.  Additionally, it has the broader goal of becoming the most useful and flexible open source tool for financial data analysis available in any language.

Some useful applications of yapo are being presented in the community developed frontend okama.io.

Ecosystem
•	Python package
•	Financial and Economic data for several markets
•	okama.io as frontend (TypeScript and Angular based)
•	JS Widgets
•	Financial terms glossary
•	Community

Yapo Package Main Features
•	New TimeSeries format for financial data
•	Error free manipulations with financial data (comprehensive testing)
•	Asset analysis tools for asset correlations and main performance indicators
•	Portfolio analysis tools for asset class allocation and portfolio backtesting
•	Portfolio optimization and efficient frontier visualization
•	Monte Carlo Simulation for financial assets and investment portfolios
•	Bonds key properties calculations
•	Access to financial data from different stock markets: EOD close, adjusted close, currency rates, inflation

Financial and Economic data with API
•	GraphQL API for data access
•	EOD adjusted close for NYSE and NASDAQ stocks and ETF
•	EOD close for Moscow Exchange stocks and ETF
•	EOD close for Russian open-end funds
•	EOD for main stock and bond Indexes
•	Bonds data for Moscow Exchange traded securities: EOD close, coupons, maturity
•	Exchange Rates for USD, EUR, RUB,
•	Inflation for US, EU and Russia
•	Key interest rates for US, EU and Russia
•	History of deposit rates for top 10 banks of Russia

Installation
??????
Jupyter Notebooks
Links from JupyterHub

Dependencies

Yapo has the following dependencies:
PyContracts>=1.8,<1.9
numpy>=1.15,<1.16
quandl>=3.4,<3.5
serum>=5.1.0,<5.2.0
pandas>=0.23,<0.24
pybuilder>=0.11,<0.12

Getting Help

For usage questions, the best place to go to is community.

Discussion and Development

Most development discussion is taking place on github in this repo. Further, the community forum can also be used for general questions and discussions, and a Gitter channel is available for quick development related questions.

Issues

We encourage you to report issues using the Github tracker. We welcome all kinds of issues, especially those related to correctness, documentation, performance, and feature requests.

Contributing to yapo

All contributions, bug reports, bug fixes, documentation improvements, enhancements, frontend implementation and ideas are welcome.
Here are some simple ways to start contributing immediately:
•	Browse the issue tracker to find issues that interest you
•	Read the yapo source code and improve the documentation, or address TODOs
•	Improve the example library and tutorials
•	Bug reports are an important part of making yapo more stable
•	Run the library through frontend on okama.io and suggest improvements (design, UI, new functionality)

The code is hosted on GitHub. To contribute you will need to sign up for a free GitHub account. We use Git for version control to allow many people to work together on the project.

Contributions should be submitted as pull requests. A member of the yapo development team will review the pull request and guide you through the contributing process.

Before starting work on your contribution, please read the contributing guide.

Feel free to ask questions on the community.

License

MIT
