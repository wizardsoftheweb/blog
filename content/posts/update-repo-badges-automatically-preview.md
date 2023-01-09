---
title: "Update Repo Badges Automatically: Preview"
slug: "update-repo-badges-automatically-preview"
date: "2017-12-11T06:49:12.000Z"
author: "CJ Harries"
tags: 
  - git
  - git hooks
  - yak shave
  - raw
  - badges
  - clean-badge-branch-hooks
---

After a day of furious coding and way more debugging, I think I finally have a collection of [`git` hooks](https://git-scm.com/docs/githooks) that will properly update badge references. Check out [the repo](https://github.com/wizardsoftheweb/clean-branch-badge-hooks); it's still pretty raw. I've manually tested it with both vanilla and `git-flow` (if you're not using `git-flow`, [use it](https://github.com/nvie/gitflow#getting-started)). I'll actually flesh out the code later; for now, I'm really excited and wanted to share.

[Repo badges](https://github.com/dwyl/repo-badges) are pretty neat. They add (basically fake) authenticity to your code, and (usually) look great. Updating them is a serious pain. For most quick features, you're not touching the documentation overview that contains badges, so you forget to swap the reference. Even when you do remember to swap the reference, you usually forget to ignore the `patch`ed hunk. (If that doesn't describe you, then I meant me instead of you.)

I've investigated a few different solutions. Until this morning, I was handling (or, rather, sometimes handling) it via `clean`/`smudge` filters. They don't get triggered as often as I'd like, and things got messy. I've looked at all sorts of different `githook` combinations, but never took the time to make something work. Finally, while writing some totally unrelated code this morning (i.e. a yak shave instead of what I've been trying to write for weeks), a solution clicked.

I wanted to do two(ish) things:

1. Update badges when a new branch is created
    i. Update badges when they're not right
2. Revert badges when a branch is merged

The first was way easier than I thought. The script stores the active branch name (essentially, I believe, the ref in `.git/HEAD`) in a hidden config file (or quits when it can't be found, e.g. checking out a commit). Via the `post-checkout` hook, the script compares the stored ref with the currently active ref. If they're different refs, it parses the tracked files. After cleaning badge names, it compares the cleaned file hashes against the real file hashes. If any of those are different, it creates a new commit with a simple "Updating badge references" message (or something like that; I've been working on this since ~7a).

The first suboption was pretty easy too. Using the `post-commit` hook, the script repeats the same process, creating a new commit if the files are updated. (Possibly; I haven't tested this one very much and I just realized a couple of ways I can break that, I think.)

The second task was much harder. [`git-merge`](https://git-scm.com/docs/git-merge) doesn't work the same way [`git-commit`](https://git-scm.com/docs/git-commit) does (Either that or I don't yet fully grok how [`pygit2`](https://github.com/libgit2/pygit2) handles commits, which is a much simpler answer). I had to break it down across a few scripts. Using the `prepare-commit-msg` hook, the script stores [the hook's args](https://git-scm.com/docs/githooks#_prepare_commit_msg) to a hidden config file (which actually also happens for any commit, but only merge commits pass `merge`). The `post-commit` hook is called as normal, ensuring the original branch's badge references are correct (I suppose it could directly create a commit here which would probably throw off the merge; I'll have to try and break that). Finally, via `post-merge`, the script loads the last commit (e.g. "Merge branch 'merge-target' into current-branch"), rewrites the tracked files with the correct references, then rewrites the commit (basically `git commit --amend` except `pygit2` doesn't provide an `amend` API so I had to reverse-engineer one).
