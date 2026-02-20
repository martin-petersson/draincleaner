# draincleaner

Remove comments from source files.

**Disclaimer: This software is not extensively tested so should only be used used for testing right now**

## Installation and use

This is how I would install and use this, I haven't spent any time to package it properly.

clone the repo to wherever you want it:
```bash
$ git clone 
```

Make the draincleaner.py executable
```bash
$ chmod +x draincleaner.py
```

In your .bashrc file add the following, but change path to your draincleaner directory:
```bash
draincleaner() {
	/path/to/draincleaner.py "$@"
}
```

Done. Now you can run it anywhere by typing:
```
$ draincleaner
```