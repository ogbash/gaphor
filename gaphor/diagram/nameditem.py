"""NamedItem diagram item
"""
# vim:sw=4:et

import itertools

import gobject
import pango
import diacanvas
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.align import ITEM_ALIGN_CT, \
    MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT, \
    H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT, \
    V_ALIGN_TOP, V_ALIGN_MIDDLE, V_ALIGN_BOTTOM
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.groupable import GroupBase


class TextElement(diacanvas.CanvasItem, diacanvas.CanvasEditable, DiagramItem):
    """
    Represents one text element of diagram item, i.e. flow guard, join node
    join specification, any UML named element name, etc.

    This class references subject, which can be diagram element subject
    or LiteralSpecification. Subject attribute is watched to update text
    element on diagram.

    Objects of this class are grouped with parent with GroupBase class.

    subject:         flow guard, join node specification, etc.
    subject_attr:    subject attribute containing text value
    subject_pattern: defaults to %s, is used to render text value, i.e. for
                     join node join specification it should be set to
                     '{ joinSpec = %s }'
    """
    __metaclass__ = DiagramItemMeta

    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, attr, pattern = '%s', default = None, id = None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)

        self.subject_attr = attr
        self.subject_pattern = pattern
        self.subject_default = default

        def f(subject, pspec):
            self.set_text(getattr(subject, self.subject_attr))
            self.parent.request_update()

        # create callback method to watch for changes of subject attribute
        setattr(self, 'on_subject_notify__%s' % self.subject_attr, f)

        self.set_flags(diacanvas.COMPOSITE)
        
        font = pango.FontDescription(self.FONT)
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(font)
        self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)
        self._name_border = diacanvas.shape.Path()
        self._name_border.set_color(diacanvas.color(128,128,128))
        self._name_border.set_line_width(1.0)
        self._name_bounds = (0, 0, 0, 0)

        # show name border when (parent) diagram item is selected
        self.show_border = True

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def set_text(self, txt):
        """
        Set text of text element. It is rendered with pattern.
        """
        if txt and txt != self.subject_default:
            self._name.set_text(self.subject_pattern % txt)
        else:
            self._name.set_text('')
        self.request_update()

    def postload(self):
        DiagramItem.postload(self)

    def edit(self):
        self.start_editing(self._name)

    def update_label(self, x, y):
        name_w, name_h = self.get_size()

        a = self.get_property('affine')
        self.set_property('affine', (a[0], a[1], a[2], a[3], x, y))

        # Now set width and height:
        self._name_bounds = (0, 0, name_w, name_h)

    def on_update(self, affine):
        diacanvas.CanvasItem.on_update(self, affine)

        # bounds calculation
        b1 = self._name_bounds
        self._name_border.rectangle((b1[0], b1[1]), (b1[2], b1[3]))
        self.set_bounds(b1)

    def on_point(self, x, y):
        p = (x, y)
        drp = diacanvas.geometry.distance_rectangle_point
        return drp(self._name_bounds, p)


    def get_size(self):
        """
        Return size of text element.
        """
        return map(max, self._name.to_pango_layout(True).get_pixel_size(), (10, 10))


    def on_shape_iter(self):
        """
        Return text element text and thin border, which is used to attract
        user attention.
        """
        if self.subject:
            yield self._name
            if self.is_selected() and self.show_border:
                yield self._name_border

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        return self._name

    def on_editable_start_editing(self, shape):
        pass
        #self.preserve_property('name')


    def on_editable_editing_done(self, shape, new_text):
        """
        If subject of text element exists, then set subject attribute to
        value entered by user. If text is embedded within pattern then
        remove pattern from real text value.
        """
        if self.subject:
            if self.subject_pattern != '%s':
                # remove pattern from real text value
                s1, s2 = self.subject_pattern.split('%s')
                if new_text.startswith(s1) and new_text.endswith(s2):
                    l1, l2 = map(len, (s1, s2))
                    new_text = new_text[l1:]
                    new_text = new_text[:-l2]

            self.canvas.get_undo_manager().begin_transaction()
            log.debug('setting %s to %s' % (self.subject_attr, new_text))
            setattr(self.subject, self.subject_attr, new_text)
            self.canvas.get_undo_manager().commit_transaction()


    # notifications
    def on_subject_notify(self, pspec, notifiers=()):
        """
        Detect changes of text element subject.

        If subject does not exist then set text to empty string.
        """
        DiagramItem.on_subject_notify(self, pspec, notifiers + (self.subject_attr,))
        if self.subject:
            self.set_text(getattr(self.subject, self.subject_attr))
        else:
            self.set_text('')
        self.request_update()



from zope import interface
from gaphor.interfaces import INamedItemView


