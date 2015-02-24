# !/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import pylab
import nest
import nest.raster_plot
import nest.topology as tp
import logging as log


# Implementation of the multi-layered local cortical network model by

# Potjans, Tobias C., and Markus Diesmann. "The cell-type specific
# cortical microcircuit: relating structure and activity in a full-scale
# spiking network model." Cerebral Cortex (2014): bhs358.

# Uses user_params.sli, sim_params.sli, and network_params.sli

# function definitions:
# - CheckParameters
# - PrepareSimulation
# - DerivedParameters
# - CreateNetworkNodes
# - WriteGIDstoFile
# - ConnectNetworkNodes

# Tobias Potjans 2008; adapted by Tom Tetzlaff, David Dahmen,
# Sacha van Albada 2013; Hannah Bos 2014
# Converted to python by Russi Chatterjee

def CheckParameters():
  if neuron_model != 'iaf_psc_exp':
    if Rank != 0:
      log.warn('Unexpected neuron type: script is tuned to "iaf_psc_exp" neurons.')

  n_layers = len(full_scale_n_neurons)
  n_pops_per_layer = np.shape(full_scale_n_neurons)[0]

  # TODO: what the fuck is this?
  # conn_probs Dimensions 0 get
  # n_layers * n_pops_per_layer
  # eq not
  # conn_probs Dimensions 1 get
  # n_layers n_pops_per_layer mul
  # eq not or
  # {
  #     /CheckParameters /conn_probs_dimensions raiseerror
  # } if

  if record_fraction_neurons_spikes:
    if frac_rec_spikes > 1:
      raise ValueError('frac_rec_spikes')
  else:
    if > area * min(Map, min(full_scale_n_neurons, n_rec_spikes)):
      raise ValueError('n_rec_spikes')

  if record_fraction_neurons_voltage:
    if frac_rec_voltage > 1:
      raise ValueError('frac_rec_voltage')
  else:
    if > area * min(Map, min(full_scale_n_neurons, n_rec_voltage)):
      raise ValueError('n_rec_voltage')


