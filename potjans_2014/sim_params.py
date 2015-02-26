#!usrbinenv =


# Contains:
# - simulation parameters
# - recording parameters

###################################################
###       Simulation parameters   ###
###################################################

run_mode = 'test'     # (test) for writing files to
                      # directory containing microcircuit.sli
                      # (production) for writing files
                      # to a chosen absolute path.

t_sim = 1000.0      # simulated time (ms)
dt = 0.1            # simulation step (ms). ault is 0.1 ms.
allgather = True    # communication protocol

# master seed for random number generators
# actual seeds will be master_seed ... master_seed + 2*n_vp
#  ==>> different master seeds must be spaced by at least 2*n_vp + 1
# see Gewaltig et al. (2012) for details
master_seed = 123456    # changes rng_seeds and grng_seed

n_mpi_procs = 1             # number of MPI processes

n_threads_per_proc = 2      # number of threads per MPI process
                            # use for instance 24 for a full-scale simulation


n_vp = n_threads_per_proc * n_mpi_procs   # number of virtual processes
                                          # This should be an integer multiple of
                                          # the number of MPI processes
                                          # See Morrison et al. (2005) Neural Comput
# walltime = (8:0:0)    # walltime for simulation

memory = '500mb'    # total memory
                    # use for instance 4gb for a full-scale simulation


###################################################
###       Recording parameters    ###
###################################################

overwrite_existing_files =  True

# whether to record spikes from a fixed fraction of neurons in each population
# If false, a fixed number of neurons is recorded in each population.
# record_fraction_neurons_spikes True with f_rec_spikes 1. records all spikes
record_fraction_neurons_spikes =  True

if record_fraction_neurons_spikes:
  frac_rec_spikes = 0.1
else:
  n_rec_spikes = 100

# whether to record voltage from a fixed fraction of neurons in each population
record_fraction_neurons_voltage =  True

if record_fraction_neurons_voltage:
  frac_rec_voltage = 0.02
else:
  n_rec_voltage = 20.

# whether to write any recorded cortical spikes to file
save_cortical_spikes =  True

# whether to write any recorded membrane potentials to file
save_voltages =  True

# whether to record thalamic spikes (only used when n_thal in
# network_params.sli is nonzero)
record_thalamic_spikes =  True

# whether to write any recorded thalamic spikes to file
save_thalamic_spikes =  True

# name of file to which to write global IDs
GID_filename =  'population_GIDs.dat'

# stem for spike detector file labels
spike_detector_label =  'spikes_'

# stem for voltmeter file labels
voltmeter_label =  'voltages_'

# stem for thalamic spike detector file labels
th_spike_detector_label =  'th_spikes_'

# file name for standard output
std_out =  'output.txt'

# file name for error output
error_out =  'errors.txt'



