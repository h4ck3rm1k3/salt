# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`


    tests.integration.shell.syndic
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Import python libs
import os
import yaml
import signal
import shutil

# Import Salt Testing libs
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

# Import salt libs
import integration
import salt.utils
import logging
log = logging.getLogger(__name__)


class SyndicTest(integration.ShellCase, integration.ShellCaseCommonTestsMixIn):

    _call_binary_ = 'salt-syndic'

    def test_issue_7754(self):
        old_cwd = os.getcwd()
        config_dir = os.path.join(integration.TMP, 'issue-7754')
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)

        os.chdir(config_dir)

        for fname in ('master', 'minion'):
            pid_path = os.path.join(config_dir, '{0}.pid'.format(fname))
            with salt.utils.fopen(self.get_config_file_path(fname), 'r') as fhr:
                config = yaml.load(fhr.read())
                config['log_file'] = config['syndic_log_file'] = 'file:///tmp/log/LOG_LOCAL3'
                config['root_dir'] = config_dir
                if 'ret_port' in config:
                    config['ret_port'] = int(config['ret_port']) + 10
                    config['publish_port'] = int(config['publish_port']) + 10

                with salt.utils.fopen(os.path.join(config_dir, fname), 'w') as fhw:
                    fhw.write(
                        yaml.dump(config, default_flow_style=False)
                    )

        ret = self.run_script(
            self._call_binary_,
            '--config-dir={0} --pid-file={1} -l debug'.format(
                config_dir,
                pid_path
            ),
            timeout=5,
            catch_stderr=True,
            with_retcode=True
        )

        # Now kill it if still running
        if os.path.exists(pid_path):
            with salt.utils.fopen(pid_path) as fhr:
                try:
                    os.kill(int(fhr.read()), signal.SIGKILL)
                except OSError as exp:
                    log.error('OSError {0}'.format(exp))
                    pass
        try:
            self.assertFalse(os.path.isdir(os.path.join(config_dir, 'file:')))
            self.assertIn(
                'Failed to setup the Syslog logging handler', '\n'.join(ret[1])
            )
            self.assertEqual(ret[2], 2)
        finally:
            os.chdir(old_cwd)
            if os.path.isdir(config_dir):
                shutil.rmtree(config_dir)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(SyndicTest)
