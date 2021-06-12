#code from: https://github.com/alexandre01/deepsvg/issues/5#issuecomment-829964251
from concurrent import futures
import os
from argparse import ArgumentParser
import logging
from tqdm import tqdm
import glob
import pickle

import sys
sys.path.append('..')
from deepsvg.svglib.svg import SVG


def convert_svg(svg_file, output_folder):
    filename = os.path.splitext(os.path.basename(svg_file))[0]
    svg = SVG.load_svg(svg_file)
    tensor_data = svg.to_tensor()

    with open(os.path.join(output_folder, f"{filename}.pkl"), "wb") as f:
        dict_data = {
            "tensors": [[tensor_data]],
            "fillings": [0]
        }
        pickle.dump(dict_data, f, pickle.HIGHEST_PROTOCOL)


def main(args):
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        svg_files = glob.glob(os.path.join(args.input_folder, "*.svg"))

        with tqdm(total=len(svg_files)) as pbar:
            preprocess_requests = [executor.submit(convert_svg, svg_file, args.output_folder) for svg_file in svg_files]
            for _ in futures.as_completed(preprocess_requests):
                pbar.update(1)

    logging.info("SVG files' conversion to tensors complete.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument("--input_folder")
    parser.add_argument("--output_folder")
    parser.add_argument("--workers", default=4, type=int)

    args = parser.parse_args()

    if not os.path.exists(args.output_folder): os.makedirs(args.output_folder)

    main(args)