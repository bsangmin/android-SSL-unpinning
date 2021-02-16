# bin/bash

alias=${1:-"repack"}

keytool -genkey -v -keystore keys.jks -alias ${alias} -keyalg RSA -sigalg SHA256withRSA -keysize 4096 -validity 3650

# store pass 123456
# key name repack
