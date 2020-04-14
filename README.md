TimeWalk
==========
[![Build Status](https://travis-ci.org/desmondlzy/timewalk-core.svg?branch=master)](https://travis-ci.org/desmondlzy/timewalk-core)
[![Coverage Status](https://coveralls.io/repos/github/desmondlzy/timewalk-core/badge.svg?branch=dev)](https://coveralls.io/github/desmondlzy/timewalk-core?branch=dev)

This is the core program of TimeWalk, a [free](https://www.gnu.org/philosophy/free-sw.en.html), extensible software 
that helps you track you coding statistics. Everything is done locally and you have full control of your own data.

The core hosted in this repo provides you with a command line interface to invoke TimeWalk.

To make TimeWalk work, find a plugin for your text editor (VS Code coming soon).


Installation
------------

Note: General users should **not** directly install the plugin from here.

Your text editor plugins (on their way) will download the core upon their installation or activation.
Then the core will be invoked by the editor plugins via command line interface and make all the magic happen.

For plugin developers who may want to get the core program.

```
git clone https://github.com/desmondlzy/timewalk-core.git
cd timewalk-core
python setup.py install
```

Note that only python **3.5 or above** is supported.


Usage
-----

To record your coding activity on a file,

```
timewalk record --file my_script.py
```

The above command will make TimeWalk generate one *heartbeat* and stored in the database.
By calling the command along your coding (done by your editor plugin so no worries),
TimeWalk collects heartbeats and stores them as *sessions*.

After recording a couple of heartbeats, see your coding statistic in json as follows,

```
timewalk query
```

For more usage, ``timewalk --help`` get your the command line arguments help.


Plugins
-----------

TimeWalk is extensible!

The core of TimeWalk is designed to be tiny, 
but extensible and resilient to demands via the plugin system.

At this point, we have two built-in plugins shipped with the core program,
allowing detecting and tracking the languages and text editors you are using.

### Develop your own plugins

You may also extend TimeWalk by writing your plugins that tailor to your needs.

A plugin developer guide will be made available recently. Stay tuned!

And if you develop a plugin that is also open-source, please let us know and we may include your plugin in the next version of TimeWalk core.

### Enable/Disable External Plugins

Please check `~/.timewalk/config.ini` for configuration file in INI format.

Find the corresponding section of the plugin and set ``enabled=false``

Known Issues / Coming Features
---------------
- Command line interface for plugin management
    - Re-design of the current plugin system
    - Distribution through `pip`
- Finish testing on macOS/~~Linux~~
- Editor plugins


Contributing
------------
You help and contribution are more than welcomed!


I have noticed there are open-source projects around having similar (or better)
functionality as TimeWalk does. I very appreciate their work, but on the other hand
, there are still a couple of significant improvements to be made.

- Users may not send their data to a third party to get their stats. 
- Users may not pay to get their stats.
- Users may freely customize what kind of stats they intend to track. 

These simple beliefs are really what motivates TimeWalk. 
If you feel the same way as I do, please leave your precious commments.
Your suggestions/feature request/code contribution would be appreicated. 
I believe your ideas will make TimeWalk better, as well as our open-source community.

Testing
-------------
To make any code contribution, please be so kind to pass the auto-test.
```
tox
```


License
-----------
MIT License
