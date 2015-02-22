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


def run(total, ratio_e, ratio_i, extent, wt_max, wt_min, delay_min, delay_max, ac_amp, ac_freq):
  pop_e = total*ratio_e
  pop_i = total*ratio_i
  ratio = ratio_e/ratio_i
  rad_e = int(math.sqrt(pop_e))
  rad_i = int(math.sqrt(pop_i))
  u = str(uuid.uuid1())

  # ratio = ratio
  nest.ResetKernel()
  nest.SetKernelStatus({'local_num_threads': 8})

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
      # 'uniform': { 'min': 0.0, 'max': wt_max }
      'gaussian': {'p_center': 1., 'sigma': 1.}
    },
    'delays': {
      'uniform': { 'min': delay_min, 'max': delay_max }
    }
  }

  i_e = {
    'connection_type': 'divergent',
    'synapse_model': 'inhibitory',
    'weights': {
      # 'uniform': { 'min': wt_min*ratio, 'max': 0.0 }
      'gaussian': {'p_center': -1.*ratio, 'sigma': 1.}
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
    'elements': 'ac',
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
  # tp.ConnectLayers(i, detector, {'connection_type': 'divergent'})


  nest.Simulate(1000)

  n1 = e[0] + 1
  n1id = tuple([x for x in xrange(n1, int(n1+(rad_e*rad_e)))])
  n1c = nest.GetConnections(n1id)
  w1 = nest.GetStatus(n1c, 'weight')
  # pylab.hist(w1, bins=100)

  pylab.figure()
  n2 = i[0] + 1
  n2id = tuple([x for x in xrange(n2, int(n2+(rad_i*rad_i)))])
  n2c = nest.GetConnections(n2id)
  w2 = nest.GetStatus(n2c, 'weight')
  # pylab.hist(w2, bins=100)

  # pylab.figure()
  spike_rows = 1
  spike_id = detector[0]+1
  spike_ids = tuple([x for x in xrange(spike_id, spike_id+(spike_rows*spike_rows))])
  # nest.raster_plot.from_device(spike_ids, hist=True)

  # find how many times it spiked
  sid = nest.GetStatus(spike_ids, 'events')
  # h = pylab.hist(sid[0]['times'], bins=100)
  h = np.histogram(sid[0]['times'], bins=100)
  h = h[0][h[0] > 0.]

  # pylab.show()
  print "Spiked " + str(len(h)) + " times"

  return ({
    'spikes': int(len(h)),
    'total': total,
    'ratio_e': ratio_e,
    'ratio_i': ratio_i,
    'extent': extent,
    'wt_max': wt_max,
    'wt_min': wt_min,
    'delay_min': delay_min,
    'delay_max': delay_max,
    'ac_amp': ac_amp,
    'ac_freq': ac_freq,
  })



total = 1000
ratio_e = 0.8
ratio_i = 0.2
extent = 1.0
wt_max = .1

# keep increasing this to see awesome bifurcation effect, around 0.8-0.9
wt_min = -.1

delay_min = 0.1
delay_max = 0.2
ac_amp = 300.0
ac_freq = 100.0

results = []

for ac_freq in xrange(2, 50, 2):
  for ac_amp in xrange(300, 500, 10):
    r = {}
    try:
      r = run(total, ratio_e, ratio_i, extent, wt_max, wt_min, delay_min, delay_max, float(ac_amp), float(ac_freq))
      results.append(r)
    except Exception as e:
      results.append({
        'spikes': 0,
        'total': total,
        'ratio_e': ratio_e,
        'ratio_i': ratio_i,
        'extent': extent,
        'wt_max': wt_max,
        'wt_min': wt_min,
        'delay_min': delay_min,
        'delay_max': delay_max,
        'ac_amp': ac_amp,
        'ac_freq': ac_freq
      })

    pylab.close('all')
    print "---------------------------------------------------------------"
    print r
    # print "total = " + str(total)
    # print "ratio_e = " + str(ratio_e)
    # print "ratio_i = " + str(ratio_i)
    # print "extent = " + str(extent)
    # print "wt_max = " + str(wt_max)
    # print "wt_min = " + str(wt_min)
    # print "delay_min = " + str(delay_min)
    # print "delay_max = " + str(delay_max)
    # print "ac_amp = " + str(ac_amp)
    # print "ac_freq = " + str(ac_freq)
    print "---------------------------------------------------------------"


amps = [a[ac_amp] for a in results]
freqs = [a[ac_freq] for a in results]
sps = [a[spikes] for a in results]

from mpl_toolkits.mplot3d import Axes3D
ax =  Axes3D(pylab.figure())
ax.scatter(freqs, amps, sps)
pylab.show()
