The mpchc platform allows you to connect a Media Player Classic Home Cinema (MPC-HC) or MPC-BE to Home Assistant. It will allow you to see the current playing item, control playback and respond to changes in the player’s state.

For this component to function, you will need to enable the Web Interface in the MPC-HC options dialog.
![image](https://github.com/albaintor/homeassistant-mpchc/assets/118518828/c2e834df-ffd8-455a-9b41-a348b8b2b398)

HACS has to be installed on your Home Assistant instance.

**Installation**
Copy the `custom_components` content to your home assistant `/config/custom_components/` folder

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
