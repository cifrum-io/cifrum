|Travis|_ |Gitter|_

.. |Travis| image:: https://travis-ci.org/okama-io/yapo.svg?branch=master
.. _Travis: https://travis-ci.org/okama-io/yapo

.. |Gitter| image:: https://badges.gitter.im/okama-io/community.svg
.. _Gitter: https://gitter.im/okama-io/community

.. contents:: Contents of this Document

YAPO
====

``yapo`` is a Python library developed to solve quantitative finance and
investments tasks. Additionally, it has the broader goal to become the most
useful and flexible open sourced tool for financial data analysis available in
popular programming languages.

Applications
------------

Useful applications of ``yapo`` in the community developed are as follows:

* Fully-functional ``Angular2+``-based web-application `okama.io`_
* `tell us more <okama-discourse_>`_ if you know any

The Ecosystem
-------------

The ecosystem around the library consists of:

* The Python package
* Financial and Economic data for several markets
* ``Angular2+`` web-application `okama.io`_
* `Financial terms glossary <okama-glossary_>`_
* `The community <okama-discourse_>`_

Main Features
-------------

* ``[x]`` ``TimeSeries`` to verify correctness of financial data manipulations
* ``[x]`` Error-free manipulations with financial data checked by tests and active community
* ``[x]`` Asset analysis tools for asset correlations and main performance indicators
* ``[x]`` Portfolio analysis tools for asset class allocation and portfolio backtesting
* ``[ ]`` Portfolio optimization and efficient frontier visualization
* ``[ ]`` Monte Carlo Simulation for financial assets and investment portfolios
* ``[ ]`` Bonds key properties calculations
* ``[x]`` Access to financial data from different stock markets: EOD close, adjusted close, currency rates, inflation
* ``[x]`` Financial and Economic data with API with GraphQL data access
* ``[x]`` EOD adjusted close for NYSE and NASDAQ stocks and ETF
* ``[ ]`` EOD close for Moscow Exchange stocks and ETF
* ``[ ]`` EOD close for Russian open-end funds
* ``[x]`` EOD for main stock and bond Indexes
* ``[ ]`` Bonds data for Moscow Exchange-traded securities: EOD close, coupons, maturity
* ``[x]`` Exchange Rates for USD, EUR, RUB,
* ``[x]`` Inflation for US, EU, and Russia
* ``[x]`` Key interest rates for US, EU, and Russia
* ``[x]`` History of deposit rates for top 10 banks of Russia

Installation
------------

TODO

Jupyter Notebooks
-----------------

TODO

Dependencies
------------

The library dependencies are listed at
`pyproject.toml <https://github.com/okama-io/yapo/blob/readme/pyproject.toml#L10>`_.

Discussion, Development, and Getting Help
-----------------------------------------

- The development discussion takes place at `the GitHub repo
  <yapo-github-issues_>`_. We encourage you to report issues using `the Github
  tracker <yapo-github-issues_>`_. We welcome all kinds of issues related to
  correctness, documentation, performance, and feature requests.
- `The community forum <okama-discourse_>`_ can also be used for general
  questions and discussions.
- Finally, the `Gitter channel <Gitter_>`_ is available for the development
  related questions.

Contributing
------------

All contributions, bug reports, bug fixes, documentation improvements,
enhancements, frontend implementation, and ideas are welcomed and the subject
to discuss. Simple ways to start contributing immediately:

- Browse the issue tracker to find issues that interest you
- Read the source code and improve the documentation or address TODOs
- Improve the example library and tutorials
- Bug reports are an important part of making the library more stable
- Run the library through `the okama.io frontend <okama.io_>`_ and suggest
  improvements in design, UI, and functionality

The code is hosted at `GitHub <yapo-github_>`_. You need an GitHub account
which is free to contribute to the project. We use git for the version control
to enable distributed work on the project.

Contributions should be submitted as a pull request. A member of the
development team will review the pull request and guide you through the
contributing process.

Before starting work on your contribution, please read the contributing guide.

Feel free to ask questions at `the community <okama-discourse_>`_.

License
-------

`MIT <license_>`_

.. _okama.io: https://okama.io/
.. _okama-glossary: https://okama.io/#/glossary
.. _okama-discourse: http://community.okama.io
.. _yapo-github: https://github.com/okama-io/yapo
.. _yapo-github-issues: https://github.com/okama-io/yapo/issues
.. _license: https://github.com/okama-io/yapo/blob/master/LICENSE
