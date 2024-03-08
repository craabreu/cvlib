"""
.. class:: Generic
   :platform: Linux, MacOS, Windows
   :synopsis: Generic collective variable

.. classauthor:: Charlles Abreu <craabreu@gmail.com>

"""

import typing as t

import openmm

from cvpack import unit as mmunit

from .cvpack import BaseCollectiveVariable


class OpenMMForceWrapper(BaseCollectiveVariable):
    r"""
    A generic collective variable.

    Parameters
    ----------
    function
        The function to be evaluated. It must be a valid
        :OpenMM:`CustomCentroidBondForce` expression
    unit
        The unit of measurement of the collective variable. It must be compatible
        with the MD unit system (mass in `daltons`, distance in `nanometers`, time
        in `picoseconds`, temperature in `kelvin`, energy in `kilojoules_per_mol`,
        angle in `radians`). If the collective variables does not have a unit, use
        `dimensionless`
    groups
        The groups of atoms to be used in the function. Each group must be specified
        as a list of atom indices with arbitrary length
    collections
        The indices of the groups in each collection, passed as a 2D array-like object
        of shape `(m, n)`, where `m` is the number of collections and `n` is the number
        groups per collection. If a 1D object is passed, it is assumed that `m` is 1 and
        `n` is the length of the object.
    period
        The period of the collective variable if it is periodic, or `None` if it is not
    pbc
        Whether to use periodic boundary conditions
    weighByMass
        Whether to define the centroid as the center of mass of the group instead of
        the geometric center

    Example:
        >>> import cvpack
        >>> import numpy as np
        >>> import openmm
        >>> from openmm import unit
        >>> from openmmtools import testsystems
        >>> model = testsystems.AlanineDipeptideVacuum()
        >>> angle = openmm.CustomAngleForce("theta")
        >>> angle.addAngle(0, 1, 2)
        0
        >>> cv = cvpack.OpenMMForceWrapper(angle, unit.radian, period=2*np.pi)
        >>> assert isinstance(cv, openmm.CustomAngleForce)
        >>> cv.setUnusedForceGroup(0, model.system)
        1
        >>> model.system.addForce(cv)
        5
        >>> integrator = openmm.VerletIntegrator(0)
        >>> platform = openmm.Platform.getPlatformByName('Reference')
        >>> context = openmm.Context(model.system, integrator, platform)
        >>> context.setPositions(model.positions)
        >>> print(cv.getValue(context))
        1.911... rad
        >>> print(cv.getEffectiveMass(context))
        0.00538... nm**2 Da/(rad**2)
    """

    yaml_tag = "!cvpack.OpenMMForceWrapper"

    def __init__(  # pylint: disable=too-many-arguments, super-init-not-called
        self,
        openmmForce: t.Union[openmm.Force, str],
        unit: mmunit.Unit,
        period: t.Optional[mmunit.ScalarQuantity] = None,
    ) -> None:
        if isinstance(openmmForce, openmm.Force):
            openmmForce = openmm.XmlSerializer.serialize(openmmForce)
        unit = mmunit.SerializableUnit(unit)
        force_copy = openmm.XmlSerializer.deserialize(openmmForce)
        self.__dict__.update(force_copy.__dict__)
        self.__class__.__bases__ += (force_copy.__class__,)
        self._registerCV(unit, openmmForce, unit, period)
        if period is not None:
            self._registerPeriod(period)
