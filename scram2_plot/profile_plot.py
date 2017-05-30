import numpy
from pylab import *  # @UnusedWildImport
import matplotlib.pyplot as plt  # @Reimport


class DNA(object):
    """
    DNA class
    """
    dna_alphabet = set("AGCTN")

    def __init__(self, sequence):
        self.sequence = sequence.upper()

    def __len__(self):
        return len(self.sequence)

    def __getitem__(self, key):
        return self.sequence[key]

    def __hash__(self):
        return hash(self.sequence)

    def __repr__(self):
        return self.sequence

    def __eq__(self, other):
        return self.sequence == other.sequence


def multi_header_plot(nt_list, search_terms, in_files, cutoff, plot_y_lim, win, pub, save_plot):
    """
    21,22,24nt profile plot
    :param nt_list: 
    :param search_terms: header search terms list
    :param in_files: alignment files prefix
    :param cutoff: highest count of the most abundant alignment of 21,22,24 nt profiles
    :param plot_y_lim: set y limits on plot 
    :param win: smoothing window size
    :param pub: remove box and axis labels
    """
    select_win = False
    alignment_file_list = load_indv_files(in_files, nt_list)
    substring = " ".join(search_terms)
    all_keys = get_all_headers(alignment_file_list)
    for header in all_keys:
        if substring.lower() in header.lower():
            nt_pos = 0
            header_alignment_tuple = ()
            ref_len_tuple = ()
            for alignment_file in alignment_file_list:
                header_alignment_tuple, ref_len_tuple = get_selected_alignments(alignment_file, header,
                                                                                header_alignment_tuple,
                                                                                ref_len_tuple,nt_list[nt_pos])
                nt_pos+=1
            above_cutoff = False
            for alignment in header_alignment_tuple:
                if alignment[2] >= cutoff:
                    above_cutoff = True
            if above_cutoff:
                if header[0] == '"':
                    plot_name = save_file_name(in_files, header[1:-2])
                else:
                    plot_name = save_file_name(in_files, header)

                print("Plotting:\n")
                print(header)
                max_ref_len = max(ref_len_tuple)

                win, select_win = select_win_size(max_ref_len, select_win, win)
                graph_processed_list = process_for_plot(header_alignment_tuple, max_ref_len, nt_list)

                generate_plot_data(graph_processed_list, header, nt_list, plot_name, plot_y_lim, pub, save_plot, win)


def load_indv_files(in_files, nt_list):
    print("\nLoading scram2 alignment files:\n")
    try:
        alignment_file_list = []
        for nt in nt_list:
            file_name = in_files + "_" + nt + ".csv"
            print("{0} \n".format(file_name))
            in_file, _ = import_scram2_profile(file_name)
            alignment_file_list.append(in_file)
    except:
        print("\nProblem loading alignment files.  Possibly a missing file for the sRNA lengths provided\n")
        sys.exit()
    return alignment_file_list


def import_scram2_profile(in_file):
    """
    Import a SCRAM2 csv file to a dictionary
    :param in_file: path/to/profile string
    :return: alignments dictionary and snra length in the alignment
    """
    alignments = {}
    srna_len = 0
    with open(in_file, 'r') as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
            else:
                line = line.strip().rsplit(',', 7)
                srna_len = len(line[2])
                if line[0] not in alignments:
                    alignments[line[0]] = [(int(line[1]), DNA(line[2]), int(line[3]), line[4], float(line[5]),
                                            float(line[6]))]
                else:
                    alignments[line[0]].append(
                        (int(line[1]), DNA(line[2]), int(line[3]), line[4], float(line[5]), float(line[6])))
    return alignments, srna_len


def get_all_headers(alignment_file_list):
    print("Extracting headers:\n")
    all_keys = set()
    for nt in alignment_file_list:
        for header in nt.keys():
            all_keys.add(header)
    return all_keys


def get_selected_alignments(alignment_file, header, header_alignment_tuple, ref_len_tuple,nt):
    alignment, ref_len = extract_header_alignment(header, alignment_file,nt)
    header_alignment_tuple = header_alignment_tuple + (alignment,)
    ref_len_tuple = ref_len_tuple + (ref_len,)
    return header_alignment_tuple, ref_len_tuple


