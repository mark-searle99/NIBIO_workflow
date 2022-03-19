import os
import pdal
from pathlib import Path, PurePath
import laspy
import numpy as np

# function to read a poin
def open_las(input_point_cloud, subsample=1):
    '''Open an input las file and save xyz (+ treeid/sp) values in numpy array.
    Also outputs pooint format, laspy open() instance and point cloud header'''
    with laspy.open(input_point_cloud) as f:
        point_format = f.header.point_format
        #print(f"Number of vlrs:     {f.header.vlrs}")
        print(list(point_format.dimension_names))
        header = f.header
        #print(header)
        scale = header.scale
        offset = header.offset

    las = laspy.read(input_point_cloud)[::subsample]
    try:
        data = np.array([las.X, las.Y, las.Z, las.treeSP, las.treeID])
    except AttributeError:
        data = np.array([las.X, las.Y, las.Z])
    for i in range(3):
        data[i, :] = data[i, :] * scale[i] + offset[i]
    return point_format, las, header, data

def create_tiles(plot_id, num_tiles, output_folder, input_xyz, input_dtm, extent, trajectory, scanner_config):
    tile_height = (extent[0][1]-extent[1][1])/num_tiles
    print('Tile height {}m'.format(tile_height))
    for i in range(1, num_tiles+1):
        print('Laying down tile number {}...'.format(i))

        #output_tif = Path('data/sceneparts/', output_folder, r'plot_{}_tile_{}.tif'.format(plot_id, i))
        output_xyz = os.path.join('data/sceneparts/', output_folder, r'p{}_t{}.xyz'.format(plot_id, i)).replace("\\","/")

        # [lower left x, lower left y, upper right x, upper right y] (of AOI)
        tile_extent = [extent[1][0], extent[1][1]+((i-1)*tile_height)-0.1, 
                            extent[0][0], extent[1][1]+(i*tile_height)+0.1]
        # Upward and downward flight lines (y direction)
        # First two lists are smaller x, second two list are bigger x
        survey_trajectory = [[trajectory[0][0], trajectory[0][1]+((i-1)*tile_height), scanner_config[5], "true"], 
                      [trajectory[1][0], trajectory[0][1]+(i*tile_height), scanner_config[5], "false"],
                      [trajectory[2][0], trajectory[0][1]+(i*tile_height), scanner_config[5], "true"], 
                      [trajectory[3][0], trajectory[0][1]+((i-1)*tile_height), scanner_config[5], "false"]]
        
        
        json_crop = """[
        "%s",
        {
            "type":"filters.crop",
            "bounds":"([%s, %s], [%s, %s])"
        },
        {
            "type":"writers.text",
            "filename": "%s",
            "order":"X,Y,Z",
            "precision":6,
            "keep_unspecified":"false",
            "write_header":"false"
        }
        ]"""
        
        pipeline = pdal.Pipeline(json_crop % (input_xyz, tile_extent[0], tile_extent[2], tile_extent[1], tile_extent[3], output_xyz))
        exe = pipeline.execute()

        print('Tile successfully layed.')
        print('Writing survey file..')

        # Write the survey file.
        survey_file_name = os.path.join('data/surveys/', output_folder, 'p{}_t{}_survey.xml'.format(plot_id, i)).replace("\\","/")
        survey_name = 'plot_{}_tile_{}'.format(plot_id, i)
        platform = "data/platforms.xml#{}".format(scanner_config[0])
        scanner = "data/scanners_als.xml#{}".format(scanner_config[1])
        scene = os.path.join('data/scenes/', output_folder, "p{}_t{}_scene.xml#plot_{}_tile_{}".format(plot_id, i, plot_id, i)).replace("\\","/")
        pulse_freq = scanner_config[3]
        scan_angle = scanner_config[2]
        scan_freq = scanner_config[4]
        speed = scanner_config[6]

        survey_file = open(survey_file_name, "w")
        survey_file.write('<?xml version="1.0"?>\n')
        survey_file.write('<document>\n')
        survey_file.write('    <survey name="{survey}" platform="{platform}" scanner="{scanner}" scene="{scene}">\n'
                          '<FWFSettings beamSampleQuality="3" winSize_ns="2.5"/>\n'
                          .format(survey=survey_name, platform=platform, scanner=scanner, scene=scene))

        # Write legs to file.
        for point in survey_trajectory:
            survey_file.write('        <leg>\n')
            survey_file.write('            <platformSettings  x="{x}" y="{y}" z="{z}" onGround="false" '
                              'movePerSec_m="{v}"/>\n'.format(x=point[0], y=point[1],
                                                              z=point[2], v=speed))
            survey_file.write(
                '            <scannerSettings  active="{active_flag}" pulseFreq_hz="{pulse_freq}" scanAngle_deg="{scan_angle}" '
                'scanFreq_hz="{scan_freq}" headRotatePerSec_deg="0.0" headRotateStart_deg="0.0" '
                'headRotateStop_deg="0.0" trajectoryTimeInterval_s="0.05"/>\n'
                .format(pulse_freq=pulse_freq, scan_angle=scan_angle, active_flag=point[3], scan_freq=scan_freq))
            survey_file.write('        </leg>\n')
        survey_file.write('    </survey>\n</document>')
        survey_file.close()

        print("Writing scene file...")
        scene_file = os.path.join('data/scenes/', output_folder, "p{}_t{}_scene.xml".format(plot_id, i, i)).replace("\\","/")
        scene = """
        <?xml version="1.0" encoding="UTF-8"?>
    <document>
        <scene id="%s" name="%s">
            
            <part>
                <filter type="geotiffloader">
                    <param type="string" key="filepath" value="%s" />
                    <param type="string" key="matfile" value="data/sceneparts/basic/groundplane/groundplane.mtl" />
                    <param type="string" key="matname" value="None" />
                </filter>
                
            </part>

            <part>
                <filter type="xyzloader">
                    <param type="string" key="filepath" value="%s" />
                    <param type="string" key="separator" value="," />
                    <param type="double" key="voxelSize" value="0.02" />
                    <!-- Normal estimation using Singular Value Decomposition (SVD)
                    MODE 1: simple mode / MODE 2: advanced mode for large files, which works in batches -->
                    <param type="int" key="estimateNormals" value="2" />
                    <!-- If less than three points fall into one voxel, it is discarded.
                    To avoid this, a default Normal can be assigned to these voxels with:-->
                    <param type="vec3" key="defaultNormal" value="0;0;1" /> 
                </filter>
                
            </part>
        </scene>
    </document>"""

        with open(scene_file, "w") as f:
            f.write(scene % ("plot_{}_tile_{}".format(plot_id, i), "Plot number {} Tile number {}".format(plot_id, i), input_dtm, output_xyz))
    print('\nTile creation successfull!')
    print('Scenes written to {}'.format(os.path.join('data/scenes/', output_folder)))
    print('Sceneparts written to {}'.format(os.path.join('data/sceneparts/', output_folder)))
    print('Surveys written to {}'.format(os.path.join('data/surveys/', output_folder)))
    
