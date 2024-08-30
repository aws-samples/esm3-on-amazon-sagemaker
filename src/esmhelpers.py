import biotite.sequence as seq
import biotite.sequence.align as align
import biotite.sequence.graphics as graphics
import matplotlib.pyplot as plt
from PIL import ImageColor
import py3Dmol


def format_seq(
    seq: str,
    width: int = 80,
    block_size: int = 10,
    gap: str = " ",
    line_numbers: bool = True,
    color_scheme_name: str = "flower",
) -> str:
    """
    Format a biological sequence into pretty blocks with (optional) line numbers.
    """

    output = ""
    output += f"{1:<4}" + " " if line_numbers else ""
    if type(seq) != str:
        seq = str(seq)

    for i, res in enumerate(seq, start=1):
        output += color_amino_acid(res, color_scheme_name)
        if i % width == 0:
            output += "\n"
            output += f"{i+1:<4}" + " " if line_numbers else ""
        elif i % block_size == 0:
            output += gap

    return output


def quick_pdb_plot(
    pdb_str: str, width: int = 800, height: int = 600, color: str = "#007FAA"
) -> None:
    """
    Plot a PDB structure using py3dmol
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_str, "pdb")
    view.setStyle({"cartoon": {"color": color}})
    view.zoomTo()
    view.show()
    return None


def quick_aligment_plot(seq_1: str, seq_2: str) -> None:
    seq1 = seq.ProteinSequence(seq_1)
    seq2 = seq.ProteinSequence(seq_2)
    # Get BLOSUM62 matrix
    matrix = align.SubstitutionMatrix.std_protein_matrix()
    # Perform pairwise sequence alignment with affine gap penalty
    # Terminal gaps are not penalized
    alignments = align.align_optimal(
        seq1, seq2, matrix, gap_penalty=(-10, -1), terminal_penalty=False
    )

    print("Alignment Score: ", alignments[0].score)
    print("Sequence identity:", align.get_sequence_identity(alignments[0]))

    # Draw first and only alignment
    # The color intensity indicates the similiarity
    fig = plt.figure()
    ax = fig.add_subplot(111)
    graphics.plot_alignment_similarity_based(
        ax,
        alignments[0],
        matrix=matrix,
        labels=["Reference", "Prediction"],
        show_numbers=False,
        show_line_position=True,
        color=(0.0, 127 / 255, 170 / 255),
    )
    fig.tight_layout()
    plt.show()
    return None


def color_text(text: str, hex: str):
    """
    Color text
    """
    rgb = ImageColor.getrgb(hex)
    color_code = f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    return color_code + text + "\033[0m"


def color_amino_acid(res, color_scheme_name="flower"):
    colors = graphics.get_color_scheme(color_scheme_name, seq.ProteinSequence.alphabet)
    color_map = dict(zip(seq.ProteinSequence.alphabet, colors))
    color_map.update(
        {
            "B": "#FFFFFF",
            "U": "#FFFFFF",
            "Z": "#FFFFFF",
            "O": "#FFFFFF",
            ".": "#FFFFFF",
            "-": "#FFFFFF",
            "|": "#FFFFFF",
            "_": "#000000",
            "✔": "#FF9900",
        }
    )
    return color_text(res, color_map[res])


def color_protein_sequence(protein_sequence: str, color_scheme_name="flower"):
    return "".join(
        [color_amino_acid(res, color_scheme_name) for res in protein_sequence]
    )


def parse_annotations_by_label(annotations) -> dict:
    """
    Generate a dictionary of annotation labels and their corresponding sequence positions
    """

    parsed_annotations = {}

    for annotation in annotations:
        annotation_idx = list(range(annotation.start, annotation.end + 1))
        if annotation.label in parsed_annotations:
            parsed_annotations[annotation.label].extend(annotation_idx)
            parsed_annotations[annotation.label] = list(
                set(parsed_annotations[annotation.label])
            )
        else:
            parsed_annotations[annotation.label] = annotation_idx
    return parsed_annotations


def parse_annotations_by_index(annotations, sequence_length) -> dict:
    """
    Generate a list of sequence positions and their corresponding annotation labels
    """

    parsed_annotations = []
    annotations_by_label = parse_annotations_by_label(annotations)

    for idx in range(1, sequence_length):
        idx_annotations = []
        for k, v in annotations_by_label.items():
            if idx in v:
                idx_annotations.append(k)
        parsed_annotations.append(idx_annotations)

    return parsed_annotations

def format_annotations(parsed_annotations, length, filter = None):
    output = {}
    parsed_annotations = {k: parsed_annotations[k] for k in filter} if filter else parsed_annotations
    for k, v in parsed_annotations.items():
        tmp = ["_"] * length
        for i in v:
            tmp[i - 1] = "✔"
        output[k] = "".join(tmp)
    return output