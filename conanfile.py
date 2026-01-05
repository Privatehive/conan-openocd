#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.system.package_manager import Apt
from conan.tools.files import patch
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.errors import ConanInvalidConfiguration
import json, os

required_conan_version = ">=2.0"

class OpenocdConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = []
    # ---Sources---
    exports = ["info.json"]
    exports_sources = ["patches/*"]
    # ---Binary model---
    settings = "os", "compiler", "build_type", "arch"
    options = {}
    default_options = {}
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = False

    def validate(self):
        valid_os = ["Linux"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def system_requirements(self):
        Apt(self).install(["libjim-dev"])

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/raspberrypi/openocd", args=["--branch sdk-%s" % self.version, "--recursive", "--depth 1"])
        patch(self, base_path="openocd", patch_file=os.path.join("patches", "add_spi_flash.patch"))

    def build(self):
        self.run("cd openocd && ./bootstrap")
        autotools = Autotools(self)
        autotools.configure(build_script_folder="openocd", args=["--enable-picoprobe", "--disable-doxygen-html", "--disable-werror"])
        autotools.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ['bin']
