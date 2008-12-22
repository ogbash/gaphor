"""
Comment and comment line items connection adapters tests.
"""

from gaphor import UML
from gaphor.diagram import items

from gaphor.tests import TestCase

class CommentLineTestCase(TestCase):
    def test_commentline_annotated_element(self):
        """Test comment line item annotated element creation
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        # while connected, but no annotated element yet
        self.assertTrue(line.head.connected_to is not None)
        self.assertTrue(comment.subject.annotatedElement is None)


    def test_commentline_same_comment_glue(self):
        """Test comment line item glueing to already connected comment item
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        self.connect(line, line.head, comment)
        glued = self.glue(line, line.tail, comment)
        self.assertFalse(glued)


    def test_commentline_element_connect(self):
        """Test comment line connecting to comment and actor items.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)
        self.assertTrue(line.tail.connected_to is ac)
        self.assertEquals(1, len(comment.subject.annotatedElement))
        self.assertTrue(ac.subject in comment.subject.annotatedElement)


    def test_commentline_element_disconnect(self):
        """Test comment line connecting to comment and disconnecting actor item.
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        ac = self.create(items.ActorItem, UML.Actor)

        self.connect(line, line.head, comment)
        self.connect(line, line.tail, ac)

        assert line.tail.connected_to is ac

        self.disconnect(line, line.tail)
        self.assertFalse(line.tail.connected_to is ac)

        
    def test_commentline_class(self):
        """
        Connect a CommentLine to a class and unlink the commentLine
        afterwards.
        """
        clazz = self.create(items.ClassItem, UML.Class)
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle, comment.ports()[0])

        adapter = component.queryMultiAdapter((clazz, line), IConnect)
        handle = line.tail
        adapter.connect(handle, clazz.ports()[0])

        assert clazz.subject in comment.subject.annotatedElement
        assert comment.subject in clazz.subject.ownedComment

        line.unlink()

        assert not comment.subject.annotatedElement
        assert not clazz.subject.ownedComment


    def test_commentline_relationship_unlink(self):
        """
        Connect a CommentLine to a relationship item.
        Removing the relationship should work.

        Demonstrates defect #103.
        """
        clazz1 = self.create(items.ClassItem, UML.Class)
        clazz2 = self.create(items.ClassItem, UML.Class)
        gen = self.create(items.GeneralizationItem)

        adapter = component.queryMultiAdapter((clazz1, gen), IConnect)
        handle = gen.head
        adapter.connect(handle, clazz1.ports()[0])

        adapter = component.queryMultiAdapter((clazz2, gen), IConnect)
        handle = gen.tail
        adapter.connect(handle, clazz2.ports()[0])

        assert gen.subject

        # And now the comment:

        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)

        adapter = component.queryMultiAdapter((comment, line), IConnect)
        handle = line.head
        adapter.connect(handle)

        adapter = component.queryMultiAdapter((gen, line), IConnect)
        handle = line.tail
        adapter.connect(handle)

        assert gen.subject in comment.subject.annotatedElement
        assert comment.subject in gen.subject.ownedComment

        gen.unlink()

        assert not comment.subject.annotatedElement
        assert not gen.subject


    def test_commentline_association(self):
        """
        Test CommentLineItem with AssociationItem.

        # TODO: check behaviour if:
          1. comment line is connected to association + comment and after that
             association is connected to two classes.
             -> association should be connected to comment.annotatedElement
          2. association is disconnected while a comment is connected:
             -> association should be removed from comment.annotatedElement
        """
        comment = self.create(items.CommentItem, UML.Comment)
        line = self.create(items.CommentLineItem)
        line.head.pos = 100, 100
        line.tail.pos = 100, 100
        c1 = self.create(items.ClassItem, UML.Class)
        c2 = self.create(items.ClassItem, UML.Class)
        assoc = self.create(items.AssociationItem)

        adapter = component.queryMultiAdapter((c1, assoc), IConnect)
        handle = assoc.head
        adapter.connect(handle, c1.ports()[0])

        adapter = component.queryMultiAdapter((c2, assoc), IConnect)
        handle = assoc.tail
        adapter.connect(handle, c2.ports()[0]) 
        assert assoc.head.connected_to is c1
        assert assoc.tail.connected_to is c2
        assert assoc.subject

        # Connect the association item to the head of the line:

        adapter = component.queryMultiAdapter((assoc, line), IConnect)
        assert adapter
        import gaphor.adapters.connectors
        assert type(adapter) is gaphor.adapters.connectors.CommentLineLineConnect
        handle = line.head
        pos = adapter.glue(handle)
        assert pos == (10, 50), pos
        adapter.connect(handle, assoc.ports()[0])

        assert handle.connected_to is assoc
        assert handle.connection_data is not None
        assert not comment.subject.annotatedElement

        # Connecting two ends of the line to the same item is not allowed:

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is None
        assert not comment.subject.annotatedElement, comment.subject.annotatedElement

        # now connect the comment

        adapter = component.queryMultiAdapter((comment, line), IConnect)

        handle = line.tail
        adapter.connect(handle)

        assert handle.connected_to is comment
        assert handle.connection_data is not None
        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Disconnect comment:

        adapter.disconnect(handle)

        assert handle.connected_to is None, handle.connected_to
        assert handle.connection_data is None
        assert len(comment.subject.annotatedElement) == 0, comment.subject.annotatedElement
        assert not assoc.subject in comment.subject.annotatedElement, comment.subject.annotatedElement

        # Connect again:

        adapter.connect(handle)
        assert handle.connected_to is not None, handle.connected_to