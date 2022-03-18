# NIBIO Workflow

Data repository for workflow developed during NIBIO internship.
The workflow is contained in the jupyter notebook `workflow` and imports some functions from `annotate.py`.

Setup:

1. Navigate to folder within an anaconda prompt.
2. Create conda environment with command `conda env create -f nibio_pyhelios.yml`.
3. Activate conda environment with `conda activate nibio_pyhelios`.
4. Open jupyter notebooks with command `jupyter notebook`.
5. Open notebook `workflow.ipynb` and run the steps as given!

Contents of workflow:
1. An annotated forestry point cloud is loaded.
2. The point cloud is seperated into ground points and vegetation points, the ground point are used to generate a dtm.
3. The AOI is split up into n tiles, as specified by user. Flight lines are plotted with a certain flight spacing, as defined by user.
4. A [scene XML](https://github.com/3dgeo-heidelberg/helios/wiki/Scene), two sceneparts (TIF and .xyz) and a [survey XML](https://github.com/3dgeo-heidelberg/helios/wiki/Survey) are generated for each tile. These are the instructions for the HELIOS++ simulation.
5. After running each simulation, the output files are merged to create the combined final output.
6. The annotations (treeSP, treeID) from the original input point cloud are transferred to the newly generated point cloud.

Further information:

[HELIOS++ Wiki](https://github.com/3dgeo-heidelberg/helios/wiki/Main-page)

[HELIOS++ Publication](https://doi.org/10.1016/j.rse.2021.112772)
