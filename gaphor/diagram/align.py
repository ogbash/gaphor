"""
Align constants.
"""

#
# Enums
#

# horizontal elign
H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT = range(3)

# vertical align
V_ALIGN_TOP, V_ALIGN_MIDDLE, V_ALIGN_BOTTOM = range(3)

# margin indices for ItemALign.margin variable
# order like in CSS
MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT = range(4)


class ItemAlign(object):
    """
    Diagram item (canvas element based) align and margins.

    By default there is no margin, item is centered on top.
    """
    def __init__(self, **kw):
        super(ItemAlign, self).__init__()

        self.margin  = (0, ) * 4
        self.align   = H_ALIGN_CENTER
        self.valign  = V_ALIGN_TOP
        self.outside = False

        for k, v in kw.items():
            setattr(self, k, v)


# common align cases for canvas based items
ITEM_ALIGN_CT   = ItemAlign()                           # center, top
ITEM_ALIGN_C    = ItemAlign(valign = V_ALIGN_MIDDLE)    # center, middle
ITEM_ALIGN_CB   = ItemAlign(valign = V_ALIGN_BOTTOM)    # center, bottom

ITEM_ALIGN_O_LT = ItemAlign(align = H_ALIGN_LEFT,       # outside, left, top
    outside = True)
ITEM_ALIGN_O_RB = ItemAlign(align = H_ALIGN_RIGHT,      # outside, right, bottom
    valign = V_ALIGN_BOTTOM, outside = True)
ITEM_ALIGN_O_CB = ItemAlign(valign = V_ALIGN_BOTTOM,    # outside, center, bottom
    outside = True)