class Named(diacanvas.CanvasEditable):
    interface.implements(INamedItemView)

    def __init__(self, id = None):
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(pango.FontDescription(self.FONT))
        self._name.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)


    #
    # utility methods
    #
    def get_name_size(self):
        """
        Return the width and height of the name shape.
        """
        return self._name.to_pango_layout(True).get_pixel_size()


    def update_name(self, x, y, width, height):
        """
        Update name position, width and height.

        @arg x: position on x axis
        @arg y: position on y axis
        @arg width: width of name
        @arg height height of name
        """
        self._name.set_pos((x, y))
        self._name.set_max_width(width)
        self._name.set_max_height(height)

    #
    # DiagramItem subject notification methods
    #
    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Subject change notification callback.
        """
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)
        self._name.set_text(self.subject and self.subject.name or '')


    def on_subject_notify__name(self, subject, pspec):
        """
        Subject name change notification callback.
        """
        assert self.subject is subject
        self._name.set_text(self.subject.name or '')
        self.request_update()


    #
    # CanvasEditable interface implementation
    #
    def on_editable_get_editable_shape(self, x, y):
        return self._name


    def on_editable_start_editing(self, shape):
        pass


    def on_editable_editing_done(self, shape, new_text):
        if new_text != self.subject.name:
            self.canvas.get_undo_manager().begin_transaction()
            self.subject.name = new_text
            self.canvas.get_undo_manager().commit_transaction()

        self.request_update()


    #
    # CanvasItem or CanvasLine callbacks
    #
    def on_event (self, event):
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            self.rename()
            return True
        else:
            return ElementItem.on_event(self, event)


    def on_shape_iter(self):
        return iter([self._name])



class NamedItem(ElementItem, Named, diacanvas.CanvasEditable):
    __gproperties__ = {
        'name': (gobject.TYPE_STRING, 'name', '', '', gobject.PARAM_READWRITE)
    }

    popup_menu = (
        'RenameItem',
        'separator',
        'EditDelete',
        'ShowElementInTreeView'
    )

    # these values can be overriden
    FONT = 'sans bold 10'
    WIDTH = 120
    HEIGHT = 60

    n_align = ITEM_ALIGN_CT

    def __init__(self, id=None):
        align = self.n_align
        if align.outside:
            align.margin = (2, ) * 4
        else:
            align.margin = (15, 30) * 2

        ElementItem.__init__(self, id)
        Named.__init__(self, id)

        self._border = self.create_border()


    def create_border(self, border = None):
        """
        Create default border.
        """
        if border is None:
            border = diacanvas.shape.Path()
        border.set_line_width(2.0)
        self.set(width = self.WIDTH, height = self.HEIGHT)
        return border


    def draw_border(self):
        """
        Draw border of simple named item, rectangle by default.
        """
        self._border.rectangle((0, 0), (self.width, self.height))


    def on_update(self, affine):
        width, height = self.get_name_size()

        align = self.n_align

        if align.outside:
            if align.align == H_ALIGN_LEFT:
                x = -width - align.margin[MARGIN_LEFT]
            elif align.align == H_ALIGN_CENTER:
                x = (self.width - width) / 2
            elif align.align == H_ALIGN_RIGHT:
                x = self.width + align.margin[MARGIN_RIGHT]
            else:
                assert False

            if align.valign == V_ALIGN_TOP:
                y = -height - align.margin[MARGIN_TOP]
            elif align.valign == V_ALIGN_MIDDLE:
                y = (self.height - height) / 2
            elif align.valign == V_ALIGN_BOTTOM:
                y = self.height + align.margin[MARGIN_BOTTOM]
            else:
                assert False

        else:
            self.set(min_width = width + align.margin[MARGIN_RIGHT] + align.margin[MARGIN_LEFT],
                min_height = height + align.margin[MARGIN_TOP] + align.margin[MARGIN_BOTTOM])

            if align.align == H_ALIGN_LEFT:
                x = align.margin[MARGIN_LEFT]
            elif align.align == H_ALIGN_CENTER:
                x = (self.width - width) / 2
            elif align.align == H_ALIGN_RIGHT:
                x = self.width - width - align.margin[MARGIN_RIGHT]
            else:
                assert False

            if align.valign == V_ALIGN_TOP:
                y = align.margin[MARGIN_TOP]
            elif align.valign == V_ALIGN_MIDDLE:
                y = (self.height - height) / 2
            elif align.valign == V_ALIGN_BOTTOM:
                y = self.height - height - align.margin[MARGIN_BOTTOM]
            else:
                assert False

        self.update_name(x, y, width, height)

        ElementItem.on_update(self, affine)

        if align.outside:
            wx, hy = x + width, y + height
            self.set_bounds((min(0, x), min(0, y),
                max(self.width, wx), max(self.height, hy)))

        self.draw_border()
        self.expand_bounds(1.0)


    def on_shape_iter(self):
        return itertools.chain([self._border],
            Named.on_shape_iter(self),
            ElementItem.on_shape_iter(self))
