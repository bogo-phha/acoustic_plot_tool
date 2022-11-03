import numpy as np

def toComplex(mag, phase):
    h = 10**(mag/20) * np.e**( 1j * phase * np.pi/180 )
    h = h.astype(np.complex128)
    return h