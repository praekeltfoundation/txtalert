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
            cov_dir = join(settings.APP_ROOT, "tmp", "coverage")
            cov.start()
            
            from django.core.management.commands import test
            command = test.Command()
            command.handle(*test_labels, **options)
            
            cov.stop()
            cov.html_report(directory=cov_dir, omit_prefixes=[
                'django',
                'lib'
            ])
            print '\n\nCoverage report available at %s/index.html' % cov_dir
            
        except ImportError, e:
            print e
            print "Coverage (http://nedbatchelder.com/code/coverage/) " \
                    "is needed for code coverage"
