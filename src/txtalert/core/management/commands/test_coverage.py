from django.core.management.base import BaseCommand
from django.conf import settings
from os.path import join
import commands

class Command(BaseCommand):
    # option_list = test.Command.option_list
    help = 'Runs the test suite for the specified applications, or the entire ' \
    'site if no apps are specified and generate coverage report'
    
    def handle(self, *test_labels, **options):
        """
        Running coverage as an external tool to make sure that it is the first
        lib that is loaded and properly checks all code from that point on. If
        coverage is started at a later point the analysis can be incomplete.
        """
        
        from django.conf import settings
        
        cov_dir = join(settings.APP_ROOT, "tmp", "coverage")
        omit_dirs = [
            'django',
            'lib', 
            'manage.py',
        ]
        
        print 'Erasing previously collected coverage.py data'
        status, output = commands.getstatusoutput("coverage erase")
        print 'Running tests with coverage.py'
        status, output = commands.getstatusoutput("coverage run ./manage.py test --settings=%s" % settings.SETTINGS_MODULE)
        
        if status is not 0:
            print "Something went wrong running the tests:"
            print output
        else:
            print 'Creating coverage.py html report, omitting directories: %s' % ', '.join(omit_dirs)
            status, _ = commands.getstatusoutput("coverage html " +
                                                    "-d %s " % cov_dir +
                                                    "--omit=%s " % ','.join(omit_dirs))
            if status is not 0:
                print "Something went wrong generating the html report:"
                print output
            else:
                print 'Coverage report available at %s/index.html' % cov_dir
