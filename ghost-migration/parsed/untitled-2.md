---
title: "Enhancing git-ls-tree"
slug: "untitled-2"
author: "CJ Harries"
draft: true
---

It's no secret that I tend to err on the side of verbosity. I like writing, I like explaining, and I like exposing minutae. I also know how tedious reading my output can be. Sharp diagrams and pretty code blocks are great tools to mask my garrulous explorations.

A good figure needs to communicate as much as possible. A naive explanation would be that your readers will use your figures to provide context for the surrounding text. Pragmatically, however, your readers are forming a tl;dr by skimming the preformatted or oddly colored elements on the page. The more information you can cram in, the better (meaningful information, that is, not just the kitchen sink).

File structure figures are widely used for plenty of good reasons. Illustrating the project tree, defining an environment, and finding patterns are some common use-cases. In general, knowing how the moving parts are connected goes a long way toward fully grasping how a tool works.

There are plenty of ways to diagram a directory tree. Some of them are a labor of love, some of them are quick and dirty, and some of them are actually pretty neat. I spent this weekend combining a couple of these methods into a package I think I'll be using heavily, and figured it was worth exploring in a post.

If you're into spoilers, the **tl;dr** is [`tree`](http://mama.indstate.edu/users/ice/tree/). If `tree` isn't available for your system, get a new one.

<!-- MarkdownTOC -->