def extract_header_alignment(header, alignments,nt):
    """
    With a provided complete header, extract the alignment and process to correct format for fill in zeros
    :param header: reference sequence header string 
    :param alignments: alignments dictionary
    :return: sorted_fwd_alignment, sorted_rvs_alignment, aln_count list
    """
    sorted_fwd_alignment = []
    sorted_rvs_alignment = []
    aln_count = 0.0
    ref_len = 0

    if header in alignments:
        extracted_alignments = alignments[header]
        for alignment in extracted_alignments:
            ref_len = alignment[0]
            if alignment[3] =="+":
                sorted_fwd_alignment.append((alignment[2], alignment[4], alignment[5]))
            elif alignment[3] =="-":
                sorted_rvs_alignment.append((alignment[2], -alignment[4], alignment[5]))
            aln_count += alignment[4]
    return [sorted_fwd_alignment, sorted_rvs_alignment, aln_count], ref_len


def select_win_size(max_ref_len, select_win, win):
    if win == 0 or select_win:
        win = int(max_ref_len / 30)
        select_win = True
    if win % 2 != 0 or win == 0: win += 1
    return win, select_win

def process_for_plot(header_alignment_tuple, max_ref_len, nt_list):
    graph_processed_list = []
    nt_pos = 0
    for alignment in header_alignment_tuple:
        graph_processed_list.append(fill_in_zeros_se(alignment, max_ref_len, int(nt_list[nt_pos])))
        nt_pos += 1
    return graph_processed_list

def fill_in_zeros_se(fwd_rvs_align_list, ref_len,nt):
    """
    Generate alignment counts for every nucleotide in the reference
    :param fwd_rvs_align_list:  list of sorted forwards and reverse alignments
    :param ref_len: number of nucleotides in the reference sequence (int)
    :return: reference_x_axis ([0,0,...] (list(int)) - length of refseq seq,
             fwd_alignment_y_axis [2,4,5.2,6,....] (list(float)) - sense strand alignment count (positive),
             fwd_rvs_align_list [-3,-4,-5.6,...] (list(float)) - antisense strand alignment count (negative)
    """
    sorted_fwd_alignment = fwd_rvs_align_list[0]
    sorted_rvs_alignment = fwd_rvs_align_list[1]

    fwd_alignment_y_axis_upper = [0] * ref_len
    fwd_alignment_y_axis_lower = [0] * ref_len
    revs_alignment_y_axis_upper = [0] * ref_len
    revs_alignment_y_axis_lower = [0] * ref_len

    reference_x_axis = list(range(0, ref_len))
    try:
        for i in sorted_fwd_alignment:
            for j in range(nt):
                fwd_alignment_y_axis_upper[i[0]+j-1] += (i[1] + i[2])
                fwd_alignment_y_axis_lower[i[0]+j-1] += (i[1] - i[2])
        for i in sorted_rvs_alignment:
            for j in range(nt):
                revs_alignment_y_axis_upper[i[0]+j-1] += (i[1] + i[2])
                revs_alignment_y_axis_lower[i[0]+j-1] += (i[1] - i[2])
    except:
        pass

    return reference_x_axis, fwd_alignment_y_axis_upper, fwd_alignment_y_axis_lower, \
           revs_alignment_y_axis_upper, revs_alignment_y_axis_lower

def generate_plot_data(graph_processed_list, header, nt_list, plot_name, plot_y_lim, pub, save_plot, win):
    x_ref = graph_processed_list[0][0]
    smoothed_for_plot_tuple = ()
    for graph_processed in graph_processed_list:
        y_fwd_smoothed_upper, y_fwd_smoothed_lower, y_rvs_smoothed_upper, \
        y_rvs_smoothed_lower = _smoothed_for_plot_se(graph_processed, win)
        smoothed_for_plot_tuple = smoothed_for_plot_tuple + ((y_fwd_smoothed_upper, y_fwd_smoothed_lower,
                                                              y_rvs_smoothed_upper, y_rvs_smoothed_lower),)
    profile_plot(nt_list, x_ref, smoothed_for_plot_tuple, header, plot_y_lim, pub, save_plot, plot_name)



