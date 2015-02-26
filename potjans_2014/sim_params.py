#!usrbinenv = python


# Contains:
# - simulation parameters
# - recording parameters

###################################################
###       Simulation parameters   ###
###################################################

run_mode = (test)     # (test) for writing files to
                      # directory containing microcircuit.sli
                      # (production) for writing files
                      # to a chosen absolute path.

t_sim = 1000.0      # simulated time (ms)
dt = 0.1            # simulation step (ms). ault is 0.1 ms.
allgather = true    # communication protocol

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

memory = (500mb)    # total memory
                    # use for instance 4gb for a full-scale simulation

