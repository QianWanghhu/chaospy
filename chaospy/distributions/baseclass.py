"""
Constructing custom probability distributions is done by subclassing the
distribution :class:`~chaospy.distributions.baseclass.Dist`::

    >>> class Uniform(Dist):
    ...     def __init__(self, lo=0, up=1):
    ...         '''Initializer.'''
    ...         Dist.__init__(self, lo=lo, up=up)
    ...     def _cdf(self, x_data, lo, up):
    ...         '''Cumulative distribution function.'''
    ...         return (x_data-lo)/(up-lo)
    ...     def _bnd(self, x_data, lo, up):
    ...         '''Lower and upper bounds.'''
    ...         return lo, up
    ...     def _pdf(self, x_data, lo, up):
    ...         '''Probability density function.'''
    ...         return 1./(up-lo)
    ...     def _ppf(self, q_data, lo, up):
    ...         '''Point percentile function.'''
    ...         return q_data*(up-lo) + lo

Usage is then straight forward::

    >>> dist = Uniform(-3, 3)
    >>> print(dist.fwd([-3, 0, 3])) # Forward Rosenblatt transformation
    [0.  0.5 1. ]

Here the two methods ``_cdf`` and ``_bnd`` are absolute requirements, while all
the others are nice to have. In addition to the once listed, it is also
possible to define the following methods:

``_mom``
    Method for creating raw statistical moments, used by the ``mom`` method.
``_ttr``
    Method for creating coefficients from three terms recursion method, used to
    perform "analytical" Stiltjes' method.
"""
import types
import numpy

from . import evaluation, approximation


class StochasticallyDependentError(Exception):
    """Error related to stochastically dependent variables."""


