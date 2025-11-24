[app]
title = SMS Bomber
package.name = smsbomber
package.domain = com.ahmedtharwat

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,kivy,requests

android.permissions = INTERNET,ACCESS_NETWORK_STATE
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
