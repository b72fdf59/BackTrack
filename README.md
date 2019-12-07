# BackTrack

### Introduction to BackTrack

BackTrack is a web-based application which helps project teams to plan, organize and track the whole project. It has all the essential features needed to perfectly manage an agile-based, scrum process framework project. 

Idle developers can create a project, invite manager(s) and developers to join the development team. Using the various roles, users login into a platform designed just for them- a product owner can manage the product backlog, development teams can make appropriate changes to the sprint backlog and the manager’s access rights limit him to just overlooking multiple projects while not making any changes.

### An Outline of the Limitations of BackTrack

Our project is almost the perfect tool for managing an agile-based project. Being just the first release, there is always scope for improvement and a few glitches which can be improved on. 

We would like to highlight some of the limitations of BackTrack:
- The filtering by various fields(by priority, effort hours, or by story points) functionality on the product backlog does not order the PBIs by the field you specify but always remains by the default ordering(by priority) criteria.
- We are unable to enforce that a development team must have at least 3 members to start a project even though we were able to enforce that there are cannot be more than 9 members.

We were unable to fix these issues due to the paucity of time. We focused on the features which were of most value to the customer and hence, have not implemented a few features which did not have a high priority.

### Setup

Please do this setup in the following order:

1.	Open the file in your preferred code editor.
2.	Create a virtual env for this project using the command ***pip env shell***
3.	In the terminal, your current directory will be ***/backtrack***. You must change the directory to backtrack inside the current directory using the command ***cd backtrack/***
4.	Now, to install all necessary libraries to support the smooth functioning of this application, install all packages using the command ***pip install -r requirements.txt***
5.	On installing all packages successfully, apply all migrations for the app using the command ***python manage.py migrate***
6.	On applying all migrations, you are ready to launch the app on your local server using the command ***python manage.py runserver***