#!/usr/bin/env python3

import plot_code as pc



from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.65
__date__ = '2016-02-08'
__updated__ = '2016-03-08'


def main(argv=None):
    """Command line options."""


    try:
        # Setup argument parser
        parser = ArgumentParser()

        subparsers = parser.add_subparsers(help="Select profile or scatter plot", dest="command")
        parser_profile = subparsers.add_parser("profile",
                                               help="Generates alignment profile/s for 1 or more reference sequences")

        #profile plot
        parser_profile.add_argument('-a', '--alignment',
                            type=str, help="sRNA alignment file/s generated by SCRAM2 profile.  For a single sRNA "
                                           "length, use the full filename.  A single alignment must end in "
                                           "_integer.csv.  "
                                           "For a combined 21,22, 24nt profile, use a single "
                                           "filename prefix (i.e. exclude _21.csv, _22.csv, "
                                           "_24.csv)")
        parser_profile.add_argument('-cutoff','--cutoff', type = int, default=1,
                            help = "Min. alignment RPMR from the most abundant profile (if multi) to generate plot")

        parser_profile.add_argument('-s','--search', type=str, help="Full header or substring of header", nargs='*')

        parser_profile.add_argument('-nt','--nt', type=str,help="Comma-seperated list of sRNA lengths to plot.  "
                                                                "SCRAM2 alignment files must be available for each "
                                                                "sRNA "
                                                                "length")


        parser_profile.add_argument('-ylim', '--ylim',
                            type=float, help='+/- y axis limit',
                            default=0)
        parser_profile.add_argument('-win','--win', type = int, help = 'Smoothing window size (default=auto)',
                                    default=0)

        parser_profile.add_argument('-pub', '--publish', action='store_true',
                            default=False,
                            help='Remove all labels from profiles for editing for publication')
        parser_profile.add_argument('-png', '--png', action='store_true',
                            default=False,
                            help='Export plot/s as 300 dpi .png file/s')


        #Compare plot
        parser_cdp = subparsers.add_parser("compare", help = "Generates a scatter plot for a SCRAM2 cpd alignment")
        parser_cdp.add_argument('-plot_type', '--plot_type', default="log_error",
                                    help='Bokeh plot type to display (log, log_error, linear or all)')
        parser_cdp.add_argument('-a','--alignment', help="SCRAM2 cdp alignment file")
        parser_cdp.add_argument('-xlab', '--x_label', default=["Treatment 1"],
                                help='x label - corresponds to -s1 treatment in SCRAM2 arguments', nargs='*')
        parser_cdp.add_argument('-ylab', '--y_label', default=["Treatment 2"],
                                help='y label - corresponds to -s2 treatment in SCRAM2 arguments', nargs='*')
        parser_cdp.add_argument('-browser', '--browser', default=False, action='store_true',
                                help='If not using Jupyter Notebook, output plot to browser')

        # Process arguments
        args = parser.parse_args()

        if args.command == "profile":
            # if args.subcommand == "multi":
            search_term = args.search
            a = args.alignment
            cutoff = args.cutoff
            ylim = args.ylim
            pub = args.publish
            win = args.win
            nt_list=args.nt.split(',')
            save_plot=args.png

            # if a[-4:]==".csv" and a.split("_")[-1].split(".")[0].isdigit():
            #     print("Attempting a single sRNA length plot\n")
            #     pc.single_header_plot(search_term, a, cutoff, ylim, win, pub)
            # else:
            #     print("Attempting a 21, 22, 24nt sRNA length plot\n")
            pc.multi_header_plot(nt_list,search_term, a, cutoff, ylim, win, pub, save_plot)

        if args.command == "compare":
            alignment_file = args.alignment
            xlab= " ".join(args.x_label)
            ylab= " ".join(args.y_label)
            plot_type=args.plot_type
            browser=args.browser
            pc.cdp_plot_bokeh(alignment_file, xlab, ylab, plot_type, browser)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0


if __name__ == "__main__":

    main()