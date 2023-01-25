"""
.. module:: cvlib
   :platform: Unix, MacOS, Windows
   :synopsis: Useful Collective Variables for OpenMM

.. moduleauthor:: Charlles Abreu <craabreu@gmail.com>

"""

from typing import List

import openmm
from openmm import unit


def _in_md_units(quantity: unit.Quantity) -> float:
    """
    Returns the numerical value of a quantity in a unit of measurement compatible with the
    Molecular Dynamics unit system (mass in Da, distance in nm, time in ps, temperature in K,
    energy in kJ/mol, angle in rad).

    """
    return quantity.value_in_unit_system(unit.md_unit_system)


class AbstractCollectiveVariable(openmm.Force):
    """
    Docstring.

    """

    _unit = unit.dimensionless

    def setUnit(self, cv_unit: unit.Unit):
        """
        Sets the unit of measurement this collective variable.

        Parameters
        ----------
            unit
                The unit of measurement of this collective variable

        """
        self._unit = cv_unit

    def getUnit(self) -> unit.Unit:
        """
        Gets the unit of measurement this collective variable.

        """
        return self._unit

    def evaluateInContext(self, context: openmm.Context) -> unit.Quantity:
        """
        Evaluates this collective variable for a given context.

        Parameters
        ----------
            context
                A context for which to evaluate this collective variable

        Returns
        -------
            The value of this collective variable in the given context

        """
        forces = context.getSystem().getForces()
        free_groups = set(range(32)) - set(f.getForceGroup() for f in forces)
        old_group = self.getForceGroup()
        new_group = next(iter(free_groups))
        self.setForceGroup(new_group)
        state = context.getState(getEnergy=True, groups={new_group})
        self.setForceGroup(old_group)
        return _in_md_units(state.getPotentialEnergy()) * self.getUnit()


class RadiusOfGyration(openmm.CustomCentroidBondForce, AbstractCollectiveVariable):
    """
    The radius of gyration of a group of atoms, defined as:

    .. math::
        R_g = \\sqrt{ \\frac{1}{n} \\sum_{i=1}^n \\|\\mathbf{r}_i - \\mathbf{r}_{\\rm mean}\\|^2 },

    where :math:`n` is the number of atoms in the group, :math:`\\mathbf{r}_i` is the coordinate of
    atom `i`, and :math:`\\mathbf{r}_{\\rm mean}` is the centroid of the group of atoms, that is,

    .. math::
        \\mathbf{r}_{\\rm mean} = \\frac{1}{n} \\sum_{i=1}^n \\mathbf{r}_i.

    Parameters
    ----------
        atoms
            The indices of the atoms in the group

    Example
    -------
        >>> import openmm
        >>> import cvlib
        >>> from openmm import unit
        >>> from openmmtools import testsystems
        >>> model = testsystems.AlanineDipeptideVacuum()
        >>> num_atoms = model.system.getNumParticles()
        >>> atoms = list(range(num_atoms))
        >>> rg = cvlib.RadiusOfGyration(atoms)
        >>> model.system.addForce(rg)
        5
        >>> platform = openmm.Platform.getPlatformByName('Reference')
        >>> context = openmm.Context(model.system, openmm.CustomIntegrator(0), platform)
        >>> context.setPositions(model.positions)
        >>> print(rg.evaluateInContext(context))
        0.295143056060787 nm
        >>> r = model.positions[atoms, :]
        >>> rmean = r.mean(axis=0)
        >>> print(unit.sqrt(((r - rmean) ** 2).sum() / num_atoms))
        0.295143056060787 nm

    """

    def __init__(self, atoms: List[int]):
        num_atoms = len(atoms)
        num_groups = num_atoms + 1
        rgsq = "+".join(
            [f"distance(g{i+1}, g{num_groups})^2" for i in range(num_atoms)]
        )
        super().__init__(num_groups, f"sqrt(({rgsq})/{num_atoms})")
        for atom in atoms:
            self.addGroup([atom], [1])
        self.addGroup(atoms, [1] * num_atoms)
        self.addBond(list(range(num_groups)), [])
        self.setUsesPeriodicBoundaryConditions(False)
        self.setUnit(unit.nanometers)
