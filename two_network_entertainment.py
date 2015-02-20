#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import pylab
import nest
import nest.raster_plot
import nest.topology as tp


nest.ResetKernel()
nest.SetKernelStatus({'local_num_threads': 8})

network_radiusulation = 100
excitatory_ratio = 0.8

I_CDC_e = (10.1, 11.3)
I_CDC_i = (3.8, 6.3)

simulation_time = 600

def rounded_radius(pop):
  return int(math.sqrt(pop))

inhibitory_ratio = 1 - excitatory_ratio
excitatory_radius = rounded_radius(network_radiusulation*excitatory_ratio)
inhibitory_radius = rounded_radius(network_radiusulation*inhibitory_ratio)

e = tp.CreateLayer({
  'rows': excitatory_radius,
  'columns': excitatory_radius,
  'elements': 'iaf_psc_alpha',
  'extent': [1.0,1.0],
  'edge_wrap': True
})

i = tp.CreateLayer({
  'rows': inhibitory_radius,
  'columns': inhibitory_radius,
  'elements': 'iaf_psc_alpha',
  'extent': [1.0,1.0],
  'edge_wrap': True
})

e_i = {
  'connection_type': 'divergent',
  'kernel': {
    'uniform': { 'min': 0.64, 'max': 0.65 }
  }
}

e_e = {
  'connection_type': 'divergent',
  'kernel': {
    'uniform': { 'min': 0.29, 'max': 0.3 }
  }
}

i_e = {
  'connection_type': 'divergent',
  'kernel': {
    'uniform': { 'min': 0.59, 'max': 0.6 }
  }
}

i_i = {
  'connection_type': 'divergent',
  'kernel': {
    'uniform': { 'min': 0.054, 'max': 0.055 }
  }
}

tp.ConnectLayers(e, i, e_i)
tp.ConnectLayers(i, e, i_e)
tp.ConnectLayers(e, e, e_e)
tp.ConnectLayers(i, i, i_i)

nest.CopyModel('dc_generator', 'dc', {'amplitude': 4000.0})
ac_rows = 1
ac = tp.CreateLayer({
  'rows': ac_rows,
  'columns': ac_rows,
  'elements': ['dc'],
  'extent': [1.0, 1.0]
})

tp.ConnectLayers(ac, e, {'connection_type': 'divergent'})
tp.ConnectLayers(ac, i, {'connection_type': 'divergent'})

spike_rows = 1
spikes = tp.CreateLayer({
  'rows': spike_rows,
  'columns': spike_rows,
  'elements': 'spike_detector',
  'extent': [1.0, 1.0]
})
tp.ConnectLayers(e, spikes, {'connection_type': 'divergent'})
tp.ConnectLayers(i, spikes, {'connection_type': 'divergent'})

nest.Simulate(simulation_time)

spike_id = spikes[0]+1
spike_ids = tuple([x for x in xrange(spike_id, spike_id+(spike_rows*spike_rows))])
nest.raster_plot.from_device(spike_ids)
pylab.show()

