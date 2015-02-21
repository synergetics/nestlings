#!/usr/bin/env python

import sys
sys.path.append('/opt/lib/python2.7/site-packages/')

import math
import numpy as np
import nest
import nest.topology as tp
import uuid


class Connector(object):
  def __init__(self, pop1, pop2, connection_type, sparse=True):
    pass

  def make_sparse_layer(sparsity=0.1):
    pass

  def connect(p1, p2, props):
    pass

