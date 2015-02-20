#!/usr/bin/env python


import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import pylab
import nest
import nest.raster_plot
import nest.topology as tp
import uuid

nest.ResetKernel()
nest.SetKernelStatus({'local_num_threads': 8})


class OscillatingPopulation(object):

  def __init__(self, size, e_to_i_ratio):
    self._pop = size

    # calculate the population sizes
    self._pop_ratio = e_to_i_ratio
    self._pop_i = self._pop / (self._pop_ratio + 1)
    self._rad_i = int(math.sqrt(self._pop_i))
    self._pop_e = self._pop_ratio * self._pop_i
    self._rad_e = int(math.sqrt(self._pop_e))

    # some defaults
    self._type = 'iaf_psc_alpha'
    self._props = {
      'tau_m'     : 20.0,
      'V_th'      : 20.0,
      'E_L'       : 10.0,
      't_ref'     : 2.0,
      'V_reset'   : 0.0,
      'C_m'       : 200.0,
      'V_m'       : 0.0
    }
    self._noise = 200.0
    self._wt = 0.1
    self._extent = float(max(self._rad_e, self._rad_i))
    self._detectors = []
    self._oscillations = []

  def oscillate(self, amplitude, freq, time=0):
    self._oscillations.append([amplitude, freq])

  def noise(self, std_dev):
    self._noise = std_dev

  def connect(self, connection):
    pass

  def detect(self, kind):
    detector = tp.CreateLayer({
      'rows': 1,
      'columns': 1,
      'elements': 'spike_detector',
      'extent': [self._extent, self._extent]
    })
    self._detectors.append([detector, kind])
    return tuple([detector[0]+1])

  def plot(self, detector):
    nest.raster_plot.from_device(detector, hist=True)
    pylab.show()

  def construct(self):
    nest.CopyModel('static_synapse', 'excitatory')
    nest.CopyModel('static_synapse', 'inhibitory')

    e_e = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory',
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt
        }
      }
    }

    e_i = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory',
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt
        }
      }
    }

    i_e = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory',
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt*self._pop_ratio
        }
      }
    }

    i_i = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory',
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt*self._pop_ratio
        }
      }
    }

    nest.CopyModel(self._type, 'neuron', self._props)

    e = tp.CreateLayer({
      'rows': int(self._rad_e),
      'columns': int(self._rad_e),
      'elements': self._type,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    i = tp.CreateLayer({
      'rows': int(self._rad_i),
      'columns': int(self._rad_i),
      'elements': self._type,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    tp.ConnectLayers(e, i, e_i)
    tp.ConnectLayers(e, e, e_e)
    tp.ConnectLayers(i, e, i_e)
    tp.ConnectLayers(i, i, i_i)

    # Create and connect oscillating inputs
    for os in self._oscillations:
      u = str(uuid.uuid4())
      nest.CopyModel('ac_generator', u, {'amplitude': float(os[0]), 'frequency':  float(os[1])})

      ac = tp.CreateLayer({
        'rows': 1,
        'columns': 1,
        'elements': u,
        'extent': [self._extent, self._extent]
      })

      tp.ConnectLayers(ac, e, {'connection_type': 'divergent'})
      tp.ConnectLayers(ac, i, {'connection_type': 'divergent'})

    # Create and connect stochastic noise generators
    nest.CopyModel('noise_generator', 'noises', {'mean': 0.0, 'std': self._noise})
    noise = tp.CreateLayer({
      'rows': 1,
      'columns': 1,
      'elements': 'noises',
      'extent': [self._extent, self._extent]
    })

    tp.ConnectLayers(noise, e, {'connection_type': 'divergent'})
    tp.ConnectLayers(noise, i, {'connection_type': 'divergent'})

    for d in self._detectors:
      if d[1] == 'excitatory':
        tp.ConnectLayers(e, d[0], {'connection_type': 'divergent'})
      elif d[1] == 'inhibitory':
        tp.ConnectLayers(i, d[0], {'connection_type': 'divergent'})
      else:
        raise ValueError("Kind specified s wrong, such kind of neurons dont exist here.")

    self._e = e
    self._i = i


p = OscillatingPopulation(1000, 5)
p.oscillate(1000, 35)
e = p.detect('excitatory')
i = p.detect('inhibitory')
p.construct()

nest.Simulate(1000)

p.plot(e)
p.plot(i)
