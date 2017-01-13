import glob
import os
import sys
import numpy as np
import multiprocessing
import click
from Cycle import Cycle
from plot_with_matplotlib import plot

# suppress unnecessary warnings
import warnings

warnings.filterwarnings("ignore")


# for multiprocessing purpose, but doesn't run reliable
# data_queue = multiprocessing.Queue()


def make_lists_and_plot(xarr, yarr, name, plot_energies: bool, savetxt: bool,
                        dest: str):
    c = Cycle(xarr, yarr)
    if not c.analyse_cycle():
        return
    number_of_cycles = c.number_of_cycles
    elastic = []
    plastic = []
    friction = []
    plastic_total = []
    x_grid = c.x_grid
    for i in range(number_of_cycles):
        e, p, f, p_t = c.evaluate_cycle(i)
        if p > 20:
            print('Fehler in Berechnung der plastic energy in {}'.format(
                  name), file=sys.stderr)

        elastic.append(e)
        plastic.append(p)
        friction.append(f)
        plastic_total.append(p_t)

    # save data as txt-file
    if savetxt:
        for directory in ['elastic', 'plastic', 'friction', 'plastic_total']:
            if not os.path.exists(os.path.join(dest, directory, '')):
                os.makedirs(os.path.join(dest, directory))
            np.savetxt(os.path.join(dest, directory, '') + name +
                   '.txt', np.transpose([x_grid, eval(directory)]), '%.2f')
    # plot energies as pdf
    if plot_energies:
        plot(x_grid, elastic, plastic, friction, plastic_total,
             xarr, yarr, name, dest)


def set_file(source: str, filename: str, dest: str, plot_energies: bool,
             savetxt: bool):
    jobs = []

    # just one single file instead of all files in directory
    if filename:
        filename = glob.glob(os.path.join(source, filename))
    else:
        filename = glob.glob(os.path.join(source, '*.TXT'))
    for file in filename:
        with open(file, 'rb') as d:
            try:
                arr = np.loadtxt(d,
                                 comments='#',
                                 skiprows=1,
                                 usecols=(2, 3),
                                 )
                xarr = arr[:, 0]
                yarr = arr[:, 1]
                print(d.name.split('/')[-1])
                for i in range(len(xarr) - 1):
                    if abs(xarr[i] - xarr[i + 1]) < 1e-6:
                        # debugging purpose
                        # leads to way too high values in integration and
                        # must be avoided by deleting one of these lines
                        print('Werte liegen weniger als 1e-6 beieinander:', i,
                              file=sys.stderr)
                jobs.append((xarr, yarr, d.name.split('/')[-1],
                             plot_energies, savetxt, dest))
            # end of file
            except StopIteration:
                pass

    return jobs


@click.command()
@click.option('--source', default='./',
              help='Pfad des Dateiordners der Rohmessungen')
@click.option('--filename', default='',
              help='Dateiname, falls nur eine bestimmte Datei und nicht alle '
                   'ausgewertet werden sollen')
@click.option('--dest', default='./plots/',
              help='Pfad des Dateiordners in den die Plots und txts '
                   'geschrieben werden. Wird erstellt falls notwendig. '
                   'Standardmäßig ./plots/')
@click.option('--plot/--no-plot', default=True,
              help='Angabe, ob Plots erstellt werden sollen. Standardmäßig '
                   'True')
@click.option('--savetxt/--no-savetxt', default=True,
              help='Angabe, ob Textdateien der ausgewerteten Energiebeiträge '
                   'erstellt werden sollen. Standardmäßig True')
def main(source='./', filename='', dest='./plots/', plot=True, savetxt=True):
    """
    Tool zur Berechnung der Energiebeiträge eines zyklischen Push-Outs.

    Standardmäßig werden die .TXTs ausgewertet, die im selben Ordner wie
    die main.py liegen.

    Benötigte Libraries: numpy, scipy, matplotlib.pyplot, click und
    optional prettyplotlib
    """
    # read file names in source-path
    jobs = set_file(source, filename, dest, plot, savetxt)
    for t in jobs:
        make_lists_and_plot(*t)

    # ### uncomment these instead of the two above
    # if you want multiprocessing features - may not work

    # pool = multiprocessing.Pool(4)
    # results = [pool.apply_async(make_lists_and_plot, t) for t in jobs]
    # for result in results:
    #     result.get()


if __name__ == '__main__':
    main()
