"""
Lyra Static Program Analyzer
============================
"""

import argparse
from lyra.engine.liveness.liveness_analysis import StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis
from lyra.engine.alias.alias_analysis import AliasAnalysis


def main():
    """Static analyzer entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'python_file',
        help='Python file to analyze')
    parser.add_argument(
        '--analysis',
        help='analysis to be used (interval, liveness, or usage)',
        default='alias')  #TODO change back to usage
    args = parser.parse_args()

    if args.analysis == 'intervals':
        ForwardIntervalAnalysis().main(args.python_file)
    if args.analysis == 'liveness':
        StrongLivenessAnalysis().main(args.python_file)
    if args.analysis == 'usage':
        SimpleUsageAnalysis().main(args.python_file)
    if args.analysis == 'alias':
        AliasAnalysis().main(args.python_file)


if __name__ == '__main__':
    main()
