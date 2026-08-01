# Installing Desktop-Cat

Prebuilt downloads for every platform are on the
[Releases page](https://github.com/gavvahar/Desktop-Cat/releases) -- grab
the latest one. This page is just "how do I run the thing I downloaded";
for building from source instead, see the [README](README.md).

## Windows

Download `Desktop-Cat-windows.zip`, extract it, and run `desktop-cat.exe`
from inside the extracted folder.

If Windows Defender or SmartScreen flags it: right-click the `.exe` ->
Properties -> Unblock, or click "More info" -> "Run anyway". It's
unsigned (no code-signing certificate involved in this project) and a
freshly-built file Windows hasn't seen before, which commonly triggers
that warning on its own -- see the README's Windows section for the full
explanation.

## Linux: AppImage

Download `Desktop-Cat-x86_64.AppImage`, then:

```
chmod +x Desktop-Cat-x86_64.AppImage
./Desktop-Cat-x86_64.AppImage
```

No installation step -- it's a single self-contained file, run it directly.

## Linux: Flatpak

Download `Desktop-Cat.flatpak`, then:

```
flatpak install --user Desktop-Cat.flatpak
flatpak run io.github.gavvahar.DesktopCat
```

(Drop `--user` for a system-wide install, e.g. `sudo flatpak install
Desktop-Cat.flatpak`.) Once installed, it also shows up in your desktop's
app launcher as "Desktop Cat" like any other installed app.

## macOS

Download `Desktop-Cat-macos.zip`, unzip it, then **right-click** (not
double-click) `Desktop Cat.app` -> Open -> Open. It's unsigned (no Apple
Developer account involved in this project), so a plain double-click gets
blocked by Gatekeeper ("can't be opened because Apple cannot check it for
malicious software"); right-click-Open bypasses that once.

`pynput`'s keyboard/scroll reactions additionally need **Accessibility
permission**: System Settings -> Privacy & Security -> Accessibility ->
enable it for Desktop Cat. Without it, those reactions just silently don't
fire -- everything else still works.

**Note:** macOS support hasn't been tested on real hardware by anyone yet
(see the README for details) -- if something's actually broken here rather
than just unverified, please open an issue.
