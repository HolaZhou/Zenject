
import sys
import os
import re

import argparse

from mtm.log.LogStreamFile import LogStreamFile
from mtm.log.LogStreamConsole import LogStreamConsole

from mtm.util.ZipHelper import ZipHelper

from mtm.util.ScriptRunner import ScriptRunner

from mtm.util.ProcessRunner import ProcessRunner
from mtm.util.SystemHelper import SystemHelper
from mtm.util.VarManager import VarManager
from mtm.config.Config import Config
from mtm.log.Logger import Logger
from mtm.util.VisualStudioHelper import VisualStudioHelper
from mtm.util.UnityHelper import UnityHelper, Platforms

from mtm.util.Assert import *

import mtm.ioc.Container as Container
from mtm.ioc.Inject import Inject

ScriptDir = os.path.dirname(os.path.realpath(__file__))
RootDir = os.path.realpath(os.path.join(ScriptDir, '../../../..'))

class Runner:
    _scriptRunner = Inject('ScriptRunner')
    _unityHelper = Inject('UnityHelper')
    _log = Inject('Logger')
    _sys = Inject('SystemHelper')

    def run(self, args):
        self._args = args
        success = self._scriptRunner.runWrapper(self._runInternal)

        if not success:
            sys.exit(1)

    def _runInternal(self):

        if self._args.all:
            self._log.heading("Building windows 3.5")
            self._changeToNetRuntime35()
            self._runBuild(Platforms.Windows)
            self._log.heading("Building windows 4.6")
            self._changeToNetRuntime46()
            self._runBuild(Platforms.Windows)
            self._log.heading("Building WindowsStoreApp")
            self._runBuild(Platforms.WindowsStoreApp)
            self._log.heading("Building WebGl")
            self._runBuild(Platforms.WebGl)
            self._log.heading("Building Ios")
            self._runBuild(Platforms.Ios)
            self._log.heading("Building Android")
            self._runBuild(Platforms.Android)
        else:
            if self._args.csharp35:
                self._changeToNetRuntime35()

            elif self._args.csharp46:
                self._changeToNetRuntime46()

            if self._args.build:
                self._log.heading("Running Build")
                self._runBuild(self._args.platform)

            elif self._args.openUnity:
                self._log.heading("Opening Unity")
                self._unityHelper.openUnity('[UnityProjectPath]', self._args.platform)

    def _runBuild(self, platform):
        self._unityHelper.runEditorFunction('[UnityProjectPath]', 'Zenject.Internal.SampleBuilder.BuildRelease', platform)

        if platform == Platforms.WebGl:
            self._sys.copyFile('[WebGlTemplate]', '[OutputRootDir]/WebGl/web.config')

    def _changeToNetRuntime46(self):
        self._unityHelper.runEditorFunction('[UnityProjectPath]', 'Zenject.Internal.SampleBuilder.EnableNet46', Platforms.Windows)

    def _changeToNetRuntime35(self):
        self._unityHelper.runEditorFunction('[UnityProjectPath]', 'Zenject.Internal.SampleBuilder.EnableNet35', Platforms.Windows)

def installBindings():

    config = {
        'PathVars': {
            'ScriptDir': ScriptDir,
            'RootDir': RootDir,
            'BuildDir': '[RootDir]/Build',
            'WebGlTemplate': '[ScriptDir]/web_config_template.xml',
            'OutputRootDir': '[RootDir]/SampleBuilds',
            'UnityExePath': 'D:/Utils/Unity/Unity2017.4.0f1/Editor/Unity.exe',
            'LogPath': '[BuildDir]/Log.txt',
            'UnityProjectPath': '[RootDir]/UnityProject',
            'MsBuildExePath': 'C:/Windows/Microsoft.NET/Framework/v4.0.30319/msbuild.exe'
        },
        'Compilation': {
            'UseDevenv': False
        },
    }
    Container.bind('Config').toSingle(Config, [config])

    Container.bind('LogStream').toSingle(LogStreamFile)
    Container.bind('LogStream').toSingle(LogStreamConsole, True, False)

    Container.bind('ScriptRunner').toSingle(ScriptRunner)
    Container.bind('VarManager').toSingle(VarManager)
    Container.bind('SystemHelper').toSingle(SystemHelper)
    Container.bind('Logger').toSingle(Logger)
    Container.bind('ProcessRunner').toSingle(ProcessRunner)
    Container.bind('ZipHelper').toSingle(ZipHelper)
    Container.bind('VisualStudioHelper').toSingle(VisualStudioHelper)
    Container.bind('UnityHelper').toSingle(UnityHelper)

if __name__ == '__main__':

    if (sys.version_info < (3, 0)):
        print('Wrong version of python!  Install python 3 and try again')
        sys.exit(2)

    parser = argparse.ArgumentParser(description='Create Sample')
    parser.add_argument('-b', '--build', action='store_true', help='')
    parser.add_argument('-ou', '--openUnity', action='store_true', help='')
    parser.add_argument('-cs35', '--csharp35', action='store_true', help='')
    parser.add_argument('-cs46', '--csharp46', action='store_true', help='')
    parser.add_argument('-pl', '--platform', type=str, default='Windows', choices=[x for x in Platforms.All], help='The platform to use.  If unspecified, windows is assumed.')
    parser.add_argument('-a', '--all', action='store_true', help='')
    args = parser.parse_args(sys.argv[1:])

    installBindings()

    Runner().run(args)

