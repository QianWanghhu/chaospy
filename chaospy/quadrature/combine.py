"""Function to combine two dataset together with a tensor product."""
import numpy


def combine(args):
    """
    All linear combination of a list of list.

    Args:
        args (numpy.ndarray):
            List of input arrays.  Components to take linear combination of
            with ``args[i].shape == (N[i], M[i])`` where ``N`` is to be taken
            linear combination of and ``M`` is constant.  ``M[i]`` is set to
            1 if missing.

    Returns:
        (numpy.array):
            Matrix of combinations with
            ``shape == (numpy.prod(N), numpy.sum(M))``.

    Examples:
        >>> A, B = [1,2], [[4,4],[5,6]]
        >>> print(chaospy.quadrature.combine([A, B]))
        [[1 4 4]
         [1 5 6]
         [2 4 4]
         [2 5 6]]
    """
    args = [numpy.asarray(arg).reshape(len(arg), -1) for arg in args]
    shapes = [arg.shape for arg in args]

    size = numpy.prod(shapes, 0)[0]*numpy.sum(shapes, 0)[1]
    if size > 10**9:
        raise MemoryError("Too large sets")

    out = args[0]
    for arg in args[1:]:
        out = numpy.hstack([
            numpy.tile(out, len(arg)).reshape(-1, out.shape[1]),
            numpy.tile(arg.T, len(out)).reshape(arg.shape[1], -1).T,
        ])
    return out


def combine_quadrature(
        abscissas,
        weights,
        domain=(),
):
    """
    Create all linear combinations of all abscissas and weights. If ``domain``
    is provided, also scale from assumed (0, 1) to said domain.

    Args:
        abscissas (List[numpy.ndarray]):
            List of abscissas to be combined.
        weights (List[numpy.ndarray]):
            List of weights to be combined.
        domain (Optional[Tuple[numpy.ndarray, numpy.ndarray]]):
            Domain to scale to.

    Returns:
        (Tuple[numpy.ndarray, numpy.ndarray]):
            Same as ``abscissas`` and ``weights``, but combined and flatten
            such that ``abscissas.shape == (dim, len(weights))``.
    """
    dim = len(abscissas)
    abscissas = combine(abscissas)
    weights = combine(weights)

    if domain:
        abscissas = (domain[1]-domain[0])*abscissas + domain[0]
        weights = weights*(domain[1]-domain[0])

    abscissas = abscissas.T.reshape(dim, -1)
    weights = numpy.prod(weights, -1)

    assert len(weights.shape) == 1
    assert abscissas.shape == (dim,) + weights.shape

    return abscissas, weights
