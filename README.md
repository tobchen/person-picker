# Person Picker

The perfect script for picking persons.

## Description

The *Person Picker* randomly proposes a person from a given list to be picked or rejected, factoring in individual weights. Whenever a person is picked, their weight is reset to 1.0 - if that person is rejected, however, their weight is increased. Each proposal, the weights of the persons not proposed are increased.

$\mathrm{weight}_i = 1.0 + \mathrm{unproposedFactor} * \mathrm{timesUnproposed}_i + \mathrm{rejectedFactor} * \mathrm{timesRejected}_i$

On startup, persons can be deactivated so as not to be considered for this script's runtime (meaning neither will they be proposed nor will their weight be changed).

## Usage

To start the *Person Picker,* run: `python3 picker.py <settings>`, with `<settings>` being the path to a settings file. If no path is given, the *Person Picker* will look for a *settings.json* in the working path.

The user is presented with a choice to exclude persons for this script's runtime. Either enter a comma-separated list of numbers for persons to exclude or leave a blank line to continue.

The *Person Picker* will now randomly propose a person (considering every non-excluded person's weights), and the user can either accept the proposal (type `y`) or reject it. Each pass will readjust every non-excluded person's weight and resave the settings file.

Note that to properly work the *Person Picker's* user needs rights to:
- Read the settings file
- Write a temporary settings file in the settings file's directory
- Replace the settings file with the temporary settings file

## Settings

See *example.json* in this project's root for an example settings file.

```jsonc
{
    "unproposedFactor": 0.5, // Optional, default: 0.5
    "rejectedFactor": 0.2, // Optional, default: 0.2
    "persons": [ // Optional, default: empty
        {
            "name": "Name", // Required
            "timesUnproposed": 0, // Optional, default: 0
            "timesRejected": 0 // Optional, default: 0
        }
    ]
}
```

Note that the settings file will be overwritten during runtime, as individual weights are changing.

## Version History

### Version 1.0 (2023-04-30)

- Initial release
