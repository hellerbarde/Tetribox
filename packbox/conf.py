parts = [
    'base-14-10',
    'side-10-a-holes',
    'side-10-b-holes',
    'side-14-a',
    'side-14-b',
    'divider-10',
    'divider-10',
    'divider-10',
    'divider-3',
    'divider-3',
    'divider-3',
    'divider-5',
    'divider-5',
    'divider-4',
    'divider-4'
]

svgdir = './svg'


# A2 = 420 × 594
# 1pt = 25.4mm / 72
# 72pt = 25.4mm
# 72pt/25.4 = 1mm
pt = lambda mm: mm * 72/25.4
sheet_width = pt(840)
sheet_height = pt(594)

# algorithm = 'shelf'
algorithm = 'guillotine'

epsilon = pt(5)