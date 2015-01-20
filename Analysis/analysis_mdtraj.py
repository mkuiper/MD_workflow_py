#!/usr/bin/env python
'''Analysis mdtraj test'''

import os
import mdtraj as md
import numpy as np
import matplotlib
import scipy.cluster.hierarchy
from pylab import *
from math import pi
from sklearn.decomposition import PCA
from itertools import combinations
import mdtraj.testing
import itertools

#loading and printing trajectories with coordinate files
#--------------------------------------------------------
traj = md.load('traj.dcd', top='coor.psf')
print traj

#printng different info about the protein such as # of atoms, residues etc
#--------------------------------------------------------------------------
print 'How many atoms? %s' % traj.n_atoms
print 'How many residues? %s' % traj.n_residues

#slicing the trajectory file into samller peices, saving it back to the disk as an hd5 format
#----------------------------------------------------------------------------------------------
traj[0:2].save_dcd('first-two-frames.dcd')
traj[::].save('traj.h5')

#we can load hd5 files and use them for analysis
#------------------------------------------------
traj1 = md.load(tarj.hd5)

#selecting certain part of the protien; in this case trajectory with only alpha carbons present
#----------------------------------------------------------------------------------------------
atoms_to_keep = [a.index for a in traj.topology.atoms if a.name == 'CA']
traj.atom_slice(atoms_to_keep)
traj.save('CA-only.h5')

#Root-mean-square deviation (RMSD), comparing target with the reference protein 
#-------------------------------------------------------------------------------
RMSD = 	md.rmsd(traj,ref_prot[0:10]) #10 frames to be compared

#Calculating the average distance between two atoms
#---------------------------------------------------
traj = md.load('traj.h5')
av_dis = np.mean(np.sqrt(np.sum((traj.xyz[:, 'X', :] - traj.xyz[:, 'Y', :])**2, axis=1)))#Change X and Y to atom of interest they should be int
print "Average distance betwen atom Y and Y: %f nm" % np.mean(av_dis)

#Computing all pairwise rmsds between conformations
#---------------------------------------------------
distances = np.empty((traj.n_frames, traj.n_frames))
for i in range(traj.n_frames):
    distances[i] = md.rmsd(traj, traj, i)
print 'Max pairwise rmsd: %f nm' % np.max(distances) 

#Plotting the cluster 
#--------------------- 
linkage = scipy.cluster.hierarchy.ward(distances)
figure()
title('RMSD Ward hierarchical clustering')
graph = scipy.cluster.hierarchy.dendrogram(linkage, no_labels=True, count_sort='descendent')
savefig('cluster.gif')
show ()

#Plotting Ramachandra plot
#--------------------------
atoms, bonds = traj1.topology.to_dataframe()
psi_indices, phi_indices = [6, 8, 14, 16], [4, 6, 8, 14]#Check the numbers here, taken from the tutorial
                                                        #directly we need to look for some common way of 
                                                        #calculation for all kinds of protein if this for 
                                                        #a specific case
angles = md.geometry.compute_dihedrals(traj1, [phi_indices, psi_indices])
figure()
title('Test Dihedral Map For Ramachandra Plot')
plot=scatter(angles[:, 0], angles[:, 1], marker='x', c=traj1.time)
cbar = colorbar()
cbar.set_label('Time [ps]')
xlabel(r'$\Phi$ Angle [radians]')
xlim(-pi, pi)
ylabel(r'$\Psi$ Angle [radians]')
ylim(-pi, pi)
savefig('ramchplot.gif')
show()

#Principal component analysis and plotting the data, should check whether the componetes and frames are good any protein simulation
#-----------------------------------------------------------------------------------------------------------------------------------
pca = PCA(n_components=2)
traj.superpose(traj1, 0)

reduced_cartesian = pca.fit_transform(traj.xyz.reshape(traj.n_frames, traj.n_atoms * 3))
print reduced_cartesian.shape

#------Plotting the data -------
figure()
scatter(reduced_cartesian[:, 0], reduced_cartesian[:,1], marker='x', c=traj.time)
xlabel('PC1')
ylabel('PC2')
title('(Principal componener analysis) Cartesian coordinate PCA')
cbar = colorbar()
cbar.set_label('Time [ps]')
savefig('pca1.gif')
show()
