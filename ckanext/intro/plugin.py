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
