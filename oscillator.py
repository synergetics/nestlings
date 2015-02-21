#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
from pylab import plot, show
import nest
import nest.raster_plot
import nest.voltage_trace
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

    self._initialized = True
    self._constructed = False

  def oscillate(self, amplitude, freq, time=0):
    self._oscillations.append([amplitude, freq])

  def noise(self, std_dev):
    self._noise = std_dev

  def _gen_props(self, properties, conn_type):
    properties.setdefault('synapse_model', 'stdp_synapse')
    properties.setdefault('probability', 0.1)
    properties.setdefault('extent', 1.0/4.0)
    properties.setdefault('delay', 100.0)

    extent = properties['extent']*self._extent

    p = {
      'connection_type': 'divergent',
      'synapse_model': properties['synapse_model'],
      'kernel': {
        'gaussian': { 'p_center': properties['probability'], 'sigma': extent }
      },
      'mask': {
        'circular': {'radius': extent}
      },
      'allow_oversized_mask': True,
      'weights': {
        'uniform': {'min': self._wt/2, 'max': self._wt*100000}
      },
      'delays': properties['delay']
    }
    return p

  def connect(self, to, connection_type='', properties={}):
    if not self._constructed:
      raise StandardError('Call construct before connecting two networks')

    if connection_type == 'excitatory to excitatory':
      tp.ConnectLayers(self._ce, to._ce, self._gen_props(properties, 'e_e'))
    elif connection_type == 'excitatory to inhibitory':
      tp.ConnectLayers(self._ce, to._ci, self._gen_props(properties, 'e_i'))
    elif connection_type == 'inhibitory to excitatory':
      tp.ConnectLayers(self._ci, to._ce, self._gen_props(properties, 'i_e'))
    elif connection_type == 'inhibitory to inhibitory':
      tp.ConnectLayers(self._ci, to._ci, self._gen_props(properties, 'i_i'))
    elif connection_type == '':
      tp.ConnectLayers(self._ce, to._ce, self._gen_props(properties, 'e_e'))
      tp.ConnectLayers(self._ce, to._ci, self._gen_props(properties, 'e_i'))
      tp.ConnectLayers(self._ci, to._ce, self._gen_props(properties, 'i_e'))
      tp.ConnectLayers(self._ci, to._ci, self._gen_props(properties, 'i_i'))
    else:
      raise ValueError('Connection type does not exist')

  def detect(self, kind, what):
    elements = None # the kind of detector device
    reverse = False # does the detector needs to reverse the input and output?

    if what == 'spikes':
      elements = 'spike_detector'
    elif what == 'voltage':
      elements = 'voltmeter'
      reverse = True
    else:
      raise ValueError('What to record from the population? ' + what + ' is not valid')

    detector = tp.CreateLayer({
      'rows': 1,
      'columns': 1,
      'elements': elements,
      'extent': [self._extent, self._extent]
    })
    self._detectors.append([detector, kind, reverse])
    return tuple([detector[0]+1])

  def plot(self, detector, kind):
    if kind == 'spikes':
      nest.raster_plot.from_device(detector, hist=True)
      show()
    elif kind == 'voltage':
      nest.voltage_trace.from_device(detector)
      show()
    else:
      raise ValueError('Wrong kind of detector specified')

  def construct(self):
    u = str(uuid.uuid4())
    nest.CopyModel('stdp_synapse', 'excitatory'+u, {'Wmax': 1.0})
    nest.CopyModel('stdp_synapse', 'inhibitory'+u, {'Wmax': -1.0})

    e_e = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt
        }
      }
    }

    e_i = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt
        }
      }
    }

    i_e = {
      'connection_type': 'divergent',
      'synapse_model': 'inhibitory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt*self._pop_ratio
        }
      }
    }

    i_i = {
      'connection_type': 'divergent',
      'synapse_model': 'inhibitory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt*self._pop_ratio
        }
      }
    }

    e_ce = {
      'connection_type': 'divergent',
      'synapse_model': 'excitatory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt
        }
      }
    }

    i_ci = {
      'connection_type': 'divergent',
      'synapse_model': 'inhibitory'+u,
      'weights': {
        'uniform': {
          'min': 0.0,
          'max': self._wt*self._pop_ratio
        }
      }
    }

    nest.CopyModel(self._type, 'neuron'+u, self._props)

    e = tp.CreateLayer({
      'rows': int(self._rad_e),
      'columns': int(self._rad_e),
      'elements': 'neuron'+u,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    i = tp.CreateLayer({
      'rows': int(self._rad_i),
      'columns': int(self._rad_i),
      'elements': 'neuron'+u,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    ce = tp.CreateLayer({
      'rows': int(self._rad_e/10),
      'columns': int(self._rad_e/10),
      'elements': 'neuron'+u,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    ci = tp.CreateLayer({
      'rows': int(self._rad_i/10),
      'columns': int(self._rad_i/10),
      'elements': 'neuron'+u,
      'extent': [self._extent, self._extent],
      'edge_wrap': True
    })

    tp.ConnectLayers(e, i, e_i)
    tp.ConnectLayers(e, e, e_e)
    tp.ConnectLayers(i, e, i_e)
    tp.ConnectLayers(i, i, i_i)
    tp.ConnectLayers(e, ce, e_ce)
    tp.ConnectLayers(i, ci, i_ci)
    tp.ConnectLayers(ce, e, e_ce)
    tp.ConnectLayers(ci, i, i_ci)

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
    nest.CopyModel('noise_generator', 'noises'+u, {'mean': 0.0, 'std': self._noise})
    noise = tp.CreateLayer({
      'rows': 1,
      'columns': 1,
      'elements': 'noises'+u,
      'extent': [self._extent, self._extent]
    })

    tp.ConnectLayers(noise, e, {'connection_type': 'divergent'})
    tp.ConnectLayers(noise, i, {'connection_type': 'divergent'})

    for d in self._detectors:
      if d[2] == True:
        fro = d[0]
        if d[1] == 'excitatory': to = e
        elif d[1] == 'inhibitory': to = e
        elif d[1] == 'excitatory interaction': to = ce
        elif d[1] == 'inhibitory interaction': to = ci
      else:
        if d[1] == 'excitatory': fro = e
        elif d[1] == 'inhibitory': fro = e
        elif d[1] == 'excitatory interaction': fro = ce
        elif d[1] == 'inhibitory interaction': fro = ci
        to = d[0]

      tp.ConnectLayers(fro, to, {'connection_type': 'divergent'})

    self._e = e
    self._i = i
    self._ce = ce
    self._ci = ci
    self._constructed = True



p1 = OscillatingPopulation(1000, 5)
p1.noise(500.0)
p1.oscillate(300, 100)

# spike event detectors
# e1 = p1.detect('excitatory interaction', 'spikes')
# i1 = p1.detect('inhibitory interaction', 'spikes')

# membrane potential detectors
# ev = p1.detect('excitatory', 'voltage')
# iv = p1.detect('inhibitory', 'voltage')

p1.construct()

p2 = OscillatingPopulation(1000, 5)
p2.noise(500.0)
p2.oscillate(300, 3)

# spike event detectors
# e2 = p2.detect('excitatory interaction', 'spikes')
# i2 = p2.detect('inhibitory interaction', 'spikes')

# membrane potential detectors
# ev = p2.detect('excitatory', 'voltage')
# iv = p2.detect('inhibitory', 'voltage')

p2.construct()

p1.connect(p2)
p2.connect(p1)

nest.Simulate(600)

# p1.plot(e1, 'spikes')
# p1.plot(i1, 'spikes')

# p2.plot(e2, 'spikes')
# p2.plot(i2, 'spikes')

# e_events = nest.GetStatus(e, 'events')
# e_events = e_events[0]
# print type(e_events['times'])


# i_events = nest.GetStatus(i, 'events')
# i_events = i_events[0]

# p.plot(ev, 'voltage')
# p.plot(iv, 'voltage')

