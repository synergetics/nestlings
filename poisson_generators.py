
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




nest.ResetKernel()

neuron_model = 'iaf_psc_exp'

model_params = {'tau_m': 10.,        # membrane time constant (ms)
                'tau_syn_ex': 0.5,   # excitatory synaptic time constant (ms)
                'tau_syn_in': 0.5,   # inhibitory synaptic time constant (ms)
                't_ref': 2.,         # absolute refractory period (ms)
                'E_L': -65.,         # resting membrane potential (mV)
                'V_th': -50.,        # spike threshold (mV)
                'C_m': 250.,         # membrane capacitance (pF)
                'V_reset': -65.      # reset potential (mV)
               }

nest.SetDefaults(neuron_model, model_params)

a = nest.Create(neuron_model, 100)
b = nest.Create('poisson_generator')
nest.SetStatus(b, {'rate': 100.*1000.})

d = nest.CopyModel('sinusoidal_poisson_generator', 'spg', {'individual_spike_trains': False})
c = nest.Create('spg')
nest.SetStatus(c, {
  'dc': 100.*100.,
  'ac': 100.*100.-1,
  'freq': 10.,
  # 'phi': 0.
})
s = nest.Create('spike_detector')
v = nest.Create('voltmeter')

nest.Connect(b, a, 'all_to_all', {'weight': 7.15, 'model': 'static_synapse'})
nest.Connect(c, a, 'all_to_all', {'weight': 7.15, 'model': 'static_synapse'})
nest.Connect(a, s)
# nest.Connect(b, s)
# nest.Connect(c, s)
nest.Connect(v, a)

nest.Simulate(500)
nest.raster_plot.from_device(s, hist=True)
# nest.voltage_trace.from_device(v)

pylab.show()

