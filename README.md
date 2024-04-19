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
