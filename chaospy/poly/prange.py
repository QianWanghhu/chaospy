"""Constructor to create a range of polynomials where the exponent vary."""
import numpoly


def prange(N=1, dim=1):
    """
    Constructor to create a range of polynomials where the exponent vary.

    Args:
        N (int):
            Number of polynomials in the array.
        dim (int):
            The dimension the polynomial should span.

    Returns:
        (chaospy.poly.ndpoly):
            A polynomial array of length N containing simple polynomials with
            increasing exponent.

    Examples:
        >>> print(chaospy.prange(4))
        [1 q0 q0**2 q0**3]
        >>> print(chaospy.prange(4, dim=3))
        [1 q2 q2**2 q2**3]
    """
    indeterminants = ["q%d" % (dim-1)]
    return numpoly.monomial(N-1, indeterminants=indeterminants)
