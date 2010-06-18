from lettuce import *
from gaphor.application import Application

@before.each_feature
def setup_application(step):
    Application.init()

@after.each_feature
def shutdown_application(step):
    Application.get_service('element_factory').shutdown()
    Application.shutdown()

@step('I load the model "([^"]+)"')
def when_i_load_the_model(step, filename):
    from gaphor.storage.storage import load
    load(filename, Application.get_service('element_factory'))

@step('I open diagram "([^"]+)"')
def when_i_open_diagram(step, name):
    pass

@step('I have (\d+) opene?d? diagrams?')
def have_n_open_diagrams(self, n):
    n = int(n)


# vim:sw=4:et:ai