class Dist(object):
    """Baseclass for all probability distributions."""

    __array_priority__ = 9000
    """Numpy override variable."""
    _repr = None

    interpret_as_integer = False
    """
    Flag indicating that return value from the methods sample, range and inv
    should be interpreted as integers instead of floating point.
    """

    def __init__(self, **prm):
        """
        Args:
            prm (numpy.ndarray):
                Other optional parameters. Will be assumed when calling any
                sub-functions.
        """
        self.prm = prm


    def range(self, x_data=None):
        """
        Generate the upper and lower bounds of a distribution.

        Args:
            x_data (numpy.ndarray) :
                The bounds might vary over the sample space. By providing
                x_data you can specify where in the space the bound should be
                taken.  If omitted, a (pseudo-)random sample is used.

        Returns:
            (numpy.ndarray):
                The lower (out[0]) and upper (out[1]) bound where
                out.shape=(2,)+x_data.shape
        """
        if x_data is None:
            try:
                x_data = evaluation.evaluate_inverse(
                    self, numpy.array([[0.5]]*len(self)))
            except StochasticallyDependentError:
                x_data = approximation.find_interior_point(self)
            shape = (len(self),)
            if hasattr(self, "_range"):
                return self._range(x_data, {})
        else:
            x_data = numpy.asfarray(x_data)
            shape = x_data.shape
            x_data = x_data.reshape(len(self), -1)

        q_data = evaluation.evaluate_bound(self, x_data)
        q_data = q_data.reshape((2,)+shape)
        if self.interpret_as_integer:
            q_data = q_data.astype(int)
        return q_data

    def fwd(self, x_data):
        """
        Forward Rosenblatt transformation.

        Args:
            x_data (numpy.ndarray):
                Location for the distribution function. ``x_data.shape`` must
                be compatible with distribution shape.

        Returns:
            (numpy.ndarray):
                Evaluated distribution function values, where
                ``out.shape==x_data.shape``.
        """
        x_data = numpy.asfarray(x_data)
        shape = x_data.shape
        x_data = x_data.reshape(len(self), -1)

        lower, upper = evaluation.evaluate_bound(self, x_data)
        q_data = numpy.zeros(x_data.shape)
        indices = x_data > upper
        q_data[indices] = 1
        indices = ~indices & (x_data >= lower)

        q_data[indices] = numpy.clip(evaluation.evaluate_forward(
            self, x_data), a_min=0, a_max=1)[indices]

        q_data = q_data.reshape(shape)
        return q_data

    def cdf(self, x_data):
        """
        Cumulative distribution function.

        Note that chaospy only supports cumulative distribution functions for
        stochastically independent distributions.

        Args:
            x_data (numpy.ndarray):
                Location for the distribution function. Assumes that
                ``len(x_data) == len(distribution)``.

        Returns:
            (numpy.ndarray):
                Evaluated distribution function values, where output has shape
                ``x_data.shape`` in one dimension and ``x_data.shape[1:]`` in
                higher dimensions.
        """
        if len(self) > 1 and evaluation.get_dependencies(*self):
            raise StochasticallyDependentError(
                "Cumulative distribution does not support dependencies.")
        q_data = self.fwd(x_data)
        if len(self) > 1:
            q_data = numpy.prod(q_data, 0)
        return q_data

    def inv(self, q_data, max_iterations=100, tollerance=1e-5):
        """
        Inverse Rosenblatt transformation.

        If possible the transformation is done analytically. If not possible,
        transformation is approximated using an algorithm that alternates
        between Newton-Raphson and binary search.

        Args:
            q_data (numpy.ndarray):
                Probabilities to be inverse. If any values are outside ``[0,
                1]``, error will be raised. ``q_data.shape`` must be compatible
                with distribution shape.
            max_iterations (int):
                If approximation is used, this sets the maximum number of
                allowed iterations in the Newton-Raphson algorithm.
            tollerance (float):
                If approximation is used, this set the error tolerance level
                required to define a sample as converged.

        Returns:
            (numpy.ndarray):
                Inverted probability values where
                ``out.shape == q_data.shape``.
        """
        q_data = numpy.asfarray(q_data)
        assert numpy.all((q_data >= 0) & (q_data <= 1)), "sanitize your inputs!"
        shape = q_data.shape
        q_data = q_data.reshape(len(self), -1)
        x_data = evaluation.evaluate_inverse(self, q_data)
        lower, upper = evaluation.evaluate_bound(self, x_data)
        x_data = numpy.clip(x_data, a_min=lower, a_max=upper)
        x_data = x_data.reshape(shape)
        if self.interpret_as_integer:
            x_data = x_data.astype(int)
        return x_data

    def pdf(self, x_data, step=1e-7):
        """
        Probability density function.

        If possible the density will be calculated analytically. If not
        possible, it will be approximated by approximating the one-dimensional
        derivative of the forward Rosenblatt transformation and multiplying the
        component parts. Note that even if the distribution is multivariate,
        each component of the Rosenblatt is one-dimensional.

        Args:
            x_data (numpy.ndarray):
                Location for the density function. ``x_data.shape`` must be
                compatible with distribution shape.
            step (float, numpy.ndarray):
                If approximation is used, the step length given in the
                approximation of the derivative. If array provided, elements
                are used along each axis.

        Returns:
            (numpy.ndarray):
                Evaluated density function values. Shapes are related through
                the identity ``x_data.shape == dist.shape+out.shape``.
        """
        x_data = numpy.asfarray(x_data)
        shape = x_data.shape
        x_data = x_data.reshape(len(self), -1)

        lower, upper = evaluation.evaluate_bound(self, x_data)
        f_data = numpy.zeros(x_data.shape)
        indices = (x_data <= upper) & (x_data >= lower)
        f_data[indices] = evaluation.evaluate_density(self, x_data)[indices]
        f_data = f_data.reshape(shape)
        if len(self) > 1:
            f_data = numpy.prod(f_data, 0)
        return f_data

    def sample(self, size=(), rule="R", antithetic=None):
        """
        Create pseudo-random generated samples.

        By default, the samples are created using standard (pseudo-)random
        samples. However, if needed, the samples can also be created by either
        low-discrepancy sequences, and/or variance reduction techniques.

        Changing the sampling scheme, use the following ``rule`` flag:

        +-------+-------------------------------------------------+
        | key   | Description                                     |
        +=======+=================================================+
        | ``C`` | Roots of the first order Chebyshev polynomials. |
        +-------+-------------------------------------------------+
        | ``NC``| Chebyshev nodes adjusted to ensure nested.      |
        +-------+-------------------------------------------------+
        | ``K`` | Korobov lattice.                                |
        +-------+-------------------------------------------------+
        | ``R`` | Classical (Pseudo-)Random samples.              |
        +-------+-------------------------------------------------+
        | ``RG``| Regular spaced grid.                            |
        +-------+-------------------------------------------------+
        | ``NG``| Nested regular spaced grid.                     |
        +-------+-------------------------------------------------+
        | ``L`` | Latin hypercube samples.                        |
        +-------+-------------------------------------------------+
        | ``S`` | Sobol low-discrepancy sequence.                 |
        +-------+-------------------------------------------------+
        | ``H`` | Halton low-discrepancy sequence.                |
        +-------+-------------------------------------------------+
        | ``M`` | Hammersley low-discrepancy sequence.            |
        +-------+-------------------------------------------------+

        All samples are created on the ``[0, 1]``-hypercube, which then is
        mapped into the domain of the distribution using the inverse Rosenblatt
        transformation.

        Args:
            size (numpy.ndarray):
                The size of the samples to generate.
            rule (str):
                Indicator defining the sampling scheme.
            antithetic (bool, numpy.ndarray):
                If provided, will be used to setup antithetic variables. If
                array, defines the axes to mirror.

        Returns:
            (numpy.ndarray):
                Random samples with shape ``(len(self),)+self.shape``.
        """
        size_ = numpy.prod(size, dtype=int)
        dim = len(self)
        if dim > 1:
            if isinstance(size, (tuple, list, numpy.ndarray)):
                shape = (dim,) + tuple(size)
            else:
                shape = (dim, size)
        else:
            shape = size

        from . import sampler
        out = sampler.generator.generate_samples(
            order=size_, domain=self, rule=rule, antithetic=antithetic)
        try:
            out = out.reshape(shape)
        except:
            if len(self) == 1:
                out = out.flatten()
            else:
                out = out.reshape(dim, int(out.size/dim))

        if self.interpret_as_integer:
            out = out.astype(int)
        return out

    def mom(self, K, **kws):
        """
        Raw statistical moments.

        Creates non-centralized raw moments from the random variable. If
        analytical options can not be utilized, Monte Carlo integration
        will be used.

        Args:
            K (numpy.ndarray):
                Index of the raw moments. k.shape must be compatible with
                distribution shape.  Sampling scheme when performing Monte
                Carlo
            rule (str):
                rule for estimating the moment if the analytical method fails.
            antithetic (numpy.ndarray):
                List of bool. Represents the axes to mirror using antithetic
                variable during MCI.

        Returns:
            (numpy.ndarray):
                Shapes are related through the identity
                ``k.shape == dist.shape+k.shape``.
        """
        K = numpy.asarray(K, dtype=int)
        shape = K.shape
        dim = len(self)

        if dim > 1:
            shape = shape[1:]

        size = int(K.size/dim)
        K = K.reshape(dim, size)

        cache = {}
        out = [evaluation.evaluate_moment(self, kdata, cache) for kdata in K.T]
        out = numpy.array(out)
        return out.reshape(shape)

    def _mom(self, *args, **kws):
        """Default moment generator, throws error."""
        raise StochasticallyDependentError("component lack support")

    def ttr(self, kloc, acc=10**3, verbose=1):
        """
        Three terms relation's coefficient generator

        Args:
            k (numpy.ndarray, int):
                The order of the coefficients.
            acc (int):
                Accuracy of discretized Stieltjes if analytical methods are
                unavailable.

        Returns:
            (Recurrence coefficients):
                Where out[0] is the first (A) and out[1] is the second
                coefficient With ``out.shape==(2,)+k.shape``.
        """
        kloc = numpy.asarray(kloc, dtype=int)
        shape = kloc.shape
        kloc = kloc.reshape(len(self), -1)
        cache = {}
        out = [evaluation.evaluate_recurrence_coefficients(self, k)
               for k in kloc.T]
        alpha, beta = numpy.asfarray(list(zip(*out)))
        out = numpy.array([alpha.T, beta.T])
        return out.reshape((2,)+shape)


    def _ttr(self, kloc, cache, **kws):
        """Default TTR generator, throws error."""
        raise NotImplementedError()

    def __str__(self):
        """X.__str__() <==> str(X)"""
        if self._repr is not None:
            kwargs = self._repr
        else:
            kwargs = self.prm
        args = [key + "=" + str(kwargs[key]) for key in sorted(kwargs)]
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def __repr__(self):
        return str(self)

    def __len__(self):
        """X.__len__() <==> len(X)"""
        return 1

    def __add__(self, X):
        """Y.__add__(X) <==> X+Y"""
        from . import operators
        return operators.Add(self, X)

    def __radd__(self, X):
        """Y.__radd__(X) <==> Y+X"""
        from . import operators
        return operators.Add(self, X)

    def __sub__(self, X):
        """Y.__sub__(X) <==> X-Y"""
        from . import operators
        return operators.Add(self, -X)

    def __rsub__(self, X):
        """Y.__rsub__(X) <==> Y-X"""
        from . import operators
        return operators.Add(X, -self)

    def __neg__(self):
        """X.__neg__() <==> -X"""
        from . import operators
        return operators.Neg(self)

    def __mul__(self, X):
        """Y.__mul__(X) <==> X*Y"""
        from . import operators
        return operators.Mul(self, X)

    def __rmul__(self, X):
        """Y.__rmul__(X) <==> Y*X"""
        from . import operators
        return operators.Mul(X, self)

    def __div__(self, X):
        """Y.__div__(X) <==> Y/X"""
        from . import operators
        return operators.Mul(self, X**-1)

    def __rdiv__(self, X):
        """Y.__rdiv__(X) <==> X/Y"""
        from . import operators
        return operators.Mul(X, self**-1)

    def __floordiv__(self, X):
        """Y.__floordiv__(X) <==> Y/X"""
        from . import operators
        return operators.Mul(self, X**-1)

    def __rfloordiv__(self, X):
        """Y.__rfloordiv__(X) <==> X/Y"""
        from . import operators
        return operators.Mul(X, self**-1)

    def __truediv__(self, X):
        """Y.__truediv__(X) <==> Y/X"""
        from . import operators
        return operators.Mul(self, X**-1)

    def __rtruediv__(self, X):
        """Y.__rtruediv__(X) <==> X/Y"""
        from . import operators
        return operators.Mul(X, self**-1)

    def __pow__(self, X):
        """Y.__pow__(X) <==> Y**X"""
        from . import operators
        return operators.Pow(self, X)

    def __rpow__(self, X):
        """Y.__rpow__(X) <==> X**Y"""
        from . import operators
        return operators.Pow(X, self)

    def __le__(self, X):
        """Y.__le__(X) <==> Y<=X"""
        from . import operators
        return operators.Trunc(self, X)

    def __lt__(self, X):
        """Y.__lt__(X) <==> Y<X"""
        from . import operators
        return operators.Trunc(self, X)

    def __ge__(self, X):
        """Y.__ge__(X) <==> Y>=X"""
        from . import operators
        return operators.Trunc(X, self)

    def __gt__(self, X):
        """Y.__gt__(X) <==> Y>X"""
        from . import operators
        return operators.Trunc(X, self)
