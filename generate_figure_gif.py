#!/usr/bin/python

import os
import seaborn as sns
import pandas as pd
import string

#### general parameters

num_of_variables = 2 # number of variables in data
num_of_clusters = np.random.randint(1, 4) # number of clusters in data
data_points_per_variable = 100 # number of data points per cluster
states_in_movie = 10 # the number of different randomly generated positions for the clusters
steps_between_states = 15 # the resolution of steps between each position
palette = sns.diverging_palette(255, 133, l=60, n=num_of_clusters, center="dark") # the color palette used
names = ['Stars','Species','Aliens','Weapons','Eyes','Tentacles','Nebulas','Energy','Allies','Enemies','Elder Gods','Spaceships','Fleet size']

### randomly choosing names for variables
var_names = np.random.choice(names, num_of_variables, replace=False)
for name in var_names:
  names.remove(name)

### randomly choosing names for clusters
cluster_names = np.random.choice(names, num_of_clusters, replace=False)
for name in cluster_names:
  names.remove(name)


### This function generates a pandas DataFrame with num_of_variables + 1 columns (one for each variable, and another for
### the cluster name value).
def generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names):
  data = np.zeros(shape=(num_of_variables, data_points_per_variable * num_of_clusters))
  ### create several clusters
  for cluster in range(num_of_clusters):
    means = np.random.rand(num_of_variables) # means of cluster for each variable
    stds = np.random.rand(num_of_variables) # std of cluster for each variable
    ### create covariance matrix between variables
    cov = np.random.rand(num_of_variables, num_of_variables) 
    for row in range(cov.shape[0]):
      for col in range(cov.shape[1]):
        cov[row, col] = cov[col, row]
    ### create correlated new data
    new_data = np.random.multivariate_normal(means, cov, data_points_per_variable).T
    ### shift cluster across the axes
    for var in range(num_of_variables):
      new_data[var, :] += np.random.randint(-num_of_clusters, num_of_clusters)
    ### add new data to data set
    data[:, (data_points_per_variable * cluster) : (data_points_per_variable * (cluster + 1))] = new_data
  data += np.abs(np.min(data))
  columns = var_names
  cluster_column = []
  for cluster in range(num_of_clusters):
    cluster_column += [cluster_names[cluster]] * data_points_per_variable
  data = pd.DataFrame(data.T, columns= columns)
  data['cluster'] = cluster_column
  return data

### This function creates a new figure using seaborn
def create_frame(frame_ind, data, palette):
  print 'plotting frame {}'.format(frame_ind)
  fig = plt.figure(figsize=(10,10))
  frame = sns.PairGrid(data = data_between_steps[step], hue='cluster', palette=palette); 
  frame = frame.map_upper(plt.scatter)
  frame = frame.map_diag(sns.kdeplot, legend=False, shade=True)
  frame = frame.map_lower(sns.kdeplot, cmap='hot_r')
  frame.set(yticks=[])
  frame.set(xticks=[])
  fig.set_size_inches(5,5)
  plt.savefig('temp/frame_{}.jpg'.format(str(frame_ind).zfill(4)), transperant=False, format='jpg',bbox_inches='tight', dpi=200)
  plt.close('all')


### This generates the first position of the clusters
original_data = generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names)
first_data = original_data.copy()

### This loop creates a new position for each state, and creates new data for the position of the clusters
### transitioning between the previous state and the new one (with a step resolution of steps_between_states)
frame_ind = 0
for state in range(states_in_movie):
  # First we set the position at the end of the state, to which the clusters with transition
  last_data = generate_data(num_of_variables, num_of_clusters, data_points_per_variable, var_names, cluster_names)
  # We will fill this list with new data for each step, gradually coming closer to the new cluster
  data_between_steps = []
  data_between_steps.append(first_data)
  for step in range(1, steps_between_states):
    new_data = data_between_steps[step - 1].copy()
    new_data[var_names] += (last_data[var_names] - first_data[var_names]) / steps_between_states
    data_between_steps.append(new_data)

  # For each step between the last state and the new, we generate a new frame
  for step in range(0, steps_between_states - 1):
    create_frame(frame_ind, data, palette)
    frame_ind += 1
  first_data = data_between_steps[-1]

### finally, we will return to the original state, creating a loop
data_between_steps = []
last_data = original_data.copy()

data_between_steps.append(first_data)
for step in range(1, steps_between_states):
  new_data = data_between_steps[step - 1].copy()
  new_data[var_names] += (last_data[var_names] - first_data[var_names]) / steps_between_states
  data_between_steps.append(new_data)

for step in range(0, steps_between_states - 1):
  create_frame(frame_ind, data, palette)
  frame_ind += 1

### If we want, we can add glitches to the figures
num_of_glitches = frame_ind / 10
for glitch in range(num_of_glitches):
  glitch_ind = np.random.randint(0, frame_ind)
  os.system('jpglitch temp/frame_{}.jpg --jpg'.format(str(glitch_ind).zfill(4), str(glitch_ind).zfill(4)))

os.system('convert temp/frame_*.jpg -set delay 10 -loop 0  -resize 300x300  animation.gif')
os.system('convert temp/frame_*.jpg -set delay 10 -loop 0   big_animation.gif')
print 'combined gif'