def _smoothed_for_plot_se(graph_processed, smooth_win_size):
    """
    Return fwd and rvs smoothed profiles
    :param graph_processed: list of fwd and rvs upper and lower se bounds
    :param smooth_win_size: smoothing window size
    :return: list of smoothed fwd and rvs upper and lower se bound
    """
    y_fwd_smoothed_upper = smooth(numpy.array(graph_processed[1]),
                                  smooth_win_size, window='blackman')
    y_fwd_smoothed_lower = smooth(numpy.array(graph_processed[2]),
                                  smooth_win_size, window='blackman')
    y_rvs_smoothed_upper = smooth(numpy.array(graph_processed[3]),
                                  smooth_win_size, window='blackman')
    y_rvs_smoothed_lower = smooth(numpy.array(graph_processed[4]),
                                  smooth_win_size, window='blackman')
    return y_fwd_smoothed_upper, y_fwd_smoothed_lower, y_rvs_smoothed_upper, y_rvs_smoothed_lower



def smooth(x, window_len, window='hamming'):
    """
    Smoothing function from scipy cookbook
    :param x:
    :param window_len:
    :param window:
    :return:
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 6:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = numpy.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
    if window == 'flat':  # moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = numpy.convolve(w / w.sum(), s, mode='valid')
    return y[int(window_len / 2 - 1):-int(window_len / 2)]


def profile_plot(nt_list, x_ref, smoothed_for_plot_tuple, header, plot_y_lim, pub, save_plot, plot_name):
    fig = plt.figure(figsize=(10, 5))
    nt_pos = 0
    for smoothed_for_plot in smoothed_for_plot_tuple:
        plt.plot(x_ref, smoothed_for_plot[0], color=_nt_colour(int(nt_list[nt_pos])), label='{0} nt'.format(nt_list[
                                                                                                                nt_pos]),
                 lw=1, alpha=0.2)
        plt.plot(x_ref, smoothed_for_plot[1], color=_nt_colour(int(nt_list[nt_pos])), lw=1, alpha=0.2)
        plt.fill_between(x_ref, smoothed_for_plot[0], smoothed_for_plot[1], color=_nt_colour(int(nt_list[nt_pos])),
                         alpha=0.5)
        plt.plot(x_ref, smoothed_for_plot[2], color=_nt_colour(int(nt_list[nt_pos])), lw=1, alpha=0.2)
        plt.plot(x_ref, smoothed_for_plot[3], color=_nt_colour(int(nt_list[nt_pos])), lw=1, alpha=0.2)
        plt.fill_between(x_ref, smoothed_for_plot[2], smoothed_for_plot[3], color=_nt_colour(int(nt_list[nt_pos])),
                         alpha=0.5)
        nt_pos += 1
    axhline(y=0)
    if pub:
        _pub_plot()
    else:
        xlabel(header)
        ylabel('Reads per million reads')
        plt.legend(loc='best', fancybox=True, framealpha=0.5)
    if plot_y_lim != 0:
        ylim(-plot_y_lim, plot_y_lim)
    if save_plot:
        plt.savefig('{0}.png'.format(plot_name), dpi=300)
    plt.show()


def _pub_plot():
    """
    Remove axis, labels, legend from plot
    """
    plt.tick_params(
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='on',  # ticks along the bottom edge are off
        top='on',
        right='on',
        left='on',  # ticks along the top edge are off
        labelbottom='off',
        labelleft='off',
        labelright='off',
        labelsize=15)  # labels along the bottom edge are off
    _clear_frame()


def save_file_name(in_files, header):
    out_file_name = in_files + "_"
    for i in header:
        if len(out_file_name) > 100:
            break
        else:
            if i == " " or not i.isalnum():
                out_file_name += "_"
            else:
                out_file_name += i
    return out_file_name


def _clear_frame(ax=None):
    """
    Removes frame for publishing plots
    """
    if ax is None:
        ax = plt.gca()
    ax.xaxis.set_visible(True)
    ax.yaxis.set_visible(True)
    for spine in ax.spines.values():
        spine.set_visible(False)


def _nt_colour(nt):
    """
    Set default colours for 21, 22 and 24 nt sRNAs
    :param nt: aligned read length (int)
    :return: colour code (str)
    """
    hex_dict = {18: '#669999', 19: '#33cccc', 20: '#33cccc', 21: '#00CC00',
                22: '#FF3399', 23: '#d8d408', 24: '#3333FF', 25: '#cccc00',
                26: '#660033', 27: '#996600', 28: '#336699', 29: '#ff6600',
                30: '#ff99ff', 31: '#669900', 32: '#993333'}

    if nt not in hex_dict:
        return "black"
    else:
        return hex_dict[nt]


