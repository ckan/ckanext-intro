import logging
import os
import csv
import tempfile

import ckan.plugins as p


log = logging.getLogger(__name__)


class IntroExamplePlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IAuthFunctions)
    p.implements(p.IActions)

    ## IConfigurer
    def update_config(self, config):
        '''
        This method allows to access and modify the CKAN configuration object
        '''

        log.info('You are using the following plugins: {0}'
                 .format(config.get('ckan.plugins')))

        # Check CKAN version
        # To raise an exception instead, use:
        #   p.toolkit.require_ckan_version('2.1')
        if not p.toolkit.check_ckan_version('2.1'):
            log.warn('This extension has only been tested on CKAN 2.1!')

        # Add the extension templates directory so it overrides the CKAN core
        # one
        p.toolkit.add_template_directory(config, 'theme/templates')

        # Add the extension public directory so we can serve our own content
        p.toolkit.add_public_directory(config, 'theme/public')

    ## IRoutes
    def after_map(self, map):

        controller = 'ckanext.intro.plugin:CustomController'
        map.connect('/custom', controller=controller, action='custom_page')

        map.connect('/csv', controller=controller, action='datasets_report')

        return map

    ## IAuthFunctions
    def get_auth_functions(self):

        # Return a dict with the auth functions that we want to override
        # or add
        return {
            'group_create': group_create,
            'datasets_report_csv': datasets_report_csv_auth,
        }

    ## IActions
    def get_actions(self):
        # Return a dict with the action functions that we want to add
        return {
            'datasets_report_csv': datasets_report_csv,
        }


def group_create(context, data_dict):
    '''
    This function overrides the default group_create authorization,
    not allowing anyone (except sysadmins) to create groups
    '''
    return {'success': False, 'msg': 'Only sysadmins can create groups'}


# Ideally auth functions should have the same name as their actions and be
# kept on different modules. To keep things simple and all the functions on
# the same file we will name this one slightly different.
def datasets_report_csv_auth(context, data_dict):

    return {'success': False, 'msg': 'Only sysadmins can get a report'}


def datasets_report_csv(context, data_dict):
    '''
    A custom action function that generates a CSV file with metadata from
    all datasets in the CKAN instance and stores it on a temporal file,
    returning its path.

    Note how we call `p.toolkit.check_access` to make sure that the user is
    authorized to perform this action.
    '''

    p.toolkit.check_access('datasets_report_csv', context, data_dict)

    # Get all datasets from the search index (actually the first 100)
    data_dict = {
        'q': '*:*',
        'rows': 100,
    }
    result = p.toolkit.get_action('package_search')(context, data_dict)

    # Create a temp file to store the csv
    fd, tmp_file_path = tempfile.mkstemp(suffix='.csv')

    with open(tmp_file_path, 'w') as f:
        field_names = ['name', 'title', 'tags',
                       'metadata_created', 'metadata_modified']
        writer = csv.DictWriter(f, fieldnames=field_names,
                                quoting=csv.QUOTE_ALL)
        writer.writerow(dict((n, n) for n in field_names))
        for dataset in result['results']:
            row = {}
            for field_name in field_names:
                if field_name == 'tags':
                    tag_names = [t['name'] for t in dataset.get('tags', [])]
                    row['tags'] = ', '.join(tag_names).encode('utf8')
                else:
                    row[field_name] = dataset[field_name].encode('utf8')
            writer.writerow(row)

        return {
            'file': tmp_file_path,
        }


class CustomController(p.toolkit.BaseController):

    def custom_page(self):

        return p.toolkit.render('custom.html')

    def datasets_report(self):

        try:
            # We don't need to pass any parameters to the action function
            # (context and data_dict), as a new context will be automatically
            # created for you, and we don't need to pass any data from the
            # user to the action function.
            result = p.toolkit.get_action('datasets_report_csv')()
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, 'Not authorized to see this report')

        with open(result['file'], 'r') as f:
            content = f.read()

        # Clean up
        os.remove(result['file'])

        # Modify the headers of the response to reflect that we are outputing
        # a CSV file
        p.toolkit.response.headers['Content-Type'] = 'application/csv'
        p.toolkit.response.headers['Content-Length'] = len(content)
        p.toolkit.response.headers['Content-Disposition'] = \
            'attachment; filename="datasets.csv"'

        return content
