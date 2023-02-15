# botsProject
This project contains bots made for the programme IT-Spåret on Ädelfors Folkhögskola.
The bots are deployed to an E2.1 Micro VM instance on the Oracle Cloud Infrastructure (OCI) - which comes with a great pro: it is, and will always be free.
OCI-based VMs use the Oracle Linux OS which does not support Python versions more recent than 3.9, though.
This means that I have hard-coded a strict requirement of Python 3.9 in every bot.

This repository is configured for development in the PyCharm IDE, use it for the optimal development experience.
Unfortunately the bots can't be tested locally, though there is a very trivial GitHub Workflow which enables automatic deployment to the OCI
instance in use.
