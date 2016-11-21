# Steam Idle Time

This program will idle multiple games at the same time to gain you play time and sometimes also *Steam Trading Cards*.

## Installation

**PIP**
```
pip install requests colorama psutil notify pypiwin32
```

## Authors

Idle-Time: [gummibeer](https://github.com/Gummibeer)

Idle-Master: [jshackles](https://github.com/jshackles)

Steamworks: [Riley Labrecque](https://github.com/rlabrecque)

Icons: [Paomedia](https://www.iconfinder.com/iconsets/small-n-flat)

## Helpers

**export black/whitelist csv from steamdb by app-ids**

```js
var csv = '';
[...].forEach(function(id) {
    csv += id + ',"' + $('[data-appid="'+id+'"]').find('a').text().trim() + '"\n';
});
console.log(csv);
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.  A copy of the GNU General Public License can be found at http://www.gnu.org/licenses/.  For your convenience, a copy of this license is included.