from freshen import *
from gaphor.application import Application

@Before
def setup_application(sc):
    print 'App init'
    Application.init()
    print 'App init done'

@After
def shutdown_application(sc):
    print 'App shitdown'
    Application.get_service('element_factory').shutdown()
    Application.shutdown()
    print 'App shitdown done'

@Given('I load the model "([^"]+)"')
def when_i_load_the_model(filename):
    print 'step 1'
    from gaphor.storage.storage import load
    load(filename, Application.get_service('element_factory'))

@When('I open diagram "([^"]+)"')
def when_i_open_diagram(name):
    print 'step 2'
    pass

@Then('I have (\d+) opene?d? diagrams?')
def have_n_open_diagrams(n):
    print 'step 3'
    n = int(n)


# vim:sw=4:et:ai
