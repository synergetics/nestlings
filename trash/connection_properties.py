#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import nest
import nest.topology as tp
import uuid


connections = {
  'connection_type': 'divergent',
  'synapse_model': None,
  'kernel': None,
  'mask': None,
  'allow_oversized_mask': True,
  'weights': None,
  'delays': None
}

masks = {
  'rectangular': {'lower_left': [-0.5,-0.5], 'upper_right': [0.5,0.5]},
  'circular': {'radius': 1.},
  'doughnut': {'inner_radius': 0., 'outer_radius': 1.},
  'box': {'lower_left': [-0.5,-0.5,0.5], 'upper_right': [0.5,0.5,0.5]},
  'spherical': {'radius': 1.}
}

kernels = {
  'linear': {'a': 1., 'c': 0.},
  'exponential': {'a': 1., 'c': 0., 'tau': 1.},
  'gaussian': {'p_center': 1., 'sigma': 1., 'mean': 0., 'c': 0.},
  'gaussian2D': {'p_center': 1., 'sigma_x': 1., 'sigma_y': 1., 'mean_x': 0., 'mean_y': 0., 'rho': 0., 'c': 0.},
  'uniform': {'min': 0., 'max': 1.},
  'normal': {'mean': 0., 'sigma': 1., 'min': 0., 'max': 1.},
  'lognormal': {'mu': 0., 'sigma': 1., 'min': 0., 'max': 1.}
}

weights = {
  'linear': {'a': 1., 'c': 0.},
  'exponential': {'a': 1., 'c': 0., 'tau': 1.},
  'gaussian': {'p_center': 1., 'sigma': 1., 'mean': 0., 'c': 0.},
  'gaussian2D': {'p_center': 1., 'sigma_x': 1., 'sigma_y': 1., 'mean_x': 0., 'mean_y': 0., 'rho': 0., 'c': 0.},
  'uniform': {'min': 0., 'max': 1.},
  'normal': {'mean': 0., 'sigma': 1., 'min': 0., 'max': 1.},
  'lognormal': {'mu': 0., 'sigma': 1., 'min': 0., 'max': 1.}
}

delays = {
  'linear': {'a': 1., 'c': 0.},
  'exponential': {'a': 1., 'c': 0., 'tau': 1.},
  'gaussian': {'p_center': 1., 'sigma': 1., 'mean': 0., 'c': 0.},
  'gaussian2D': {'p_center': 1., 'sigma_x': 1., 'sigma_y': 1., 'mean_x': 0., 'mean_y': 0., 'rho': 0., 'c': 0.},
  'uniform': {'min': 0., 'max': 1.},
  'normal': {'mean': 0., 'sigma': 1., 'min': 0., 'max': 1.},
  'lognormal': {'mu': 0., 'sigma': 1., 'min': 0., 'max': 1.}
}

defaults = {
  'radius': 1.,
  'mask': 1.,
  'kernel': 1.,
  'weight': 1.,
  'delay': 0.
}


class ConnectionBuilder(object):

  def __init__(self, properties):
    self.conn = {
      'synapse_model': 'stdp_synapse',
      'connection_type': 'divergent',
      'synapse_model': None,
      'kernel': None,
      'mask': None,
      'allow_oversized_mask': True,
      'weights': None,
      'delays': None
    }

    self.id = str(uuid.uuid1())
    properties = self._defaults(properties)
    self.conn['synapse_model'] = properties['synapse_model']
    self.conn['mask'] = self._mask(properties)
    self.conn['kernel'] = self._kernel(properties)
    self.conn['weights'] = self._weights(properties)
    self.conn['delay'] = self._delay(properties)

    self.connection = self.conn

  def _defaults(self, p):
    p.setdefault('radius', defaults['synapse_model'])
    p.setdefault('radius', defaults['radius'])
    p.setdefault('mask', defaults['mask'])
    p.setdefault('kernel', defaults['kernel'])
    p.setdefault('weight', defaults['weight'])
    p.setdefault('delay', defaults['delay'])
    return p

  def _mask(self, properties):
    if type(properties['mask']) is str:
      return masks[properties['mask']]
    else:
      return properties['mask']

  def _kernel(self, properties):
    if type(properties['kernel']) is str:
      return kernels[properties['kernel']]
    else:
      return properties['kernel']

  def _weights(self, properties):
    if type(properties['weight']) is str:
      return weights[properties['weight']]
    else:
      return properties['weight']

  def _delay(self, properties):
    if type(properties['delay']) is str:
      return delays[properties['delay']]
    else:
      return properties['delay']



e_e = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt
    }
  }
}

e_i = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt
    }
  }
}

i_e = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt*self._pop_ratio
    }
  }
}

i_i = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt*self._pop_ratio
    }
  }
}

e_ce = {
  'connection_type': 'divergent',
  'synapse_model': 'excitatory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt
    }
  }
}

i_ci = {
  'connection_type': 'divergent',
  'synapse_model': 'inhibitory'+u,
  'weights': {
    'uniform': {
      'min': 0.,
      'max': self._wt*self._pop_ratio
    }
  }
}


def gen_props(properties, conn_type):
  properties.setdefault('synapse_model', 'stdp_synapse')
  properties.setdefault('probability', 0.1)
  properties.setdefault('extent', 1.0/4.0)
  properties.setdefault('delay', 100.)

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
      'uniform': {'min': self._wt/2, 'max': self._wt}
    },
    'delays': properties['delay']
  }
  return p

