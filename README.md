# botsProject
This project contains bots made for the programme IT-Spåret on Ädelfors Folkhögskola.
The bots are deployed to an e2-micro VM instance on the Google Cloud Platform (GCP).
This VM instance uses Ubuntu 22.04 LTS which currently supports Python version 3.10.
This means that I have hard-coded a strict requirement of Python 3.10 in every bot.

This repository is configured for development in the PyCharm IDE, use it for the optimal development experience.
The bots can be tested locally (with some difficulty, and ONLY ON LINUX), the process required to do so is documented below.


## How to develop and test the bots
NOTE: THE BOTS CAN CURRENTLY ONLY BE TESTED ON LINUX!! You can develop just fine on Windows, but you can't test the bots on a Windows machine.

Firstly, make sure that you have Python 3.10 installed. It is the default version on Ubuntu 22.04 & 22.10, Debian 11, and a few other distros. It is required by this project.

Secondly, install  PyCharm (for a vastly improved development experience), [install the Community edition here](https://www.jetbrains.com/pycharm/download/).

Thirdly, create a new project in PyCharm, by "Get from VCS" in the Welcome window -> then choose "GitHub" among the options in the left pane, and follow the config. Once set up, choose the right project.

Now, from the built-in cosole in PyCharm, run `pip install -r requirements.txt` which installs the dependencies of the bots.

!!!LINUX ONLY PART STARTS HERE!!!
IMPORTANT STEP: Send the messages !stopWorky and !stopFoody on the Discord server to kill the bots.

Now you can freely test anyone of the bots simply py pushing the "run" (green right triangle) button while in one of the scripts in PyCharm.
!!!LINUX ONLY PART ENDS HERE!!!

WHEN YOU'RE DONE: Push the changes to GitHub. The changes are automagically deployed to the GCP instance.