- [The Bad](#thebad)
    - [Screenshots](#screenshots)
    - [Manual Generation](#manualgeneration)
- [The Ugly](#theugly)
    - [`find`](#find)
    - [`ls`](#ls)
    - [`git`](#git)
        - [`git-ls-files`](#git-ls-files)
        - [`git-ls-tree`](#git-ls-tree)
- [The Good](#thegood)
    - [`tree`](#tree)
    - [`git-ls-anytree`](#git-ls-anytree)

<!-- /MarkdownTOC -->

## The Bad

### Screenshots

Unless you're writing a book that will only ever be printed and will never be digitized, taking a screenshot of your file explorer is a great way to annoy the hell out of your readers. Any benefits gained from the visual cues icons provide are immediately lost the second someone loads the totally static, non-interactable figure electronically.

### Manual Generation

It's really easy to slap together an example structure using preformatted text. Because it's easy, it's both accessible and widespread. I'm sure you've seen something like this on GitHub in the last week:

```
root-directory/
    .rcfile - not as cool as rc cars
    src/ - holds the source files
        main-file - probably does important things
    test/ - holds the test files
        test-main-file - you test your code, right
    dist/ - holds code ready for distribution
        compiled-posix-binaries-only - too easy to pass up
```

Figures like this are a labor of love. I can't imagine any other reason why someone would manually build a static representation of a dynamic system. You can't guarantee many things about code, compilation included, but you can guarantee that the API will always change. API changes often mean file system changes, so the only way that figure will stay updated is if you love the tedious process of manually recreating all your trees.

Before you point out the initial creation investment is fairly low, which would make manual generation an attraction option, I'd like to rehash that last sentence: quick manual generation is followed by lengthy manual maintenance. I'm not a helicopter coder; I believe in letting go of the things I love.

## The Ugly

### `find`

[`find`](http://man7.org/linux/man-pages/man1/find.1.html) should be in every coder's repertoire. Its `exec` action commands an incredible amount of versality that other ubiquitious tools lack (often because chaining `find` is a better idea than reimplementing). If you need to perform an action on a subset of your tree, `find` will carry the day.

Out of the box, though, `find` is about as spartan as it gets. Its default action, `print`, simply prints the discovered files, one per line.

```
$ find . -type f -name '*.py'
./old_post/compile.py
./posts/compile.py
./posts/scratch.py
```

The structure is certainly there, but its context is missing. There are no visual cues to intrinsically establish relationships either. Remember. `find`'s purpse in POSIX is to locate files, not print them. It is easily capable of more complicated printing via [the `-ls` flag](http://man7.org/linux/man-pages/man1/find.1.html). It's a shortcut to `ls -dils`.

```
$ find . -type f -name '*.py' -ls
532902  120 -rw-r--r--   1 root     root       120842 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/xcodeproj_file.py
532841    8 -rw-r--r--   1 root     root         6387 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/MSVSProject.py
532851   20 -rw-r--r--   1 root     root        20063 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/common.py
532898   64 -rw-r--r--   1 root     root        65086 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/xcode_emulation.py
532896    4 -rw-r--r--   1 root     root         1247 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/simple_copy.py
532853    8 -rw-r--r--   1 root     root         4945 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/easy_xml.py
532895   12 -rw-r--r--   1 root     root        10366 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/ordered_dict.py
532901   12 -rw-r--r--   1 root     root        10585 Mar 21  2017 ./node_modules/node-gyp/gyp/pylib/gyp/xcode_ninja.py
```

Even so, you typically see users on SO telling you to just `-exec ls` (well, I saw three posts while trying to document `-ls`, and zero about `-ls`). It is the file lister, after all. Again, the context of the information is lost. Neither one of these presentations demonstrate at a glance what's actually happening with the structure.

### `ls`

`ls` is another [ridiculously useful tool](http://man7.org/linux/man-pages/man1/ls.1.html). I think I actually have three separate aliases for my most common `ls` usage in my `.zshrc` alone. For the most part, I use something like this (sadly you can't see the color):

```
$ ls --group-directories-first --color=auto --all --human-readable -l
total 0
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 .
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 ..
drwxrwxrwx 0 cjharries cjharries 512 Nov 12 18:56 bin
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 include
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 lib
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 local
-rw-rw-rw- 1 cjharries cjharries  60 Nov  5 20:45 pip-selfcheck.json
```

`ls` has a massive amount of options. It can do so many things. If, like me, you've just been using defaults because you never knew they defaults, you're in for a surprise. The `--color` option is [ridiculously extensible](http://linux-sxs.org/housekeeping/lscolors.html). You probably have something like this in your `env` already.

```
$ echo $LS_COLORS
rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:
su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:
*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:
*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:
*.lzo=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:
*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:
*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:
*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:
*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:
*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:
*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:
*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:
*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:
*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:
*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:
```
That's a bunch of text to figure out. [This repo](https://github.com/trapd00r/LS_COLORS) has an amazing example of a large collection, and there are more great examples [from SE](https://askubuntu.com/questions/17299/what-do-the-different-colors-mean-in-ls).

Now, having gushed about `ls`, I again have to point out that it too lacks visual cues and context. The most detailed color scheme is just a bank of Christmas lights to anyone not in the know. Learning to read `ls` well takes years of practice. I'd hazard a guess and say forever, but I might suddenly gain some massive insight into how 42 applies to everything in a few years.

It's also got some downsides. By default, it operates on a single directory. That's a big deal. I don't remember the last time I worked on a project that that stayed in a single directory (okay, well, a good and maintainable project that's still around). `ls` provides a recursive option, but's almost offensive.

```bash
$ ls -R . -alh
.:
total 193K
drwxrwxrwx 0 cjharries cjharries  512 Nov  5 20:45 .
drwxrwxrwx 0 cjharries cjharries  512 Nov 12 18:56 ..
drwxrwxrwx 0 cjharries cjharries  512 Nov  5 20:45 signatures
drwxrwxrwx 0 cjharries cjharries  512 Nov  5 20:45 tool
-rw-rw-rw- 1 cjharries cjharries 2.4K Nov  5 20:45 archive.py
-rw-rw-rw- 1 cjharries cjharries 2.6K Nov  5 20:45 archive.pyc
-rw-rw-rw- 1 cjharries cjharries  19K Nov  5 20:45 bdist_wheel.py
-rw-rw-rw- 1 cjharries cjharries  17K Nov  5 20:45 bdist_wheel.pyc

./signatures:
total 48K
drwxrwxrwx 0 cjharries cjharries  512 Nov  5 20:45 .
drwxrwxrwx 0 cjharries cjharries  512 Nov  5 20:45 ..
-rw-rw-rw- 1 cjharries cjharries 6.9K Nov  5 20:45 djbec.py
-rw-rw-rw- 1 cjharries cjharries  12K Nov  5 20:45 djbec.pyc

./tool:
total 32K
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 .
drwxrwxrwx 0 cjharries cjharries 512 Nov  5 20:45 ..
-rw-rw-rw- 1 cjharries cjharries 14K Nov  5 20:45 __init__.py
-rw-rw-rw- 1 cjharries cjharries 14K Nov  5 20:45 __init__.pyc
```

This is, by far, the worst showing of the good tools. Context was not hidden in this presentation, it now lives in three separate postal codes. I think I do that accidentally once every few months because I forget just how terrible it is. It's much worse without list formatting. Not only does any look connected to anything, `ls` has just throw filenames on the screen wherever (which is what happens when you're great at focusing on a single thing but can't see the big picture):

```
$ /bin/ls -R .
./virtualenv-15.1.0-py2.7.egg/EGG-INFO:
dependency_links.txt  entry_points.txt  not-zip-safe  PKG-INFO  SOURCES.txt  top_level.txt

./virtualenv-15.1.0-py2.7.egg/virtualenv_support:
argparse-1.4.0-py2.py3-none-any.whl  __init__.py  __init__.pyc  pip-9.0.1-py2.py3-none-any.whl  setuptools-28.8.0-py2.py3-none-any.whl  wheel-0.29.0-py2.py3-none-any.whl

./werkzeug:
_compat.py   datastructures.py   exceptions.py   filesystem.pyc  http.py      __init__.pyc   local.py           posixemulation.pyc  routing.py   script.pyc    serving.py   testapp.pyc  urls.py        useragents.pyc  wrappers.py   wsgi.pyc
_compat.pyc  datastructures.pyc  exceptions.pyc  formparser.py   http.pyc     _internal.py   local.pyc          _reloader.py        routing.pyc  security.py   serving.pyc
```

### `git`

`git`'s got two amazing directory utilities. By now, I'm sure you understand that I mean they're great for doing your work and absolutely terrible at quickly and conveniently communicating information.

#### `git-ls-files`

#### `git-ls-tree`

## The Good

### `tree`

### `git-ls-anytree`

Shameless self-plug here.
