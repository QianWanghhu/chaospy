"""Hermite Genz-Keister 22 rule."""
import numpy


def quad_genz_keister_22(order):
    """
    Hermite Genz-Keister 22 rule.

    Args:
        order (int):
            The quadrature order. Must be in the interval (0, 8).

    Returns:
        (:py:data:typing.Tuple[numpy.ndarray, numpy.ndarray]):
            Abscissas and weights

    Examples:
        >>> abscissas, weights = quad_genz_keister_22(1)
        >>> print(numpy.around(abscissas, 4))
        [-1.7321  0.      1.7321]
        >>> print(numpy.around(weights, 4))
        [0.1667 0.6667 0.1667]
    """
    order = sorted(GENZ_KEISTER_22.keys())[order]

    abscissas, weights = GENZ_KEISTER_22[order]
    abscissas = numpy.array(abscissas)
    weights = numpy.array(weights)

    weights /= numpy.sum(weights)
    abscissas *= numpy.sqrt(2)

    return abscissas, weights


GENZ_KEISTER_22 = {
    1 : ((
        0.0000000000000000,
    ), (
        1.7724538509055159E+00,
    )),
    3 : ((
        -1.2247448713915889,
        0.0000000000000000,
        1.2247448713915889,
    ), (
        2.9540897515091930E-01,
        1.1816359006036772E+00,
        2.9540897515091930E-01,
    )),
    9 : ((
        -2.9592107790638380,
        -2.0232301911005157,
        -1.2247448713915889,
        -0.52403354748695763,
        0.0000000000000000,
        0.52403354748695763,
        1.2247448713915889,
        2.0232301911005157,
        2.9592107790638380,
    ), (
        1.6708826306882348E-04,
        1.4173117873979098E-02,
        1.6811892894767771E-01,
        4.7869428549114124E-01,
        4.5014700975378197E-01,
        4.7869428549114124E-01,
        1.6811892894767771E-01,
        1.4173117873979098E-02,
        1.6708826306882348E-04,
    )),
    19 : ((
        -4.4995993983103881,
        -3.6677742159463378,
        -2.9592107790638380,
        -2.2665132620567876,
        -2.0232301911005157,
        -1.8357079751751868,
        -1.2247448713915889,
        -0.87004089535290285,
        -0.52403354748695763,
        0.0000000000000000,
        0.52403354748695763,
        0.87004089535290285,
        1.2247448713915889,
        1.8357079751751868,
        2.0232301911005157,
        2.2665132620567876,
        2.9592107790638380,
        3.6677742159463378,
        4.4995993983103881,
    ), (
        1.5295717705322357E-09,
        1.0802767206624762E-06,
        1.0656589772852267E-04,
        5.1133174390883855E-03,
        -1.1232438489069229E-02,
        3.2055243099445879E-02,
        1.1360729895748269E-01,
        1.0838861955003017E-01,
        3.6924643368920851E-01,
        5.3788160700510168E-01,
        3.6924643368920851E-01,
        1.0838861955003017E-01,
        1.1360729895748269E-01,
        3.2055243099445879E-02,
        -1.1232438489069229E-02,
        5.1133174390883855E-03,
        1.0656589772852267E-04,
        1.0802767206624762E-06,
        1.5295717705322357E-09,
    )),
    41 : ((
        -7.251792998192644,
        -6.547083258397540,
        -5.961461043404500,
        -5.437443360177798,
        -4.953574342912980,
        -4.4995993983103881,
        -4.070919267883068,
        -3.6677742159463378,
        -3.296114596212218,
        -2.9592107790638380,
        -2.630415236459871,
        -2.2665132620567876,
        -2.043834754429505,
        -2.0232301911005157,
        -1.8357079751751868,
        -1.585873011819188,
        -1.2247448713915889,
        -0.87004089535290285,
        -0.52403354748695763,
        -0.195324784415805,
        0.0000000000000000,
        0.195324784415805,
        0.52403354748695763,
        0.87004089535290285,
        1.2247448713915889,
        1.585873011819188,
        1.8357079751751868,
        2.0232301911005157,
        2.043834754429505,
        2.2665132620567876,
        2.630415236459871,
        2.9592107790638380,
        3.296114596212218,
        3.6677742159463378,
        4.070919267883068,
        4.4995993983103881,
        4.953574342912980,
        5.437443360177798,
        5.961461043404500,
        6.547083258397540,
        7.251792998192644,
    ), (
        0.664195893812757801E-23,
        0.860427172512207236E-19,
        0.1140700785308509E-15,
        0.408820161202505983E-13,
        0.581803393170320419E-11,
        0.400784141604834759E-09,
        0.149158210417831408E-07,
        0.315372265852264871E-06,
        0.381182791749177506E-05,
        0.288976780274478689E-04,
        0.189010909805097887E-03,
        0.140697424065246825E-02,
        - 0.144528422206988237E-01,
        0.178852543033699732E-01,
        0.705471110122962612E-03,
        0.165445526705860772E-01,
        0.45109010335859128E-01,
        0.928338228510111845E-01,
        0.145966293895926429E+00,
        0.165639740400529554E+00,
        0.562793426043218877E-01,
        0.165639740400529554E+00,
        0.145966293895926429E+00,
        0.928338228510111845E-01,
        0.45109010335859128E-01,
        0.165445526705860772E-01,
        0.705471110122962612E-03,
        0.178852543033699732E-01,
        - 0.144528422206988237E-01,
        0.140697424065246825E-02,
        0.189010909805097887E-03,
        0.288976780274478689E-04,
        0.381182791749177506E-05,
        0.315372265852264871E-06,
        0.149158210417831408E-07,
        0.400784141604834759E-09,
        0.581803393170320419E-11,
        0.408820161202505983E-13,
        0.1140700785308509E-15,
        0.860427172512207236E-19,
        0.664195893812757801E-23,
    )),
}
