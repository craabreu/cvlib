"""
.. class:: Utils
   :platform: Linux, MacOS, Windows
   :synopsis: Utility functions and classes for CVpack

.. classauthor:: Charlles Abreu <craabreu@gmail.com>

"""

import typing as t

import openmm

from cvpack import unit as mmunit


class NonbondedForceSurrogate:  # pylint: disable=too-many-instance-attributes
    """A surrogate class for the NonbondedForce class in OpenMM."""

    def __init__(self, other: openmm.NonbondedForce) -> None:
        self._cutoff = other.getCutoffDistance()
        self._uses_pbc = other.usesPeriodicBoundaryConditions()
        self._num_particles = other.getNumParticles()
        self._particle_parameters = list(
            map(other.getParticleParameters, range(self._num_particles))
        )
        self._num_exceptions = other.getNumExceptions()
        self._exception_parameters = list(
            map(other.getExceptionParameters, range(self._num_exceptions))
        )
        self._use_switching_function = other.getUseSwitchingFunction()
        self._switching_distance = other.getSwitchingDistance()

    def __getstate__(self) -> t.Dict[str, str]:
        return {
            "cutoff": self.getCutoffDistance(),
            "uses_pbc": self.usesPeriodicBoundaryConditions(),
            "num_particles": self.getNumParticles(),
            "particle_parameters": [
                self.getParticleParameters(i) for i in range(self.getNumParticles())
            ],
            "num_exceptions": self.getNumExceptions(),
            "exception_parameters": [
                self.getExceptionParameters(i) for i in range(self.getNumExceptions())
            ],
            "use_switching_function": self.getUseSwitchingFunction(),
            "switching_distance": self.getSwitchingDistance(),
        }

    def __setstate__(self, state: t.Dict[str, str]) -> None:
        self._cutoff = state["cutoff"]
        self._uses_pbc = state["uses_pbc"]
        self._num_particles = state["num_particles"]
        self._particle_parameters = state["particle_parameters"]
        self._num_exceptions = state["num_exceptions"]
        self._exception_parameters = state["exception_parameters"]
        self._use_switching_function = state["use_switching_function"]
        self._switching_distance = state["switching_distance"]

    def getCutoffDistance(self) -> float:
        """Get the cutoff distance."""
        return mmunit.value_in_md_units(self._cutoff)

    def usesPeriodicBoundaryConditions(self) -> bool:
        """Return whether periodic boundary conditions are used."""
        return self._uses_pbc

    def getNumParticles(self) -> int:
        """Get the number of particles."""
        return self._num_particles

    def getParticleParameters(self, index: int) -> t.Tuple[float, float, float]:
        """Get the parameters of a particle at the given index."""
        return tuple(map(mmunit.value_in_md_units, self._particle_parameters[index]))

    def getNumExceptions(self):
        """Get the number of exceptions."""
        return self._num_exceptions

    def getExceptionParameters(
        self, index: int
    ) -> t.Tuple[int, int, float, float, float]:
        """Get the parameters of an exception at the given index."""
        i, j, *params = self._exception_parameters[index]
        return i, j, *map(mmunit.value_in_md_units, params)

    def getUseSwitchingFunction(self) -> bool:
        """Return whether a switching function is used."""
        return self._use_switching_function

    def getSwitchingDistance(self) -> float:
        """Get the switching distance."""
        return mmunit.value_in_md_units(self._switching_distance)
