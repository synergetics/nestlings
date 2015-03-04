#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import pylab
import nest
import nest.raster_plot
import nest.voltage_trace
import nest.topology as tp
import ggplot


t_sim = 500

populations = [1, 100]

no_recurrent = True

neuron_model = 'iaf_psc_exp'
model_params = {
  'tau_m': 10.,        # membrane time constant (ms)
  'tau_syn_ex': 0.5,   # excitatory synaptic time constant (ms)
  'tau_syn_in': 0.5,   # inhibitory synaptic time constant (ms)
  't_ref': 2.,         # absolute refractory period (ms)
  'E_L': -65.,         # resting membrane potential (mV)
  'V_th': -50.,        # spike threshold (mV)
  'C_m': 250.,         # membrane capacitance (pF)
  'V_reset': -65.      # reset potential (mV)
}

wt_e = 1.

extent = 1.

delay_max = 2.
delay_min = 1.

ac_amp = 3000.0
ac_freq = 4.0


nest.ResetKernel()
nest.SetKernelStatus({'local_num_threads': 8})

nest.CopyModel('iaf_psc_exp', 'exp_nrn', model_params)

layers = []

spike_detector = tp.CreateLayer({
  'rows': 1,
  'columns': 1,
  'elements': 'spike_detector',
  'extent': [extent, extent]
})
spike_detector_nrn = (spike_detector[0]+1,)

voltmeter = tp.CreateLayer({
  'rows': 1,
  'columns': 1,
  'elements': 'voltmeter',
  'extent': [extent, extent]
})
voltmeter_nrn = (voltmeter[0]+1,)

nest.CopyModel('ac_generator', 'ac', {'amplitude': ac_amp, 'frequency':  ac_freq})
input = tp.CreateLayer({
  'rows': 1,
  'columns': 1,
  'elements': 'ac',
  'extent': [extent, extent]
})


for pop in populations:
  rows = columns = int(math.sqrt(pop))
  l = tp.CreateLayer({
    'rows': rows,
    'columns': columns,
    'extent': [extent, extent],
    'elements': 'exp_nrn',
    # 'edge_wrap': False
  })

  layers.append(l)


conn = {
  'connection_type': 'divergent',
  'synapse_model': 'static_synapse',
  'weights': {
    'gaussian': {'p_center': wt_e, 'sigma': extent}
  },
  'delays': {
    'uniform': { 'min': delay_min, 'max': delay_max }
  }
}

for source in layers:
  for target in layers:
    if no_recurrent:
      if source != target:
        tp.ConnectLayers(source, target, conn)
    else:
      tp.ConnectLayers(source, target, conn)


for layer in layers:
  tp.ConnectLayers(layer, spike_detector, {'connection_type': 'convergent'})
  tp.ConnectLayers(voltmeter, layer, {'connection_type': 'divergent'})

tp.ConnectLayers(input, layers[0], {'connection_type': 'convergent'})

nest.Simulate(t_sim)

nest.raster_plot.from_device(spike_detector_nrn)
# nest.voltage_trace.from_device(voltmeter_nrn)
pylab.show()


