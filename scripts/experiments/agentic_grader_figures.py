"""Generate reference-design SVGs; no measured timing implied by placement."""
from pathlib import Path
from xml.sax.saxutils import escape

DEST = Path('images/ic-design-platform/2026-10-20')
DEST.mkdir(parents=True, exist_ok=True)


def diagram(name, title, boxes, footer):
    height = 120 + len(boxes)*136 + 75
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{height}" viewBox="0 0 640 {height}" role="img">',
             f'<title>{escape(title)}</title>',
             '<rect width="640" height="100%" fill="#ffffff"/>',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#315e86"/></marker></defs>',
             '<g font-family="sans-serif" fill="#172c3d">',
             f'<text x="32" y="42" font-size="25" font-weight="bold">{escape(title)}</text>',
             '<text x="32" y="75" font-size="18" fill="#475c6d">Reference design · Tools check, engineers accept</text>']
    for i, (heading, a, b) in enumerate(boxes):
        y = 100+i*136
        if i:
            lines.append(f'<path d="M320,{y-24} V{y-6}" stroke="#315e86" stroke-width="2" marker-end="url(#arrow)"/>')
        lines += [f'<rect x="32" y="{y}" width="576" height="108" rx="12" fill="#eef5fb" stroke="#a7bfd1"/>',
                  f'<text x="52" y="{y+30}" font-size="23" font-weight="bold">{escape(heading)}</text>',
                  f'<text x="52" y="{y+61}" font-size="20">{escape(a)}</text>',
                  f'<text x="52" y="{y+88}" font-size="20">{escape(b)}</text>']
    lines += [f'<text x="32" y="{height-55}" font-size="17">{escape(footer)}</text>',
              f'<text x="608" y="{height-20}" text-anchor="end" font-size="10" fill="#475c6d">Scott Yo-Ru Chen · 2026-10-20</text>', '</g></svg>']
    (DEST/name).write_text('\n'.join(lines)+'\n', encoding='utf-8')


diagram('artifact-grader-flow.svg', 'One submission, one checked result', [
    ('1  Pin the task and inputs', 'RTL · test · seed · SDC · tool recipe', 'Method owner sets versions and criteria'),
    ('2  Agent proposes a candidate', 'Write test or RTL patch; request tool jobs', 'Keep passing versions; submit each change'),
    ('3  Runner executes and seals', 'Trace and reports share one execution', 'Coverage and checker use matching inputs'),
    ('4  Grader reads immutable outputs', 'Check completeness and identity first', 'Record missing data, failure and timeout'),
    ('5  Deliver quality and cost together', 'Versions · checks · CPU / license / labor', 'Engineer accepts through the design flow')
], 'Arrows show order, not measured timing or throughput.')

diagram('artifact-grader-rejection.svg', 'Ask which execution the report belongs to', [
    ('1  Read completion and output records', 'Require a completed job and sealed output', 'Timeout / missing file: retain diagnostics'),
    ('2  Match inputs and execution', 'Compare RTL, test, seed and tool versions', 'Old RTL / other stimulus: reject the result'),
    ('3  Verify content and same-trace check', 'Digest detects changes after sealing', 'Missing checker / wrong data: reject'),
    ('4  Merge qualified coverage only', 'Add bins from valid executions', 'A new RTL revision gets its own result set')
], 'Digests compare content; producer trust is a separate task.')
