import matplotlib.pyplot as plt

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","Uniform rounds","Prop. energy","Prop. time"]
times_soc_8_to_10 = [4222,174]
times_soc_8_to_10_err = [88, 3]
times_soc_10_to_40 = [3470, 164]
times_soc_10_to_40_err = [52, 3.6]

x = range(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))

ax.bar(x, )