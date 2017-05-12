from distutils.core import setup

setup(
  name='irq_reeler',
  packages=['irq_reeler'],
  license="GPL-3.0",
  version='0.2',
  description="""
  Frontend to the linux kernel exported
  IRQs (soft and hard) procfs interface
  """,
  author='Matthias Tafelmeier',
  author_email='matthias.tafelmeier@gmx.net',
  scripts=['./irq_reeler/irq_reeler'],
  url='https://github.com/cherusk/opes',
  download_url='https://github.com/cherusk/opes/irq/dist/0.1.tar.gz',
  install_requires=['tabulate'],
  keywords=['IRQ', 'linux', 'tool', 'kernel', 'tuning', 'softirq', 'hardIRQ', 'analytics'],
  classifiers=[],
)
