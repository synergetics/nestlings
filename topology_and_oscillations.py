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

a = {
  "tau_m"     : 20.0,
  "V_th"      : -55.0,
  "E_L"       : -65.0,
  "t_ref"     : 2.0,
  "V_reset"   : -75.0,
  "C_m"       : 250.0,
  "V_m"       : 0.0,
}

alpha = {
  "tau_m"     : 20.0,
  "V_th"      : -55.0,
  "E_L"       : -65.0,
  "t_ref"     : 2.0,
  "V_reset"   : -75.0,
  "C_m"       : 250.0,
  "V_m"       : 0.0,
}

beta = {
  "tau_m"     : 20.0,
  "V_th"      : -55.0,
  "E_L"       : -65.0,
  "t_ref"     : 2.0,
  "V_reset"   : -75.0,
  "C_m"       : 250.0,
  "V_m"       : 0.0,
}

gamma = {
  "tau_m"     : 6.0,
  "V_th"      : -55.0,
  "E_L"       : -65.0,
  "t_ref"     : 2.0,
  "V_reset"   : -75.0,
  "C_m"       : 250.0,
  "V_m"       : 0.0,
}

# The population sizes

# The total population of layer 4 of area W
layer_4_population = 1000

# ratio of number of excitatory to inhibitory neurons (alpha/beta)
alpha_beta_ratio = 0.5

# A dict of all the populations
population_sizes = [
  2*layer_4_population, # area A
  alpha_beta_ratio*layer_4_population, # alpha excitatory neurons of layer 4 of area W
  (1-alpha_beta_ratio)*layer_4_population, # beta inhibitory neurons of layer 4 of area W
  0.03*layer_4_population # gamma excitatory neurons of area W
]

# An array of all the areas
population_properties = [a, alpha, beta, gamma]

simulation_time = 1000

radius = float(int(math.sqrt(layer_4_population)/10)*10)

# Create the neuronal populations
noises = [] # todo
spike_detectors = []
layers = []
for ctr in xrange(len(population_properties)):
  nest.CopyModel('iaf_psc_alpha', 'neuron'+str(ctr), population_properties[ctr])

  pop = math.sqrt(population_sizes[ctr])
  l = tp.CreateLayer({
    'rows': int(pop),
    'columns': int(pop),
    'elements': 'neuron'+str(ctr),
    'extent': [radius, radius],
    'edge_wrap': True
  })

  layers.append(l)


# Create the input source (how? - connect mic?)
# For list of all synapse types, execute nest.Models('synapses')
# nest.CopyModel('stdp_synapse', 'excitatory', {'mu_plus': 1.0, 'mu_minus':1.0})
# nest.CopyModel('stdp_synapse', 'inhibitory', {'mu_plus': -1.0, 'mu_minus':-1.0})

nest.CopyModel('static_synapse', 'excitatory')
nest.CopyModel('static_synapse', 'inhibitory')

# Connection topologies
tonotopic_excitatory = {
  'connection_type': 'divergent',
  # 'mask': {
  #   'doughnut': {
  #     'inner_radius': radius/10,
  #     'outer_radius': radius
  #   }
  #   # 'circular': {'radius': radius}
  # },
  'weights': {
    # 'gaussian': {
    #   'p_center': 1.0,
    #   'sigma': 10.0
    # }
    'uniform': {
      'min': 0.0,
      'max': 1.0
    }
  },
  'allow_oversized_mask': True,
  # 'kernel': {
  #   'gaussian': {
  #     'p_center': 1.0,
  #     'sigma': 1.0
  #   }
  # },
  'synapse_model': 'excitatory'
}

tonotopic_excitatory_noSTDP = {
  'connection_type': 'divergent',
  'mask': {
    'circular': {
      'radius': radius/2
    }
  },
  'allow_oversized_mask': True,
  'kernel': {
    'gaussian': {
      'p_center': 1.0,
      'sigma': 1.0
    }
  }
}

excitatory = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory',
  'weights': {
    'uniform': {
      'min': 0.0,
      'max': 0.1
    }
  }
}

excitatory_layerW = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory',
  'weights': {
    'uniform': {
      'min': 0.0,
      'max': 1.0
    }
  }
}

