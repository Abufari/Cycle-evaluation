import matplotlib.pyplot as plt
try:
    import prettyplotlib as ppl
except ImportError:
    # no prettyplot installed
    ppl = plt
import os

counter = 0


def plot(x_steps, elastic, plastic, friction, plastic_total, x, y, name, dest):
    global counter
    counter += 1
    fig = plt.figure(num=counter, figsize=(12, 8))

    cols = 2

    # for coloring
    figure, axes = plt.subplots()
    axes.color_cycle = axes._get_lines.prop_cycler
    color = 'royalblue'

    plt.subplot(3, cols, 1)

    ppl.plot(x_steps, elastic, marker='o', markersize=4, color=color, )
    plt.grid()
    plt.title('Elastic')

    plt.subplot(3, cols, 2)
    ppl.plot(x_steps, plastic, marker='o', markersize=4, color=color, )
    plt.grid()
    plt.title('Plastic')

    plt.subplot(3, cols, 3)
    ppl.plot(x_steps, friction, marker='o', markersize=4,
             color=color, )
    plt.grid()
    plt.title('Friction')

    plt.subplot(3, cols, 4)
    ppl.plot(x_steps, plastic_total, marker='o', markersize=4,
             color=color, )
    plt.grid()
    plt.title('Plastic total')

    plt.subplot(3, 1, 3)
    ppl.plot(x, y, linewidth=0.75, color=color, )
    plt.grid()

    fig.set_tight_layout(True)

    # Save graph
    if not os.path.exists(os.path.join(dest, '')):
        os.makedirs(os.path.join(dest, ''))
    plt.savefig(os.path.join(dest, '') + '{}.pdf'.format(name))
    plt.close()
