# Copyright (c) 2018, Arm Limited and affiliates.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile

from .host_test_plugins import HostTestPluginBase
from ..host_tests_logger import HtrunLogger


RESET_FILE = "reset.jlink"

class HostTestPluginResetMethod_Jlink(HostTestPluginBase):

    # Plugin interface
    name = 'HostTestPluginResetMethod_Jlink'
    type = 'ResetMethod'
    capabilities = ['JTAG', 'SWD']
    #TODO: Isn't MCU required?
    required_parameters = []
    #TODO: What is this?
    stable = False

    def is_os_supported(self, os_name=None):
        """! In this implementation this plugin only is supporeted under Windows machines
        """
        # If no OS name provided use host OS name
        if not os_name:
            os_name = self.mbed_os_support()

        # This plugin only works on Windows
        if os_name and os_name.startswith('Windows'):
            return True
        return False

    def setup(self, *args, **kwargs):
        """! Configure plugin, this function should be called before plugin execute() method is used.
        """
        self.logger = HtrunLogger('JLINK_RESET_PLUGIN')
        #Note you need to have jlink.exe on your system path!
        self.JLINK = 'JLink.exe'
        return True
    
    def build_jlink_script(self, path):
        """! write a jlink commander file that
            reset the target

        @param path the file path of the script we are writing in the function
        """
        with open(path, "w") as jlink_script:
            #TODO: Fix this wierd os.linesep in every line
            jlink_script.write("r {}".format(os.linesep))
            jlink_script.write("go {}".format(os.linesep))
            jlink_script.write("exit {}".format(os.linesep))

    def internal_param_check(self, **kwargs):
        """! Internal check for the JLINK sepcial kwargs
        """
        #TODO: Isn't this function's behaviour already covered in `required_parameters`? If so do we need to remove the logger as well?
        if kwargs['mcu'] == None:
            self.logger.prn_err("MCU isn't sepcified")
            return False
        return True

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments

        @details Each capability e.g. may directly just call some command line program or execute building pythonic function

        @return Capability call return value
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            
            if not self.internal_param_check(**kwargs):
                return False
            
            #TODO: This line does not exist in our files, have we even ran in lately?
            mcu = os.path.normpath(kwargs['mcu'])

            jlink_file_path = os.path.join(tempfile.gettempdir(), RESET_FILE)

            self.build_jlink_script(jlink_file_path)

            #TODO: Should these params be configurable somehow?
            if capability == 'JTAG':
                cmd = [self.JLINK,
                       "-device", mcu,
                       "-if", "JTAG",
                       "-jtagconf", "-1,-1",
                       "speed", "1000",
                       "-CommanderScript", jlink_file_path]

            elif capability == 'SWD':
                cmd = [self.JLINK,
                       "-device", mcu,
                       "-if", "SWD",
                       "speed", "1000",
                       "-CommanderScript", jlink_file_path]
            else:
                #TODO: We don't have this condition internally.
                self.logger.prn_err("Unsupported capability")

            result = self.run_command(cmd)

        return result


def load_plugin():
    """ Returns plugin available in this module
    """
    return HostTestPluginResetMethod_Jlink()
