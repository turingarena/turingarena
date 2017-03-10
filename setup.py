#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build and installation routines for task-wizard.

"""

import io
import re
import os

from setuptools import setup, find_packages


setup(
    name="task-wizard",
    version="0.2",
    author="",
    author_email="",
    url="",
    download_url="",
    description="",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cmsRunTests=cmstestsuite.RunTests:main",
            "cmsReplayContest=cmstestsuite.ReplayContest:main",
            "cmsAdaptContest=cmstestsuite.AdaptContest:main",
            "cmsTestFileCacher=cmstestsuite.TestFileCacher:main",
            "cmsAuthServer=cmscontrib.AuthServer:main",
            "cmsAddAdmin=cmscontrib.AddAdmin:main",
            "cmsAddParticipation=cmscontrib.AddParticipation:main",
            "cmsAddStatement=cmscontrib.AddStatement:main",
            "cmsAddSubmission=cmscontrib.AddSubmission:main",
            "cmsAddTeam=cmscontrib.AddTeam:main",
            "cmsAddTestcases=cmscontrib.AddTestcases:main",
            "cmsAddUser=cmscontrib.AddUser:main",
            "cmsCleanFiles=cmscontrib.CleanFiles:main",
            "cmsComputeComplexity=cmscontrib.ComputeComplexity:main",
            "cmsDumpExporter=cmscontrib.DumpExporter:main",
            "cmsDumpImporter=cmscontrib.DumpImporter:main",
            "cmsDumpUpdater=cmscontrib.DumpUpdater:main",
            "cmsExportSubmissions=cmscontrib.ExportSubmissions:main",
            "cmsImportContest=cmscontrib.ImportContest:main",
            "cmsImportTask=cmscontrib.ImportTask:main",
            "cmsImportDataset=cmscontrib.ImportDataset:main",
            "cmsImportTeam=cmscontrib.ImportTeam:main",
            "cmsImportUser=cmscontrib.ImportUser:main",
            "cmsRWSHelper=cmscontrib.RWSHelper:main",
            "cmsRemoveContest=cmscontrib.RemoveContest:main",
            "cmsRemoveParticipation=cmscontrib.RemoveParticipation:main",
            "cmsRemoveSubmissions=cmscontrib.RemoveSubmissions:main",
            "cmsRemoveTask=cmscontrib.RemoveTask:main",
            "cmsRemoveUser=cmscontrib.RemoveUser:main",
            "cmsSpoolExporter=cmscontrib.SpoolExporter:main",
            "cmsMake=cmstaskenv.cmsMake:main",
            "cmsYamlImporter=cmscompat.YamlImporter:main",
            "cmsYamlReimporter=cmscompat.YamlReimporter:main",
        ]
    },
    install_requires=[
        "grako"
    ],
    keywords="",
    license="",
    classifiers=[]
)
