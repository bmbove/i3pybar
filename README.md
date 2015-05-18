i3pybar
-------

Not being particularly happy with the existing python options for an i3 status
bar, this is an attempt at writing my own to fit some basic needs.

**Current Goals:**

* Use only the python standard library and basic \*nix system info for all core
  functionality.
* **Efficiently** monitor the following:
    * Time
    * CPU usage
    * RAM usage
    * Disk usage
    * Network Info, including speed and transmitted data, and wifi status
    * ACPI
* Provide an extremely simple framework for writing plugins