excitatory_topological = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory',
  'weights': {
    'uniform': {
      'min': 0.0,
      'max': 5.0
    }
  },
  'kernel': {
    'gaussian': {
      'p_center': 1.0,
      'sigma': radius/2
    }
  }
}

inhibitory_layerW = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory',
  'weights': {
    'uniform': {
      'min': -5.0,
      'max': 0.0
    }
  }
}

inhibitory_delay_layerW = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory',
  'weights': {
    'uniform': {
      'min': -5.0,
      'max': 0.0
    }
  }
}

inhibitory = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory',
  'weights': {
    'uniform': {
      'min': -0.1,
      'max': 0.0
    }
  }
}


inhibitory_topolocical = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory',
  'weights': {
    'uniform': {
      'min': -0.1,
      'max': 0.0
    }
  },
  'kernel': {
    'gaussian': {
      'p_center': 1.0,
      'sigma': radius/2
    }
  }
}

# Area A to layer 4 of area W connectionso
tp.ConnectLayers(layers[0], layers[1], excitatory_topological)
tp.ConnectLayers(layers[0], layers[2], excitatory_topological)

# Layer 4 Area W interconnections
tp.ConnectLayers(layers[2], layers[1], inhibitory_layerW)
tp.ConnectLayers(layers[1], layers[2], excitatory_layerW)
tp.ConnectLayers(layers[1], layers[1], excitatory_layerW)
# tp.ConnectLayers(layers[2], layers[2], inhibitory)

# Layer 4 to layer 5/6 of Area W connections
tp.ConnectLayers(layers[1], layers[3], excitatory_layerW)
tp.ConnectLayers(layers[1], layers[3], inhibitory_layerW)

# Provide inputs
nest.CopyModel('ac_generator', 'ac', {'amplitude': 200.0, 'frequency': 20.0})
nest.CopyModel('ac_generator', 'ac2', {'amplitude': 50.0, 'frequency': 3.0})

nest.CopyModel('dc_generator', 'dc', {'amplitude': 100.0})
ac_rows = 1
ac = tp.CreateLayer({
  'rows': ac_rows,
  'columns': ac_rows,
  'elements': ['ac', 'ac2'],
  'extent': [radius, radius]
})


nest.CopyModel('noise_generator', 'noises', {'mean': 0.0, 'std': 200.0})
noise = tp.CreateLayer({
  'rows': ac_rows,
  'columns': ac_rows,
  'elements': 'noises',
  'extent': [radius, radius]
})

# Create a raster plotter
spike_rows = int(math.sqrt(population_sizes[len(population_sizes)-1]))
spikes = tp.CreateLayer({
  'rows': spike_rows,
  'columns': spike_rows,
  'elements': 'spike_detector',
  'extent': [radius, radius]
})

# tp.PlotLayer(layers[2])

tp.ConnectLayers(ac, layers[0], {'connection_type': 'divergent'})
# tp.ConnectLayers(ac, layers[2], {'connection_type': 'divergent'})
tp.ConnectLayers(noise, layers[0], {'connection_type': 'divergent'})
# tp.ConnectLayers(noise, layers[2], {'connection_type': 'divergent'})

tp.ConnectLayers(layers[0], spikes, {'connection_type': 'convergent'})
tp.ConnectLayers(layers[1], spikes, {'connection_type': 'convergent'})
tp.ConnectLayers(layers[2], spikes, {'connection_type': 'convergent'})
tp.ConnectLayers(layers[3], spikes, {'connection_type': 'convergent'})

nest.Simulate(simulation_time)

spike_id = spikes[0]+1
spike_ids = tuple([x for x in xrange(spike_id, spike_id+(spike_rows*spike_rows))])
nest.raster_plot.from_device(spike_ids)
pylab.show()

n1 = p1._e[0] + 1
n1id = tuple([x for x in xrange(n1, int(n1+(p1._extent*p1._extent)))])
n1c = nest.GetConnections(n1id)
w1 = nest.GetStatus(n1c, 'weight')
pylab.hist(w1, bins=100)
pylab.show()

n2 = p1._i[0] + 1
n2id = tuple([x for x in xrange(n2, int(n2+(p1._extent*p1._extent)))])
n2c = nest.GetConnections(n2id)
w2 = nest.GetStatus(n2c, 'weight')
pylab.hist(w2, bins=100)
pylab.show()


