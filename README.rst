+----------+----------------------------------------+
| Status   | |Travis|_ |Gitter|_ |Pepy|_ |Codecov|_ |
+----------+----------------------------------------+
| Examples | |Binder|_                              |
+----------+----------------------------------------+
| Support  | |Donate|_                              |
+----------+----------------------------------------+

.. |Travis| image:: https://travis-ci.org/okama-io/cifrum.svg?branch=master
.. _Travis: https://travis-ci.org/okama-io/cifrum

.. |Gitter| image:: https://badges.gitter.im/okama-io/community.svg
.. _Gitter: https://gitter.im/okama-io/community

.. |Pepy| image:: https://pepy.tech/badge/cifrum
.. _Pepy: https://pepy.tech/badge/cifrum

.. |Codecov| image:: https://codecov.io/gh/okama-io/cifrum/branch/master/graph/badge.svg
.. _Codecov: https://codecov.io/gh/okama-io/cifrum

.. |Binder| image:: https://mybinder.org/badge_logo.svg
.. _Binder: https://mybinder.org/v2/gh/okama-io/cifrum/master?filepath=examples

.. |Donate| image:: https://img.shields.io/badge/Donate-PayPal-green.svg
.. _Donate: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=SC8RT7A7FT5HC&currency_code=USD&source=url

**cifrum** |--| a flexible and easy-to-use Python 3.6+ library for analysis &
manipulation with financial & economic data

**cifrum** is released under the terms of GPL license. We appreciate all kinds of
contributions, financial resources to maintain the project and accelerate its
development.

If you find **cifrum** useful in your financial research, private investments or
company, please consider making a donation to the project commensurate with
your resources. Any amount helps!

All donations will be used strictly to fund cifrum development supporting
activities: the Python library development, `frontend solutions <okama.io_>`_,
documentation and maintenance work, and paying for hosting costs of servers.

If you are interested in donating to the project, please, use the Paypal
button: |Donate|_

.. contents:: Contents of this Document

Introduction
============

``cifrum`` is a Python library developed to solve quantitative finance and
investments tasks. Additionally, it has the broader goal to become the most
useful and flexible open sourced tool for financial data analysis available in
popular programming languages.

Applications
============

Useful applications of ``cifrum`` in the community developed are as follows:

* Fully-functional ``Angular2+``-based web-application `okama.io`_
* `tell us more <okama-discourse_>`_ if you know any

The Ecosystem
=============

The ecosystem around the library consists of:

* The Python package
* Financial and Economic data for several markets
* ``Angular2+`` web-application `okama.io`_
* `Financial terms glossary <okama-glossary_>`_
* `The community <okama-discourse_>`_

Main Features
=============

* ``[x]`` ``TimeSeries`` to verify correctness of financial data manipulations
* ``[x]`` Error-free manipulations with financial data checked by tests and active community
* ``[x]`` Asset analysis tools for asset correlations and main performance indicators
* ``[ ]`` Portfolio analysis tools for asset class allocation and portfolio backtesting
* ``[ ]`` Portfolio optimization and efficient frontier visualization
* ``[ ]`` Monte Carlo Simulation for financial assets and investment portfolios
* ``[ ]`` Bonds key properties calculations
* ``[x]`` Access to financial data from different stock markets: EOD close, adjusted close, currency rates, inflation
* ``[x]`` Financial and Economic data with API with GraphQL data access

Financial and Economic data freely available
============================================
* ``[x]`` EOD adjusted close for NYSE and NASDAQ stocks and ETF
* ``[x]`` EOD close for Moscow Exchange stocks and ETF
* ``[x]`` EOD close for Russian open-end funds
* ``[ ]`` EOD close for BSE and NSE stocks and ETF (India)
* ``[x]`` EOD for main stock and bond Indexes
* ``[ ]`` Bonds data for Moscow Exchange-traded securities: EOD close, coupons, maturity
* ``[x]`` Exchange Rates for USD, EUR, RUB
* ``[ ]`` Exchange Rates for Bitcoin [BTC], Ethereum [ETH], Binance Coin [BNB] and other cryptocurrencies
* ``[x]`` Inflation for US, EU, and Russia
* ``[x]`` Key interest rates for US, EU, and Russia
* ``[x]`` History of deposit rates for top 10 banks of Russia

Installation
============

The library is published to `pypi.org <https://pypi.org/project/cifrum/>`_.

Install stable version:

.. code :: bash

    pip install -U cifrum


Install development version:

.. code :: bash

    pip install -U git+https://github.com/okama-io/cifrum.git


Jupyter Notebooks
=================

The `examples <https://github.com/okama-io/cifrum/tree/master/examples>`_ folder contains Jupyter notebooks
that show how to use the library parts in depth.

`examples <https://github.com/okama-io/cifrum/tree/master/examples>`_ are also compatible with
binder. You can try it by pressing the |Binder|_ button.

Dependencies
============

The library dependencies are listed at
`pyproject.toml <https://github.com/okama-io/cifrum/blob/master/pyproject.toml>`_ under
``[tool.poetry.dependencies]`` section.

Discussion, Development, and Getting Help
=========================================

- The development discussion takes place at `the GitHub repo
  <cifrum-github-issues_>`_. We encourage you to report issues using `the Github
  tracker <cifrum-github-issues_>`_. We welcome all kinds of issues related to
  correctness, documentation, performance, and feature requests.
- `The community forum <okama-discourse_>`_ can also be used for general
  questions and discussions.
- Finally, the `Gitter channel <Gitter_>`_ is available for the development
  related questions.

Contributing
============

All contributions, bug reports, bug fixes, documentation improvements,
enhancements, frontend implementation, and ideas are welcomed and the subject
to discuss. Simple ways to start contributing immediately:

- Browse the issue tracker to find issues that interest you
- Read the source code and improve the documentation or address TODOs
- Improve the example library and tutorials
- Bug reports are an important part of making the library more stable
- Run the library through `the okama.io frontend <okama.io_>`_ and suggest
  improvements in design, UI, and functionality

The code is hosted at `GitHub <cifrum-github_>`_. You need an GitHub account
which is free to contribute to the project. We use git for the version control
to enable distributed work on the project.

Contributions should be submitted as a pull request. A member of the
development team will review the pull request and guide you through the
contributing process.

Feel free to ask questions at `the community <okama-discourse_>`_.

License
=======

`GPL <license_>`_

.. |--| unicode:: U+2013
.. _okama.io: https://okama.io/
.. _okama-glossary: https://okama.io/#/glossary
.. _okama-discourse: http://community.okama.io
.. _cifrum-github: https://github.com/okama-io/cifrum
.. _cifrum-github-issues: https://github.com/okama-io/cifrum/issues
.. _license: https://github.com/okama-io/cifrum/blob/master/LICENSE
