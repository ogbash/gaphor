'''
Use case diagram item
'''
# vim:sw=4

from __future__ import generators

import diacanvas
from gaphor import UML
from nameditem import NamedItem

class UseCaseItem(NamedItem):
    __uml__   = UML.UseCase
    __align__ = NamedItem.NAMED_ITEM_C

    def create_border(self):
        border = diacanvas.shape.Ellipse()
        return NamedItem.create_border(self, border)


    def draw_border(self):
        self._border.ellipse(center = (self.width / 2, self.height / 2),
            width = self.width, height = self.height)


