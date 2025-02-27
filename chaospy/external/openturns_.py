# -*- coding: utf-8 -*-
"""
`OpenTURNS`_ is an open source initiative for the treatment of uncertainties,
risks and statistics in a structured industrial approach. It is a mature
toolkit with a lot of functionality beyond what ``chaospy`` delivers. If one
wants to combine the strength of the two projects, it is possible to interpret
distributions in `OpenTURNS`_ as ``chaospy`` distributions or vise versa.

To interpret a ``chaospy`` distribution as an `OpenTURNS`_ distribution, see
the `OpenTURNS distribution wrapper`_.

To interpret an `OpenTURNS`_ distribution as a ``chaospy`` distribution, it is
possible to use the :class:`OpenTURNSDist` wrapper. For example to interpret
a simple univariate Gaussian random variable::

    >>> import openturns
    >>> distribution = chaospy.OpenTURNSDist(openturns.Normal(0, 1))
    >>> print(distribution)
    OpenTURNSDist([Normal(mu = 0, sigma = 1)])

This distribution then behaves as a normal ``chaospy`` distribution::

    >>> print(numpy.around(distribution.pdf([-1, 0, 1]), 4))
    [0.242  0.3989 0.242 ]
    >>> print(distribution.mom([0, 1, 2]))
    [1. 0. 1.]

The wrapper also supports multivariate distributions::

    >>> composed_distribution = openturns.ComposedDistribution([
    ...     openturns.Triangular(-1, 0, 1), openturns.Uniform(-1, 1)])
    >>> mv_distribution = chaospy.OpenTURNSDist(composed_distribution)
    >>> print(mv_distribution)  # doctest: +NORMALIZE_WHITESPACE
    OpenTURNSDist([Triangular(a = -1, m = 0, b = 1),
                   Uniform(a = -1, b = 1)])
    >>> print(numpy.around(mv_distribution.sample(4), 4))
    [[ 0.1676 -0.5204  0.6847 -0.018 ]
     [ 0.7449 -0.5753 -0.9186 -0.2056]]

As a shorthand, it is also possible to construct multivariate distributions
form lists::

    >>> mv_distribution = chaospy.OpenTURNSDist([
    ...     openturns.Triangular(-1, 0, 1), openturns.Uniform(-1, 1)])
    >>> print(mv_distribution)  # doctest: +NORMALIZE_WHITESPACE
    OpenTURNSDist([Triangular(a = -1, m = 0, b = 1),
                   Uniform(a = -1, b = 1)])

Though multivariate distributions are supported, dependencies are not::

    >>> correlation = openturns.CorrelationMatrix(2)
    >>> correlation[0, 1] = 0.3
    >>> copula = openturns.NormalCopula(correlation)
    >>> dependent_distribution = openturns.ComposedDistribution(
    ...     [openturns.Normal(), openturns.Uniform()], copula)
    >>> chaospy.OpenTURNSDist(dependent_distribution)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    chaospy...DependencyError: Stochastically dependent OpenTURNS distribution unsupported

.. _OpenTURNS distribution wrapper: http://openturns.github.io/\
openturns/latest/user_manual/_generated/openturns.ChaospyDistribution.html
"""
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
import numpy

from ..distributions import Dist, J, DependencyError


class openturns_dist(Dist):
    """One dimensional OpenTURNS distribution."""

    def __init__(self, distribution):
        """
        Args:
            distribution (openturns.Distribution):
                Distribution created in OpenTURNS.
        """
        assert distribution.isContinuous(), (
            "Only continuous distributions are supported")
        Dist.__init__(self)
        self.distribution = distribution

    def _pdf(self, x_loc):
        return numpy.array(self.distribution.computePDF(
            numpy.atleast_2d(x_loc).T).asPoint())

    def _cdf(self, x_loc):
        return numpy.array(self.distribution.computeCDF(
            numpy.atleast_2d(x_loc).T).asPoint())

    def _ppf(self, q_loc):
        return numpy.array(self.distribution.computeQuantile(
            q_loc[0]).asPoint())

    def _bnd(self, x_loc):
        del x_loc
        rng = self.distribution.getRange()
        return rng.getLowerBound()[0], rng.getUpperBound()[0]

    def _mom(self, k_loc):
        return self.distribution.getMoment(int(k_loc))[0]

    def __str__(self):
        return str(self.distribution)


class OpenTURNSDist(J):
    """
    OpenTURNS distribution constructor.

    Args:
        distribution (openturns.Distribution):
            Distribution created in OpenTURNS.

    Examples:
        >>> from openturns import ComposedDistribution, Normal
        >>> ot_distribution = ComposedDistribution([Normal(), Normal()])
        >>> distribution = chaospy.OpenTURNSDist(ot_distribution)
        >>> print(distribution)  # doctest: +NORMALIZE_WHITESPACE
        OpenTURNSDist([Normal(mu = 0, sigma = 1),
                       Normal(mu = 0, sigma = 1)])
    """

    def __init__(self, distribution):
        from openturns import ComposedDistribution, ContinuousDistribution
        if isinstance(distribution, ComposedDistribution):
            if not distribution.hasIndependentCopula():
                raise DependencyError("Stochastically dependent "
                                      "OpenTURNS distribution unsupported")
            distributions = [
                openturns_dist(dist)
                for dist in distribution.getDistributionCollection()
            ]
        elif isinstance(distribution, ContinuousDistribution):
            distributions = [openturns_dist(distribution)]
        else:
            assert isinstance(distribution, Iterable) and all([
                isinstance(dist, ContinuousDistribution)
                for dist in distribution
            ]), "Only (iterable of) continuous OpenTURNS distributions supported"
            distributions = [openturns_dist(dist) for dist in distribution]
        J.__init__(self, *distributions)

    def __str__(self):
        args = [str(self.prm[key]) for key in sorted(list(self.prm))]
        return self.__class__.__name__ + "([" + ", ".join(args) + "])"
