# Ulauncher Firefox History
![screenshot](screenshot.png)
### [Ulauncher](https://ulauncher.io) extension for quickly accessing already visited websites.

## Use
> fh

List the five most popular websites in Firefox history.

> fh query

List the five most popular websites in Firefox history that matches the query

## Settings

The search results can be **aggregated by hostname**, so that visiting _twitter.com/UlauncherApp_ and _twitter.com/github_ generates _twitter.com_ as result.

The **number of results** and the **popularity criteria** can be changed in the extension's settings. The popularity can be determined by last visit date, visit count or [Firefox Frecency](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/Places/Frecency_algorithm) heuristic.


Search results can be filtered to show **bookmarks only**.

The extension also allows configuring the **Firefox Profile Location**. Since different OSs and package managers (like Snap or Flatpak) might store Firefox profiles in different places, you can provide a comma-separated list of paths to search for `profiles.ini`. The extension will use the first valid path found.

## Install
> https://github.com/rmassidda/ulauncher-firefox-history

Copy and paste this repository link inside __Add extension__ in Ulauncher's settings panel.
