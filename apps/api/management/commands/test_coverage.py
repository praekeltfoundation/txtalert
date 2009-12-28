from django.core.management.base import BaseCommand
from django.conf import settings
from os.path import join

class Command(BaseCommand):
    help = 'Runs the test suite for the specified applications, or the entire ' \
    'site if no apps are specified and generate coverage report'
    args = '[appname ...]'
    
    def handle(self, *test_labels, **options):
        try:
            from coverage import coverage
            
            cov = coverage()
            cov.exclude('django')
            cov.exclude('_django')
            
            cov_log = join(settings.APP_ROOT, "tmp", "coverage")
            cov.start()
            
            from django.core.management.commands import test
            command = test.Command()
            command.handle(*test_labels, **options)
            
            cov.stop()
            cov.html_report(directory=cov_log)
            
        except ImportError, e:
            print e
            print "Coverage (http://nedbatchelder.com/code/coverage/) " \
                    "is needed for code coverage"
