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
  (1-alpha_beta_ratio)*layer_4_population, # beta excitatory neurons of layer 4 of area W
  0.03*layer_4_population # gamma excitatory neurons of area W
]

# An array of all the areas
population_properties = [a, alpha, beta, gamma]

simulation_time = 2000

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

  # tp.PlotLayer(l)
  # pylab.show()

  # s = tp.CreateLayer({
  #   'rows': int(pop),
  #   'columns': int(pop),
  #   'elements': 'spike_detector',
  #   'extent': [float(pop), float(pop)]
  # })

  if ctr > 0:
    # intra-layer connections - neighbours only
    tp.ConnectLayers(l, l, {
      'connection_type': 'divergent',
      'mask': {
        'doughnut': {
          'inner_radius': radius/10,
          'outer_radius': radius/4
        }
      },
      'kernel': {
        'gaussian': {
          'p_center': 1.0,
          'sigma': 1.0
        }
      }
    })

  # tp.ConnectLayers(s, l, {'connection_type': 'convergent'})

  # spike_detectors.append(s)
  layers.append(l)


# Create the input source (how? - connect mic?)
nest.CopyModel('stdp_synapse', 'excitatory', {'mu_plus': 1.0, 'mu_minus':0.0})
nest.CopyModel('stdp_synapse', 'inhibitory', {'mu_plus': 0.0, 'mu_minus':1.0})

# Connection topologies
tonotopic_excitatory = {
  'connection_type': 'divergent',
  'mask': {
    'doughnut': {
      'inner_radius': radius/10,
      'outer_radius': radius/4
    }
  },
  'kernel': {
    'gaussian': {
      'p_center': 1.0,
      'sigma': 1.0
    }
  },
  'synapse_model': 'excitatory'
}

excitatory = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory'
}

inhibitory = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory'
}

# Area A to layer 4 of area W connections
tp.ConnectLayers(layers[0], layers[1], tonotopic_excitatory)
tp.ConnectLayers(layers[0], layers[2], tonotopic_excitatory)

# Layer 4 Area W interconnections
tp.ConnectLayers(layers[2], layers[1], inhibitory)
tp.ConnectLayers(layers[1], layers[2], excitatory)
tp.ConnectLayers(layers[1], layers[1], excitatory)
tp.ConnectLayers(layers[2], layers[2], inhibitory)

# Layer 4 to layer 5/6 of Area W connections
tp.ConnectLayers(layers[1], layers[3], excitatory)
tp.ConnectLayers(layers[1], layers[3], inhibitory)

# tp.ConnectLayers(layers[3], spike_detectors[len(spike_detectors)-1],
#   {'connection_type': 'divergent'})

# nest.Simulate(simulation_time)

