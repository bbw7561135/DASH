import numpy as np
from scipy.fftpack import fft
from dash.array_tools import mean_zero_spectra


def cross_correlation(inputFlux, tempFlux, nw, tempMinMaxIndex):
    tempFlux = mean_zero_spectra(tempFlux, tempMinMaxIndex[0], tempMinMaxIndex[1], nw)
    inputFourier = fft(inputFlux)
    tempFourier = fft(tempFlux)
    # kinput = 2 * np.pi / inputwave
    # ktemp = 2 * np.pi / tempwave

    product = inputFourier * np.conj(tempFourier)
    xCorr = fft(product)

    rmsInput = np.std(inputFourier)
    rmsTemp = np.std(tempFourier)

    xCorrNorm = (1. / (nw * rmsInput * rmsTemp)) * xCorr

    rmsXCorr = np.std(product)

    xCorrNormRearranged = np.concatenate((xCorrNorm[int(len(xCorrNorm) / 2):], xCorrNorm[0:int(len(xCorrNorm) / 2)]))

    # return xCorr, rmsInput, rmsTemp, xCorrNorm, rmsXCorr, xCorrNormRearranged
    return xCorrNormRearranged


def calc_redshift_from_crosscorr(crossCorr, nw, dwlog):
    deltaPeak = np.argmax(abs(crossCorr))

    # z = np.exp(deltaPeak * dwlog) - 1 #equation 13 of Blondin)
    zAxisIndex = np.concatenate((np.arange(-nw / 2, 0), np.arange(0, nw / 2)))
    if deltaPeak < nw / 2:
        z = (np.exp(abs(zAxisIndex) * dwlog) - 1)[deltaPeak]
    else:
        z = -(np.exp(abs(zAxisIndex) * dwlog) - 1)[deltaPeak]

    return z, crossCorr


def get_redshift_axis(nw, dwlog):
    zAxisIndex = np.concatenate((np.arange(-nw / 2, 0), np.arange(0, nw / 2)))
    zAxis = np.zeros(nw)
    zAxis[0:int(nw / 2 - 1)] = -(np.exp(abs(zAxisIndex[0:int(nw / 2 - 1)]) * dwlog) - 1)
    zAxis[int(nw / 2):] = (np.exp(abs(zAxisIndex[int(nw / 2):]) * dwlog) - 1)
    zAxis = zAxis[::-1]

    return zAxis


def get_redshift(inputFlux, tempFlux, nw, dwlog, tempMinMaxIndex):
    crossCorr = cross_correlation(inputFlux, tempFlux, nw, tempMinMaxIndex)
    redshift, crossCorr = calc_redshift_from_crosscorr(crossCorr, nw, dwlog)

    return redshift, crossCorr


def get_median_redshift(inputFlux, tempFluxes, nw, dwlog, inputMinMaxIndex, tempMinMaxIndexes, tempNames):
    inputFlux = mean_zero_spectra(inputFlux, inputMinMaxIndex[0], inputMinMaxIndex[1], nw)

    redshifts = []
    crossCorrs = {}

    for i in range(len(tempFluxes)):
        redshift, crossCorr = get_redshift(inputFlux, tempFluxes[i], nw, dwlog, tempMinMaxIndexes[i])
        redshifts.append(redshift)
        crossCorrs[tempNames[i]] = crossCorr

    if redshifts != []:
        medianIndex = np.argsort(redshifts)[len(redshifts)//2]
        medianRedshift = redshifts[medianIndex]
        medianName = tempNames[medianIndex]
    else:
        return None, None, None

    if len(redshifts) >= 10:
        redshiftError = np.std(redshifts)
    else:
        pass # redshiftError = 1/rlap * kz

    return medianRedshift, crossCorrs, medianName
