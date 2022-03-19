import pyhelios

# ---  M A I N  --- #
# ----------------- #
if __name__ == '__main__':
    # Configure simulation context
    pyhelios.loggingVerbose2()
    pyhelios.setDefaultRandomnessGeneratorSeed("123")

    # Build a simulation
    sim = pyhelios.Simulation(
        'data/surveys/voxels/als_detailedVoxels_mode_comparison.xml',
        'assets/',
        'output/',
        0,          # Num Threads
        False,      # LAS output FLAG
        False       # Zip output FLAG
    )
    sim.loadSurvey(
        True,       # Leg Noise Disabled FLAG
        False,      # Rebuild Scene FLAG
        True,       # Write Waveform FLAG
        True,       # Calc Echowidth FLAG
        False,      # Full Wave Noise FLAG
        True        # Platform Noise Disabled FLAG
    )

    # Edit simulation
    surveyPath = sim.getSurveyPath()
    print('survey path: {s}'.format(s=surveyPath))

    survey = sim.getSurvey()
    survey.name = "My survey"
    print('survey.name = "{s}"'.format(s=survey.name))

    scanner = sim.getScanner()
    scanner.numRays = 20
    scanner.calcEchowidth = True
    scanner.writeFullwave = True
    print('scanner.numRays = {n}'.format(n=scanner.numRays))
    print('scanner.numTimeBins = {n}'.format(n=scanner.numTimeBins))
    print('scanner.timeWave[0] = {n}'.format(n=scanner.getTimeWave()[0]))
    print('scanner.averagePower = {n}'.format(n=scanner.averagePower))
    print('scanner.fullWaveNoise = {b}'.format(b=scanner.fullWaveNoise))
    print('scanner.peakIntensityIndex = {i}'.format(
        i=scanner.peakIntensityIndex))
    print(
        'scanner.fwfSettings.binSize_ns = {n}'
        .format(n=scanner.fwfSettings.binSize_ns)
    )
    print(
        'scanner.fwfSettings.winSize_ns = {n}'
        .format(n=scanner.fwfSettings.winSize_ns)
    )
    print(
        'scanner.maxFullwaveRange_ns = {n}'
        .format(n=scanner.fwfSettings.maxFullwaveRange_ns)
    )
    print('scanner.calcEchowidth = {b}'.format(b=scanner.calcEchowidth))
    print('scanner.writeFullwave = {b}'.format(b=scanner.writeFullwave))
    head = scanner.getScannerHead()
    print('head.rotatePerSec = {n}'.format(n=head.rotatePerSec))
    attitude = head.getMountRelativeAttitude()
    print('attitude.q0 = {n}'.format(n=attitude.q0))
    attitude.q0 += 0.3
    attitude = head.getMountRelativeAttitude()
    print('attitude.q0 = {n}'.format(n=attitude.q0))
    axis = attitude.getAxis()
    axis.y += 0.5
    print('attitude.getAxis() = ({x}, {y}, {z})'
          .format(x=axis.x, y=axis.y, z=axis.z))
    angle = attitude.getAngle()
    print('attitude.angle = {n}'.format(n=angle))

    print('sim.numLegs = {n}'.format(n=sim.getNumLegs()))
    leg = sim.newLeg(0)
    leg = sim.getLeg(sim.getNumLegs()-1)
    leg.length = 1.5
    leg = sim.getLeg(sim.getNumLegs()-1)
    print('leg.length = {n}'.format(n=leg.length))
    print('leg.getPlatformSettings().x = {n}'
          .format(n=leg.getPlatformSettings().x))
    leg.getPlatformSettings().x += 1.0
    print('leg.getPlatformSettings().x = {n}'
          .format(n=leg.getPlatformSettings().x))
    print('sim.numLegs = {n}'.format(n=sim.getNumLegs()))
    sim.removeLeg(sim.getNumLegs()-1)
    print('sim.numLegs = {n}'.format(n=sim.getNumLegs()))
    leg = sim.getLeg(sim.getNumLegs()-1)
    print('leg.length = {n}'.format(n=leg.length))
    print('leg.getScannerSettings().beamSampleQuality = {n}'
          .format(n=leg.getScannerSettings().beamSampleQuality))

    deflector = scanner.getBeamDeflector()
    print('deflector.scanFreqMin = {n}'.format(n=deflector.scanFreqMin))
    deflector.scanFreqMin -= 0.67
    deflector = scanner.getBeamDeflector()
    deflAtti = deflector.getEmitterRelativeAttitude()
    print('deflector.scanFreqMin = {n}'.format(n=deflector.scanFreqMin))
    print('deflector.angleDiff = {n}'.format(n=deflector.angleDiff))
    print('deflector.attitude.q0 = {n}'.format(n=deflAtti.q0))
    deflector.angleDiff += 0.1
    deflAtti.q0 += 0.1
    deflector = scanner.getBeamDeflector()
    deflAtti = deflector.getEmitterRelativeAttitude()
    print('deflector.angleDiff = {n}'.format(n=deflector.angleDiff))
    print('deflector.attitude.q0 = {n}'.format(n=deflAtti.q0))

    detector = scanner.getDetector()
    print('detector.accuracy = {n}'.format(n=detector.accuracy))
    detector.accuracy += 0.00167
    detector = scanner.getDetector()
    print('detector.accuracy = {n}'.format(n=detector.accuracy))

    intlst = scanner.getSupportedPulseFrequencies()
    intlst[0] += 1
    intlst = scanner.getSupportedPulseFrequencies()
    print('scanner.supPulseFreqs[0] = {n}'.format(n=intlst[0]))
    print('scanner.supPulseFreqs len = {n}'.format(n=len(intlst)))

    scanAtti = scanner.getRelativeAttitude()
    print('scanner.relativeAttitude.q0 = {n}'.format(n=scanAtti.q0))
    scanPos = scanner.getRelativePosition()
    scanPos.x += 0.2
    scanPos = scanner.getRelativePosition()
    print('scanner.relativePosition.x = {n}'.format(n=scanPos.x))

    ihns = scanner.getIntersectionHandlingNoiseSource()
    print(
        'scanner.ihns = {ihns} '
        '(None is ok because it has not been instantiated yet)'
        .format(ihns=ihns)
    )
    rndgen1 = scanner.getRandGen1()
    print(
        'scanner.getRandGen1() = {r} '
        '(None is ok because it has not been instantiated yet)'
        .format(r=rndgen1)
    )

    sim.getPlatform().movePerSec = 0.01
    sim.getPlatform().getCachedVectorToTargetXY().x = 1.3
    sim.getPlatform().getCachedVectorToTargetXY().y = 3.7
    sim.getPlatform().getCachedAbsoluteAttitude().q0 = 2.2
    plat = sim.getPlatform()
    vttxy = plat.getCachedVectorToTargetXY()
    absat = plat.getCachedAbsoluteAttitude()
    attzns = plat.getAttitudeZNoiseSource()
    print('platform.movePerSec = {n}'.format(n=plat.movePerSec))
    print(
        'platform.vttxy = ({x}, {y}, {z})'
        .format(x=vttxy.x, y=vttxy.y, z=vttxy.z)
    )
    print(
        'platform.absat = ({q0}, {q1}i, {q2}j, {q3}k)'
        .format(q0=absat.q0, q1=absat.q1, q2=absat.q2, q3=absat.q3)
    )
    print(
        'platform.getAttitudeZNoiseSource() = {azns} '
        '(None is ok because it has not been instantiated yet)'
        .format(azns=attzns)
    )

    scene = sim.getScene()
    print('scene = {scene}'.format(scene=scene))
    prim0 = scene.getPrimitive(0)
    centr = prim0.getCentroid()
    print('prim0.centroid = ({x}, {y}, {z})'
          .format(x=centr.x, y=centr.y, z=centr.z))
    aabb = scene.getAABB()
    minpos = aabb.getMinVertex().getPosition()
    print('minpos = ({x}, {y}, {z})'
          .format(x=minpos.x, y=minpos.y, z=minpos.z))
    intsc = prim0.getRayIntersection(5.5, 5.5, 0.1, 0.1, 0.1, 0.8)
    print('intsc = ({t0}, {t1})'.format(t0=intsc[0], t1=intsc[1]))
    sp = prim0.getScenePart()
    sp.id = "SpId"
    print('sp.id = {id}'.format(id=sp.id))
    mat = prim0.getMaterial()
    print('mat.ka = ({ka0}, {ka1}, {ka2}, {ka3})'
          .format(ka0=mat.ka0, ka1=mat.ka1, ka2=mat.ka2, ka3=mat.ka3))
    tri = scene.newTriangle()
    norm = tri.getFaceNormal()
    print('tri.norm = ({x}, {y}, {z})'
          .format(x=norm.x, y=norm.y, z=norm.z))
    print('tri.getNumVertices() = {n}'
          .format(n=tri.getNumVertices()))
    dv = scene.newDetailedVoxel()
    print('dv.nbEchos = {n}'.format(n=dv.nbEchos))
    dvc = dv.getCentroid()
    print('dv.centroid = ({x}, {y}, {z})'
          .format(x=dvc.x, y=dvc.y, z=dvc.z))
