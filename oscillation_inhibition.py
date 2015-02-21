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


total = 1000
pop_e = total*0.8
pop_i = total*0.2
ratio = 0.8/0.2
rad_e = int(math.sqrt(pop_e))
rad_i = int(math.sqrt(pop_i))
extent = 1.0
wt_max = .1

# keep increasing this to see awesome bifurcation effect, around 0.8-0.9
wt_min = -.895

delay_min = 0.1
delay_max = 0.2
ac_amp = 200.0
ac_freq = 10.0

u = uuid.uuid1()


nest.SetDefaults('iaf_psc_alpha', {
  'tau_m'     : 20.0,
  'V_th'      : 20.0,
  'E_L'       : 10.0,
  't_ref'     : 2.0,
  'V_reset'   : 0.0,
  'C_m'       : 200.0,
  'V_m'       : 0.0
})

e = tp.CreateLayer({
  'rows': int(rad_e),
  'columns': int(rad_e),
  'elements': 'iaf_psc_alpha',
  'extent': [extent, extent],
  'edge_wrap': True
})

i = tp.CreateLayer({
  'rows': int(rad_i),
  'columns': int(rad_i),
  'elements': 'iaf_psc_alpha',
  'extent': [extent, extent],
  'edge_wrap': True
})

# nest.CopyModel('stdp_synapse', 'excitatory', {'Wmax': 10.0})
nest.CopyModel('static_synapse', 'excitatory')
nest.CopyModel('static_synapse', 'inhibitory')

e_i = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory',
  'weights': {
    'uniform': { 'min': wt_max/2, 'max': wt_max }
  },
  'delays': {
    'uniform': { 'min': delay_min, 'max': delay_max }
  }
}

i_e = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory',
  'weights': {
    'uniform': { 'min': wt_min*ratio, 'max': ratio*wt_min + .1 }
  },
  'delays': {
    'uniform': { 'min': delay_min, 'max': delay_max }
  }
}

nest.CopyModel('ac_generator', 'ac', {'amplitude': ac_amp, 'frequency':  ac_freq})
nest.CopyModel('dc_generator', 'dc', {'amplitude': ac_amp})

ac = tp.CreateLayer({
  'rows': 1,
  'columns': 1,
  'elements': 'dc',
  'extent': [extent, extent]
})

detector = tp.CreateLayer({
  'rows': 1,
  'columns': 1,
  'elements': 'spike_detector',
  'extent': [extent, extent]
})

tp.ConnectLayers(e, i, e_i)
tp.ConnectLayers(i, e, i_e)
tp.ConnectLayers(ac, e, {'connection_type': 'divergent'})
tp.ConnectLayers(ac, i, {'connection_type': 'divergent'})
tp.ConnectLayers(e, detector, {'connection_type': 'divergent'})
tp.ConnectLayers(i, detector, {'connection_type': 'divergent'})


nest.Simulate(1000)

n1 = e[0] + 1
n1id = tuple([x for x in xrange(n1, int(n1+(rad_e*rad_e)))])
n1c = nest.GetConnections(n1id)
w1 = nest.GetStatus(n1c, 'weight')
pylab.hist(w1, bins=100)

pylab.figure()
n2 = i[0] + 1
n2id = tuple([x for x in xrange(n2, int(n2+(rad_i*rad_i)))])
n2c = nest.GetConnections(n2id)
w2 = nest.GetStatus(n2c, 'weight')
pylab.hist(w2, bins=100)

# pylab.figure()
spike_rows = 1
spike_id = detector[0]+1
spike_ids = tuple([x for x in xrange(spike_id, spike_id+(spike_rows*spike_rows))])
nest.raster_plot.from_device(spike_ids, hist=True)

pylab.show()

