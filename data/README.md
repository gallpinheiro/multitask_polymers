# Overview

This folder contains a collection of datasets from polymer literature. Each dataset includes specific property measurements of polymers, derived from either simulations or experiments. Below is a table with the following information about the data:

- Citation of the original work
- Number of samples
- Source type (simulation or experiment)
- Property name

Note that all the datasets were processed and each contains the SMILES of the monomers and the polymer property. Some datasets include additional features about the monomers and polymers, such as monomer fraction or molecular weight. For these cases, an additional column was created to hold this information.


| ID | Ref  | \# of Samples | Type        | Property                           |
|---|----------|-------------------|-------------|------------------------------------|
| 0 | [Paper \#1](https://doi.org/10.1039/D2SC02839E)  | 18,414            | Simulated   | Electron affinity |
| 1 | [Paper \#1](https://doi.org/10.1039/D2SC02839E)  | 18,414            | Simulated   | Ionization potential|
| 2 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4)  | 1,077             | Simulated   | Radius of gyration |
| 3 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238)  | 390               | Simulated   | Atomization energy |
| 4 | [Paper \#4](https://doi.org/10.1063/5.0044306)  | 4,127             | Simulated   | Bandgap (Chain) |
| 5 | [Paper \#4](https://doi.org/10.1063/5.0044306)  | 1,747             | Simulated   | Electron injection barrier |
| 6 | [Paper \#5](https://doi.org/10.1021/acsapm.0c00524) | 314               | Simulated   | Rubber coefficient of thermal expansion |
| 7 | [Paper \#5](https://doi.org/10.1021/acsapm.0c00524)  | 223               | Simulated   | Glass coefficient of thermal expansion |
| 8 | [Paper \#5](https://doi.org/10.1021/acsapm.0c00524)  | 314               | Simulated   | Density at 300K |
| 9 | [Paper \#6](https://doi.org/10.1038/s41597-024-03212-4) | 662               | Simulated   | Glass transition temperature |
| 10 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 432               | Simulated   | Crystallization tendency |
| 11 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 3,380             | Simulated   | Bandgap (Chain) |
| 12 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 561               | Simulated   | Bandgap (Bulk) |
| 13 | [Paper \#7](https://doi.org/10.1021/acs.jpclett.2c00995) | 42                | Simulated   | Ring-opening polymerization |
| 14 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 370               | Simulated   | Ionization energy |
| 15 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 382               | Simulated   | Refractive index |
| 16 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,070             | Simulated   | Thermal conductivity |
| 17 | [Paper \#4](https://doi.org/10.1063/5.0044306) | 232               | Simulated   | Bandgap (Crystal) |
| 18 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 382               | Simulated   | Dielectric constant |
| 19 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Self-diffusion coefficient |
| 20 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,069             | Simulated   | Thermal diffusivity |
| 21 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Isentropic bulk modulus |
| 22 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,077             | Simulated   | Density |
| 23 | [Paper \#8](https://doi.org/10.1021/acs.jpca.3c05870) | 350               | Simulated   | Ring-opening polymerization |
| 24 | [Paper \#9](https://doi.org/10.1021/acsapm.0c00524) | 314               | Simulated   | Glass transition temperature |
| 25 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,075             | Simulated   | Refractive index |
| 26 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,077             | Simulated   | Static dielectric constant |
| 27 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Volume expansion coefficient |
| 28 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Linear expansion coefficient |
| 29 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Bulk modulus |
| 30 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Isentropic compressibility |
| 31 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Compressibility |
| 32 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Constant volume |
| 33 | [Paper \#2](https://doi.org/10.1038/s41524-022-00906-4) | 1,076             | Simulated   | Constant pressure |
| 34 | [Paper \#3](https://doi.org/10.1016/j.patter.2021.100238) | 368               | Experimental| Electron affinity |
| 35 | [Paper \#10](https://doi.org/10.1038/s41524-023-01034-3) | 210               | Experimental| Glass transition temperature |
| 36 | [Paper \#10](https://doi.org/10.1038/s41524-023-01034-3) | 243               | Experimental| Inherent viscosity |
| 37 | [Paper \#11](https://doi.org/10.1021/jacs.1c08181) | 204               | Experimental| 19F NMR Signal-to-noise ratio |
| 38 | [Paper \#5](https://doi.org/10.1021/acsapm.0c00524) | 314               | Experimental| Glass transition temperature |
| 39 | [Paper \#6](https://doi.org/10.1038/s41597-024-03212-4) | 304               | Experimental| Glass transition temperature |
| 40 | [Paper \#12](https://doi.org/10.1021/acs.jcim.3c01232) | 676               | Experimental| CO2/N2 selectivity |
| 41 | [Paper \#12](https://doi.org/10.1021/acs.jcim.3c01232) | 611               | Experimental| CO2/CH4 selectivity |
| 42 | [Paper \#12](https://doi.org/10.1021/acs.jcim.3c01232) | 727               | Experimental| N2 permeability |
| 43 | [Paper \#12](https://doi.org/10.1021/acs.jcim.3c01232) | 690               | Experimental| CO2 permeability |
| 44 | [Paper \#12](https://doi.org/10.1021/acs.jcim.3c01232) | 613               | Experimental| CH4 permeability |
| 45 | [Paper \#7](https://doi.org/10.1021/acs.jpclett.2c00995) and [Paper \#8](https://doi.org/10.1021/acs.jpca.3c05870) | 116               | Experimental| Ring-opening polymerization |
| 46 | [Paper \#5](https://doi.org/10.1021/acsapm.0c00524) | 117               | Experimental| Density at 300K |
