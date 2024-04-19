# Home Assistant integration for MPC-HC and MPC-BE
This integration was in the past integrated into Home Assistant core then abandonned. I have updated it to make it work with new releases and added new functionalities

The mpchc platform allows you to connect a Media Player Classic Home Cinema (MPC-HC) or MPC-BE to Home Assistant. It will allow you to see the current playing item, control playback and respond to changes in the player’s state.

For this component to function, you will need to enable the Web Interface in the MPC-HC options dialog.
![image](https://github.com/albaintor/homeassistant-mpchc/assets/118518828/c2e834df-ffd8-455a-9b41-a348b8b2b398)

HACS has to be installed on your Home Assistant instance.

## Features to be considered in the future
- ~~Add remote entity for additional commands~~ [done]
- ~~Migrate code to asyncio~~ [done]
- Media browsing
- ~~Add config flow to avoid manual configuration inside `configuration.yaml`~~ [done]


## Installation

Copy the `custom_components` content to your home assistant `/config/custom_components/` folder.

Beware that the existing custom_components folder in Home Assistant could contain other integrations. You just have to copy the `mpchc` subfolder into the `custom_components` folder so that it sits next to the other components.


## Configuration through setup flow
Go into Integrations > Add an integration, and select MPC-HC
![image](https://github.com/albaintor/homeassistant-mpchc/assets/118518828/2b7c4a71-1248-4d5b-8d67-1b2b83570bc2)

Then configure :
- Name of your MPC-HC instance that will be displayed in Home Assistant
- Host of the MPC-HC (ip or hostname)
- Port (if not changed else let default port)


## Configuration from config file (not recommended)
Then to add MPC-HC to your installation, add the following to your `configuration.yaml` file:
```yaml
# Example configuration.yaml entry
media_player:
  - platform: mpchc
    host: http://192.168.0.123
```

Configuration variables:
- host (Required): The host name or address of the device that is running MPC-HC.
- port (Optional): The port number. Defaults to 13579.
- name (Optional): The name of the device used in the frontend.

Restart Home Assistant and you should have your new component available. MPC-HC has to be running of course

## List of commands for remote entity
The remote entity lets send commands
Here is the commands list :

| Command                        | Description |
|--------------------------------|-------------|
| OPEN_FILE_QUICK                |             |
| OPEN_FILE                      |             |
| OPEN_DVD                       |             |
| OPEN_DEVICE                    |             |
| OPEN_FOLDER                    |             |
| OPEN_ISO_FILE                  |             |
| RESUME_FILE                    |             |
| SAVE_AS                        |             |
| SAVE_PICTURE                   |             |
| SAVE_PICTURE_AUTO              |             |
| SAVE_DISPLAYED_PICTURE_AUTO    |             |
| SAVE_PICTURE_CLIPBOARD         |             |
| SAVE_THUMBS                    |             |
| LOAD_SUBTITLES_EXT             |             |
| SAVE_SUBTITLES                 |             |
| CLOSE                          |             |
| PROPERTIES                     |             |
| EXIT                           |             |
| PLAY_PAUSE                     |             |
| PLAY                           |             |
| PAUSE                          |             |
| STOP                           |             |
| MENU_SUBTITLES                 |             |
| MENU_AUDIO                     |             |
| MENU_GOTO                      |             |
| NEXT_PICTURE                   |             |
| PREVIOUS_PICTURE               |             |
| GOTO                           |             |
| SPEED_UP                       |             |
| SPEED_DOWN                     |             |
| SPEED_NORMAL                   |             |
| AUDIO_DELAY_INCREASE           |             |
| AUDIO_DELAY_DECREASE           |             |
| STEP_FORWARD                   |             |
| STEP_BACKWARD                  |             |
| STEP_FORWARD_MEDIUM            |             |
| STEP_BACKWARD_MEDIUM           |             |
| STEP_FORWARD_MEDIUM_LARGE      |             |
| STEP_BACKWARD_LARGE            |             |
| NEXT_KEY_PICTURE               |             |
| PREVIOUS_KEY_PICTURE           |             |
| GOTO_START                     |             |
| NEXT                           |             |
| PREVIOUS                       |             |
| NEXT_FILE                      |             |
| PREVIOUS_FILE                  |             |
| REPEAT                         |             |
| MENU_RECENT_FILES              |             |
| MENU_HISTORY                   |             |
| BOOKMARK_ADD                   |             |
| MENU_BOOKMARK                  |             |
| SHOW_HEADER_MENUS              |             |
| SHOW_STATUSBAR                 |             |
| SHOW_CONTROLBAR                |             |
| SHOW_OSD                       |             |
| SHOW_STATS                     |             |
| SHOW_STATUS                    |             |
| SUBTITLES_SYNC                 |             |
| SHOW_PLAYLIST                  |             |
| VIEW_MINIMAL                   |             |
| VIEW_COMPACT                   |             |
| VIEW_NORMAL                    |             |
| VIEW_FULLSCREEN                |             |
| VIEW_FULLSCREEN_KEEPRESOLUTION |             |
| VIEW_ZOOM_50                   |             |
| VIEW_ZOOM_100                  |             |
| VIEW_ZOOM_200                  |             |
| VIEW_ZOOM_AUTO                 |             |
| VIEW_NEXT                      |             |
| VIEW_WINDOW_HALF               |             |
| VIEW_WINDOW_ORIGIN             |             |
| VIEW_WINDOW_DOUBLE             |             |
| VIEW_WINDOW_ADJUST             |             |
| VIEW_WINDOW_ADJUST_INSIDE      |             |
| VIEW_WINDOW_VIDEO1             |             |
| VIEW_WINDOW_VIDEO2             |             |
| VIEW_WINDOW_ADJUST_OUTSIDE     |             |
| VIEW_WINDOW_SWAP_VIDEO         |             |
| VIEW_ALWAYS_ONTOP              |             |
| VIEW_RESET                     |             |
| VOLUME_UP                      |             |
| VOLUME_DOWN                    |             |
| VOLUME_MUTE                    |             |
| VOLUME_GAIN_UP                 |             |
| VOLUME_GAIN_DOWN               |             |
| VOLUME_GAIN_OFF                |             |
| VOLUME_GAIN_MAX                |             |
| VOLUME_CENTER_UP               |             |
| VOLUME_CENTER_DOWN             |             |
| VOLUME_AUTO                    |             |
| BRIGHTNESS_UP                  |             |
| BRIGHTNESS_DOWN                |             |
| CONTRAST_UP                    |             |
| CONTRAST_DOWN                  |             |
| SATURATION_UP                  |             |
| SATURATION_DOWN                |             |
| COLORS_RESET                   |             |
| MENU_DVD_TITLE                 |             |
| MENU_DVD_MAIN                  |             |
| MENU_DVD_SUBTITLES             |             |
| MENU_DVD_AUDIO                 |             |
| MENU_DVD_ANGLE                 |             |
| MENU_DVD_CHAPTERS              |             |
| MENU_DVD_LEFT                  |             |
| MENU_DVD_RIGHT                 |             |
| MENU_DVD_UP                    |             |
| MENU_DVD_DOWN                  |             |
| MENU_DVD_SELECT                |             |
| MENU_DVD_BACK                  |             |
| MENU_DVD_EXIT                  |             |
| MENU_OPTIONS                   |             |
| AUDIO_TRACK_NEXT               |             |
| AUDIO_TRACK_PREVIOUS           |             |
| SUBTITLES_NEXT                 |             |
| SUBTITLES_PREVIOUS             |             |
| SUBTITLES_TOGGLE               |             |
| SUBTITLES_RELOAD               |             |
| SUBTITLES_POSITION_UP          |             |
| SUBTITLES_POSITION_DOWN        |             |
| SUBTITLES_POSITION_LEFT        |             |
| SUBTITLES_POSITION_RIGHT       |             |
| SUBTITLES_POSITION_RESET       |             |
| SUBTITLES_SIZE_DECREASE        |             |
| SUBTITLES_SIZE_INCREASE        |             |
| MENU_OSD_TIMELEFT              |             |
| MENU_OSD_LOCALTIME             |             |
| MENU_OSD_CURRENTFILE           |             |
| SUBTITLES_PREVIOUS2            |             |
| SUBTITLES_NEXT2                |             |
| SUBTITLES_OFFSET_LEFT          |             |
| SUBTITLES_OFFSET_RIGHT         |             |
| SUBTITLES_DELAY_INCREASE       |             |
| SUBTITLES_DELAY_DECREASE       |             |
| VIEW_WINDOW_MOVE_MAINSCREEN    |             |
| VIEW_PIVOTE_INV_CLOCKWISE      |             |
| VIEW_PIVOTE_CLOCKWISE          |             |
| VIEW_PIVOTE_FLIP               |             |
