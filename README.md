# draincleaner

Remove comments from source files.

**Disclaimer: This software is not extensively tested so should only be used used for testing right now**

## Installation instructions (Linux and MacOS)

This is how I would install and use this, I haven't spent any time to package it properly.

clone the repo to wherever you want it:
```bash
$ git clone https://gitea.efforting.tech/interface/draincleaner.git
```

Make the draincleaner.py executable
```bash
$ chmod +x draincleaner.py
```

In your .bashrc file located in your users home directory (on MacOS it's the .zshrc file in /Users/user/) add the following:

```bash
draincleaner() {
	/path/to/draincleaner.py "$@"
}
```
change the path to point to the directory where draincleaner is located.

Done. Now you can run it anywhere from your terminal by typing:
```
$ draincleaner
```

# Known issues

* --show-strings fails to detect and print f-strings.
