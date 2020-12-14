# Timewarrior extension: catreport

[Timewarrior](https://timewarrior.net/) is an open source software that tracks time from the command line.
Blocks of time can be associated with tags, e. g. to get an overview of what sort of things you have been working on last week or how much time did you spend on one particular task during the last six months. 

Catreport is an extension for Timewarrior that creates a report of the tracked time for tasks in hierarchical categories.

## How to use it?
Every block of time gets only one tag of the form `project.subproject.task`. The depth of the hierarchy is arbitrary, but with more than five subcategories the output may look a bit awkward. 

After some time tracking, run:
```bash
timew catreport
```

This will create a report like this:
```bash
Task                    Time [h]            Share [%]
===========================================================
root                    200                 100.0
    projectA                110                 55.0
        task1                   20                  18.2
        task2                   30                  27.3
        task3                   20                  18.2
        unknown                 40                  36.4
    projectB                90                  45.0
        task1                   10                  11.1
        task2                   50                  55.6
        unknown                 30                  33.3
```
The given time for a category always includes the time spend in all of it's associated subcategories. For example, 110 h for projectA means task1 + task2 + task3 + unknown = 110 h. The given shares are calculated with respect to the next higher category. For example, task3 makes 18.2 % of projectA.

There are often things to do which are not easy to classify. In these cases you could always add a task to collect random arbitrary stuff like `projectA.organisation`, but you can also tag these things just with `projectA` without going down the hierarchy. Times tagged with `projectA` will automatically appear in the report as `unknown` under `projectA`.


## Installing

The extension requires only Python 3 and the python module timew-report, which can be installed via pip.
To install the extension, you just need to put the file catreport.py in your timewarrior-extensions directory (running `timew extensions` will show the right path, usually it is `~/.timewarrior/extensions`). 

## Missing features, bugs & issues

* Add option to restrict the report to a maximum depth. 
* In a report that is restricted to a time frame, there may be many tasks without any time tracked in this time frame. These are currently not shown. Add an option to include or exclude such tasks.
