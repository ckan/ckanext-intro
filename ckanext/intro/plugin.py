import logging

import ckan.plugins as p


log = logging.getLogger(__name__)


class IntroExamplePlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer)

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
