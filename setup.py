from setuptools import setup, find_packages
import os

version_file = os.path.join('on', 'video', 'version.txt')
version = open(version_file).read().strip()

setup(name='on.video',
      version=version,
      description="dynamic display of video files",
      long_description=open("README.rst").read() + \
                       open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone video dexterity',
      author='oeko.net mueller & brandt gbr',
      author_email='support@oeko.net',
      url='http://www.oeko.net/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['on'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.dexterity [grok]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'collective.autopermission',
          'plone.app.registry',
          #'plone.namedfile[blobs]',
          #'gdata',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      #setup_requires=["PasteScript"],
      setup_requires=['setuptools-git'],
      #paster_plugins = ["ZopeSkel"],
      )
