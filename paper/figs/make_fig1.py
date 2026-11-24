"""Figure 1. (a) Schematic (stage-2 instructions, section 3): two rows from the same encoding h0 of a sentence containing "March"; latents
drawn as rows of token boxes with the slot highlighted and labelled with the slot readout. Top, instruction write (C1): the slot readout
stays "Mar", an added instruction arrow sits beside the latent; h1 decodes to "April" (correct), h2 is wrong. Bottom, state write (RRR-16 /
C3): the slot reads Mar -> Apr -> May and both decodes are correct. Intermediate decodes in dashed boxes, "decoded here only to score".
(b) BART-base, month, one-way plus R_k of v1 C1 (CE), the closed-form RRR-16 and v4 C3-U4 on v5 confirm5 (v5 L cells)."""
from matplotlib.patches import FancyArrowPatch, Rectangle
from _style import *
V5 = 'experiments/composability_mechanisms_v4/results/chains.csv'
INK, SLOT, ACC = '#333333', '#1f4e79', '#c0504d'


def latent(ax, x, y, label, slot_txt, n=6, slot=3, w=.15, h=.17):
    for i in range(n):
        s = i == slot
        ax.add_patch(Rectangle((x + i * w, y), w * .9, h, fc=SLOT if s else 'white', ec=INK, lw=.6))
        if s: ax.text(x + i * w + w * .45, y + h / 2, slot_txt, ha='center', va='center', fontsize=4.8, color='white', fontweight='bold')
    ax.text(x + n * w / 2, y + h + .04, label, ha='center', va='bottom', fontsize=7)
    return x, x + n * w * .97, y, y + h


def arrow(ax, x0, y0, x1, y1, **kw):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=7, lw=.8, color=kw.pop('color', INK), **kw))


def row(ax, y, title, slots, decodes, instruction):
    ax.text(-.05, y + .42, title, ha='left', va='center', fontsize=7, fontweight='bold')
    ax.text(1.45, y + .42, '(rank-16 affine map)', ha='left', va='center', fontsize=5.5, style='italic', color=INK)
    xs = [.0, 1.25, 2.5]; boxes = []
    for i, (x, s) in enumerate(zip(xs, slots)): boxes.append(latent(ax, x, y, f'$h_{i}$', s))
    for i in range(2):
        arrow(ax, boxes[i][1] + .03, y + .08, boxes[i + 1][0] - .03, y + .08); ax.text((boxes[i][1] + boxes[i + 1][0]) / 2, y + .12, 'edit', ha='center', fontsize=5.5)
        if instruction:
            bx = boxes[i + 1]; arrow(ax, bx[1] + .02, bx[3] + .06, bx[1] - .12, bx[3] + .01, color=ACC, linestyle='-')
            ax.text(bx[1] + .03, bx[3] + .07, '+instr.', fontsize=5, color=ACC, va='bottom')
    for i, (txt, ok) in enumerate(decodes):
        bx = boxes[i + 1]; cx = (bx[0] + bx[1]) / 2
        ax.add_patch(Rectangle((cx - .3, y - .33), .6, .15, fc='white', ec=INK, lw=.6, ls='--'))
        ax.text(cx, y - .255, f"{txt} {'✓' if ok else '✗'}", ha='center', va='center', fontsize=6, color=INK if ok else ACC)
        arrow(ax, cx, y - .02, cx, y - .17, linestyle=':')


def main():
    require_slurm(); ch = chains(V5); fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1.55, 1]))
    ax = axs[0]; ax.set_xlim(-.1, 3.7); ax.set_ylim(-.95, 1.0); ax.axis('off')
    row(ax, .55, 'instruction write (C1)', ['Mar', 'Mar', 'Mar'], [('April', True), ('', False)], True)
    row(ax, -.45, 'state write (RRR-16 / C3)', ['Mar', 'Apr', 'May'], [('April', True), ('May', True)], False)
    ax.text(3.68, -.92, 'dashed: decoded here only to score', ha='right', fontsize=5.5, style='italic')
    ax.set_title('(a) same edit rank, different writes', fontsize=8)
    ax = axs[1]
    for stem, lab, c, ls in (('C1v1', 'C1 (CE, one-step)', '#9467bd', '-'), ('C3U4v4', 'C3-U4 (state-supervised, unrolled)', '#2ca02c', '-')):
        x = seed_median(ch, 'bart', 'month', stem, 'plus')
        if x: ax.plot(*x, c=c, ls=ls, label=f'{lab}, seed median')
    x = curve(ch, ('bart', 'month', 'F_empty', 'plus'))
    if x: ax.plot(*x, c='k', ls='--', label='RRR-16 (closed form)')
    ax.set_xlabel('chain length $k$'); ax.set_ylabel('$R_k$ (trajectory success)'); ax.set_ylim(-.03, 1.03); ax.set_title('(b) BART-base, month, one-way plus')
    ax.legend(loc='center right', fontsize=5.5)
    finish(fig, 'fig1', [V5])


if __name__ == '__main__':
    main()
