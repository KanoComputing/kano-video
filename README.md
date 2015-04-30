#Kano Video

***Kano Video*** is a basic media player which allows watching of videos from
both YouTube and from local media. It allows the creation of playlists of your
favourite videos and it endeavours to make every feature easy to use. It is
designed for the ***Kano OS***.

![Kano Video Home Window](http://i.imgur.com/ZarQO4t.png)

YouTube videos are searchable from the input at the top and playlists can be
created from each video. A detailed view is also available for each video by
just clicking on the video entry

The program is written entirely in Python using **GTK 3.12** via the
[gi](https://wiki.gnome.org/action/show/Projects/GObjectIntrospection) bindings
and interfaces with either omxplayer or VLC to actually play the videos.

## Installation

To install **Kano Video** on your system, get the **kano-video** from our
package repository:

```bash
sudo apt-get install kano-video
```

If not on **Kano OS**, you might need to add our repo to your sources list:

```bash
deb http://repo.kano.me/archive/ release main
```

## Testing

This project doesn't require any compiling to run, just clone the repo and run
the main script:

```bash
git clone git@github.com:KanoComputing/kano-video.git
cd kano-video/bin
./kano-video
```

## Contributing

We welcome anyone who would like contribute to this project. Check out the [bug
tracker](https://github.com/KanoComputing/kano-video/issues) and
[wiki](https://github.com/KanoComputing/kano-video/wiki). You might also find
some useful information in the [generic contributor's
guidelines](http://developers.kano.me/get-involved/) that apply to all of our
projects.

## License

This program is licensed under the terms of the **GNU GPLv2**. See the `LICENSE`
file for the full text.
