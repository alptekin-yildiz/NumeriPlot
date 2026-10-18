# Install NumeriPlot on a Mac

This guide covers NumeriPlot 0.2.0. No Terminal, Python, or coding knowledge
is needed: drag the app from the downloaded file into **Applications** and open
it like any other Mac app. Installation takes about five minutes.
[Türkçe](MACOS_INSTALL_TR.md)

1. [Is your Mac supported?](#1-is-your-mac-supported)
2. [Download](#2-download)
3. [Copy to Applications](#3-copy-to-applications)
4. [First launch (once only)](#4-first-launch-once-only)
5. [Try the example project](#5-try-the-example-project)
6. [Updating](#6-updating)
7. [Uninstalling](#7-uninstalling)
8. [Troubleshooting](#8-troubleshooting)

## 1. Is your Mac supported?

Open **About This Mac** from the Apple menu ():

- The **Chip** line should name an Apple chip such as *Apple M1, M2, M3…*.
- **macOS** should be version 14 (Sonoma) or later.

If it says **Processor: Intel**, this app does not run on that Mac. Intel Mac,
Windows, and Linux users can run NumeriPlot from source at their own effort:
[source installation guide](SOURCE_INSTALL.md).

The app was tested only on an Apple Silicon Mac with macOS 27. macOS 14–26 is
supported but has not been tested separately.

## 2. Download

1. Open the NumeriPlot
   [0.2.0 release page](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.2.0).
2. Under **Assets** at the bottom of the page, download
   `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` (about 85 MB). The file goes to
   your **Downloads** folder.

Download NumeriPlot only from this official page.

**Optional check:** also download
`NumeriPlot-0.2.0-macOS-AppleSilicon.dmg.sha256` from the same page. Open the
Terminal app and run these two commands one after the other:

```bash
cd ~/Downloads
shasum -a 256 -c NumeriPlot-0.2.0-macOS-AppleSilicon.dmg.sha256
```

The result should say `OK`. If it says `FAILED`, do not open the file;
download it again.

## 3. Copy to Applications

1. Double-click `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` in Downloads. A window
   named **NumeriPlot 0.2.0** opens. It contains the **NumeriPlot** app, a
   shortcut to the **Applications** folder, and `Lisanslar - Licenses.txt`.

   ![The NumeriPlot 0.2.0 disk image window](images/macos-install/01-dmg-penceresi.png)

2. Drag the **NumeriPlot** icon onto the **Applications** shortcut. Copying
   takes a few seconds.
3. In the Finder sidebar, eject the **NumeriPlot 0.2.0** disk with ⏏. You can
   now delete the downloaded `.dmg` file.

Do not open the app from that window; copy it to Applications first.

## 4. First launch (once only)

NumeriPlot is free and does not carry Apple's paid developer signature. macOS
therefore stops the first launch and asks for your permission once.

> In these messages the highlighted blue button is **Move to Trash**. Do not
> choose it or press Return; choose the button named below.

1. In Finder, open **Applications** and double-click **NumeriPlot**.
2. A **“NumeriPlot” Not Opened** message appears. Choose **Done**.
3. Open **System Settings** from the Apple menu () and select
   **Privacy & Security** on the left. Scroll down to the **Security** section.
   Next to **“NumeriPlot” was blocked to protect your Mac.**, choose
   **Open Anyway**.
4. An **Open “NumeriPlot”?** message appears. Choose **Open Anyway**.
5. macOS asks for Touch ID or, with **Use Password…**, your Mac password.
   Confirm.
6. NumeriPlot opens within a few seconds.

These steps are needed only once per Mac; later launches do not ask again.
You can also open NumeriPlot from Launchpad, Spotlight (⌘ Space, then
"NumeriPlot"), or the Dock. The [Turkish guide](MACOS_INSTALL_TR.md#4-uygulamaya-ilk-açılışta-izin-verme)
shows screenshots of each message.

The **Open Anyway** button appears for about an hour after the blocked
attempt. If you cannot see it, repeat step 1 and return to Privacy & Security
right away. Apple describes this route in
[Open a Mac app from an unknown developer](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac).

> **Security:** Do not bypass a warning that says the app is **damaged** or
> contains **malware**; do not open the file, and report it. Do not use
> quarantine-removal (`xattr`) commands suggested online; the route above is
> enough.

## 5. Try the example project

1. In NumeriPlot, choose **File → 🧪 Open Example Project**. A synthetic
   Gaussian dataset opens with its plot and saved fit.
2. Look at the plot and the **Analysis Report** in the tabs on the right.
3. To keep your own copy, choose **File → 📝 Save Project As…** and pick a
   folder such as Documents. The example file itself does not change.
4. Save the figure as PNG, PDF, or SVG with **File → 🖼 Export as Image…**.

To start with your own data, use **File → 📥 Load Data…**. For detailed use,
see the [illustrated guide](https://alptekin-yildiz.github.io/NumeriPlot/en.html).

## 6. Updating

Download the new version's `.dmg` and drag it onto **Applications** as in
section 3. Choose **Replace** when macOS asks. Your projects are not inside the
app; they stay in the folders where you saved them. macOS may ask for the
permission in section 4 once more for the new version.

## 7. Uninstalling

Move **NumeriPlot** from **Applications** to the Trash. If you like, also
delete the two folders the app creates. In Finder, choose
**Go → Go to Folder…** and enter:

- `~/Library/Logs/NumeriPlot` (diagnostic logs)
- `~/Library/Caches/NumeriPlot` (font cache)

Your projects are not in these folders; they stay where you saved them.

## 8. Troubleshooting

- **No "Open Anyway" button:** follow the note in section 4. On a Mac managed
  by your institution this setting may be locked; ask your IT department.
- **Opening takes long:** NumeriPlot normally opens within a few seconds. Do
  not click the icon repeatedly. If it has not opened after a minute,
  Control-click its Dock icon, choose **Quit**, and open it again.
- **"Move to Trash" chosen by mistake:** open the Trash, Control-click
  NumeriPlot, choose **Put Back**, and repeat section 4.
- **The app opens and quits immediately:** the log file is
  `~/Library/Logs/NumeriPlot/numeriplot.log`. Remove personal paths and
  sensitive content before sharing it, and follow the
  [support guide](../SUPPORT.md).
- **Intel Mac, or macOS 13 or earlier:** this app is not supported; see the
  [source installation guide](SOURCE_INSTALL.md).

## License and source code

NumeriPlot is free software licensed under the GNU GPL v3 (version 3 only).
The app contains Qt (GNU LGPL v3), PyQt6 (GNU GPL v3), and other open-source
components under their own licenses. The full texts are in the app under
**File → ℹ️ About NumeriPlot → Third-Party Licenses**. Source archives are
published on the release page; see
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