def sim_iter(num_iterations, survey_name_template):
    outfolders = []
    for i in range(1, num_iterations+1):
        outfolders.append(run_sim(survey_name_template.format(i)))
    return outfolders
        
def run_sim(survey_name):
    import pyhelios

    pyhelios.loggingVerbose()
    pyhelios.setDefaultRandomnessGeneratorSeed("123")

    sim = pyhelios.Simulation(
        survey_name,
        'assets/',
        'output/',
        0,  # Num Threads
        True,  # LAS output
        False,  # LAS1.0 output
        False,  # ZIP output
    )

    # Enable final output.
    sim.finalOutput = True

    # Set sim frequency.
    sim.simFrequency = 1000

    # Load survey file. Further configuration of survey possible.
    sim.loadSurvey(
        True,  # Leg Noise Disabled FLAG
        False,  # Rebuild Scene FLAG
        False,  # Write Wavef orm FLAG
        False,  # Calc Echowidth FLAG
        False,  # Full Wave Noise FLAG
        True  # Platform Noise Disabled FLAG
    )
    
    print('Simulation has started!\nSurvey Name: {survey_name}\n{scanner_info}'.format(
        survey_name=sim.getSurvey().name,
        scanner_info=sim.getScanner().toString()))
    sim.start()
    
    output = sim.join()
    
    output_folder = output.filepath
    
    return output_folder